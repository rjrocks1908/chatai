from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache


class Settings(BaseSettings):
    # Application settings
    app_name: str = "Chat AI"
    app_version: str = "1.0.0"
    debug: bool = False

    # API settings
    google_api_key: str

    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000

    # CORS settings
    allowed_origins: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # Memory settings
    max_conversation_history: int = 50

    # Gemini settings
    gemini_model: str = "gemini-2.0-flash-exp"
    max_tokens: int = 8192
    temperature: float = 0.1

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
