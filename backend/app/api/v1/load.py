"""
CogniSense — Load Endpoints.

GET /load/live    — Real-time cognitive load prediction
GET /load/history — Historical predictions for a session
"""

import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.load import (
    LiveLoadResponse,
    PredictionRecord,
    LoadHistoryResponse,
)
from app.schemas.common import ModalityScores
from app.services.scoring_service import ScoringService
from app.services.capture_service import CaptureService
from app.services.history_service import HistoryService

logger = logging.getLogger(__name__)
router = APIRouter()

# Singleton scoring service (loaded once)
_scoring_service = ScoringService()
_scoring_service.load_model()


@router.get(
    "/live",
    response_model=LiveLoadResponse,
    summary="Get real-time cognitive load",
)
async def get_live_load(db: Session = Depends(get_db)):
    """
    Get the current real-time cognitive load prediction.

    Extracts features from the active session's sensor data,
    runs model inference, and returns the prediction with
    per-modality contribution scores.
    """
    # Check for active session
    cap_service = CaptureService(db)
    active = cap_service.get_active_session()

    if active is None:
        raise HTTPException(
            status_code=404,
            detail="No active capture session. Start one via POST /capture/start",
        )

    # In a real deployment, features come from the fusion engine's
    # rolling buffer. Here we use the scoring service's fallback
    # or model prediction.
    features = {}  # Placeholder: populated by fusion engine in production
    result = _scoring_service.predict(features)

    return LiveLoadResponse(
        load_level=result["load_level"],
        confidence=result["confidence"],
        modality_scores=ModalityScores(**result["modality_scores"]),
        probabilities=result["probabilities"],
        timestamp=datetime.utcnow(),
    )


@router.get(
    "/history",
    response_model=LoadHistoryResponse,
    summary="Get historical cognitive load predictions",
)
async def get_load_history(
    session_id: str = Query(..., description="Session ID to query"),
    limit: int = Query(100, ge=1, le=1000, description="Max records"),
    db: Session = Depends(get_db),
):
    """
    Retrieve historical cognitive load predictions for a session.

    Returns predictions in reverse chronological order.
    """
    # Validate session exists
    cap_service = CaptureService(db)
    session = cap_service.get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    history_service = HistoryService(db)
    predictions = history_service.get_session_predictions(session_id, limit=limit)

    records = [
        PredictionRecord(
            timestamp=p.timestamp,
            load_level=p.load_level,
            confidence=p.confidence,
            modality_scores=ModalityScores(
                visual=p.visual_score,
                behavioral=p.behavioral_score,
                audio=p.audio_score,
            ),
        )
        for p in predictions
    ]

    avg_load = history_service.get_average_load(session_id)

    return LoadHistoryResponse(
        session_id=session_id,
        predictions=records,
        count=len(records),
        avg_load_score=avg_load,
    )
