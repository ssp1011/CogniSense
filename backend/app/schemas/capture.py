"""
CogniSense — Capture Schemas.

Request/response models for the /capture endpoints.
"""

from typing import Optional
from datetime import datetime

from pydantic import BaseModel

from app.schemas.common import Scenario


class CaptureStartRequest(BaseModel):
    """Request to start a capture session."""
    scenario: Scenario = Scenario.GENERAL
    notes: Optional[str] = None


class CaptureStartResponse(BaseModel):
    """Response after starting a capture session."""
    status: str
    session_id: str
    started_at: datetime
    scenario: str


class CaptureStopRequest(BaseModel):
    """Request to stop a capture session."""
    session_id: str


class CaptureStopResponse(BaseModel):
    """Response after stopping a capture session."""
    status: str
    session_id: str
    duration_sec: float
    avg_load_score: Optional[float] = None
    total_predictions: int = 0
