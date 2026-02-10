"""
CogniSense — API Dependency Injection Helpers.

Provides shared dependencies for route handlers such as
database sessions and settings access.
"""

from typing import Generator

from sqlalchemy.orm import Session

from app.db.engine import SessionLocal
from app.config import get_settings, Settings


def get_db() -> Generator[Session, None, None]:
    """Yield a database session, ensuring cleanup on exit."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_app_settings() -> Settings:
    """Return the application settings singleton."""
    return get_settings()
