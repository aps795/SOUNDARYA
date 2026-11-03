"""Application Launcher and process execution plugin for SOUNDARYA."""

from __future__ import annotations
from typing import Dict, Any
from app.core.state import PermissionLevel, ExecutionResult
from app.plugins.base_plugin import BasePlugin
from app.system.app_launcher import app_launcher


class AppLauncherPlugin(BasePlugin):
    @property
    def name(self) -> str:
        return "app:open"

    @property
    def description(self) -> str:
        return "Finds and launches approved system applications by name or natural language alias."

    @property
    def required_permission(self) -> PermissionLevel:
        return PermissionLevel.LEVEL_1

    def execute(self, params: Dict[str, Any]) -> ExecutionResult:
        app_name = params.get("app_name", "").strip()
        if not app_name:
            return ExecutionResult(success=False, message="No application name specified.")

        success, msg = app_launcher.launch_app(app_name)
        return ExecutionResult(
            success=success,
            message=msg,
            data={"app_name": app_name}
        )
