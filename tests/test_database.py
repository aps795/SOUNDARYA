"""Unit tests for SOUNDARYA Personal Database & Repositories."""

import unittest
import tempfile
import shutil
from pathlib import Path
from app.database.db_engine import DatabaseEngine
from app.database.repositories import (
    UserProfileRepository, PersonalMemoryRepository,
    AppRegistryRepository, ConversationRepository, TaskRepository
)


class TestDatabaseRepositories(unittest.TestCase):
    def setUp(self) -> None:
        self.test_dir = tempfile.mkdtemp()
        self.db_file = Path(self.test_dir) / "test_soundarya.db"
        self.engine = DatabaseEngine(self.db_file)

    def tearDown(self) -> None:
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_user_profile(self) -> None:
        repo = UserProfileRepository(self.engine)
        profile = repo.get_profile()
        self.assertEqual(profile["preferred_name"], "Commander")
        self.assertEqual(profile["preferred_language"], "Hinglish")

        repo.update_profile(name="Tony Stark", language="English", voice_rate=180)
        updated = repo.get_profile()
        self.assertEqual(updated["preferred_name"], "Tony Stark")
        self.assertEqual(updated["preferred_language"], "English")

    def test_personal_memory_crud(self) -> None:
        repo = PersonalMemoryRepository(self.engine)
        mem_id = repo.add_memory(
            category="fact",
            title="Iron Man Armor",
            content="Mark 85 incorporates nanotechnology and vibranium shielding.",
            tags="avengers,ironman,tech",
            importance=5
        )
        self.assertGreater(mem_id, 0)

        results = repo.search_memories("nanotechnology")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "Iron Man Armor")

        tag_results = repo.search_memories("avengers")
        self.assertEqual(len(tag_results), 1)

        deleted = repo.delete_memory(mem_id)
        self.assertTrue(deleted)
        self.assertEqual(len(repo.search_memories("nanotechnology")), 0)

    def test_app_registry(self) -> None:
        repo = AppRegistryRepository(self.engine)
        repo.register_app(
            name="Visual Studio Code",
            executable_path="/Applications/Visual Studio Code.app",
            aliases=["vscode", "code", "editor"],
            category="development"
        )

        found = repo.find_app("vscode")
        self.assertIsNotNone(found)
        self.assertEqual(found["name"], "Visual Studio Code")

        repo.record_launch(found["id"])
        apps = repo.list_apps()
        self.assertEqual(apps[0]["launch_count"], 1)

    def test_conversation_logging(self) -> None:
        repo = ConversationRepository(self.engine)
        repo.log_message(
            session_id="session-1",
            role="user",
            content="Soundarya, Chrome kholo",
            intent="app:open"
        )
        repo.log_message(
            session_id="session-1",
            role="assistant",
            content="Chrome open kar diya hai.",
            intent="app:open",
            tool_used="app:open"
        )

        history = repo.get_recent("session-1")
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["content"], "Soundarya, Chrome kholo")
        self.assertEqual(history[1]["content"], "Chrome open kar diya hai.")

    def test_task_reminders(self) -> None:
        repo = TaskRepository(self.engine)
        task_id = repo.add_task(title="Deploy Soundarya v1.0", priority="high")
        self.assertGreater(task_id, 0)

        pending = repo.list_tasks(status="pending")
        self.assertEqual(len(pending), 1)
        self.assertEqual(pending[0]["title"], "Deploy Soundarya v1.0")

        repo.complete_task(task_id)
        self.assertEqual(len(repo.list_tasks(status="pending")), 0)
        self.assertEqual(len(repo.list_tasks(status="completed")), 1)


if __name__ == "__main__":
    unittest.main()
