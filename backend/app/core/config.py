"""
Application configuration using Pydantic settings.

This module provides centralized configuration management for the GNC calculations API.
All environment variables and application settings are defined here.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application metadata
    app_name: str = "GNC Calculations API"
    app_version: str = "0.1.0"
    debug: bool = False

    # API configuration
    api_prefix: str = "/api"

    # CORS settings for frontend integration
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()
