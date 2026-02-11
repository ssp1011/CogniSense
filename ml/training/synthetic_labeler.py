"""
CogniSense — Synthetic Data Labeler.

Generates synthetic cognitive load labels from feature vectors
using rule-based heuristics when no real labeled dataset is available.

Labeling strategy:
  - High load: High blink rate, low EAR, high error rate, fast mouse
  - Medium load: Moderate values across modalities
  - Low load: Relaxed patterns across all signals

Usage:
    from ml.training.synthetic_labeler import SyntheticLabeler
    labeler = SyntheticLabeler()
    labels = labeler.label(feature_matrix, feature_names)
"""

import logging
from typing import Dict, List

import numpy as np

logger = logging.getLogger(__name__)

LABEL_LOW = 0
LABEL_MEDIUM = 1
LABEL_HIGH = 2


class SyntheticLabeler:
    """
    Rule-based labeler that generates synthetic cognitive load labels.

    Scores each sample across multiple stress indicators and maps
    the aggregate score to low / medium / high.
    """

    def __init__(self):
        # Stress indicator rules: feature_name → (high_threshold, weight)
        # Values above threshold contribute to high-load score
        self._high_indicators: Dict[str, tuple] = {
            "vis_blink_rate": (22.0, 1.5),       # High blink rate
            "vis_head_movement": (3.0, 1.0),      # Restless head
            "vis_head_pitch_std": (4.0, 1.0),     # Head instability
            "vis_gaze_deviation_mean": (0.08, 1.0),
            "beh_error_rate": (0.15, 2.0),        # Many typos
            "beh_pause_count": (3.0, 1.0),        # Many pauses
            "beh_mouse_velocity_std": (500.0, 1.0),
            "beh_click_rate": (2.0, 0.5),
            "aud_pitch_std": (30.0, 1.5),         # Voice stress
            "aud_jitter": (0.02, 1.5),
            "aud_shimmer": (0.05, 1.0),
            "aud_speaking_rate": (4.0, 1.0),
        }
        # Low-load indicators: feature below threshold → low score
        self._low_indicators: Dict[str, tuple] = {
            "vis_ear_mean": (0.35, 1.5),          # Eyes wide open
            "vis_blink_rate": (12.0, 1.0),        # Calm blink rate
            "beh_burst_rate": (8.0, 1.0),         # Steady typing
            "beh_flight_std": (0.1, 1.0),         # Consistent rhythm
            "beh_idle_time": (0.5, 0.5),          # Minimal idle
            "beh_movement_straightness": (0.5, 1.0),
            "aud_pitch_std": (10.0, 1.0),         # Stable voice
        }
        logger.info("SyntheticLabeler initialized with %d rules",
                     len(self._high_indicators) + len(self._low_indicators))

    def label(
        self, X: np.ndarray, feature_names: List[str]
    ) -> np.ndarray:
        """
        Generate synthetic labels for a feature matrix.

        Args:
            X: 2-D array (n_samples, n_features).
            feature_names: List of feature names matching columns.

        Returns:
            1-D array of labels (0=low, 1=medium, 2=high).
        """
        name_to_idx = {name: i for i, name in enumerate(feature_names)}
        n_samples = X.shape[0]
        scores = np.zeros(n_samples, dtype=np.float64)

        # High-load scoring
        for feat, (threshold, weight) in self._high_indicators.items():
            if feat in name_to_idx:
                idx = name_to_idx[feat]
                scores += weight * (X[:, idx] > threshold).astype(float)

        # Low-load scoring (subtract)
        for feat, (threshold, weight) in self._low_indicators.items():
            if feat in name_to_idx:
                idx = name_to_idx[feat]
                scores -= weight * (X[:, idx] < threshold).astype(float)

        # Add noise to create natural variation
        rng = np.random.RandomState(42)
        scores += rng.normal(0, 0.5, n_samples)

        # Map scores to labels
        labels = np.full(n_samples, LABEL_MEDIUM, dtype=int)
        labels[scores > 2.0] = LABEL_HIGH
        labels[scores < -1.0] = LABEL_LOW

        counts = {
            "low": int(np.sum(labels == 0)),
            "medium": int(np.sum(labels == 1)),
            "high": int(np.sum(labels == 2)),
        }
        logger.info("Synthetic labels: %s", counts)
        return labels

    def generate_synthetic_dataset(
        self, n_samples: int = 500, n_features: int = 59
    ) -> tuple:
        """
        Generate a fully synthetic feature matrix + labels.

        Creates random feature values within realistic ranges
        and labels them using the rule-based system.

        Args:
            n_samples: Number of samples.
            n_features: Number of features.

        Returns:
            (X, y, feature_names) tuple.
        """
        rng = np.random.RandomState(42)

        # Generate feature names matching fusion engine output
        feature_names = sorted([
            "vis_blink_count", "vis_blink_rate",
            "vis_ear_mean", "vis_ear_std", "vis_ear_min", "vis_ear_range",
            "vis_eyebrow_dist_mean", "vis_eyebrow_dist_std",
            "vis_mar_mean", "vis_mar_std",
            "vis_head_pitch_mean", "vis_head_pitch_std",
            "vis_head_yaw_std", "vis_head_roll_std", "vis_head_movement",
            "vis_gaze_deviation_mean", "vis_gaze_deviation_std",
            "vis_face_presence",
            "beh_wpm", "beh_key_count",
            "beh_dwell_mean", "beh_dwell_std",
            "beh_flight_mean", "beh_flight_std",
            "beh_error_rate", "beh_burst_rate", "beh_pause_count",
            "beh_mouse_distance", "beh_mouse_velocity_mean",
            "beh_mouse_velocity_std", "beh_mouse_acceleration_mean",
            "beh_click_count", "beh_click_rate",
            "beh_left_click_ratio", "beh_scroll_total",
            "beh_direction_changes", "beh_idle_time",
            "beh_movement_straightness",
            "aud_pitch_mean", "aud_pitch_std",
            "aud_jitter", "aud_shimmer",
        ] + [f"aud_mfcc_{i+1}_mean" for i in range(13)] + [
            "aud_spectral_centroid", "aud_spectral_rolloff",
            "aud_rms_energy", "aud_zcr", "aud_speaking_rate",
        ])

        # Realistic value ranges per feature
        ranges = {
            "vis_blink_rate": (8, 35), "vis_ear_mean": (0.2, 0.4),
            "vis_head_movement": (0.5, 8.0), "vis_head_pitch_std": (1, 8),
            "vis_gaze_deviation_mean": (0.02, 0.15),
            "beh_wpm": (20, 90), "beh_error_rate": (0.0, 0.3),
            "beh_burst_rate": (3, 15), "beh_pause_count": (0, 8),
            "beh_mouse_velocity_std": (100, 800),
            "beh_click_rate": (0.2, 4.0),
            "beh_idle_time": (0.0, 3.0),
            "beh_movement_straightness": (0.1, 1.0),
            "aud_pitch_mean": (100, 300), "aud_pitch_std": (5, 50),
            "aud_jitter": (0.005, 0.04), "aud_shimmer": (0.01, 0.08),
            "aud_speaking_rate": (1.5, 5.5),
        }

        X = rng.uniform(0, 1, size=(n_samples, len(feature_names)))

        # Scale known features to realistic ranges
        for feat, (lo, hi) in ranges.items():
            if feat in feature_names:
                idx = feature_names.index(feat)
                X[:, idx] = rng.uniform(lo, hi, n_samples)

        y = self.label(X, feature_names)
        logger.info("Generated synthetic dataset: %d samples, %d features", n_samples, len(feature_names))
        return X, y, feature_names
