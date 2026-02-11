"""
CogniSense — Load Schemas.

Request/response models for the /load endpoints.
"""

from typing import List, Optional, Dict
from datetime import datetime

from pydantic import BaseModel

from app.schemas.common import LoadLevel, ModalityScores


class LiveLoadResponse(BaseModel):
    """Real-time cognitive load prediction response."""
    load_level: LoadLevel
    confidence: float
    modality_scores: ModalityScores
    probabilities: Dict[str, float]
    timestamp: datetime


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
    avg_load_score: Optional[float] = None


class AnalysisResponse(BaseModel):
    """Response for interview/exam analysis endpoints."""
    session_id: str
    scenario: str
    avg_load_level: str
    avg_confidence: float
    peak_load_level: str
    peak_timestamp: Optional[datetime] = None
    total_predictions: int
    time_in_high: float       # Percentage of time in high load
    time_in_medium: float
    time_in_low: float
    modality_averages: ModalityScores
    recommendations: List[str]
