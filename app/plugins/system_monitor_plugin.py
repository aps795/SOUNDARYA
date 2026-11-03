"""System monitoring and telemetry plugin for SOUNDARYA."""

from __future__ import annotations
from typing import Dict, Any
from app.core.state import PermissionLevel, ExecutionResult
from app.plugins.base_plugin import BasePlugin
from app.system.monitor import system_monitor


class SystemMonitorPlugin(BasePlugin):
    @property
    def name(self) -> str:
        return "system:status"

    @property
    def description(self) -> str:
        return "Reports real-time CPU, RAM, Battery, Disk, and system uptime metrics."

    @property
    def required_permission(self) -> PermissionLevel:
        return PermissionLevel.LEVEL_1

    def execute(self, params: Dict[str, Any]) -> ExecutionResult:
        metrics = system_monitor.get_metrics()
        summary = system_monitor.get_summary_text()
        return ExecutionResult(
            success=True,
            message=summary,
            data={
                "cpu_percent": metrics.cpu_percent,
                "ram_percent": metrics.ram_percent,
                "disk_free_gb": metrics.disk_free_gb,
                "battery_percent": metrics.battery_percent
            }
        )
