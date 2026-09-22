from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import get_cors_origins
from app.routers import assess, chat, health


BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"


app = FastAPI(
    title="ClearPath Justice Agent",
    description=(
        "AI-assisted digital justice navigation for "
        "criminal-record relief and expungement."
    ),
    version="0.2.1",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)


app.include_router(health.router)
app.include_router(chat.router)
app.include_router(assess.router)


@app.get("/")
async def root():
    return FileResponse(FRONTEND_DIR / "index.html")


app.mount(
    "/frontend",
    StaticFiles(directory=FRONTEND_DIR),
    name="frontend",
)        
