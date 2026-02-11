"""
CogniSense — Capture Service.

Orchestrates starting/stopping of multimodal sensor capture sessions.
All sensors (webcam, keystroke, mouse, audio) are mandatory.
"""

import logging
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.session import CaptureSession
from app.models.prediction import CognitiveLoadPrediction

logger = logging.getLogger(__name__)


class CaptureService:
    """Business logic for managing capture sessions."""

    def __init__(self, db: Session):
        self.db = db

    def start_session(
        self,
        scenario: str = "general",
        notes: Optional[str] = None,
    ) -> CaptureSession:
        """
        Create and persist a new capture session.

        All modalities are enabled by default (mandatory).

        Args:
            scenario: Use-case scenario (general | coding | exam | interview).
            notes: Optional session notes.

        Returns:
            Created CaptureSession ORM object.
        """
        session = CaptureSession(
            session_id=str(uuid.uuid4()),
            scenario=scenario,
            webcam_enabled=True,
            audio_enabled=True,
            keystroke_enabled=True,
            mouse_enabled=True,
            notes=notes,
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        logger.info("Started capture session %s (scenario=%s)", session.session_id, scenario)
        return session

    def stop_session(self, session_id: str) -> Optional[CaptureSession]:
        """
        Mark a capture session as stopped and compute aggregates.

        Calculates duration and average load score from predictions.
        """
        session = (
            self.db.query(CaptureSession)
            .filter(CaptureSession.session_id == session_id)
            .first()
        )
        if session is None:
            logger.warning("Session %s not found", session_id)
            return None

        if not session.is_active:
            logger.warning("Session %s already stopped", session_id)
            return session

        session.is_active = False
        session.ended_at = datetime.utcnow()
        session.duration_sec = (
            (session.ended_at - session.started_at).total_seconds()
            if session.started_at else 0.0
        )

        # Compute aggregates from predictions
        pred_stats = (
            self.db.query(
                func.count(CognitiveLoadPrediction.id),
                func.avg(CognitiveLoadPrediction.confidence),
            )
            .filter(CognitiveLoadPrediction.session_id == session_id)
            .first()
        )
        session.total_predictions = pred_stats[0] or 0
        session.avg_load_score = round(float(pred_stats[1] or 0.0), 3)

        # Peak load level
        peak = (
            self.db.query(CognitiveLoadPrediction.load_level)
            .filter(CognitiveLoadPrediction.session_id == session_id)
            .order_by(CognitiveLoadPrediction.confidence.desc())
            .first()
        )
        session.peak_load_level = peak[0] if peak else None

        self.db.commit()
        self.db.refresh(session)
        logger.info(
            "Stopped session %s (duration=%.1fs, predictions=%d)",
            session_id, session.duration_sec, session.total_predictions,
        )
        return session

    def get_session(self, session_id: str) -> Optional[CaptureSession]:
        """Retrieve a session by ID."""
        return (
            self.db.query(CaptureSession)
            .filter(CaptureSession.session_id == session_id)
            .first()
        )

    def get_active_session(self) -> Optional[CaptureSession]:
        """Retrieve the currently active session, if any."""
        return (
            self.db.query(CaptureSession)
            .filter(CaptureSession.is_active == True)
            .order_by(CaptureSession.started_at.desc())
            .first()
        )
