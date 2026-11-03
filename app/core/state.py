"""State machine and event definitions for SOUNDARYA Assistant."""

from __future__ import annotations
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional


class AssistantState(str, Enum):
    """Execution states for the AI Assistant."""
    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    SPEAKING = "speaking"
    EXECUTING = "executing"
    ERROR = "error"


class PermissionLevel(str, Enum):
    """Security clearance tiers."""
    LEVEL_1 = "SAFE"
    LEVEL_2 = "CONFIRMATION_REQUIRED"
    LEVEL_3 = "RESTRICTED"


@dataclass
class ActionRequest:
    """Represents a planned action to be validated by the security engine."""
    action_id: str
    action_name: str
    category: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    permission_level: PermissionLevel = PermissionLevel.LEVEL_1
    description: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    confirmed: bool = False


@dataclass
class ExecutionResult:
    """Outcome of an executed command or action."""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    action_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
