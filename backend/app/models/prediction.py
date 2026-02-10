"""
CogniSense — CognitiveLoadPrediction ORM Model.

Stores individual cognitive load predictions with timestamps.
"""

from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from app.db.engine import Base


class CognitiveLoadPrediction(Base):
    """A single cognitive load prediction at a point in time."""

    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(64), ForeignKey("capture_sessions.session_id"), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    load_level = Column(String(16), nullable=False)  # low | medium | high
    confidence = Column(Float, nullable=False, default=0.0)
    visual_score = Column(Float, default=0.0)
    behavioral_score = Column(Float, default=0.0)
    audio_score = Column(Float, default=0.0)
    model_version = Column(String(32), nullable=True)
