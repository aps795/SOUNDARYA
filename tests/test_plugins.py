"""Integration tests for SOUNDARYA core engine command processing and plugins."""

import unittest
from app.core.engine import core_engine
from app.memory.memory_manager import memory_manager


class TestCoreEngineAndPlugins(unittest.TestCase):
    def test_command_system_status(self) -> None:
        reply = core_engine.process_command("system status batao", speak_output=False)
        self.assertIn("System status", reply)
        self.assertIn("CPU", reply)

    def test_command_memory_add_and_search(self) -> None:
        add_reply = core_engine.process_command(
            "Soundarya, remember that the secret master password is alpha-99",
            speak_output=False
        )
        self.assertIn("personal memory mein save", add_reply)

        search_reply = core_engine.process_command(
            "Soundarya, meri personal notes mein secret master password search karo",
            speak_output=False
        )
        self.assertIn("alpha-99", search_reply)

    def test_command_task_add_and_list(self) -> None:
        add_reply = core_engine.process_command("add task complete the security audit", speak_output=False)
        self.assertIn("security audit", add_reply)

        list_reply = core_engine.process_command("aaj ka schedule batao", speak_output=False)
        self.assertIn("security audit", list_reply)

    def test_command_fallback_conversation(self) -> None:
        reply = core_engine.process_command("Soundarya, who are you?", speak_output=False)
        self.assertIn("SOUNDARYA", reply)


if __name__ == "__main__":
    unittest.main()
