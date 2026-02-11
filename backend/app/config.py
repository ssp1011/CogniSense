"""
CogniSense — Application Configuration.

Loads settings from environment variables and YAML config files.
Uses Pydantic BaseSettings for type-safe configuration management.
"""

import os
from pathlib import Path
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment and .env file."""

    # ── App ──────────────────────────────────────────────────────────
    APP_NAME: str = "CogniSense"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"  # development | production

    # ── Database (SQLite) ────────────────────────────────────────────
    DATABASE_URL: str = "sqlite:///./cognisense.db"

    # ── Logging ──────────────────────────────────────────────────────
    LOG_LEVEL: str = "INFO"
    LOG_DIR: str = str(Path(__file__).resolve().parents[2] / "logs")

    # ── ML Models ────────────────────────────────────────────────────
    MODEL_DIR: str = str(
        Path(__file__).resolve().parents[2].parent / "ml" / "saved_models"
    )

    # ── Capture ──────────────────────────────────────────────────────
    WEBCAM_INDEX: int = 0
    AUDIO_ENABLED: bool = True
    CAPTURE_FPS: int = 15
    FEATURE_WINDOW_SEC: float = 5.0

    # ── CORS ─────────────────────────────────────────────────────────
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }


@lru_cache()
def get_settings() -> Settings:
    """Return cached application settings singleton."""
    return Settings()
