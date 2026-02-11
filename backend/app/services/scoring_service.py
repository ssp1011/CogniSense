"""
CogniSense — Scoring Service.

Loads the trained ensemble model and scaler, accepts fused feature
vectors, and returns cognitive load predictions with confidence
scores and per-modality contributions.

Note: ML dependencies are imported lazily to allow the backend to
start even when ML packages aren't installed.
"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path

import numpy as np

logger = logging.getLogger(__name__)

LABEL_MAP = {0: "low", 1: "medium", 2: "high"}


class ScoringService:
    """
    Runs model inference for cognitive load scoring.

    Loads the trained ensemble classifier and StandardScaler from disk,
    then provides predict() for real-time scoring.
    """

    def __init__(self, model_dir: str = "ml/saved_models"):
        self.model_dir = Path(model_dir)
        self._model = None
        self._scaler = None
        self._is_loaded = False
        logger.info("ScoringService initialized (model_dir=%s)", model_dir)

    def load_model(self) -> bool:
        """
        Load the trained model and scaler from disk.

        Returns:
            True if loaded successfully, False otherwise.
        """
        model_path = self.model_dir / "latest.pkl"
        scaler_path = self.model_dir / "scaler.pkl"

        if not model_path.exists():
            logger.warning("No model found at %s — scoring will use fallback", model_path)
            return False

        try:
            import joblib
            # Try lazy import of ensemble
            import sys
            project_root = Path(__file__).resolve().parents[3]
            if str(project_root) not in sys.path:
                sys.path.insert(0, str(project_root))
            from ml.models.ensemble import EnsembleModel

            self._model = EnsembleModel()
            self._model.load(str(model_path))
            if scaler_path.exists():
                self._scaler = joblib.load(str(scaler_path))
            self._is_loaded = True
            logger.info("Model and scaler loaded successfully")
            return True
        except Exception as e:
            logger.warning("Could not load model: %s — using fallback", e)
            return False

    def predict(self, features: Dict[str, float]) -> Dict[str, Any]:
        """
        Run inference on a fused feature vector.

        Args:
            features: Dict of feature_name → value from FeatureFusionEngine.

        Returns:
            Dict with load_level, confidence, probabilities, and modality_scores.
        """
        if not self._is_loaded or self._model is None:
            return self._fallback_prediction(features)

        # Convert to sorted numpy array
        feature_names = sorted(features.keys())
        X = np.array([features[k] for k in feature_names], dtype=np.float64).reshape(1, -1)

        # Scale
        if self._scaler is not None:
            X = self._scaler.transform(X)

        # Predict
        result = self._model.predict_with_details(X)

        # Compute per-modality contribution scores
        importance = self._model.feature_importance()
        modality_scores = self._compute_modality_scores(features, importance)
        result["modality_scores"] = modality_scores

        logger.debug(
            "Prediction: %s (conf=%.2f)",
            result["load_level"], result["confidence"],
        )
        return result

    def _compute_modality_scores(
        self, features: Dict[str, float], importance: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Compute per-modality contribution scores.

        Aggregates feature importance × feature value for each modality prefix.
        """
        modality_sums = {"visual": 0.0, "behavioral": 0.0, "audio": 0.0}

        for name, imp in importance.items():
            val = features.get(name, 0.0)
            weighted = abs(imp * val)
            if name.startswith("vis_"):
                modality_sums["visual"] += weighted
            elif name.startswith("beh_"):
                modality_sums["behavioral"] += weighted
            elif name.startswith("aud_"):
                modality_sums["audio"] += weighted

        # Normalize to 0-1 range
        total = sum(modality_sums.values())
        if total > 0:
            return {k: round(v / total, 3) for k, v in modality_sums.items()}
        return {"visual": 0.33, "behavioral": 0.33, "audio": 0.34}

    def _fallback_prediction(self, features: Dict[str, float]) -> Dict[str, Any]:
        """
        Rule-based fallback when no trained model is available.

        Uses simple heuristics on key features to estimate load level.
        """
        score = 0.0
        if features.get("vis_blink_rate", 0) > 22:
            score += 1
        if features.get("beh_error_rate", 0) > 0.15:
            score += 1
        if features.get("aud_pitch_std", 0) > 30:
            score += 1
        if features.get("vis_head_movement", 0) > 3:
            score += 0.5
        if features.get("aud_jitter", 0) > 0.02:
            score += 0.5

        if score >= 2:
            level, conf = "high", 0.5
        elif score >= 1:
            level, conf = "medium", 0.4
        else:
            level, conf = "low", 0.4

        return {
            "load_level": level,
            "confidence": conf,
            "probabilities": {"low": 0.33, "medium": 0.34, "high": 0.33},
            "modality_scores": {"visual": 0.33, "behavioral": 0.33, "audio": 0.34},
            "per_model": {"fallback": level},
        }

    @property
    def is_loaded(self) -> bool:
        """Return whether a trained model is loaded."""
        return self._is_loaded
