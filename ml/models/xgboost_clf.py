"""
CogniSense — XGBoost Classifier Wrapper.

Standardized wrapper around XGBoost for cognitive load prediction.

Usage:
    from ml.models.xgboost_clf import XGBoostModel
    model = XGBoostModel(n_estimators=200, learning_rate=0.1)
    model.train(X_train, y_train)
    predictions = model.predict(X_test)
"""

import logging
from typing import Dict, Optional
from pathlib import Path

import numpy as np
import joblib
from xgboost import XGBClassifier

logger = logging.getLogger(__name__)


class XGBoostModel:
    """
    XGBoost classifier for cognitive load levels.

    Wraps XGBClassifier with a unified interface matching other
    model wrappers: train, predict, predict_proba, save, load.
    """

    def __init__(
        self,
        n_estimators: int = 200,
        max_depth: int = 6,
        learning_rate: float = 0.1,
        subsample: float = 0.8,
        colsample_bytree: float = 0.8,
        random_state: int = 42,
    ):
        self.model = XGBClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            learning_rate=learning_rate,
            subsample=subsample,
            colsample_bytree=colsample_bytree,
            random_state=random_state,
            objective="multi:softprob",
            num_class=3,
            eval_metric="mlogloss",
            use_label_encoder=False,
            n_jobs=-1,
        )
        self._feature_names: list = []
        self._is_trained = False
        logger.info(
            "XGBoostModel created (n_estimators=%d, lr=%.3f, depth=%d)",
            n_estimators, learning_rate, max_depth,
        )

    def train(
        self, X: np.ndarray, y: np.ndarray,
        feature_names: Optional[list] = None,
        eval_set: Optional[list] = None,
    ) -> None:
        """
        Train the model.

        Args:
            X: 2-D array (n_samples, n_features).
            y: 1-D array of labels (0=low, 1=medium, 2=high).
            feature_names: Optional list of feature name strings.
            eval_set: Optional [(X_val, y_val)] for early stopping.
        """
        fit_params = {}
        if eval_set:
            fit_params["eval_set"] = eval_set
            fit_params["verbose"] = False
        self.model.fit(X, y, **fit_params)
        self._feature_names = feature_names or [f"f_{i}" for i in range(X.shape[1])]
        self._is_trained = True
        logger.info("XGBoost trained on %d samples, %d features", *X.shape)

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict class labels."""
        return self.model.predict(X)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Predict class probabilities."""
        return self.model.predict_proba(X)

    def feature_importance(self) -> Dict[str, float]:
        """Return dict of feature_name → importance (gain)."""
        if not self._is_trained:
            return {}
        importances = self.model.feature_importances_
        return dict(zip(self._feature_names, importances.tolist()))

    def save(self, path: str) -> None:
        """Save model to disk."""
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({
            "model": self.model,
            "feature_names": self._feature_names,
        }, path)
        logger.info("XGBoost saved to %s", path)

    def load(self, path: str) -> None:
        """Load model from disk."""
        data = joblib.load(path)
        self.model = data["model"]
        self._feature_names = data["feature_names"]
        self._is_trained = True
        logger.info("XGBoost loaded from %s", path)
