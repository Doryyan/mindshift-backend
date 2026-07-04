from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./mindshift_dev.db"
    SECRET_KEY: str = "mindshift-dev-secret-2026"
    ZHIPUAI_API_KEY: str = "your-api-key-here"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    PROJECT_NAME: str = "念转 MindShift"
    VERSION: str = "1.0.0"
    DEBUG: bool = True

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


settings = Settings()
