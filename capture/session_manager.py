"""
CogniSense — Session Manager.

Coordinates all sensor modules (webcam, keystroke, mouse, audio)
into a unified capture session lifecycle. Audio is always enabled.

Usage:
    sm = SessionManager(camera_index=0, fps=15)
    sm.start_all()
    # ... capture loop ...
    sm.stop_all()
"""

import logging
from typing import Optional

from capture.webcam_capture import WebcamCapture
from capture.keystroke_logger import KeystrokeLogger
from capture.mouse_tracker import MouseTracker
from capture.audio_capture import AudioCapture

logger = logging.getLogger(__name__)


class SessionManager:
    """
    Orchestrates sensor start/stop and data collection.

    All four modalities (webcam, keystroke, mouse, audio) are
    always active. Provides a single interface for the backend
    to manage the full capture pipeline.
    """

    def __init__(
        self,
        camera_index: int = 0,
        fps: int = 15,
        audio_sample_rate: int = 16000,
    ):
        self.webcam = WebcamCapture(camera_index=camera_index, fps=fps)
        self.keystroke = KeystrokeLogger()
        self.mouse = MouseTracker()
        self.audio = AudioCapture(sample_rate=audio_sample_rate)
        self._active = False
        logger.info(
            "SessionManager initialized (camera=%d, fps=%d, audio_rate=%d)",
            camera_index, fps, audio_sample_rate,
        )

    def start_all(self) -> None:
        """Start all four sensors."""
        self.webcam.start()
        self.keystroke.start()
        self.mouse.start()
        self.audio.start()
        self._active = True
        logger.info("All sensors started (webcam, keystroke, mouse, audio)")

    def stop_all(self) -> None:
        """Stop all sensors and flush buffers."""
        self.webcam.stop()
        self.keystroke.stop()
        self.mouse.stop()
        self.audio.stop()
        self._active = False
        logger.info("All sensors stopped")

    @property
    def is_active(self) -> bool:
        """Return whether the session is currently capturing."""
        return self._active
