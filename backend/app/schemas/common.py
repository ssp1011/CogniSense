"""
CogniSense — Common Schemas.

Shared Pydantic models used across multiple endpoints.
"""

from enum import Enum
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class LoadLevel(str, Enum):
    """Cognitive load classification levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Scenario(str, Enum):
    """Supported capture scenarios."""
    GENERAL = "general"
    CODING = "coding"
    EXAM = "exam"
    INTERVIEW = "interview"


class ModalityScores(BaseModel):
    """Per-modality contribution scores."""
    visual: float = 0.0
    behavioral: float = 0.0
    audio: float = 0.0


class TimestampMixin(BaseModel):
    """Mixin providing timestamp fields."""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
