from fastapi import APIRouter

from app.schemas.assess import AssessRequest, AssessResponse
from app.services.knowledge import KnowledgeService

router = APIRouter(tags=["assessment"])


@router.post("/assess", response_model=AssessResponse)
async def assess(request: AssessRequest):
    knowledge_service = KnowledgeService()

    pathway = knowledge_service.identify_pathway(request.message)

    information_needed = []

    if not request.message.strip():
        information_needed.append(
            "Please provide information about the criminal record "
            "or legal remedy you are seeking."
        )

    if pathway == "unknown":
        information_needed.append(
            "The relevant legal pathway could not yet be identified."
        )

    return AssessResponse(
        possible_pathway=pathway,
        information_needed=information_needed,
        preliminary_guidance=(
            "This is a preliminary navigation assessment only. "
            "ClearPath Justice does not make a final legal determination."
        ),
        disclaimer="AI assists, not adjudicates.",
    )