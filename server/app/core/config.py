import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import field_validator
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application settings
    app_name: str = "CoAgentics AI System"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"
    
    # API settings
    api_host: str = "0.0.0.0"
    api_port: int = 8002
    api_prefix: str = "/api/v1"
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    access_token_expire_minutes: int = 30
    algorithm: str = "HS256"
    
    # Database settings
    database_url: Optional[str] = None
    db_echo: bool = False
    
    # Google Cloud settings
    google_cloud_project: Optional[str] = None
    google_application_credentials: Optional[str] = None
    
    # Vertex AI settings
    vertex_ai_location: str = "us-central1"
    vertex_ai_model: str = "gemini-pro"
    
    # Vector Search settings
    vertex_vector_search_index: Optional[str] = None
    vertex_vector_search_endpoint: Optional[str] = None
    
    # Cloud Storage settings
    gcs_bucket_name: Optional[str] = None
    
    # Agent settings
    max_agent_iterations: int = 10
    agent_timeout_seconds: int = 300
    
    # Tool settings
    web_search_api_key: Optional[str] = None
    financial_data_api_key: Optional[str] = None
    
    # CORS settings
    allowed_origins: List[str] = ["http://localhost:3000", "http://localhost:8080", "http://localhost:8501", "https://coagentics-frontend-978710537953.us-central1.run.app", "*"]
    allowed_methods: List[str] = ["GET", "POST", "PUT", "DELETE"]
    allowed_headers: List[str] = ["*"]
    
    @field_validator("database_url", mode="before")
    @classmethod
    def validate_database_url(cls, v):
        if v is None:
            # Default to SQLite for development
            return "sqlite:///./coagentics.db"
        return v
    
    @field_validator("secret_key", mode="before")
    @classmethod
    def validate_secret_key(cls, v):
        if v == "your-secret-key-change-in-production":
            import secrets
            return secrets.token_urlsafe(32)
        return v
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "env_prefix": ""
    }

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()

# Global settings instance
settings = get_settings() 