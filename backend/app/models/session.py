"""
CogniSense — CaptureSession ORM Model.

Represents a single multimodal data capture session.
"""

from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float
from sqlalchemy.orm import relationship
from app.db.engine import Base


class CaptureSession(Base):
    """A capture session spanning sensor activation to deactivation."""

    __tablename__ = "capture_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(64), unique=True, nullable=False, index=True)
    scenario = Column(String(32), default="general")  # coding | exam | interview
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    duration_sec = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True)

    # Sensors (all mandatory now)
    webcam_enabled = Column(Boolean, default=True)
    audio_enabled = Column(Boolean, default=True)
    keystroke_enabled = Column(Boolean, default=True)
    mouse_enabled = Column(Boolean, default=True)

    # Session-level aggregates
    avg_load_score = Column(Float, nullable=True)
    peak_load_level = Column(String(16), nullable=True)
    total_predictions = Column(Integer, default=0)
    notes = Column(String(512), nullable=True)

    # Relationships
    predictions = relationship("CognitiveLoadPrediction", back_populates="session")
    feature_records = relationship("FeatureRecord", back_populates="session")
