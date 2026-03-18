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
    groq_api_key: Optional[str] = None
    groq_model: str = "llama-3.3-70b-versatile"
    
    # Stack Auth Configuration
    stack_project_id: str
    stack_publishable_client_key: str
    stack_secret_server_key: str

    # Database Configuration
    database_url: str

    # Google Drive Configuration
    google_service_account_json: Optional[str] = None
    google_drive_folder_id: Optional[str] = None
    
    # Cloudflare R2 / S3 Configuration
    r2_endpoint_url: Optional[str] = None
    r2_access_key_id: Optional[str] = None
    r2_secret_access_key: Optional[str] = None
    r2_bucket_name: Optional[str] = None
    r2_public_domain: Optional[str] = None  # Optional: for public URLs

    # LLM Configuration
    max_allowed_tokens: int = 20_000
    llm_strategy: str = "auto"  # Choices: auto, local, remote, groq
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3"
    groq_model: str = "llama-3.3-70b-versatile"
    groq_api_key: Optional[str] = None

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