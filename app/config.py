import os

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

from app.config import DEEPSEEK_API_KEY

if not DEEPSEEK_API_KEY:
    raise RuntimeError("DEEPSEEK_API_KEY is not configured")