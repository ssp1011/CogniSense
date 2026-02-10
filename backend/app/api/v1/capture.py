"""
CogniSense — Capture Endpoints.

Handles starting and stopping multimodal capture sessions.
"""

import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/start", summary="Start a capture session")
async def start_capture(db: Session = Depends(get_db)):
    """
    Start a new multimodal data capture session.

    Activates webcam, keystroke, mouse, and (optionally) audio sensors.
    Returns a session_id for tracking.
    """
    # TODO: Implement in Phase 5
    logger.info("Capture session start requested")
    return {"status": "started", "session_id": "placeholder"}


@router.post("/stop", summary="Stop a capture session")
async def stop_capture(db: Session = Depends(get_db)):
    """
    Stop the active capture session and persist collected data.
    """
    # TODO: Implement in Phase 5
    logger.info("Capture session stop requested")
    return {"status": "stopped"}
