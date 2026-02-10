"""
CogniSense — Keystroke Dynamics Logger.

Captures key press/release events with timestamps for
computing typing rhythm features (dwell time, flight time, WPM).
"""

import logging

logger = logging.getLogger(__name__)


class KeystrokeLogger:
    """
    Logs keyboard events using pynput.

    Produces a stream of (key, event_type, timestamp) tuples.
    """

    def __init__(self):
        self._listener = None
        self._events = []
        logger.info("KeystrokeLogger initialized")

    def start(self) -> None:
        """Begin listening for keyboard events."""
        # TODO: Implement — pynput.keyboard.Listener
        logger.info("Keystroke logging started")

    def get_events(self) -> list:
        """Return and clear buffered keystroke events."""
        events = self._events.copy()
        self._events.clear()
        return events

    def stop(self) -> None:
        """Stop the keyboard listener."""
        # TODO: Implement cleanup
        logger.info("Keystroke logging stopped")
