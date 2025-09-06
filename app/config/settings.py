from pydantic_settings import BaseSettings
import os
from typing import Optional


class Settings(BaseSettings):
    """Application settings from environment variables"""

    # Database settings
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "whatsapp_ai"

    # Twilio WhatsApp API settings
    TWILIO_ACCOUNT_SID: str
    TWILIO_AUTH_TOKEN: str
    TWILIO_PHONE_NUMBER: str = "whatsapp:+14155238886"

    # Google Gemini API settings
    GEMINI_API_KEY: str
    GEMINI_MODEL: str = "gemini-1.5-flash"

    # App settings
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env.example"
        case_sensitive = True


# Global settings instance
settings = Settings()
