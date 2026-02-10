"""
CogniSense — Audio Capture Module.

Captures microphone audio stream for voice stress analysis.
This module is optional and toggled via configuration.
"""

import logging

logger = logging.getLogger(__name__)


class AudioCapture:
    """
    Records audio from the microphone using sounddevice/PyAudio.

    Produces audio chunks for downstream feature extraction
    (pitch, jitter, shimmer, MFCC).
    """

    def __init__(self, sample_rate: int = 16000, chunk_duration: float = 1.0):
        self.sample_rate = sample_rate
        self.chunk_duration = chunk_duration
        self._stream = None
        logger.info(
            "AudioCapture initialized (rate=%d, chunk=%.1fs)",
            sample_rate,
            chunk_duration,
        )

    def start(self) -> None:
        """Open microphone stream."""
        # TODO: Implement — sounddevice.InputStream
        logger.info("Audio capture started")

    def read_chunk(self):
        """Read a chunk of audio samples."""
        # TODO: Implement
        return None

    def stop(self) -> None:
        """Close microphone stream."""
        # TODO: Implement cleanup
        logger.info("Audio capture stopped")
