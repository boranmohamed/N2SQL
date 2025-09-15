"""
Configuration management for the Vanna AI application.
"""
import os
from typing import Optional

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application settings
    app_name: str = Field(default="Vanna AI Web App", env="APP_NAME")
    app_version: str = Field(default="0.1.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")
    
    # Server settings
    host: str = Field(default="127.0.0.1", env="HOST")
    port: int = Field(default=8000, env="PORT")
    
    # Database settings
    database_url: str = Field(
        default="sqlite:///./vanna_app_clean.db",
        env="DATABASE_URL"
    )
    database_echo: bool = Field(default=False, env="DATABASE_ECHO")
    
    # Vanna Client Selection
    use_local_vanna: bool = Field(default=False, env="USE_LOCAL_VANNA")
    
    # Local Vanna Server settings
    local_vanna_server_url: str = Field(default="http://localhost:8001", env="LOCAL_VANNA_SERVER_URL")
    local_vanna_timeout: int = Field(default=30, env="LOCAL_VANNA_TIMEOUT")
    local_vanna_max_retries: int = Field(default=3, env="LOCAL_VANNA_MAX_RETRIES")
    
    # Vanna AI settings
    vanna_api_key: Optional[str] = Field(default="vn-3382b82aaf534991a546dec6cc2c72c5", env="VANNA_API_KEY")
    vanna_model: str = Field(default="gpt-4", env="VANNA_MODEL")
    vanna_email: str = Field(default="boranmohammed2@gmail.com", env="VANNA_EMAIL")
    vanna_org_id: str = Field(default="81b7acb3-b431-43c4-ba3b-d29919c6ab69", env="VANNA_ORG_ID")
    vanna_max_tokens: int = Field(default=1000, env="VANNA_MAX_TOKENS")
    
    # Logging settings
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(
        default="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        env="LOG_FORMAT"
    )
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()
