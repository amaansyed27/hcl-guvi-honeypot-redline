"""
Honeypot Application Configuration

Loads environment variables and provides centralized configuration.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Configuration
    api_key: str = Field(..., description="API key for authenticating requests")
    port: int = Field(default=8080)
    
    # Google Gemini Configuration
    google_api_key: str = Field(..., description="Gemini API key")
    model_name: str = Field(default="gemini-3-flash-preview")
    
    # GUVI Callback
    guvi_callback_url: str = Field(
        default="https://hackathon.guvi.in/api/updateHoneyPotFinalResult"
    )
    
    # Agent Configuration
    max_conversation_turns: int = Field(default=20)
    min_turns_for_callback: int = Field(default=5)
    agent_temperature: float = Field(default=1.0)
    
    # Session Storage
    redis_url: Optional[str] = Field(default=None)
    session_timeout: int = Field(default=3600)
    
    # Logging
    log_level: str = Field(default="INFO")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Export settings instance
settings = get_settings()
