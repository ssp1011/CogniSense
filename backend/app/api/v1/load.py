"""
CogniSense — Cognitive Load Endpoints.

Serves live cognitive load scores and historical data.
"""

import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/live", summary="Get live cognitive load score")
async def get_live_load(db: Session = Depends(get_db)):
    """
    Return the current real-time cognitive load prediction.

    Response includes load level (low/medium/high), confidence,
    and per-modality contribution scores.
    """
    # TODO: Implement in Phase 5
    return {
        "load_level": "medium",
        "confidence": 0.0,
        "modality_scores": {
            "visual": 0.0,
            "behavioral": 0.0,
            "audio": 0.0,
        },
    }


@router.get("/history", summary="Get cognitive load history")
async def get_load_history(
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """
    Return historical cognitive load predictions for the active session.
    """
    # TODO: Implement in Phase 5
    return {"predictions": [], "count": 0}
