"""
CogniSense — Feature Fusion Engine.

Merges visual (18), behavioral (20), and audio (21) features into
a single unified vector for classification. Applies modality
prefixing, normalization, and handles windowed data collection
from all sensor modules.

Usage:
    from ml.features.fusion import FeatureFusionEngine

    engine = FeatureFusionEngine(window_sec=5.0, fps=15)
    engine.push_landmark_frame(frame)
    engine.push_keystroke_events(key_events)
    engine.push_mouse_events(mouse_events)
    engine.push_audio_chunk(chunk)

    fused = engine.extract()   # Dict[str, float] with ~59 features
"""

import time
import logging
from typing import Dict, List, Optional
from collections import deque

import numpy as np
from sklearn.preprocessing import StandardScaler

from capture.webcam_capture import LandmarkFrame
from capture.keystroke_logger import KeyEvent
from capture.mouse_tracker import MouseEvent
from capture.audio_capture import AudioChunk
from ml.features.visual_features import extract_visual_features
from ml.features.behavioral_features import (
    extract_keystroke_features,
    extract_mouse_features,
)
from ml.features.audio_features import extract_audio_features_window

logger = logging.getLogger(__name__)


class FeatureFusionEngine:
    """
    Collects sensor data over a time window and produces a fused
    feature vector across all modalities.

    Maintains rolling buffers for each modality and extracts
    features on demand via the extract() method.

    Attributes:
        window_sec: Duration of the feature extraction window.
        fps: Webcam frame rate (for visual feature calculations).
    """

    # Modality prefixes for namespacing
    VIS_PREFIX = "vis_"
    BEH_PREFIX = "beh_"
    AUD_PREFIX = "aud_"

    def __init__(self, window_sec: float = 5.0, fps: int = 15):
        self.window_sec = window_sec
        self.fps = fps

        # Rolling buffers
        self._landmark_frames: deque = deque()
        self._keystroke_events: List[KeyEvent] = []
        self._mouse_events: List[MouseEvent] = []
        self._audio_chunks: List[AudioChunk] = []

        # Normalization (fitted during training, applied at inference)
        self._scaler: Optional[StandardScaler] = None
        self._is_fitted = False

        logger.info(
            "FeatureFusionEngine initialized (window=%.1fs, fps=%d)",
            window_sec, fps,
        )

    # ── Data Push Methods ────────────────────────────────────────

    def push_landmark_frame(self, frame: LandmarkFrame) -> None:
        """Add a face landmark frame to the visual buffer."""
        self._landmark_frames.append(frame)
        self._trim_visual_buffer()

    def push_landmark_frames(self, frames: List[LandmarkFrame]) -> None:
        """Add multiple landmark frames."""
        self._landmark_frames.extend(frames)
        self._trim_visual_buffer()

    def push_keystroke_events(self, events: List[KeyEvent]) -> None:
        """Add keystroke events to the behavioral buffer."""
        self._keystroke_events.extend(events)
        self._trim_keystroke_buffer()

    def push_mouse_events(self, events: List[MouseEvent]) -> None:
        """Add mouse events to the behavioral buffer."""
        self._mouse_events.extend(events)
        self._trim_mouse_buffer()

    def push_audio_chunk(self, chunk: AudioChunk) -> None:
        """Add an audio chunk to the audio buffer."""
        self._audio_chunks.append(chunk)
        self._trim_audio_buffer()

    def push_audio_chunks(self, chunks: List[AudioChunk]) -> None:
        """Add multiple audio chunks."""
        self._audio_chunks.extend(chunks)
        self._trim_audio_buffer()

    # ── Buffer Trimming ──────────────────────────────────────────

    def _trim_visual_buffer(self) -> None:
        """Keep only frames within the current window."""
        cutoff = time.time() - self.window_sec
        while self._landmark_frames and self._landmark_frames[0].timestamp < cutoff:
            self._landmark_frames.popleft()

    def _trim_keystroke_buffer(self) -> None:
        """Keep only keystroke events within the current window."""
        cutoff = time.time() - self.window_sec
        self._keystroke_events = [
            e for e in self._keystroke_events if e.timestamp >= cutoff
        ]

    def _trim_mouse_buffer(self) -> None:
        """Keep only mouse events within the current window."""
        cutoff = time.time() - self.window_sec
        self._mouse_events = [
            e for e in self._mouse_events if e.timestamp >= cutoff
        ]

    def _trim_audio_buffer(self) -> None:
        """Keep only audio chunks within the current window."""
        cutoff = time.time() - self.window_sec
        self._audio_chunks = [
            c for c in self._audio_chunks if c.timestamp >= cutoff
        ]

    # ── Feature Extraction ───────────────────────────────────────

    def extract(self) -> Dict[str, float]:
        """
        Extract and fuse features from all modality buffers.

        Returns:
            Dict with ~59 prefixed features:
                vis_* (18) + beh_* (20) + aud_* (21)
        """
        fused: Dict[str, float] = {}

        # ── Visual features ─────────────────────────────────────
        vis_frames = list(self._landmark_frames)
        vis_features = extract_visual_features(vis_frames, fps=self.fps)
        for k, v in vis_features.items():
            fused[f"{self.VIS_PREFIX}{k}"] = v

        # ── Behavioral features (keystroke) ─────────────────────
        ks_features = extract_keystroke_features(
            self._keystroke_events, window_sec=self.window_sec
        )
        for k, v in ks_features.items():
            fused[f"{self.BEH_PREFIX}{k}"] = v

        # ── Behavioral features (mouse) ─────────────────────────
        ms_features = extract_mouse_features(
            self._mouse_events, window_sec=self.window_sec
        )
        for k, v in ms_features.items():
            fused[f"{self.BEH_PREFIX}{k}"] = v

        # ── Audio features ──────────────────────────────────────
        aud_features = extract_audio_features_window(self._audio_chunks)
        for k, v in aud_features.items():
            fused[f"{self.AUD_PREFIX}{k}"] = v

        logger.debug(
            "Fused %d features (vis=%d, beh=%d, aud=%d)",
            len(fused), len(vis_features),
            len(ks_features) + len(ms_features), len(aud_features),
        )
        return fused

    def extract_array(self) -> np.ndarray:
        """
        Extract features as a sorted 1-D numpy array.

        Useful for direct model input. Keys are sorted alphabetically
        for consistent ordering.

        Returns:
            1-D numpy array of feature values.
        """
        features = self.extract()
        keys = sorted(features.keys())
        return np.array([features[k] for k in keys], dtype=np.float64)

    def get_feature_names(self) -> List[str]:
        """Return sorted list of all feature names."""
        features = self.extract()
        return sorted(features.keys())

    # ── Normalization ────────────────────────────────────────────

    def fit_scaler(self, feature_matrix: np.ndarray) -> None:
        """
        Fit the StandardScaler on a training feature matrix.

        Args:
            feature_matrix: 2-D array (n_samples, n_features).
        """
        self._scaler = StandardScaler()
        self._scaler.fit(feature_matrix)
        self._is_fitted = True
        logger.info("Scaler fitted on %d samples", feature_matrix.shape[0])

    def normalize(self, feature_array: np.ndarray) -> np.ndarray:
        """
        Normalize a feature array using the fitted scaler.

        Args:
            feature_array: 1-D or 2-D array of features.

        Returns:
            Normalized array.
        """
        if not self._is_fitted or self._scaler is None:
            logger.warning("Scaler not fitted, returning raw features")
            return feature_array
        if feature_array.ndim == 1:
            return self._scaler.transform(feature_array.reshape(1, -1))[0]
        return self._scaler.transform(feature_array)

    # ── Buffer Management ────────────────────────────────────────

    def clear_buffers(self) -> None:
        """Clear all modality buffers."""
        self._landmark_frames.clear()
        self._keystroke_events.clear()
        self._mouse_events.clear()
        self._audio_chunks.clear()
        logger.debug("All buffers cleared")

    def buffer_stats(self) -> Dict[str, int]:
        """Return counts of items in each buffer."""
        return {
            "landmark_frames": len(self._landmark_frames),
            "keystroke_events": len(self._keystroke_events),
            "mouse_events": len(self._mouse_events),
            "audio_chunks": len(self._audio_chunks),
        }
