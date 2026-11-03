"""Unit tests for SOUNDARYA Intent Recognition and Entity Extraction."""

import unittest
from app.ai.intent_engine import intent_engine


class TestIntentEngine(unittest.TestCase):
    def test_app_launch_intent_hindi_hinglish(self) -> None:
        queries = [
            ("Soundarya, Chrome kholo", "chrome"),
            ("Chrome kholo please", "chrome"),
            ("open VS Code", "vs code"),
            ("launch Spotify", "spotify"),
            ("Terminal start karo", "terminal"),
            ("kholo Calculator", "calculator")
        ]
        for q, expected_app in queries:
            parsed = intent_engine.parse(q)
            self.assertEqual(parsed.action_name, "app:open", f"Failed action for: {q}")
            self.assertIn("app_name", parsed.parameters)
            self.assertEqual(parsed.parameters["app_name"].lower(), expected_app)

    def test_folder_open_intent(self) -> None:
        parsed = intent_engine.parse("Soundarya, meri Downloads folder open karo")
        self.assertEqual(parsed.action_name, "folder:open")
        self.assertEqual(parsed.parameters["folder_name"], "downloads")

        parsed2 = intent_engine.parse("open documents folder")
        self.assertEqual(parsed2.action_name, "folder:open")
        self.assertEqual(parsed2.parameters["folder_name"], "documents")

    def test_system_status_intent(self) -> None:
        parsed = intent_engine.parse("Soundarya, system status batao")
        self.assertEqual(parsed.action_name, "system:status")

        parsed2 = intent_engine.parse("battery kitni hai")
        self.assertEqual(parsed2.action_name, "system:status")

    def test_personal_notes_search_intent(self) -> None:
        parsed = intent_engine.parse("Soundarya, meri personal notes mein AI project search karo")
        self.assertEqual(parsed.action_name, "memory:search")
        self.assertIn("ai project", parsed.parameters["query"].lower())

    def test_personal_notes_add_intent(self) -> None:
        parsed = intent_engine.parse("Soundarya, remember that my car number is DL-01-AB-1234")
        self.assertEqual(parsed.action_name, "memory:add")
        self.assertIn("car number", parsed.parameters["content"])

    def test_schedule_list_intent(self) -> None:
        parsed = intent_engine.parse("Soundarya, aaj ka schedule batao")
        self.assertEqual(parsed.action_name, "task:list")

    def test_file_search_intent(self) -> None:
        parsed = intent_engine.parse("search files named report")
        self.assertEqual(parsed.action_name, "file:search")
        self.assertEqual(parsed.parameters["query"], "report")


if __name__ == "__main__":
    unittest.main()
