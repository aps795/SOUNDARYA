"""Unit tests for UI data flow and state transitions."""

import unittest
from app.core.state import AssistantState
from app.core.engine import core_engine
from app.ui.components.ai_orb import SoundaryaOrb
from app.ui.components.chat_panel import ChatPanel


class TestUIComponentsDataFlow(unittest.TestCase):
    def test_state_transitions(self) -> None:
        observed_states = []

        def _listener(s: AssistantState) -> None:
            observed_states.append(s)

        core_engine.add_state_listener(_listener)
        core_engine.set_state(AssistantState.LISTENING)
        core_engine.set_state(AssistantState.PROCESSING)
        core_engine.set_state(AssistantState.SPEAKING)
        core_engine.set_state(AssistantState.IDLE)

        self.assertIn(AssistantState.LISTENING, observed_states)
        self.assertIn(AssistantState.PROCESSING, observed_states)
        self.assertIn(AssistantState.SPEAKING, observed_states)
        self.assertIn(AssistantState.IDLE, observed_states)


if __name__ == "__main__":
    unittest.main()
