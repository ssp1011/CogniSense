"""
CogniSense — Session Manager.

Coordinates all sensor modules (webcam, keystroke, mouse, audio)
into a unified capture session lifecycle.
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

    Provides a single interface for the backend to manage
    all capture modalities.
    """

    def __init__(
        self,
        camera_index: int = 0,
        fps: int = 15,
        audio_enabled: bool = False,
    ):
        self.webcam = WebcamCapture(camera_index=camera_index, fps=fps)
        self.keystroke = KeystrokeLogger()
        self.mouse = MouseTracker()
        self.audio: Optional[AudioCapture] = (
            AudioCapture() if audio_enabled else None
        )
        self._active = False
        logger.info("SessionManager initialized (audio=%s)", audio_enabled)

    def start_all(self) -> None:
        """Start all configured sensors."""
        self.webcam.start()
        self.keystroke.start()
        self.mouse.start()
        if self.audio:
            self.audio.start()
        self._active = True
        logger.info("All sensors started")

    def stop_all(self) -> None:
        """Stop all sensors and flush buffers."""
        self.webcam.stop()
        self.keystroke.stop()
        self.mouse.stop()
        if self.audio:
            self.audio.stop()
        self._active = False
        logger.info("All sensors stopped")

    @property
    def is_active(self) -> bool:
        """Return whether the session is currently capturing."""
        return self._active
