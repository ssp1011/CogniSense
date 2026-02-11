"""
CogniSense — Random Forest Classifier Wrapper.

Standardized wrapper around scikit-learn RandomForestClassifier
for cognitive load prediction (low / medium / high).

Usage:
    from ml.models.random_forest import RandomForestModel
    model = RandomForestModel(n_estimators=200)
    model.train(X_train, y_train)
    predictions = model.predict(X_test)
    model.save("ml/saved_models/rf_model.pkl")
"""

import logging
from typing import Dict, Optional
from pathlib import Path

import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier

logger = logging.getLogger(__name__)


class RandomForestModel:
    """
    Random Forest classifier for cognitive load levels.

    Wraps scikit-learn RandomForestClassifier with a unified interface:
    train, predict, predict_proba, save, load, feature_importance.
    """

    def __init__(
        self,
        n_estimators: int = 200,
        max_depth: Optional[int] = None,
        min_samples_split: int = 5,
        min_samples_leaf: int = 2,
        random_state: int = 42,
        class_weight: str = "balanced",
    ):
        self.model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            min_samples_leaf=min_samples_leaf,
            random_state=random_state,
            class_weight=class_weight,
            n_jobs=-1,
        )
        self._feature_names: list = []
        self._is_trained = False
        logger.info(
            "RandomForestModel created (n_estimators=%d, max_depth=%s)",
            n_estimators, max_depth,
        )

    def train(
        self, X: np.ndarray, y: np.ndarray,
        feature_names: Optional[list] = None,
    ) -> None:
        """
        Train the model on feature matrix X and labels y.

        Args:
            X: 2-D array (n_samples, n_features).
            y: 1-D array of labels (0=low, 1=medium, 2=high).
            feature_names: Optional list of feature name strings.
        """
        self.model.fit(X, y)
        self._feature_names = feature_names or [f"f_{i}" for i in range(X.shape[1])]
        self._is_trained = True
        logger.info("RandomForest trained on %d samples, %d features", *X.shape)

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict class labels. Returns 1-D array of ints."""
        return self.model.predict(X)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Predict class probabilities. Returns (n_samples, 3) array."""
        return self.model.predict_proba(X)

    def feature_importance(self) -> Dict[str, float]:
        """Return dict of feature_name → importance score."""
        if not self._is_trained:
            return {}
        importances = self.model.feature_importances_
        return dict(zip(self._feature_names, importances.tolist()))

    def save(self, path: str) -> None:
        """Save model to disk via joblib."""
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({
            "model": self.model,
            "feature_names": self._feature_names,
        }, path)
        logger.info("RandomForest saved to %s", path)

    def load(self, path: str) -> None:
        """Load model from disk."""
        data = joblib.load(path)
        self.model = data["model"]
        self._feature_names = data["feature_names"]
        self._is_trained = True
        logger.info("RandomForest loaded from %s", path)
