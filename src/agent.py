from fastapi import HTTPException, UploadFile
from pathlib import Path
import aiofiles
import openai
from dotenv import load_dotenv
import os
import json
import logging
from openai import  AsyncOpenAI

logger = logging.getLogger(__name__)

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "1500"))
# Configuration
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_FILE_TYPES = {".txt", ".md", ".rtf"}


openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    logger.warning("OPENAI_API_KEY not found in environment variables")

class ArticleAnalyzer:
    """Service class for analyzing articles using OpenAI API"""

    
    @staticmethod
    def create_summary_prompt(text: str) -> str:
        """Create a well-engineered prompt for article summarization"""
        return f"""
            Please provide a concise summary of the following article. Focus on:
            - Main events or topics discussed
            - Key people or organizations mentioned
            - Important outcomes or implications
            - Timeline if relevant

            Keep the summary between 3-5 sentences and make it informative yet accessible.

            Article text:
            {text}

            Summary:
        """

    @staticmethod
    def create_nationality_prompt(text: str) -> str:
        """Create a well-engineered prompt for nationality extraction"""
        return f"""
            Analyze the following article and extract ALL nationalities, countries, or geographic regions mentioned. 
            Include:
            - Countries explicitly mentioned
            - Nationalities of people mentioned (e.g., "American", "Chinese", "British")
            - Geographic regions that represent nations (e.g., "United States", "United Kingdom")

            Return ONLY a JSON array of strings with the nationalities/countries found. 
            If none are found, return an empty array [].
            Avoid duplicates and use standard country/nationality names.

            Example format: ["American", "Chinese", "German", "France", "United Kingdom"]

            Article text:
            {text}

            Nationalities/Countries (JSON array only):
            """

    @staticmethod
    async def analyze_with_openai(text: str) -> dict:
        openai_client = AsyncOpenAI(api_key=openai_api_key) if openai_api_key else None
        """Analyze text using OpenAI API"""
        if not openai_client:
            raise HTTPException(
                status_code=500,
                detail="OpenAI client not initialized. Check API key configuration."
            )
        
        try:
            # Get summary
            summary_response = await openai_client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that summarizes articles clearly and concisely."},
                    {"role": "user", "content": ArticleAnalyzer.create_summary_prompt(text)}
                ],
                max_tokens=MAX_TOKENS,
                temperature=0.3
            )
            
            # Extract and validate summary
            summary_content = summary_response.choices[0].message.content
            if summary_content is None:
                raise HTTPException(
                    status_code=500,
                    detail="OpenAI API returned empty summary response"
                )
            summary = summary_content.strip()
            
            # Get nationalities
            nationality_response = await openai_client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that extracts nationalities and countries from text. Always respond with valid JSON."},
                    {"role": "user", "content": ArticleAnalyzer.create_nationality_prompt(text)}
                ],
                max_tokens=500,
                temperature=0.1
            )
            
            # Extract and validate nationality response
            nationality_content = nationality_response.choices[0].message.content
            if nationality_content is None:
                logger.warning("OpenAI API returned empty nationality response")
                nationality_text = "[]"  # Default to empty array
            else:
                nationality_text = nationality_content.strip()
            
            # Parse nationalities JSON
            try:
                nationalities = json.loads(nationality_text)
                if not isinstance(nationalities, list):
                    nationalities = []
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse nationalities JSON: {nationality_text}")
                nationalities = []
            
            return {
                "summary": summary,
                "nationalities": nationalities
            }
            
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to analyze article with AI service: {str(e)}"
            )

async def read_uploaded_file(file: UploadFile) -> str:
    """Read and validate uploaded file"""
    # Read file content
    content = await file.read()
    file_size = len(content)
    
    # Check file size
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB"
        )
    
    # Check file extension
    file_extension = Path(file.filename).suffix.lower() if file.filename else ""
    if file_extension not in ALLOWED_FILE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed types: {', '.join(ALLOWED_FILE_TYPES)}"
        )
    
    # Decode content
    try:
        text_content = content.decode('utf-8')
    except UnicodeDecodeError:
        try:
            text_content = content.decode('latin-1')
        except UnicodeDecodeError:
            raise HTTPException(
                status_code=400,
                detail="Unable to decode file. Please ensure it's a valid text file."
            )
    
    if len(text_content.strip()) == 0:
        raise HTTPException(
            status_code=400,
            detail="File appears to be empty"
        )
    
    return text_content