"""
CogniSense — History Service.

Queries historical cognitive load predictions from the database,
computes session-level analysis with time distribution and
generates recommendations based on load patterns.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.prediction import CognitiveLoadPrediction
from app.models.session import CaptureSession

logger = logging.getLogger(__name__)


class HistoryService:
    """Query and aggregate historical prediction data."""

    def __init__(self, db: Session):
        self.db = db

    def get_session_predictions(
        self, session_id: str, limit: int = 100
    ) -> List[CognitiveLoadPrediction]:
        """Retrieve predictions for a given session (most recent first)."""
        return (
            self.db.query(CognitiveLoadPrediction)
            .filter(CognitiveLoadPrediction.session_id == session_id)
            .order_by(CognitiveLoadPrediction.timestamp.desc())
            .limit(limit)
            .all()
        )

    def get_average_load(self, session_id: str) -> Optional[float]:
        """Compute average confidence score for a session."""
        result = (
            self.db.query(func.avg(CognitiveLoadPrediction.confidence))
            .filter(CognitiveLoadPrediction.session_id == session_id)
            .scalar()
        )
        return round(float(result), 3) if result else None

    def analyze_session(self, session_id: str) -> Dict[str, Any]:
        """
        Full session analysis: time distribution, peaks, and recommendations.

        Returns:
            Dict with avg_load_level, time_in_high/medium/low percentages,
            peak info, modality averages, and recommendations.
        """
        predictions = (
            self.db.query(CognitiveLoadPrediction)
            .filter(CognitiveLoadPrediction.session_id == session_id)
            .order_by(CognitiveLoadPrediction.timestamp.asc())
            .all()
        )

        if not predictions:
            return self._empty_analysis(session_id)

        total = len(predictions)

        # Time distribution
        high_count = sum(1 for p in predictions if p.load_level == "high")
        med_count = sum(1 for p in predictions if p.load_level == "medium")
        low_count = sum(1 for p in predictions if p.load_level == "low")

        time_in_high = round(high_count / total * 100, 1)
        time_in_medium = round(med_count / total * 100, 1)
        time_in_low = round(low_count / total * 100, 1)

        # Average confidence
        avg_confidence = sum(p.confidence for p in predictions) / total

        # Average load level (numeric)
        avg_load_num = sum(p.load_level_int for p in predictions) / total
        if avg_load_num < 0.8:
            avg_load_level = "low"
        elif avg_load_num < 1.5:
            avg_load_level = "medium"
        else:
            avg_load_level = "high"

        # Peak prediction
        peak_pred = max(predictions, key=lambda p: p.confidence)

        # Modality averages
        modality_averages = {
            "visual": round(sum(p.visual_score for p in predictions) / total, 3),
            "behavioral": round(sum(p.behavioral_score for p in predictions) / total, 3),
            "audio": round(sum(p.audio_score for p in predictions) / total, 3),
        }

        # Generate recommendations
        recommendations = self._generate_recommendations(
            time_in_high, time_in_medium, modality_averages, avg_load_level,
        )

        # Get session info
        session = (
            self.db.query(CaptureSession)
            .filter(CaptureSession.session_id == session_id)
            .first()
        )
        scenario = session.scenario if session else "general"

        return {
            "session_id": session_id,
            "scenario": scenario,
            "avg_load_level": avg_load_level,
            "avg_confidence": round(avg_confidence, 3),
            "peak_load_level": peak_pred.load_level,
            "peak_timestamp": peak_pred.timestamp,
            "total_predictions": total,
            "time_in_high": time_in_high,
            "time_in_medium": time_in_medium,
            "time_in_low": time_in_low,
            "modality_averages": modality_averages,
            "recommendations": recommendations,
        }

    def _generate_recommendations(
        self, time_high: float, time_med: float,
        modality_avg: Dict[str, float], avg_level: str,
    ) -> List[str]:
        """Generate actionable recommendations based on load patterns."""
        recs = []

        if time_high > 40:
            recs.append("⚠️ High cognitive load detected for >40% of session. Consider taking breaks every 25 minutes.")
        if time_high > 60:
            recs.append("🔴 Sustained high load is unsustainable. Reduce task complexity or switch contexts.")

        if modality_avg.get("visual", 0) > 0.5:
            recs.append("👁️ Visual stress indicators are elevated — reduce screen brightness or increase text size.")
        if modality_avg.get("behavioral", 0) > 0.5:
            recs.append("⌨️ Typing/mouse patterns suggest frustration — consider restructuring the task.")
        if modality_avg.get("audio", 0) > 0.5:
            recs.append("🎤 Voice stress is high — take deep breaths and slow speech pace.")

        if avg_level == "low" and time_high < 10:
            recs.append("✅ Overall cognitive load is healthy. Performance should be sustainable.")

        if not recs:
            recs.append("📊 Moderate cognitive load detected. Monitor for extended periods.")

        return recs

    def _empty_analysis(self, session_id: str) -> Dict[str, Any]:
        """Return empty analysis when no predictions exist."""
        return {
            "session_id": session_id,
            "scenario": "general",
            "avg_load_level": "unknown",
            "avg_confidence": 0.0,
            "peak_load_level": "unknown",
            "peak_timestamp": None,
            "total_predictions": 0,
            "time_in_high": 0.0,
            "time_in_medium": 0.0,
            "time_in_low": 0.0,
            "modality_averages": {"visual": 0.0, "behavioral": 0.0, "audio": 0.0},
            "recommendations": ["No data available for analysis."],
        }
