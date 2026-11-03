"""Task and schedule management plugin for SOUNDARYA."""

from __future__ import annotations
from typing import Dict, Any
from app.core.state import PermissionLevel, ExecutionResult
from app.plugins.base_plugin import BasePlugin
from app.database.repositories import TaskRepository


class TaskListPlugin(BasePlugin):
    @property
    def name(self) -> str:
        return "task:list"

    @property
    def description(self) -> str:
        return "Retrieves today's schedule and pending tasks."

    @property
    def required_permission(self) -> PermissionLevel:
        return PermissionLevel.LEVEL_1

    def execute(self, params: Dict[str, Any]) -> ExecutionResult:
        repo = TaskRepository()
        tasks = repo.list_tasks(status="pending")
        if tasks:
            task_titles = [f"• {t['title']}" for t in tasks[:5]]
            msg = "Aapka schedule aur pending tasks ye hain:\n" + "\n".join(task_titles)
        else:
            msg = "Aapke paas filhaal koi pending task nahi hai. Schedule bilkul clear hai."

        return ExecutionResult(success=True, message=msg, data={"tasks": tasks})


class TaskAddPlugin(BasePlugin):
    @property
    def name(self) -> str:
        return "task:add"

    @property
    def description(self) -> str:
        return "Adds a new task or reminder."

    @property
    def required_permission(self) -> PermissionLevel:
        return PermissionLevel.LEVEL_1

    def execute(self, params: Dict[str, Any]) -> ExecutionResult:
        title = params.get("title", "").strip()
        if not title:
            return ExecutionResult(success=False, message="Task title cannot be empty.")
        
        repo = TaskRepository()
        task_id = repo.add_task(title=title)
        return ExecutionResult(
            success=True,
            message=f"Task '{title}' schedule mein add kar diya gaya hai.",
            data={"task_id": task_id}
        )
