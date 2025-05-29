from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import openai
import os
from dotenv import load_dotenv
import logging
from pathlib import Path
import aiofiles
import uvicorn

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
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

if __name__ == "__main__":
    
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=os.getenv("ENV") == "dev"
    )