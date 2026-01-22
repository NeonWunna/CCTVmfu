from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    # Use SQLite as default for development/Codespaces (no Docker needed)
    # For production with PostgreSQL, set DATABASE_URL in .env
    DATABASE_URL: str = "sqlite:///./cctv.db"
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
