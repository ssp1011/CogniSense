"""
CogniSense — Mouse Movement Tracker.

Captures mouse position, clicks, and scroll events with timestamps
using pynput. Buffers events for windowed feature extraction of
velocity, acceleration, click patterns, and idle detection.

Usage:
    mt = MouseTracker()
    mt.start()
    events = mt.get_events()   # Returns list of MouseEvent
    mt.stop()
"""

import time
import logging
import threading
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum

from pynput import mouse

logger = logging.getLogger(__name__)


class MouseEventType(str, Enum):
    """Type of mouse event."""
    MOVE = "move"
    CLICK = "click"
    SCROLL = "scroll"


@dataclass
class MouseEvent:
    """A single mouse event with position and timing."""
    event_type: MouseEventType
    x: int
    y: int
    timestamp: float              # time.time() epoch seconds
    button: Optional[str] = None  # "left" | "right" | "middle"
    pressed: Optional[bool] = None  # True=press, False=release (clicks)
    scroll_dx: int = 0
    scroll_dy: int = 0


class MouseTracker:
    """
    Tracks mouse move, click, and scroll events using pynput.

    Thread-safe event buffer that captures position, button identity,
    and scroll deltas for downstream feature extraction (velocity,
    acceleration, click rate, idle time).
    """

    def __init__(self):
        self._listener: Optional[mouse.Listener] = None
        self._events: List[MouseEvent] = []
        self._lock = threading.Lock()
        self._running = False
        self._last_move_time: float = 0.0
        self._move_throttle: float = 0.02  # Min 20ms between move events
        logger.info("MouseTracker initialized")

    def _on_move(self, x: int, y: int) -> None:
        """Handle mouse move event (throttled)."""
        now = time.time()
        if now - self._last_move_time < self._move_throttle:
            return
        self._last_move_time = now

        event = MouseEvent(
            event_type=MouseEventType.MOVE,
            x=x, y=y,
            timestamp=now,
        )
        with self._lock:
            self._events.append(event)

    def _on_click(self, x: int, y: int, button, pressed: bool) -> None:
        """Handle mouse click (press/release) event."""
        btn_name = str(button).replace("Button.", "")
        event = MouseEvent(
            event_type=MouseEventType.CLICK,
            x=x, y=y,
            timestamp=time.time(),
            button=btn_name,
            pressed=pressed,
        )
        with self._lock:
            self._events.append(event)

    def _on_scroll(self, x: int, y: int, dx: int, dy: int) -> None:
        """Handle mouse scroll event."""
        event = MouseEvent(
            event_type=MouseEventType.SCROLL,
            x=x, y=y,
            timestamp=time.time(),
            scroll_dx=dx,
            scroll_dy=dy,
        )
        with self._lock:
            self._events.append(event)

    def start(self) -> None:
        """Begin listening for mouse events in a background thread."""
        if self._running:
            logger.warning("MouseTracker already running")
            return
        self._listener = mouse.Listener(
            on_move=self._on_move,
            on_click=self._on_click,
            on_scroll=self._on_scroll,
        )
        self._listener.start()
        self._running = True
        logger.info("Mouse tracking started")

    def get_events(self) -> List[MouseEvent]:
        """
        Return all buffered events and clear the buffer.

        Returns:
            List of MouseEvent objects captured since last call.
        """
        with self._lock:
            events = self._events.copy()
            self._events.clear()
        return events

    def peek_events(self) -> List[MouseEvent]:
        """Return buffered events without clearing."""
        with self._lock:
            return self._events.copy()

    def stop(self) -> None:
        """Stop the mouse listener."""
        self._running = False
        if self._listener is not None:
            self._listener.stop()
            self._listener = None
        logger.info("Mouse tracking stopped (%d events buffered)", len(self._events))

    @property
    def is_running(self) -> bool:
        """Return whether the tracker is active."""
        return self._running
