"""
CogniSense — FeatureRecord ORM Model.

Stores extracted feature vectors associated with predictions.
Supports full 59-feature fused vectors and per-modality subsets.
"""

from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.db.engine import Base


class FeatureRecord(Base):
    """A feature vector extracted at a given time window."""

    __tablename__ = "feature_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(64), ForeignKey("capture_sessions.session_id"), nullable=False, index=True)
    prediction_id = Column(Integer, ForeignKey("predictions.id"), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    window_sec = Column(Float, default=5.0)

    # Feature data (stored as JSON dicts)
    features_json = Column(JSON, nullable=False)     # Full fused feature dict (~59 keys)
    feature_count = Column(Integer, nullable=True)    # Number of features stored
    modality = Column(String(32), default="fused")    # fused | visual | behavioral | audio

    # Relationship
    session = relationship("CaptureSession", back_populates="feature_records")
