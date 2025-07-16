from pydantic_settings import BaseSettings
from functools import lru_cache
import logging
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""

    # OpenAI Configuration
    openai_api_key: Optional[str] = None

    # Application Configuration
    app_name: str = "SALLTO Herald API Gateway"
    debug: bool = False

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # CORS Configuration
    cors_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings."""
    try:
        return Settings()
    except Exception as e:
        logging.error(f"Failed to load settings: {e}")
        raise