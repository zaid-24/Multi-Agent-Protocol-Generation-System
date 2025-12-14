from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # LLM Settings
    GOOGLE_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    
    # Model Choices
    DEFAULT_MODEL_PROVIDER: str = "google" # google, openai, anthropic
    DEFAULT_MODEL_NAME: str = "gemini-1.5-flash"

    # Database
    DATABASE_URL: str = "postgresql+psycopg2://user:password@localhost/cerina_db" # Example for pgvector

    class Config:
        env_file = ".env"

settings = Settings()

