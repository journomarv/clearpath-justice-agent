"""
Schemas used by the ClearPath Justice Agent orchestration layer.
"""

from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from app.privacy import contains_pii
from app.schemas.rules import ReliefType


class ChatRequest(BaseModel):
    """Minimal, privacy-conscious request sent to Path."""

    message: str = Field(..., min_length=1)
    relief_type_hint: Optional[ReliefType] = None

    @field_validator("message")
    @classmethod
    def reject_sensitive_identifiers(cls, value: str) -> str:
        if contains_pii(value):
            raise ValueError(
                "Please remove identifying numbers such as an ID or phone "
                "number. ClearPath collects only what is needed to route "
                "your question."
            )
        return value


class SourceRef(BaseModel):
    """Traceable knowledge source returned with an agent response."""

    id: str
    title: str
    source_type: str
    verified_date: Optional[str] = None
    url: Optional[str] = None


class ChatResponse(BaseModel):
    """Structured response returned by the ClearPath agent."""

    message: str
    next_action: str
    requires_human: bool = False
    confidence: float = 0.0
    sources: List[SourceRef] = Field(default_factory=list)
    relief_type: Optional[ReliefType] = None


class HealthChecks(BaseModel):
    """Safe health checks exposed by the API."""

    api: bool = True
    configuration: bool = True
    deepseek_available: bool = False


class HealthResponse(BaseModel):
    """Safe health response that never exposes secrets."""

    status: str
    service: str
    version: str
    checks: HealthChecks
