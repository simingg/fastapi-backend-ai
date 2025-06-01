from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.requests import Request
import openai
import os
from dotenv import load_dotenv
import logging
from .agents.agent import ArticleAnalyzer, read_uploaded_file
from .schemas.agent import AnalysisResponse, ErrorResponse
from typing import Optional
import sys
# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO,     
                    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                    handlers=[
                        logging.StreamHandler(sys.stdout)
                    ])
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Article Analyzer API",
    description="API for analyzing articles to extract summaries and nationalities",
    version="0.0.1"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    logger.warning("OPENAI_API_KEY not found in environment variables")


OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "1500"))

@app.get("/")
async def root():
    return {"message": "Article Analyzer API is running", "status": "ok"}


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "openai_configured": bool(openai.api_key),
        "model": OPENAI_MODEL,
        "max_tokens": MAX_TOKENS
    }

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_article(
    file: Optional[UploadFile] = File(None),
    text: Optional[str] = Form(None)
):
    """
    Analyze an article to extract summary and nationalities.
    
    You can provide either:
    - A text file upload (txt, md, rtf)
    - Raw text in the 'text' form field
    """
    
    # Validate input
    if not file and not text:
        raise HTTPException(
            status_code=400,
            detail="Either 'file' or 'text' parameter must be provided"
        )  
    try:
        # Get article text
        if file:
            article_text = await read_uploaded_file(file)
        else:
            article_text = text.strip()
            if not article_text:
                raise HTTPException(
                    status_code=400,
                    detail="Text parameter cannot be empty"
                )
        
        # Validate text length
        if len(article_text) < 50:
            raise HTTPException(
                status_code=400,
                detail="Article text is too short (minimum 50 characters)"
            )
        
        if len(article_text) > 50000:  # ~50k chars limit
            raise HTTPException(
                status_code=400,
                detail="Article text is too long (maximum 50,000 characters)"
            )
        
        # Analyze article
        logger.info(f"Analyzing article of length: {len(article_text)} characters")
        analysis_result = await ArticleAnalyzer().analyze_with_openai(article_text)
        
        return AnalysisResponse(
            summary=analysis_result["summary"],
            nationalities=analysis_result["nationalities"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in analyze_article: {str(e)}")
        raise

# Global exception handler for HTTPException
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    error_response = ErrorResponse(
        error=exc.detail,
        details=f"HTTP {exc.status_code}"
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump()
    )