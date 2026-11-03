"""Abstract base specification for SOUNDARYA automation plugins."""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple
from app.core.state import PermissionLevel, ExecutionResult


class BasePlugin(ABC):
    """Base class for all capability plugins."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier of the plugin."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable explanation of capability."""
        pass

    @property
    @abstractmethod
    def required_permission(self) -> PermissionLevel:
        """Security clearance level required to execute this plugin."""
        pass

    @abstractmethod
    def execute(self, params: Dict[str, Any]) -> ExecutionResult:
        """Run the plugin action with validated parameters."""
        pass
