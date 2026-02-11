"""
CogniSense — Keystroke Dynamics Logger.

Captures key press and release events with millisecond timestamps
using pynput. Buffers events for windowed feature extraction of
dwell time, flight time, typing speed, and error patterns.

Usage:
    ks = KeystrokeLogger()
    ks.start()
    events = ks.get_events()   # Returns list of KeyEvent
    ks.stop()
"""

import time
import logging
import threading
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum

from pynput import keyboard

logger = logging.getLogger(__name__)


class KeyEventType(str, Enum):
    """Type of keyboard event."""
    PRESS = "press"
    RELEASE = "release"


@dataclass
class KeyEvent:
    """A single keyboard event with timing information."""
    key: str
    event_type: KeyEventType
    timestamp: float              # time.time() epoch seconds
    is_error_key: bool = False    # True for backspace, delete


# Keys considered as error corrections
ERROR_KEYS = {
    keyboard.Key.backspace, keyboard.Key.delete,
}

# Keys to skip entirely (modifiers captured but not useful alone)
MODIFIER_KEYS = {
    keyboard.Key.shift, keyboard.Key.shift_r,
    keyboard.Key.ctrl, keyboard.Key.ctrl_r,
    keyboard.Key.alt, keyboard.Key.alt_r,
    keyboard.Key.cmd, keyboard.Key.cmd_r,
}


class KeystrokeLogger:
    """
    Logs keyboard press/release events using pynput.

    Thread-safe event buffer that captures key identity, timing,
    and error-key detection for downstream feature extraction.
    """

    def __init__(self):
        self._listener: Optional[keyboard.Listener] = None
        self._events: List[KeyEvent] = []
        self._lock = threading.Lock()
        self._running = False
        logger.info("KeystrokeLogger initialized")

    def _key_to_str(self, key) -> str:
        """Convert pynput key to string representation."""
        try:
            return key.char if key.char else str(key)
        except AttributeError:
            return str(key)

    def _on_press(self, key) -> None:
        """Handle key press event."""
        if key in MODIFIER_KEYS:
            return
        event = KeyEvent(
            key=self._key_to_str(key),
            event_type=KeyEventType.PRESS,
            timestamp=time.time(),
            is_error_key=(key in ERROR_KEYS),
        )
        with self._lock:
            self._events.append(event)

    def _on_release(self, key) -> None:
        """Handle key release event."""
        if key in MODIFIER_KEYS:
            return
        event = KeyEvent(
            key=self._key_to_str(key),
            event_type=KeyEventType.RELEASE,
            timestamp=time.time(),
            is_error_key=(key in ERROR_KEYS),
        )
        with self._lock:
            self._events.append(event)

    def start(self) -> None:
        """Begin listening for keyboard events in a background thread."""
        if self._running:
            logger.warning("KeystrokeLogger already running")
            return
        self._listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release,
        )
        self._listener.start()
        self._running = True
        logger.info("Keystroke logging started")

    def get_events(self) -> List[KeyEvent]:
        """
        Return all buffered events and clear the buffer.

        Returns:
            List of KeyEvent objects captured since last call.
        """
        with self._lock:
            events = self._events.copy()
            self._events.clear()
        return events

    def peek_events(self) -> List[KeyEvent]:
        """Return buffered events without clearing."""
        with self._lock:
            return self._events.copy()

    def stop(self) -> None:
        """Stop the keyboard listener and flush remaining events."""
        self._running = False
        if self._listener is not None:
            self._listener.stop()
            self._listener = None
        logger.info("Keystroke logging stopped (%d events buffered)", len(self._events))

    @property
    def is_running(self) -> bool:
        """Return whether the logger is active."""
        return self._running
