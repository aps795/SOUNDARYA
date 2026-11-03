"""Base abstract provider for AI text and reasoning engines."""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class BaseAIProvider(ABC):
    """Abstract interface for all language model providers."""

    @abstractmethod
    def generate_response(self, prompt: str, system_prompt: Optional[str] = None, history: Optional[List[Dict[str, str]]] = None) -> str:
        """Generate conversational completion from prompt and context."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider credentials/endpoint are reachable."""
        pass
