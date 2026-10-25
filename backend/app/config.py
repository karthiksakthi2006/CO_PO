from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "CO-ATTAIN PRO AI"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    
    # Database
    DATABASE_URL: str = "sqlite:///./co_attain.db"
    
    # JWT Authentication
    JWT_SECRET_KEY: str = "coattain-super-secret-production-and-dev-key-change-in-prod-2026"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    
    # Optional AI Provider (OpenAI/Gemini/Custom)
    AI_PROVIDER: str = "deterministic"  # "deterministic" or "openai" or "gemini"
    AI_API_KEY: str = ""
    AI_API_URL: str = ""
    AI_MODEL: str = "gpt-4o-mini"
    
    # Security & limits
    MAX_UPLOAD_SIZE_MB: int = 15
    PASSWORD_MIN_LENGTH: int = 8
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()

# Updated: skill-gap project configuration v1.1
