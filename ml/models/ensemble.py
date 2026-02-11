"""
CogniSense — Ensemble Classifier.

Combines Random Forest, XGBoost, and SVM via soft voting
or optional stacking for robust cognitive load prediction.

Usage:
    from ml.models.ensemble import EnsembleModel
    model = EnsembleModel(method="voting")
    model.train(X_train, y_train)
    predictions = model.predict(X_test)
"""

import logging
from typing import Dict, Optional
from pathlib import Path

import numpy as np
import joblib

from ml.models.random_forest import RandomForestModel
from ml.models.xgboost_clf import XGBoostModel
from ml.models.svm_clf import SVMModel

logger = logging.getLogger(__name__)

LABEL_MAP = {0: "low", 1: "medium", 2: "high"}


class EnsembleModel:
    """
    Ensemble classifier combining RF, XGBoost, and SVM.

    Supports two methods:
      - 'voting': Soft voting (averaged probabilities)
      - 'weighted': Weighted voting based on individual accuracy

    Attributes:
        method: Ensemble strategy ('voting' or 'weighted').
        weights: Per-model weights for weighted voting.
    """

    def __init__(
        self,
        method: str = "voting",
        weights: Optional[Dict[str, float]] = None,
    ):
        self.method = method
        self.weights = weights or {"rf": 1.0, "xgb": 1.0, "svm": 1.0}

        self.rf = RandomForestModel()
        self.xgb = XGBoostModel()
        self.svm = SVMModel()

        self._feature_names: list = []
        self._is_trained = False
        logger.info("EnsembleModel created (method=%s)", method)

    def train(
        self, X: np.ndarray, y: np.ndarray,
        feature_names: Optional[list] = None,
    ) -> Dict[str, float]:
        """
        Train all three base models.

        Args:
            X: 2-D array (n_samples, n_features).
            y: 1-D array of labels.
            feature_names: Optional feature name list.

        Returns:
            Dict of model_name → training accuracy.
        """
        self._feature_names = feature_names or [f"f_{i}" for i in range(X.shape[1])]

        self.rf.train(X, y, feature_names=self._feature_names)
        self.xgb.train(X, y, feature_names=self._feature_names)
        self.svm.train(X, y, feature_names=self._feature_names)

        # Training accuracy for reference
        accuracies = {
            "rf": float(np.mean(self.rf.predict(X) == y)),
            "xgb": float(np.mean(self.xgb.predict(X) == y)),
            "svm": float(np.mean(self.svm.predict(X) == y)),
        }

        self._is_trained = True
        logger.info(
            "Ensemble trained — RF: %.3f, XGB: %.3f, SVM: %.3f",
            accuracies["rf"], accuracies["xgb"], accuracies["svm"],
        )
        return accuracies

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        Predict ensemble class probabilities via weighted averaging.

        Returns:
            (n_samples, 3) array of probabilities.
        """
        w_rf = self.weights["rf"]
        w_xgb = self.weights["xgb"]
        w_svm = self.weights["svm"]
        total_w = w_rf + w_xgb + w_svm

        proba = (
            w_rf * self.rf.predict_proba(X)
            + w_xgb * self.xgb.predict_proba(X)
            + w_svm * self.svm.predict_proba(X)
        ) / total_w

        return proba

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict class labels from ensemble probabilities."""
        proba = self.predict_proba(X)
        return np.argmax(proba, axis=1)

    def predict_with_details(self, X: np.ndarray) -> Dict:
        """
        Predict with full details: label, confidence, per-model probs.

        Args:
            X: 2-D array (n_samples, n_features) or 1-D for single sample.

        Returns:
            Dict with keys: load_level, confidence, probabilities,
            per_model_predictions.
        """
        if X.ndim == 1:
            X = X.reshape(1, -1)

        ensemble_proba = self.predict_proba(X)[0]
        predicted_class = int(np.argmax(ensemble_proba))
        confidence = float(ensemble_proba[predicted_class])

        return {
            "load_level": LABEL_MAP[predicted_class],
            "confidence": confidence,
            "probabilities": {
                "low": float(ensemble_proba[0]),
                "medium": float(ensemble_proba[1]),
                "high": float(ensemble_proba[2]),
            },
            "per_model": {
                "rf": LABEL_MAP[int(self.rf.predict(X)[0])],
                "xgb": LABEL_MAP[int(self.xgb.predict(X)[0])],
                "svm": LABEL_MAP[int(self.svm.predict(X)[0])],
            },
        }

    def feature_importance(self) -> Dict[str, float]:
        """Return averaged feature importance across models."""
        rf_imp = self.rf.feature_importance()
        xgb_imp = self.xgb.feature_importance()
        # SVM importance is 0 for non-linear, so skip averaging it
        combined = {}
        for name in self._feature_names:
            rf_val = rf_imp.get(name, 0.0)
            xgb_val = xgb_imp.get(name, 0.0)
            combined[name] = (rf_val + xgb_val) / 2.0
        return combined

    def save(self, path: str) -> None:
        """Save all models and metadata."""
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({
            "rf": self.rf.model,
            "xgb": self.xgb.model,
            "svm": self.svm.model,
            "feature_names": self._feature_names,
            "weights": self.weights,
            "method": self.method,
        }, path)
        logger.info("Ensemble saved to %s", path)

    def load(self, path: str) -> None:
        """Load all models from disk."""
        data = joblib.load(path)
        self.rf.model = data["rf"]
        self.xgb.model = data["xgb"]
        self.svm.model = data["svm"]
        self._feature_names = data["feature_names"]
        self.rf._feature_names = data["feature_names"]
        self.xgb._feature_names = data["feature_names"]
        self.svm._feature_names = data["feature_names"]
        self.weights = data["weights"]
        self.method = data["method"]
        self.rf._is_trained = True
        self.xgb._is_trained = True
        self.svm._is_trained = True
        self._is_trained = True
        logger.info("Ensemble loaded from %s", path)
