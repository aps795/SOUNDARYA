"""File manager and directory navigation plugin for SOUNDARYA."""

from __future__ import annotations
from typing import Dict, Any
from app.core.state import PermissionLevel, ExecutionResult
from app.plugins.base_plugin import BasePlugin
from app.system.os_bridge import os_bridge
from app.system.file_manager import file_manager


class FolderOpenPlugin(BasePlugin):
    @property
    def name(self) -> str:
        return "folder:open"

    @property
    def description(self) -> str:
        return "Opens standard user folders (Downloads, Documents, Desktop, Pictures)."

    @property
    def required_permission(self) -> PermissionLevel:
        return PermissionLevel.LEVEL_1

    def execute(self, params: Dict[str, Any]) -> ExecutionResult:
        folder = params.get("folder_name", "downloads").strip()
        success = os_bridge.open_folder(folder)
        msg = f"{folder.capitalize()} folder open kar diya hai." if success else f"Could not find or open '{folder}'."
        return ExecutionResult(success=success, message=msg, data={"folder": folder})


class FileSearchPlugin(BasePlugin):
    @property
    def name(self) -> str:
        return "file:search"

    @property
    def description(self) -> str:
        return "Searches local user files by name or extension."

    @property
    def required_permission(self) -> PermissionLevel:
        return PermissionLevel.LEVEL_1

    def execute(self, params: Dict[str, Any]) -> ExecutionResult:
        query = params.get("query", "").strip()
        if not query:
            return ExecutionResult(success=False, message="Please specify a search term.")
        
        matches = file_manager.search_files(query, max_results=5)
        if matches:
            file_names = ", ".join([m["name"] for m in matches[:3]])
            msg = f"Found {len(matches)} matching files: {file_names}."
        else:
            msg = f"No files matching '{query}' were found in user directories."

        return ExecutionResult(success=True, message=msg, data={"matches": matches})
