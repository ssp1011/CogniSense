"""
CogniSense — Interview Analysis Endpoint.

POST /interview/analyze — Analyze cognitive load during an interview session
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.load import AnalysisResponse
from app.schemas.common import ModalityScores
from app.services.capture_service import CaptureService
from app.services.history_service import HistoryService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/analyze",
    response_model=AnalysisResponse,
    summary="Analyze interview session",
)
async def analyze_interview(
    session_id: str = Query(..., description="Session ID to analyze"),
    db: Session = Depends(get_db),
):
    """
    Analyze cognitive load patterns during an interview session.

    Provides:
    - Average and peak load levels
    - Time distribution across load levels
    - Per-modality contribution averages
    - Actionable recommendations for interviewees
    """
    # Validate session
    cap_service = CaptureService(db)
    session = cap_service.get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    # Run analysis
    history_service = HistoryService(db)
    analysis = history_service.analyze_session(session_id)

    if analysis["total_predictions"] == 0:
        raise HTTPException(
            status_code=422,
            detail="No predictions available for this session. Capture data first.",
        )

    # Add interview-specific recommendations
    recs = analysis["recommendations"]
    if analysis["time_in_high"] > 30:
        recs.append("💡 Practice mock interviews to build familiarity and reduce cognitive load.")
    if analysis["modality_averages"].get("audio", 0) > 0.4:
        recs.append("🗣️ Voice stress detected — practice speaking at a measured pace.")

    return AnalysisResponse(
        session_id=analysis["session_id"],
        scenario=analysis["scenario"],
        avg_load_level=analysis["avg_load_level"],
        avg_confidence=analysis["avg_confidence"],
        peak_load_level=analysis["peak_load_level"],
        peak_timestamp=analysis["peak_timestamp"],
        total_predictions=analysis["total_predictions"],
        time_in_high=analysis["time_in_high"],
        time_in_medium=analysis["time_in_medium"],
        time_in_low=analysis["time_in_low"],
        modality_averages=ModalityScores(**analysis["modality_averages"]),
        recommendations=recs,
    )
