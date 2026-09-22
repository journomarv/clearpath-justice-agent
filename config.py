"""
Configuration management for ClearPath Justice Agent.

All configuration comes from environment variables. Nothing sensitive is
hard-coded. This module is read once (via lru_cache) and the resulting
Settings singleton is used everywhere else in the app.
"""
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings, loaded from environment variables / .env."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- DeepSeek LLM API ---
    deepseek_api_key: str = ""
    deepseek_model: str = "deepseek-chat"
    deepseek_api_base: str = "https://api.deepseek.com"

    # --- Server ---
    host: str = "127.0.0.1"
    port: int = 8000
    environment: str = "development"
    log_level: str = "INFO"

    # --- CORS ---
    cors_origins: str = "*"

    # --- Privacy ---
    pii_guard_enabled: bool = True

    @property
    def cors_origin_list(self) -> List[str]:
        if self.cors_origins.strip() == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"

    @property
    def deepseek_configured(self) -> bool:
        """True only if a non-placeholder API key is present."""
        return bool(self.deepseek_api_key) and self.deepseek_api_key != "your_api_key_here"

    def __repr__(self) -> str:  # pragma: no cover - defensive redaction
        # Never let the API key leak through logs, debuggers, or repr().
        return (
            f"Settings(environment={self.environment!r}, "
            f"deepseek_model={self.deepseek_model!r}, "
            f"deepseek_configured={self.deepseek_configured})"
        )

    __str__ = __repr__


@lru_cache
def get_settings() -> Settings:
    """Return the cached Settings singleton. Environment is read once."""
    return Settings()
