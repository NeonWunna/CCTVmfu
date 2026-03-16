from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    # Database
    # Use SQLite as default for development/Codespaces (no Docker needed)
    # For production with PostgreSQL, set DATABASE_URL in .env
    DATABASE_URL: str = "sqlite:///./cctv.db"

    # Google OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/auth/google/callback"
    FRONTEND_URL: str = "http://localhost:5173"

    # JWT
    JWT_SECRET_KEY: str = ""  # Generate with: openssl rand -hex 32
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
