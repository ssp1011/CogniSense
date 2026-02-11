"""
CogniSense — Capture Endpoints.

POST /capture/start — Start a multimodal capture session
POST /capture/stop  — Stop the active session
GET  /capture/status — Get current session status
"""

import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.capture import (
    CaptureStartRequest,
    CaptureStartResponse,
    CaptureStopRequest,
    CaptureStopResponse,
)
from app.services.capture_service import CaptureService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/start",
    response_model=CaptureStartResponse,
    summary="Start a capture session",
)
async def start_capture(
    request: CaptureStartRequest,
    db: Session = Depends(get_db),
):
    """
    Start a new multimodal data capture session.

    Activates all sensors (webcam, keystroke, mouse, audio).
    Returns a session_id for tracking.
    """
    service = CaptureService(db)

    # Check if there's already an active session
    active = service.get_active_session()
    if active:
        raise HTTPException(
            status_code=409,
            detail=f"Session {active.session_id} is already active. Stop it first.",
        )

    session = service.start_session(
        scenario=request.scenario.value,
        notes=request.notes,
    )

    logger.info("Capture session started: %s", session.session_id)
    return CaptureStartResponse(
        status="started",
        session_id=session.session_id,
        started_at=session.started_at,
        scenario=session.scenario,
    )


@router.post(
    "/stop",
    response_model=CaptureStopResponse,
    summary="Stop a capture session",
)
async def stop_capture(
    request: CaptureStopRequest,
    db: Session = Depends(get_db),
):
    """
    Stop the active capture session and persist collected data.

    Computes session aggregates (duration, avg load, peak level).
    """
    service = CaptureService(db)
    session = service.stop_session(request.session_id)

    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    logger.info("Capture session stopped: %s", request.session_id)
    return CaptureStopResponse(
        status="stopped",
        session_id=session.session_id,
        duration_sec=session.duration_sec or 0.0,
        avg_load_score=session.avg_load_score,
        total_predictions=session.total_predictions or 0,
    )


@router.get("/status", summary="Get current session status")
async def session_status(db: Session = Depends(get_db)):
    """Return the currently active session, or indicate none active."""
    service = CaptureService(db)
    active = service.get_active_session()

    if active is None:
        return {"active": False, "session_id": None}

    return {
        "active": True,
        "session_id": active.session_id,
        "scenario": active.scenario,
        "started_at": active.started_at.isoformat(),
        "total_predictions": active.total_predictions or 0,
    }
