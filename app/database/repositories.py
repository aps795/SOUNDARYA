"""Data access repositories for SOUNDARYA Personal Database."""

from __future__ import annotations
import json
import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional
from app.database.db_engine import DatabaseEngine, db_engine


class UserProfileRepository:
    def __init__(self, engine: DatabaseEngine = db_engine) -> None:
        self.engine = engine

    def get_profile(self) -> Dict[str, Any]:
        with self.engine.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user_profiles ORDER BY id ASC LIMIT 1")
            row = cursor.fetchone()
            if row:
                return dict(row)
            # Create default profile
            cursor.execute(
                "INSERT INTO user_profiles (preferred_name, preferred_language) VALUES (?, ?)",
                ("Commander", "Hinglish")
            )
            conn.commit()
            return {
                "id": cursor.lastrowid,
                "preferred_name": "Commander",
                "preferred_language": "Hinglish",
                "voice_gender": "female",
                "voice_rate": 175
            }

    def update_profile(self, name: str, language: str, voice_rate: int = 175) -> None:
        profile = self.get_profile()
        with self.engine.get_connection() as conn:
            conn.execute(
                """
                UPDATE user_profiles
                SET preferred_name = ?, preferred_language = ?, voice_rate = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (name, language, voice_rate, profile["id"])
            )
            conn.commit()


class PersonalMemoryRepository:
    def __init__(self, engine: DatabaseEngine = db_engine) -> None:
        self.engine = engine

    def add_memory(self, category: str, title: str, content: str, tags: str = "", importance: int = 3) -> int:
        with self.engine.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO personal_memories (category, title, content, tags, importance)
                VALUES (?, ?, ?, ?, ?)
                """,
                (category, title, content, tags, importance)
            )
            conn.commit()
            return cursor.lastrowid or 0

    def search_memories(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        search_pattern = f"%{query}%"
        with self.engine.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM personal_memories
                WHERE title LIKE ? OR content LIKE ? OR tags LIKE ?
                ORDER BY importance DESC, updated_at DESC
                LIMIT ?
                """,
                (search_pattern, search_pattern, search_pattern, limit)
            )
            return [dict(row) for row in cursor.fetchall()]

    def list_memories(self, category: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        with self.engine.get_connection() as conn:
            cursor = conn.cursor()
            if category:
                cursor.execute(
                    "SELECT * FROM personal_memories WHERE category = ? ORDER BY updated_at DESC LIMIT ?",
                    (category, limit)
                )
            else:
                cursor.execute(
                    "SELECT * FROM personal_memories ORDER BY updated_at DESC LIMIT ?",
                    (limit,)
                )
            return [dict(row) for row in cursor.fetchall()]

    def delete_memory(self, memory_id: int) -> bool:
        with self.engine.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM personal_memories WHERE id = ?", (memory_id,))
            conn.commit()
            return cursor.rowcount > 0

    def clear_all(self) -> int:
        with self.engine.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM personal_memories")
            conn.commit()
            return cursor.rowcount


class AppRegistryRepository:
    def __init__(self, engine: DatabaseEngine = db_engine) -> None:
        self.engine = engine

    def register_app(self, name: str, executable_path: str, aliases: List[str], category: str = "general") -> None:
        aliases_json = json.dumps([a.lower().strip() for a in aliases])
        with self.engine.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO app_registry (name, executable_path, aliases, category)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(name) DO UPDATE SET
                    executable_path = excluded.executable_path,
                    aliases = excluded.aliases,
                    category = excluded.category
                """,
                (name, executable_path, aliases_json, category)
            )
            conn.commit()

    def find_app(self, search_term: str) -> Optional[Dict[str, Any]]:
        term = search_term.lower().strip()
        with self.engine.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM app_registry")
            rows = [dict(r) for r in cursor.fetchall()]

        # Exact name match
        for r in rows:
            if r["name"].lower() == term:
                return r

        # Alias match
        for r in rows:
            try:
                aliases = json.loads(r["aliases"])
            except Exception:
                aliases = []
            if term in [a.lower() for a in aliases]:
                return r

        # Substring in name or alias
        for r in rows:
            if term in r["name"].lower():
                return r
            try:
                aliases = json.loads(r["aliases"])
                if any(term in a.lower() for a in aliases):
                    return r
            except Exception:
                pass

        return None

    def list_apps(self) -> List[Dict[str, Any]]:
        with self.engine.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM app_registry ORDER BY launch_count DESC, name ASC")
            return [dict(row) for row in cursor.fetchall()]

    def record_launch(self, app_id: int) -> None:
        with self.engine.get_connection() as conn:
            conn.execute(
                """
                UPDATE app_registry
                SET launch_count = launch_count + 1,
                    last_launched_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (app_id,)
            )
            conn.commit()


class ConversationRepository:
    def __init__(self, engine: DatabaseEngine = db_engine) -> None:
        self.engine = engine

    def log_message(self, session_id: str, role: str, content: str, intent: str = "", tool_used: str = "") -> int:
        with self.engine.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO conversation_messages (session_id, role, content, intent, tool_used)
                VALUES (?, ?, ?, ?, ?)
                """,
                (session_id, role, content, intent, tool_used)
            )
            conn.commit()
            return cursor.lastrowid or 0

    def get_recent(self, session_id: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        with self.engine.get_connection() as conn:
            cursor = conn.cursor()
            if session_id:
                cursor.execute(
                    "SELECT * FROM conversation_messages WHERE session_id = ? ORDER BY id DESC LIMIT ?",
                    (session_id, limit)
                )
            else:
                cursor.execute(
                    "SELECT * FROM conversation_messages ORDER BY id DESC LIMIT ?",
                    (limit,)
                )
            rows = cursor.fetchall()
            # Return in chronological order
            return [dict(r) for r in reversed(rows)]


class TaskRepository:
    def __init__(self, engine: DatabaseEngine = db_engine) -> None:
        self.engine = engine

    def add_task(self, title: str, description: str = "", priority: str = "medium", due_date: Optional[str] = None) -> int:
        with self.engine.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO task_reminders (title, description, priority, due_date)
                VALUES (?, ?, ?, ?)
                """,
                (title, description, priority, due_date)
            )
            conn.commit()
            return cursor.lastrowid or 0

    def list_tasks(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        with self.engine.get_connection() as conn:
            cursor = conn.cursor()
            if status:
                cursor.execute(
                    "SELECT * FROM task_reminders WHERE status = ? ORDER BY id DESC",
                    (status,)
                )
            else:
                cursor.execute("SELECT * FROM task_reminders ORDER BY id DESC")
            return [dict(row) for row in cursor.fetchall()]

    def complete_task(self, task_id: int) -> bool:
        with self.engine.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE task_reminders
                SET status = 'completed', completed_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (task_id,)
            )
            conn.commit()
            return cursor.rowcount > 0
