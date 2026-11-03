"""Database models and schema definitions for SOUNDARYA Personal Database."""

from __future__ import annotations
import json
from datetime import datetime
from typing import Any, List, Optional

try:
    from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float
    from sqlalchemy.orm import declarative_base
    Base = declarative_base()
    HAS_SQLALCHEMY = True
except ImportError:
    # Minimal stub if SQLAlchemy is pending installation
    Base = object  # type: ignore
    HAS_SQLALCHEMY = False


if HAS_SQLALCHEMY:
    class UserProfileModel(Base):
        __tablename__ = "user_profiles"

        id = Column(Integer, primary_key=True, autoincrement=True)
        preferred_name = Column(String(100), default="User")
        preferred_language = Column(String(50), default="Hinglish")
        voice_gender = Column(String(20), default="female")
        voice_rate = Column(Integer, default=175)
        created_at = Column(DateTime, default=datetime.utcnow)
        updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    class PersonalMemoryModel(Base):
        __tablename__ = "personal_memories"

        id = Column(Integer, primary_key=True, autoincrement=True)
        category = Column(String(50), nullable=False) # fact, note, goal, instruction
        title = Column(String(200), nullable=False)
        content = Column(Text, nullable=False)
        tags = Column(String(255), default="")
        importance = Column(Integer, default=3) # 1 to 5
        created_at = Column(DateTime, default=datetime.utcnow)
        updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    class ConversationMessageModel(Base):
        __tablename__ = "conversation_messages"

        id = Column(Integer, primary_key=True, autoincrement=True)
        session_id = Column(String(64), nullable=False)
        role = Column(String(20), nullable=False) # user, assistant, system
        content = Column(Text, nullable=False)
        intent = Column(String(100), default="")
        tool_used = Column(String(100), default="")
        timestamp = Column(DateTime, default=datetime.utcnow)

    class AppRegistryModel(Base):
        __tablename__ = "app_registry"

        id = Column(Integer, primary_key=True, autoincrement=True)
        name = Column(String(150), unique=True, nullable=False)
        aliases = Column(Text, default="[]") # JSON list of string aliases
        executable_path = Column(Text, nullable=False)
        category = Column(String(50), default="general")
        launch_count = Column(Integer, default=0)
        last_launched_at = Column(DateTime, nullable=True)

        def get_aliases(self) -> List[str]:
            try:
                return json.loads(self.aliases)
            except Exception:
                return [a.strip() for a in self.aliases.split(",") if a.strip()]

        def set_aliases(self, alias_list: List[str]) -> None:
            self.aliases = json.dumps(alias_list)

    class TaskReminderModel(Base):
        __tablename__ = "task_reminders"

        id = Column(Integer, primary_key=True, autoincrement=True)
        title = Column(String(250), nullable=False)
        description = Column(Text, default="")
        priority = Column(String(20), default="medium") # low, medium, high
        status = Column(String(20), default="pending") # pending, completed
        due_date = Column(DateTime, nullable=True)
        created_at = Column(DateTime, default=datetime.utcnow)
        completed_at = Column(DateTime, nullable=True)
