"""
CogniSense — CognitiveLoadPrediction ORM Model.

Stores individual cognitive load predictions with timestamps,
confidence scores, per-modality contributions, and model metadata.
"""

from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.db.engine import Base


class CognitiveLoadPrediction(Base):
    """A single cognitive load prediction at a point in time."""

    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(64), ForeignKey("capture_sessions.session_id"), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    # Prediction output
    load_level = Column(String(16), nullable=False)  # low | medium | high
    load_level_int = Column(Integer, nullable=False)  # 0 | 1 | 2
    confidence = Column(Float, nullable=False, default=0.0)

    # Per-class probabilities
    prob_low = Column(Float, default=0.0)
    prob_medium = Column(Float, default=0.0)
    prob_high = Column(Float, default=0.0)

    # Per-modality contribution scores
    visual_score = Column(Float, default=0.0)
    behavioral_score = Column(Float, default=0.0)
    audio_score = Column(Float, default=0.0)

    # Model metadata
    model_name = Column(String(32), nullable=True)  # Ensemble | RandomForest | etc.
    model_version = Column(String(32), nullable=True)

    # Relationship
    session = relationship("CaptureSession", back_populates="predictions")
