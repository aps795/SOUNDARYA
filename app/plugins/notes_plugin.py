"""Personal Notes and Memory management plugin for SOUNDARYA."""

from __future__ import annotations
from typing import Dict, Any
from app.core.state import PermissionLevel, ExecutionResult
from app.plugins.base_plugin import BasePlugin
from app.memory.memory_manager import memory_manager


class MemorySearchPlugin(BasePlugin):
    @property
    def name(self) -> str:
        return "memory:search"

    @property
    def description(self) -> str:
        return "Searches private personal notes and facts database."

    @property
    def required_permission(self) -> PermissionLevel:
        return PermissionLevel.LEVEL_1

    def execute(self, params: Dict[str, Any]) -> ExecutionResult:
        query = params.get("query", "").strip()
        if not query:
            return ExecutionResult(success=False, message="Please specify what to search for in notes.")

        results = memory_manager.search(query)
        structured = results.get("structured_memories", [])
        docs = results.get("document_passages", [])

        if structured:
            first = structured[0]
            msg = f"Aapke personal notes mein mila: '{first['title']}' — {first['content']}"
        elif docs:
            first_doc = docs[0]
            msg = f"Document '{first_doc['filename']}' mein mila: {first_doc['content'][:150]}..."
        else:
            msg = f"Notes mein '{query}' se related koi record nahi mila."

        return ExecutionResult(success=True, message=msg, data=results)


class MemoryAddPlugin(BasePlugin):
    @property
    def name(self) -> str:
        return "memory:add"

    @property
    def description(self) -> str:
        return "Saves an approved fact or note to personal memory."

    @property
    def required_permission(self) -> PermissionLevel:
        return PermissionLevel.LEVEL_1

    def execute(self, params: Dict[str, Any]) -> ExecutionResult:
        content = params.get("content", "").strip()
        category = params.get("category", "note")
        title = params.get("title", content[:30])

        if not content:
            return ExecutionResult(success=False, message="Memory content cannot be empty.")

        mem_id = memory_manager.remember_fact(content=content, category=category, title=title)
        return ExecutionResult(
            success=True,
            message="Ye information maine aapki personal memory mein save kar li hai.",
            data={"memory_id": mem_id}
        )
