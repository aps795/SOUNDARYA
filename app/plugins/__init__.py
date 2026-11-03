"""Plugin registry and dispatcher for SOUNDARYA."""

from __future__ import annotations
from typing import Dict, List, Optional
from app.plugins.base_plugin import BasePlugin
from app.plugins.app_launcher_plugin import AppLauncherPlugin
from app.plugins.file_manager_plugin import FolderOpenPlugin, FileSearchPlugin
from app.plugins.system_monitor_plugin import SystemMonitorPlugin
from app.plugins.notes_plugin import MemorySearchPlugin, MemoryAddPlugin
from app.plugins.tasks_plugin import TaskListPlugin, TaskAddPlugin
from app.plugins.rag_knowledge_plugin import KnowledgeSearchPlugin


class PluginRegistry:
    """Central catalog of extensible capability plugins."""

    def __init__(self) -> None:
        self._plugins: Dict[str, BasePlugin] = {}
        self._register_defaults()

    def register(self, plugin: BasePlugin) -> None:
        self._plugins[plugin.name] = plugin

    def get(self, action_name: str) -> Optional[BasePlugin]:
        return self._plugins.get(action_name)

    def list_all(self) -> List[BasePlugin]:
        return list(self._plugins.values())

    def _register_defaults(self) -> None:
        plugins = [
            AppLauncherPlugin(),
            FolderOpenPlugin(),
            FileSearchPlugin(),
            SystemMonitorPlugin(),
            MemorySearchPlugin(),
            MemoryAddPlugin(),
            TaskListPlugin(),
            TaskAddPlugin(),
            KnowledgeSearchPlugin(),
        ]
        for p in plugins:
            self.register(p)


# Global instance
plugin_registry = PluginRegistry()
