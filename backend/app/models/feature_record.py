"""
CogniSense — FeatureRecord ORM Model.

Stores extracted feature vectors associated with predictions.
"""

from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, ForeignKey
from app.db.engine import Base


class FeatureRecord(Base):
    """A feature vector extracted at a given time window."""

    __tablename__ = "feature_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(64), ForeignKey("capture_sessions.session_id"), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    window_sec = Column(Float, default=5.0)
    features_json = Column(JSON, nullable=False)  # Full feature dict
    modality = Column(String(32), nullable=True)   # visual | behavioral | audio | fused
