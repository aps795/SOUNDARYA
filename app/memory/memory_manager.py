"""High-level Personal Memory and Privacy Lifecycle Manager for SOUNDARYA."""

from __future__ import annotations
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.database.repositories import PersonalMemoryRepository, UserProfileRepository, TaskRepository
from app.memory.vector_store import vector_store

logger = logging.getLogger("Soundarya.Memory.Manager")


class MemoryManager:
    """Manages personal knowledge, goals, facts, and privacy operations."""

    def __init__(self) -> None:
        self.mem_repo = PersonalMemoryRepository()
        self.profile_repo = UserProfileRepository()
        self.task_repo = TaskRepository()
        self.vector_store = vector_store

    def remember_fact(self, content: str, category: str = "fact", title: Optional[str] = None) -> int:
        """Store an authorized personal fact or note in the SQLite database."""
        t = title or content[:35]
        return self.mem_repo.add_memory(
            category=category,
            title=t,
            content=content,
            importance=4
        )

    def search(self, query: str) -> Dict[str, Any]:
        """Search across both structured personal memories and vectorized documents."""
        db_results = self.mem_repo.search_memories(query, limit=5)
        doc_results = self.vector_store.search(query, top_k=3)
        return {
            "structured_memories": db_results,
            "document_passages": doc_results
        }

    def export_all_data(self, export_path: str | Path) -> bool:
        """Export full database content to a clean, user-controlled JSON archive."""
        path = Path(export_path)
        data = {
            "exported_at": datetime.utcnow().isoformat(),
            "profile": self.profile_repo.get_profile(),
            "memories": self.mem_repo.list_memories(limit=1000),
            "tasks": self.task_repo.list_tasks()
        }
        try:
            path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
            return True
        except Exception as e:
            logger.error(f"Export failed: {e}")
            return False

    def clear_all_personal_data(self) -> int:
        """Execute approved privacy wipe of all personal memories."""
        return self.mem_repo.clear_all()


# Global instance
memory_manager = MemoryManager()
