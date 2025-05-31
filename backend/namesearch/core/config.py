"""Application configuration module."""
from typing import List, Optional, Dict, Any

from pydantic import AnyHttpUrl, validator
from pydantic_settings import BaseSettings


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
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # WHOIS settings
    WHOIS_TIMEOUT: int = 10  # seconds
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
