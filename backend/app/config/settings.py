from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    GROK_API_KEY: str
    GROK_API_URL: str = "https://api.x.ai/v1/chat/completions"
    GROK_MODEL: str = "grok-4-latest"

    # Email Configuration (SMTP)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = "aadit.bhatia93@gmail.com"
    SMTP_PASSWORD: str = ""  # Gmail App Password (not regular password)
    FROM_EMAIL: str = "aadit.bhatia93@gmail.com"
    FROM_NAME: str = "Sales AI Team"
    COMPANY_NAME: str = "Sales AI"

    ZAPIER_WEBHOOK_URL: str = ""

    class Config:
        env_file = ".env"

settings = Settings()
