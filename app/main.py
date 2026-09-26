"""
ClearPath Justice Agent - FastAPI application.

Endpoints:
    GET  /health         Liveness/readiness + configuration check
    POST /chat            Main conversational entry point
    GET  /relief-types    Supported relief types (for client menus, e.g. WhatsApp/Paige)

This module stays thin: it wires HTTP to app.agent and returns errors that
never expose secrets or stack traces to the caller.
"""
import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.agent import process_message
from app.config import get_settings
from app.deepseek import DeepSeekClient
from app.rules import list_supported_relief_types
from app.schemas.agent import ChatRequest, ChatResponse, HealthChecks, HealthResponse

logging.basicConfig(level=get_settings().log_level)
logger = logging.getLogger("clearpath.main")

app = FastAPI(
    title="ClearPath Justice Agent",
    description="AI-assisted navigation for criminal-record relief in South Africa. "
    "AI assists; it does not adjudicate.",
    version=__version__,
)

settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    current_settings = get_settings()
    return HealthResponse(
        status="ok",
        service="clearpath-justice-agent",
        version=__version__,
        checks=HealthChecks(
            api=True,
            configuration=True,
            deepseek_available=current_settings.deepseek_configured,
        ),
    )


@app.get("/relief-types")
async def relief_types() -> dict:
    """List relief types the agent currently has a rules handler for."""
    return {"relief_types": [rt.value for rt in list_supported_relief_types()]}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    try:
        return await process_message(request, deepseek_client=DeepSeekClient())
    except Exception as exc:  # pragma: no cover - defensive catch-all
        # Never leak internals (which could include partial secrets from
        # dependency error messages) to the caller.
        logger.exception("Unhandled error while processing chat message")
        raise HTTPException(
            status_code=500,
            detail="Something went wrong processing your message. Please try again.",
        ) from exc
