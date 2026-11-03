"""Security and permission enforcement engine for SOUNDARYA."""

from __future__ import annotations
import logging
from typing import Callable, Dict, Optional, Tuple
from app.core.config import config
from app.core.state import ActionRequest, ExecutionResult, PermissionLevel

logger = logging.getLogger("Soundarya.Security")


class SecurityManager:
    """Enforces 3-tier permission control on all computer automation and data operations."""

    def __init__(self) -> None:
        self.permissions = config.permissions.get("levels", {})
        self.confirmation_handler: Optional[Callable[[ActionRequest], bool]] = None
        self.action_history: list[Dict[str, any]] = []

    def register_confirmation_handler(self, handler: Callable[[ActionRequest], bool]) -> None:
        """Register a UI callback (modal dialog or voice confirmation prompt) for Level 2 operations."""
        self.confirmation_handler = handler

    def classify_action(self, action_name: str) -> PermissionLevel:
        """Determine permission tier for a given action string (e.g., 'app:open', 'file:delete')."""
        # Level 3 Prohibited Check
        level_3 = self.permissions.get("level_3", {})
        prohibited = level_3.get("prohibited_actions", [
            "system:shutdown_force", "security:disable_firewall",
            "credentials:read_passwords", "filesystem:format_drive",
            "arbitrary_shell_injection"
        ])
        if action_name in prohibited:
            return PermissionLevel.LEVEL_3

        # Level 2 Confirmation Check
        level_2 = self.permissions.get("level_2", {})
        confirmation_required = level_2.get("allowed_actions", [
            "file:delete", "file:move", "folder:delete", "process:kill",
            "memory:delete", "memory:clear_all", "system:screenshot", "script:execute"
        ])
        if action_name in confirmation_required:
            return PermissionLevel.LEVEL_2

        # Level 1 Safe (Default for registered safe operations)
        return PermissionLevel.LEVEL_1

    def validate_and_authorize(self, request: ActionRequest) -> Tuple[bool, Optional[str]]:
        """
        Validate whether the action can proceed.
        Returns: (is_authorized, rejection_reason)
        """
        level = self.classify_action(request.action_name)
        request.permission_level = level

        logger.info(f"Evaluating action '{request.action_name}' under tier [{level.value}]")

        if level == PermissionLevel.LEVEL_3:
            msg = f"SECURITY ALERT: Action '{request.action_name}' is strictly RESTRICTED and was blocked."
            logger.warning(msg)
            self._log_audit(request, allowed=False, reason="Level 3 Violation")
            return False, msg

        if level == PermissionLevel.LEVEL_2:
            if request.confirmed:
                self._log_audit(request, allowed=True, reason="User previously confirmed")
                return True, None

            if self.confirmation_handler:
                user_approved = self.confirmation_handler(request)
                if user_approved:
                    request.confirmed = True
                    self._log_audit(request, allowed=True, reason="User confirmed via dialog")
                    return True, None
                else:
                    self._log_audit(request, allowed=False, reason="User rejected authorization")
                    return False, "Operation cancelled by user."
            else:
                # If no UI confirmation handler is bound, pause and reject safely
                return False, f"Action '{request.action_name}' requires explicit user confirmation."

        # Level 1 is safe to proceed
        self._log_audit(request, allowed=True, reason="Safe Level 1 Action")
        return True, None

    def _log_audit(self, request: ActionRequest, allowed: bool, reason: str) -> None:
        """Record all access attempts for user auditing and transparency."""
        entry = {
            "timestamp": request.timestamp.isoformat(),
            "action_id": request.action_id,
            "action_name": request.action_name,
            "params": request.parameters,
            "level": request.permission_level.value,
            "allowed": allowed,
            "reason": reason
        }
        self.action_history.append(entry)


# Global instance
security_engine = SecurityManager()
