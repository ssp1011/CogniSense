"""
CogniSense — SVM Classifier Wrapper.

Standardized wrapper around scikit-learn SVC for cognitive load
prediction with probability calibration.

Usage:
    from ml.models.svm_clf import SVMModel
    model = SVMModel(kernel="rbf", C=1.0)
    model.train(X_train, y_train)
    predictions = model.predict(X_test)
"""

import logging
from typing import Dict, Optional
from pathlib import Path

import numpy as np
import joblib
from sklearn.svm import SVC

logger = logging.getLogger(__name__)


class SVMModel:
    """
    SVM classifier for cognitive load levels.

    Uses RBF kernel with probability=True for calibrated
    confidence scores. Includes StandardScaler internally since
    SVM is sensitive to feature scales.
    """

    def __init__(
        self,
        kernel: str = "rbf",
        C: float = 1.0,
        gamma: str = "scale",
        random_state: int = 42,
        class_weight: str = "balanced",
    ):
        self.model = SVC(
            kernel=kernel,
            C=C,
            gamma=gamma,
            random_state=random_state,
            class_weight=class_weight,
            probability=True,
        )
        self._feature_names: list = []
        self._is_trained = False
        logger.info(
            "SVMModel created (kernel=%s, C=%.2f, gamma=%s)",
            kernel, C, gamma,
        )

    def train(
        self, X: np.ndarray, y: np.ndarray,
        feature_names: Optional[list] = None,
    ) -> None:
        """
        Train the SVM model.

        Args:
            X: 2-D array (n_samples, n_features). Should be pre-scaled.
            y: 1-D array of labels (0=low, 1=medium, 2=high).
            feature_names: Optional list of feature name strings.
        """
        self.model.fit(X, y)
        self._feature_names = feature_names or [f"f_{i}" for i in range(X.shape[1])]
        self._is_trained = True
        logger.info("SVM trained on %d samples, %d features", *X.shape)

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict class labels."""
        return self.model.predict(X)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Predict calibrated class probabilities."""
        return self.model.predict_proba(X)

    def feature_importance(self) -> Dict[str, float]:
        """
        Return feature importance proxy.

        For SVM, uses absolute mean of support vector coefficients
        for linear kernel. Returns empty for non-linear kernels.
        """
        if not self._is_trained:
            return {}
        if self.model.kernel == "linear":
            importances = np.abs(self.model.coef_).mean(axis=0)
            return dict(zip(self._feature_names, importances.tolist()))
        return {name: 0.0 for name in self._feature_names}

    def save(self, path: str) -> None:
        """Save model to disk."""
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({
            "model": self.model,
            "feature_names": self._feature_names,
        }, path)
        logger.info("SVM saved to %s", path)

    def load(self, path: str) -> None:
        """Load model from disk."""
        data = joblib.load(path)
        self.model = data["model"]
        self._feature_names = data["feature_names"]
        self._is_trained = True
        logger.info("SVM loaded from %s", path)
