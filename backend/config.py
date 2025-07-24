from pydantic_settings import BaseSettings
from functools import lru_cache
import logging
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""

    # API Keys
    api_key: str
    openai_api_key: Optional[str] = None
    openrouter_api_key: Optional[str] = None
    anthropic_api_key: str
    
    # Stack Auth Configuration
    stack_project_id: str
    stack_publishable_client_key: str
    stack_secret_server_key: str

    # Database Configuration
    database_url: str

    # LLM Configuration
    max_allowed_tokens: int = 20_000

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


def configure_logging():
    """Configure logging for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings.
    
    Returns:
        Settings: Application settings loaded from environment variables.
        
    Raises:
        ValueError: If required environment variables are missing.
    """
    configure_logging()
    logger = logging.getLogger("config")
    
    try:
        settings = Settings()
        logger.info(f"Loaded settings for {settings.app_name}")
        return settings
    except Exception as e:
        logger.error(f"Failed to load settings: {e}")
        raise ValueError(f"Configuration error: {e}. Please check your environment variables.")