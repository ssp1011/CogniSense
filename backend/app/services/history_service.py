"""
CogniSense — History Service.

Queries historical cognitive load predictions from the database.
"""

import logging
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.prediction import CognitiveLoadPrediction

logger = logging.getLogger(__name__)


class HistoryService:
    """Query and aggregate historical prediction data."""

    def __init__(self, db: Session):
        self.db = db

    def get_session_predictions(
        self, session_id: str, limit: int = 100
    ) -> List[CognitiveLoadPrediction]:
        """Retrieve predictions for a given session."""
        return (
            self.db.query(CognitiveLoadPrediction)
            .filter(CognitiveLoadPrediction.session_id == session_id)
            .order_by(CognitiveLoadPrediction.timestamp.desc())
            .limit(limit)
            .all()
        )

    def get_average_load(self, session_id: str) -> Optional[float]:
        """Compute average confidence score for a session."""
        from sqlalchemy import func

        result = (
            self.db.query(func.avg(CognitiveLoadPrediction.confidence))
            .filter(CognitiveLoadPrediction.session_id == session_id)
            .scalar()
        )
        return result
