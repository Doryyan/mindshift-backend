from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    APP_NAME: str = "MindShift API"
    APP_VERSION: str = "1.0"
    DEBUG: bool = True
    
    DATABASE_URL: str = "sqlite+aiosqlite:///./mindshift.db"
    DATABASE_URL_SYNC: str = "sqlite:///./mindshift.db"
    USE_SQLITE: str = "true"  # "true" or "false" as string
    
    REDIS_URL: str = ""
    SECRET_KEY: str = "mindshift-dev-secret-key-change-in-production-32!"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    AI_API_KEY: Optional[str] = None
    AI_BASE_URL: str = "https://open.bigmodel.cn/api/paas/v4"
    AI_MODEL: str = "glm-4-flash"
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    APP_BUNDLE_ID: str = "com.nianzhuan.mindshift"
    CORS_ORIGINS: str = "*"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    def is_sqlite(self) -> bool:
        return self.USE_SQLITE.strip().lower() in ("true", "1", "yes")

    def async_db_url(self) -> str:
        if self.is_sqlite():
            return self.DATABASE_URL
        # Strip any existing driver and add asyncpg
        url = self.DATABASE_URL
        if "+" in url.split("://")[0]:
            url = url.replace(url.split("://")[0].split("+")[0], "postgresql+asyncpg")
        elif url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://")
        return url

settings = Settings()
