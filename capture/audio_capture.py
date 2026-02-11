"""
CogniSense — Audio Capture Module.

Records microphone audio in fixed-size chunks using sounddevice.
Provides raw audio buffers for downstream voice-stress feature
extraction via Librosa.

Usage:
    ac = AudioCapture(sample_rate=16000, chunk_duration=1.0)
    ac.start()
    chunk = ac.read_chunk()   # Returns AudioChunk or None
    ac.stop()
"""

import time
import logging
import threading
import queue
from dataclasses import dataclass
from typing import Optional

import numpy as np
import sounddevice as sd

logger = logging.getLogger(__name__)


@dataclass
class AudioChunk:
    """A single chunk of captured audio data."""
    timestamp: float              # time.time() epoch seconds
    samples: np.ndarray           # 1-D float32 array, mono
    sample_rate: int
    duration_sec: float


class AudioCapture:
    """
    Captures microphone audio in fixed-duration chunks.

    Uses sounddevice's InputStream with a callback that pushes
    audio data into a thread-safe queue for consumption by the
    feature extraction pipeline.

    Attributes:
        sample_rate: Audio sample rate in Hz (default 16000).
        chunk_duration: Duration of each chunk in seconds (default 1.0).
        device_index: Audio input device index (None = system default).
    """

    def __init__(
        self,
        sample_rate: int = 16000,
        chunk_duration: float = 1.0,
        device_index: Optional[int] = None,
    ):
        self.sample_rate = sample_rate
        self.chunk_duration = chunk_duration
        self.device_index = device_index
        self._block_size = int(sample_rate * chunk_duration)
        self._stream: Optional[sd.InputStream] = None
        self._queue: queue.Queue = queue.Queue(maxsize=50)
        self._buffer: np.ndarray = np.array([], dtype=np.float32)
        self._lock = threading.Lock()
        self._running = False
        logger.info(
            "AudioCapture initialized (rate=%d, chunk=%.1fs, device=%s)",
            sample_rate, chunk_duration, device_index,
        )

    def _audio_callback(
        self, indata: np.ndarray, frames: int,
        time_info, status
    ) -> None:
        """Sounddevice callback — accumulates samples into chunks."""
        if status:
            logger.warning("Audio stream status: %s", status)

        # Convert to mono float32
        mono = indata[:, 0].astype(np.float32)

        with self._lock:
            self._buffer = np.concatenate([self._buffer, mono])

            # Emit full chunks
            while len(self._buffer) >= self._block_size:
                chunk_data = self._buffer[:self._block_size].copy()
                self._buffer = self._buffer[self._block_size:]

                chunk = AudioChunk(
                    timestamp=time.time(),
                    samples=chunk_data,
                    sample_rate=self.sample_rate,
                    duration_sec=self.chunk_duration,
                )
                try:
                    self._queue.put_nowait(chunk)
                except queue.Full:
                    # Drop oldest to prevent memory buildup
                    try:
                        self._queue.get_nowait()
                    except queue.Empty:
                        pass
                    self._queue.put_nowait(chunk)

    def start(self) -> None:
        """Open audio stream and begin recording."""
        if self._running:
            logger.warning("AudioCapture already running")
            return

        self._stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype="float32",
            device=self.device_index,
            blocksize=1024,
            callback=self._audio_callback,
        )
        self._stream.start()
        self._running = True
        logger.info("Audio capture started")

    def read_chunk(self) -> Optional[AudioChunk]:
        """
        Read the next available audio chunk.

        Returns:
            AudioChunk if available, None if queue is empty.
        """
        try:
            return self._queue.get_nowait()
        except queue.Empty:
            return None

    def read_chunk_blocking(self, timeout: float = 2.0) -> Optional[AudioChunk]:
        """
        Read the next audio chunk, blocking until available.

        Args:
            timeout: Max seconds to wait.

        Returns:
            AudioChunk if available within timeout, None otherwise.
        """
        try:
            return self._queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def stop(self) -> None:
        """Stop audio stream and flush buffers."""
        self._running = False
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None
        with self._lock:
            self._buffer = np.array([], dtype=np.float32)
        # Clear queue
        while not self._queue.empty():
            try:
                self._queue.get_nowait()
            except queue.Empty:
                break
        logger.info("Audio capture stopped")

    @property
    def is_running(self) -> bool:
        """Return whether the capture is active."""
        return self._running

    @property
    def queue_size(self) -> int:
        """Return number of chunks waiting in queue."""
        return self._queue.qsize()
