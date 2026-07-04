from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    APP_NAME: str = "MindShift API"
    APP_VERSION: str = "1.0"
    DEBUG: bool = True
    
    # Database - auto-detect: use SQLite if no Postgres DSN set
    DATABASE_URL: str = "sqlite+aiosqlite:///./mindshift.db"
    DATABASE_URL_SYNC: str = "sqlite:///./mindshift.db"
    USE_SQLITE: bool = True  # Set False for PostgreSQL
    
    # Redis (optional, not used in SQLite mode)
    REDIS_URL: str = ""
    
    # JWT
    SECRET_KEY: str = "mindshift-dev-secret-key-change-in-production-32!"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # AI (ZhipuAI / OpenAI compatible)
    AI_API_KEY: Optional[str] = None
    AI_BASE_URL: str = "https://open.bigmodel.cn/api/paas/v4"
    AI_MODEL: str = "glm-4-flash"
    
    # Stripe
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    
    # App Store
    APP_BUNDLE_ID: str = "com.nianzhuan.mindshift"
    
    # CORS
    CORS_ORIGINS: str = "*"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
