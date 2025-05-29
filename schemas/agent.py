
from pydantic import BaseModel, ValidationError
from typing import List, Optional, Union

class AnalysisRequest(BaseModel):
    text: str

class AnalysisResponse(BaseModel):
    summary: str
    nationalities: List[str]

class ErrorResponse(BaseModel):
    error: str
    details: Optional[str] = None