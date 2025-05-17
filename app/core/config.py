from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
import logging
import os
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "Jesi"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5433/jesi")
    
    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Email
    SMTP_TLS: bool = Field(
        default=True,
        description="Use TLS for SMTP connection"
    )
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_HOST: str = os.getenv("SMTP_HOST", "")
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    EMAILS_FROM_EMAIL: str = Field(
        default="",
        description="Email address to send from"
    )
    EMAILS_FROM_NAME: str = Field(
        default="",
        description="Name to send emails from"
    )
    
    # Frontend URL
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    # Google OAuth settings
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: Optional[str] = Field(
        default=None,
        description="Google OAuth client secret"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        logger.info("Environment variables loaded:")
        logger.info(f"Database URL: {self.DATABASE_URL}")
        logger.info(f"SMTP Host: {self.SMTP_HOST}")
        logger.info(f"SMTP Port: {self.SMTP_PORT}")
        logger.info(f"SMTP User: {self.SMTP_USER}")
        logger.info(f"SMTP Password: {'*' * len(self.SMTP_PASSWORD) if self.SMTP_PASSWORD else 'Not set'}")
        logger.info(f"Frontend URL: {self.FRONTEND_URL}")

settings = Settings() 