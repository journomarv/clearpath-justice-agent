from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    deepseek_api_key: str | None = None
    deepseek_model: str = "deepseek-chat"
    deepseek_api_base: str = "https://api.deepseek.com"

    cors_origins: str = "*"
    environment: str = "development"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()


def get_cors_origins() -> list[str]:
    value = settings.cors_origins.strip()

    if value == "*":
        return ["*"]

    return [
        origin.strip()
        for origin in value.split(",")
        if origin.strip()
    ]