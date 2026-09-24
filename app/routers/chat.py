from fastapi import APIRouter, HTTPException

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.deepseek import (
    DeepSeekError,
    DeepSeekService,
)
from app.services.knowledge import KnowledgeService


router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    knowledge_service = KnowledgeService()

    # Determine the matter/pathway when the frontend has not supplied one.
    pathway = request.pathway

    if not pathway:
        pathway = knowledge_service.identify_pathway(
            request.message
        )

    # Keep the underlying matter separate from the user's intent.
    intent = knowledge_service.identify_intent(
        request.message
    )

    context = knowledge_service.retrieve(
        message=request.message,
        pathway=pathway,
    )

    if not context:
        context = [
            {
                "source": "ClearPath Justice safeguards",
                "content": (
                    "AI assists, not adjudicates. "
                    "Do not make final legal determinations or guarantees."
                ),
            }
        ]

    service = DeepSeekService()

    try:
        result = await service.generate_response(
            message=request.message,
            knowledge=context,
            pathway=pathway,
            intent=intent,
        )

    except DeepSeekError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from None

    except Exception:
        raise HTTPException(
            status_code=502,
            detail="The AI service could not be reached.",
        ) from None

    return ChatResponse(
        answer=result["answer"],
        pathway=result.get("pathway", pathway),
        intent=result.get("intent", intent),
        knowledge_sources=result.get("knowledge_sources", []),
        uncertainty=result.get("uncertainty"),
        next_step=result.get("next_step"),
    )
