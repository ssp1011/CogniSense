"""
CogniSense — Capture Service.

Orchestrates starting/stopping of multimodal sensor capture sessions.
"""

import logging
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.models.session import CaptureSession

logger = logging.getLogger(__name__)


class CaptureService:
    """Business logic for managing capture sessions."""

    def __init__(self, db: Session):
        self.db = db

    def start_session(
        self,
        scenario: str = "general",
        webcam_enabled: bool = True,
        audio_enabled: bool = False,
        notes: Optional[str] = None,
    ) -> CaptureSession:
        """Create and persist a new capture session."""
        session = CaptureSession(
            session_id=str(uuid.uuid4()),
            scenario=scenario,
            webcam_enabled=webcam_enabled,
            audio_enabled=audio_enabled,
            notes=notes,
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        logger.info("Started capture session %s", session.session_id)
        return session

    def stop_session(self, session_id: str) -> Optional[CaptureSession]:
        """Mark a capture session as stopped."""
        session = (
            self.db.query(CaptureSession)
            .filter(CaptureSession.session_id == session_id)
            .first()
        )
        if session and session.is_active:
            session.is_active = False
            session.ended_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(session)
            logger.info("Stopped capture session %s", session_id)
        return session
