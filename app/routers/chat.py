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

    question_type = knowledge_service.identify_question_type(
        request.message
    )

    pathway = request.pathway

    if not pathway:
        pathway = knowledge_service.identify_pathway(
            request.message
        )

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
            question_type=question_type,
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
        question_type=result.get(
            "question_type",
            question_type,
        ),
        knowledge_sources=result.get(
            "knowledge_sources",
            [],
        ),
        uncertainty=result.get("uncertainty"),
        next_step=result.get("next_step"),
    )