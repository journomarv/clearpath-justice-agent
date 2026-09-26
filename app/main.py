from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import get_cors_origins
from app.routers import assess, chat, health

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse


BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"


app = FastAPI(
    title="ClearPath Justice Agent",
    description=(
        "Path is an AI-assisted digital justice assistant "
        "helping people navigate criminal-record relief "
        "and expungement in South Africa."
    ),
    version="0.2.1",
)

app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
async def read_index():
    return FileResponse('frontend/index.html')
    
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    python - <<'PY'
from pathlib import Path

p = Path("app/main.py")
s = p.read_text()
s = s.replace("    allow_credentials=True,", "    allow_credentials=False,")
p.write_text(s)
PY

    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)


app.include_router(health.router)
app.include_router(chat.router)
app.include_router(assess.router)


@app.get("/")
async def root():
    """Serve the Path conversational interface."""
    return FileResponse(FRONTEND_DIR / "index.html")


app.mount(
    "/frontend",
    StaticFiles(directory=FRONTEND_DIR),
    name="frontend",
)
