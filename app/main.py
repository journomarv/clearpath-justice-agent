from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import health, chat, assess


app = FastAPI(
    title="ClearPath Justice Agent",
    description="AI-assisted digital justice navigation for criminal-record relief.",
    version="0.2.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Register API routers
app.include_router(health.router)
app.include_router(chat.router)
app.include_router(assess.router)


@app.get("/")
async def root():
    return {
        "service": "ClearPath Justice Agent",
        "status": "ok",
        "version": "0.2.0",
    }