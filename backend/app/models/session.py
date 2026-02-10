"""
CogniSense — CaptureSession ORM Model.

Represents a single multimodal data capture session.
"""

from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float
from app.db.engine import Base


class CaptureSession(Base):
    """A capture session spanning sensor activation to deactivation."""

    __tablename__ = "capture_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(64), unique=True, nullable=False, index=True)
    scenario = Column(String(32), default="general")  # coding | exam | interview
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    webcam_enabled = Column(Boolean, default=True)
    audio_enabled = Column(Boolean, default=False)
    avg_load_score = Column(Float, nullable=True)
    notes = Column(String(512), nullable=True)
