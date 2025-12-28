from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    GROK_API_KEY: str
    GROK_API_URL: str = "https://api.x.ai/v1/chat/completions"
    GROK_MODEL: str = "grok-4-latest"

    # Resend (Email)
    RESEND_API_KEY: str
    FROM_EMAIL: str = "onboarding@resend.dev"
    COMPANY_NAME: str = "Sales AI"

    ZAPIER_WEBHOOK_URL: str = ""
    
    class Config:
        env_file = ".env"

settings = Settings()
