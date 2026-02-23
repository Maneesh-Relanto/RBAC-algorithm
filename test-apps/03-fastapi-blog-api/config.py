"""
Configuration for FastAPI Blog API.
Settings are loaded from environment variables with sensible defaults.
"""
import os
from datetime import timedelta


class Settings:
    """Application settings (read from environment variables)."""

    # JWT
    JWT_SECRET_KEY: str = os.environ.get(
        "JWT_SECRET_KEY", "jwt-secret-key-change-in-production"
    )
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION: timedelta = timedelta(
        minutes=int(os.environ.get("JWT_EXPIRATION_MINUTES", 60 * 24))
    )

    # API metadata
    API_TITLE: str = "FastAPI Blog API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "Blog API with RBAC authorization (FastAPI edition)"

    # CORS
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:8000",
    ]

    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    # Multi-tenancy
    DEFAULT_DOMAIN: str = "default"


class TestingSettings(Settings):
    """Shorter token expiry for tests."""
    JWT_EXPIRATION = timedelta(minutes=5)


settings = Settings()
testing_settings = TestingSettings()
