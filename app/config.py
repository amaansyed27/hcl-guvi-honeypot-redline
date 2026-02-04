"""
Honeypot Application Configuration

Loads environment variables and provides centralized configuration.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Configuration
    api_key: str = Field(..., env="API_KEY", description="API key for authenticating requests")
    port: int = Field(default=8000, env="PORT")
    
    # Google Gemini Configuration
    google_api_key: str = Field(..., env="GOOGLE_API_KEY", description="Gemini API key
    ")
    model_name: str = Field(default="gemini-2.5-flash", env="MODEL_NAME")
    
    # GUVI Callback
    guvi_callback_url: str = Field(
        default="https://hackathon.guvi.in/api/updateHoneyPotFinalResult",
        env="GUVI_CALLBACK_URL"
    )
    
    # Agent Configuration
    max_conversation_turns: int = Field(default=20, env="MAX_CONVERSATION_TURNS")
    min_turns_for_callback: int = Field(default=5, env="MIN_TURNS_FOR_CALLBACK")
    agent_temperature: float = Field(default=0.7, env="AGENT_TEMPERATURE")
    
    # Session Storage
    redis_url: Optional[str] = Field(default=None, env="REDIS_URL")
    session_timeout: int = Field(default=3600, env="SESSION_TIMEOUT")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Export settings instance
settings = get_settings()
