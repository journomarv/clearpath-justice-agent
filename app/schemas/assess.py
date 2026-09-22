from pydantic import BaseModel, Field


class AssessRequest(BaseModel):
    message: str = Field(..., min_length=1)


class AssessResponse(BaseModel):
    possible_pathway: str
    information_needed: list[str]
    preliminary_guidance: str
    disclaimer: str