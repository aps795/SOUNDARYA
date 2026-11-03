"""Database engine and schema manager for SOUNDARYA Personal Database."""

from __future__ import annotations
import sqlite3
import logging
from pathlib import Path
from typing import Optional
from app.core.config import config

logger = logging.getLogger("Soundarya.Database")

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS user_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    preferred_name TEXT DEFAULT 'User',
    preferred_language TEXT DEFAULT 'Hinglish',
    voice_gender TEXT DEFAULT 'female',
    voice_rate INTEGER DEFAULT 175,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS personal_memories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    tags TEXT DEFAULT '',
    importance INTEGER DEFAULT 3,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS conversation_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    intent TEXT DEFAULT '',
    tool_used TEXT DEFAULT '',
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS app_registry (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    aliases TEXT DEFAULT '[]',
    executable_path TEXT NOT NULL,
    category TEXT DEFAULT 'general',
    launch_count INTEGER DEFAULT 0,
    last_launched_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS task_reminders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT DEFAULT '',
    priority TEXT DEFAULT 'medium',
    status TEXT DEFAULT 'pending',
    due_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);
"""


class DatabaseEngine:
    """Manages SQLite storage, table initialization, and connection pooling."""

    def __init__(self, db_path: Optional[Path] = None) -> None:
        self.db_path = db_path or config.db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def get_connection(self) -> sqlite3.Connection:
        """Provide a configured sqlite3 connection with dictionary row factory."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        """Ensure all required tables and indexes exist."""
        try:
            with self.get_connection() as conn:
                conn.executescript(SCHEMA_SQL)
                conn.commit()
            logger.info(f"Database initialized at: {self.db_path}")
        except Exception as e:
            logger.error(f"Failed to initialize database schema: {e}", exc_info=True)
            raise


# Global singleton instance
db_engine = DatabaseEngine()
