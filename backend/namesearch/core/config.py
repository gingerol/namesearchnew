"""Application configuration module."""
import os
import secrets
from typing import List, Optional, Dict, Any, Union

from pydantic import AnyHttpUrl, validator, EmailStr, HttpUrl
from pydantic_settings import BaseSettings


def generate_secret_key() -> str:
    """Generate a secure secret key."""
    return secrets.token_urlsafe(32)


class Settings(BaseSettings):
    """Application settings."""
    
    # Application settings
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 5000  # Using port 5000 as requested
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Namesearch.io API"
    
    # CORS
    CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:3000",  # Default frontend port
        "http://localhost:5000",  # Default backend port
    ]
    
    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "namesearch"
    DATABASE_URI: Optional[str] = None
    
    @validator("DATABASE_URI", pre=True)
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> str:
        """Assemble database connection string."""
        if v is not None and isinstance(v, str):
            return v
        return f"postgresql+psycopg2://{values.get('POSTGRES_USER')}:{values.get('POSTGRES_PASSWORD')}@{values.get('POSTGRES_SERVER')}/{values.get('POSTGRES_DB')}"
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"  # Change this in production
    ALGORITHM: str = "HS256"
    
    # Access token settings
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15  # 15 minutes
    
    # Refresh token settings
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7  # 7 days
    REFRESH_TOKEN_LEEWAY: int = 60  # 1 minute leeway for clock skew
    
    # Email verification token settings
    EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS: int = 24  # 24 hours
    
    # Password reset token settings
    RESET_PASSWORD_TOKEN_EXPIRE_MINUTES: int = 60  # 1 hour
    
    # CORS settings
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:3000",  # Default frontend port
        "http://localhost:5000",  # Default backend port
    ]
    
    # Security headers
    SECURE_HEADERS: bool = True
    SECURE_CONTENT_TYPE_NOSNIFF: bool = True
    SECURE_BROWSER_XSS_FILTER: bool = True
    SESSION_COOKIE_SECURE: bool = not DEBUG
    SESSION_COOKIE_HTTPONLY: bool = True
    SESSION_COOKIE_SAMESITE: str = "lax"
    
    # Rate limiting
    RATE_LIMIT: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # Email settings
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = 587
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[EmailStr] = None
    EMAILS_FROM_NAME: Optional[str] = None
    EMAILS_ENABLED: bool = False
    
    # Frontend URLs
    FRONTEND_URL: str = "http://localhost:3000"
    
    # First superuser (for initial setup)
    FIRST_SUPERUSER_EMAIL: Optional[EmailStr] = None
    FIRST_SUPERUSER_PASSWORD: Optional[str] = None
    
    @validator("EMAILS_ENABLED", pre=True)
    @classmethod
    def get_emails_enabled(cls, v: bool, values: Dict[str, Any]) -> bool:
        """Check if email sending is enabled."""
        return bool(
            values.get("SMTP_HOST")
            and values.get("SMTP_PORT")
            and values.get("EMAILS_FROM_EMAIL")
        )
    
    @validator("FIRST_SUPERUSER_EMAIL", pre=True)
    @classmethod
    def get_first_superuser_email(cls, v: Optional[str]) -> Optional[str]:
        """Get first superuser email from environment."""
        if v is not None:
            return v
        return os.getenv("FIRST_SUPERUSER_EMAIL")
    
    @validator("FIRST_SUPERUSER_PASSWORD", pre=True)
    @classmethod
    def get_first_superuser_password(cls, v: Optional[str]) -> Optional[str]:
        """Get first superuser password from environment."""
        if v is not None:
            return v
        return os.getenv("FIRST_SUPERUSER_PASSWORD")
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # WHOIS settings
    WHOIS_TIMEOUT: int = 10  # seconds
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        
        @classmethod
        def customise_sources(
            cls,
            init_settings,
            env_settings,
            file_secret_settings,
        ):
            """Customize settings sources."""
            # Load .env file if it exists
            env_file = ".env"
            if os.path.isfile(env_file):
                from dotenv import load_dotenv
                load_dotenv(env_file)
            
            # Return the default sources
            return env_settings, init_settings, file_secret_settings


settings = Settings()
