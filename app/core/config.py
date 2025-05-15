from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    PROJECT_NAME: str = "Jesi"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = Field(
        default="postgresql://postgres:password@localhost:5432/jesi",
        description="Database connection URL"
    )
    
    # JWT
    SECRET_KEY: str = Field(
        default="your-secret-key-here",
        description="Secret key for JWT token generation"
    )
    ALGORITHM: str = Field(
        default="HS256",
        description="Algorithm for JWT token generation"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30,
        description="Access token expiration time in minutes"
    )
    
    # Email
    SMTP_TLS: bool = Field(
        default=True,
        description="Use TLS for SMTP connection"
    )
    SMTP_PORT: int = Field(
        default=587,
        description="SMTP port"
    )
    SMTP_HOST: str = Field(
        default="smtp.gmail.com",
        description="SMTP host"
    )
    SMTP_USER: str = Field(
        default="",
        description="SMTP user email"
    )
    SMTP_PASSWORD: str = Field(
        default="",
        description="SMTP password"
    )
    EMAILS_FROM_EMAIL: str = Field(
        default="",
        description="Email address to send from"
    )
    EMAILS_FROM_NAME: str = Field(
        default="",
        description="Name to send emails from"
    )
    
    # Frontend URL
    FRONTEND_URL: str = Field(..., env="FRONTEND_URL")
    
    # Google OAuth settings
    GOOGLE_CLIENT_ID: Optional[str] = Field(
        default=None,
        description="Google OAuth client ID"
    )
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