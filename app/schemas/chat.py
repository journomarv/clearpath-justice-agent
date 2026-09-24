from typing import Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    pathway: Optional[str] = None


class ChatResponse(BaseModel):
    answer: str
    pathway: Optional[str] = None
    intent: Optional[str] = None
    question_type: Optional[str] = None
    knowledge_sources: list[str] = []
    uncertainty: Optional[str] = None
    next_step: Optional[str] = None