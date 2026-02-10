"""
CogniSense — Custom Exceptions.

Application-specific exception classes for consistent error handling.
"""


class CogniSenseError(Exception):
    """Base exception for all CogniSense errors."""

    def __init__(self, message: str = "An error occurred"):
        self.message = message
        super().__init__(self.message)


class SessionNotFoundError(CogniSenseError):
    """Raised when a capture session ID is not found."""

    def __init__(self, session_id: str):
        super().__init__(f"Capture session not found: {session_id}")
        self.session_id = session_id


class SessionAlreadyActiveError(CogniSenseError):
    """Raised when trying to start a session while one is already active."""

    def __init__(self):
        super().__init__("A capture session is already active")


class ModelNotLoadedError(CogniSenseError):
    """Raised when inference is attempted before model is loaded."""

    def __init__(self):
        super().__init__("ML model is not loaded. Call load_model() first.")


class SensorError(CogniSenseError):
    """Raised when a sensor (webcam, mic, etc.) fails to initialize."""

    def __init__(self, sensor: str, detail: str = ""):
        super().__init__(f"Sensor '{sensor}' error: {detail}")
        self.sensor = sensor
