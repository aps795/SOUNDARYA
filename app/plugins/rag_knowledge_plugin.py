"""Document Knowledge Base and RAG query plugin for SOUNDARYA."""

from __future__ import annotations
from typing import Dict, Any
from app.core.state import PermissionLevel, ExecutionResult
from app.plugins.base_plugin import BasePlugin
from app.memory.vector_store import vector_store


class KnowledgeSearchPlugin(BasePlugin):
    @property
    def name(self) -> str:
        return "rag:search"

    @property
    def description(self) -> str:
        return "Answers questions using retrieved context from imported personal documents."

    @property
    def required_permission(self) -> PermissionLevel:
        return PermissionLevel.LEVEL_1

    def execute(self, params: Dict[str, Any]) -> ExecutionResult:
        query = params.get("query", "").strip()
        if not query:
            return ExecutionResult(success=False, message="Please provide a query for knowledge base search.")

        passages = vector_store.search(query, top_k=2)
        if passages:
            best = passages[0]
            msg = f"Document '{best['filename']}' ke reference se:\n{best['content']}"
            return ExecutionResult(success=True, message=msg, data={"passages": passages})
        else:
            return ExecutionResult(
                success=True,
                message=f"Aapke personal documents mein '{query}' ke bare mein koi context nahi mila.",
                data={"passages": []}
            )
