"""
CogniSense — Mouse Movement Tracker.

Captures mouse position, clicks, and scroll events
for computing mouse dynamics features.
"""

import logging

logger = logging.getLogger(__name__)


class MouseTracker:
    """
    Tracks mouse events using pynput.

    Produces (x, y, event_type, timestamp) entries for
    velocity, acceleration, and click pattern features.
    """

    def __init__(self):
        self._listener = None
        self._events = []
        logger.info("MouseTracker initialized")

    def start(self) -> None:
        """Begin listening for mouse events."""
        # TODO: Implement — pynput.mouse.Listener
        logger.info("Mouse tracking started")

    def get_events(self) -> list:
        """Return and clear buffered mouse events."""
        events = self._events.copy()
        self._events.clear()
        return events

    def stop(self) -> None:
        """Stop the mouse listener."""
        # TODO: Implement cleanup
        logger.info("Mouse tracking stopped")
