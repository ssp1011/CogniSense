"""
CogniSense — Database Engine & Session Factory.

Configures SQLAlchemy engine for SQLite and provides
session factory and declarative base.
"""

import logging
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

# ── SQLite Engine ────────────────────────────────────────────────────
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=settings.DEBUG,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def init_db() -> None:
    """Create all tables that don't yet exist."""
    from app.models import session, prediction, feature_record  # noqa: F401

    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized (SQLite)")
