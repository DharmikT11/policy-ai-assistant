# schemas.py
from pydantic import BaseModel, Field
from typing import Optional, List

class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, description="User's query")
    company_id: str = Field(..., description="The ID of the company context")

class ChatResponse(BaseModel):
    answer: str
    sources: Optional[List[str]] = None
    confidence_score: Optional[float] = None
