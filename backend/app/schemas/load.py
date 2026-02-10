"""
CogniSense — Load Schemas.

Request/response models for the /load endpoints.
"""

from typing import List, Optional
from datetime import datetime

from pydantic import BaseModel

from app.schemas.common import LoadLevel, ModalityScores


class LiveLoadResponse(BaseModel):
    """Real-time cognitive load prediction response."""
    load_level: LoadLevel
    confidence: float
    modality_scores: ModalityScores
    timestamp: Optional[datetime] = None


class PredictionRecord(BaseModel):
    """A single historical prediction entry."""
    timestamp: datetime
    load_level: LoadLevel
    confidence: float
    modality_scores: ModalityScores


class LoadHistoryResponse(BaseModel):
    """Historical cognitive load predictions response."""
    session_id: str
    predictions: List[PredictionRecord]
    count: int
