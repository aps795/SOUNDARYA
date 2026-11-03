"""Central Operational Orchestrator for SOUNDARYA Assistant."""

from __future__ import annotations
import uuid
import logging
from typing import Callable, Dict, Any, Optional
from app.core.state import AssistantState, ActionRequest, ExecutionResult, PermissionLevel
from app.core.security import security_engine
from app.ai.intent_engine import intent_engine, ParsedIntent
from app.voice.tts import tts_engine
from app.plugins import plugin_registry
from app.database.repositories import ConversationRepository
from app.system.app_launcher import app_launcher

logger = logging.getLogger("Soundarya.Core")


class SoundaryaEngine:
    """The central brain linking UI, AI reasoning, voice, database, and system automation."""

    def __init__(self) -> None:
        self.state = AssistantState.IDLE
        self.session_id = str(uuid.uuid4())[:8]
        self.conv_repo = ConversationRepository()
        self.state_listeners: list[Callable[[AssistantState], None]] = []
        self.response_listeners: list[Callable[[str, str], None]] = []

        # Auto scan apps on startup
        try:
            app_launcher.scan_installed_applications()
        except Exception as e:
            logger.warning(f"Initial application scan error: {e}")

    def add_state_listener(self, listener: Callable[[AssistantState], None]) -> None:
        self.state_listeners.append(listener)

    def add_response_listener(self, listener: Callable[[str, str], None]) -> None:
        self.response_listeners.append(listener)

    def set_state(self, new_state: AssistantState) -> None:
        self.state = new_state
        logger.info(f"Assistant state transition: [{new_state.value.upper()}]")
        for listener in self.state_listeners:
            try:
                listener(new_state)
            except Exception as e:
                logger.error(f"Error in state listener: {e}")

    def process_command(self, user_text: str, speak_output: bool = True) -> str:
        """Process natural language command from text chat or transcribed voice."""
        if not user_text.strip():
            return ""

        self.set_state(AssistantState.PROCESSING)

        # 1. Parse Intent & Extract Entities
        parsed: ParsedIntent = intent_engine.parse(user_text)
        logger.info(f"Parsed intent: category={parsed.intent_category}, action={parsed.action_name}")

        # 2. Check if it's a registered operating system action
        plugin = plugin_registry.get(parsed.action_name)
        reply_text = ""

        if plugin:
            # 3. Security & Permission Validation
            action_req = ActionRequest(
                action_id=str(uuid.uuid4())[:8],
                action_name=plugin.name,
                category=parsed.intent_category,
                parameters=parsed.parameters,
                permission_level=plugin.required_permission
            )

            is_authorized, reason = security_engine.validate_and_authorize(action_req)
            if not is_authorized:
                reply_text = reason or "Access denied by security policy."
                self.set_state(AssistantState.ERROR)
            else:
                self.set_state(AssistantState.EXECUTING)
                try:
                    result: ExecutionResult = plugin.execute(parsed.parameters)
                    reply_text = result.message
                except Exception as e:
                    logger.error(f"Execution error in plugin '{plugin.name}': {e}", exc_info=True)
                    reply_text = f"An error occurred while executing {plugin.name}: {e}"
                    self.set_state(AssistantState.ERROR)
        else:
            # 4. Conversational reasoning through AI Provider
            try:
                active_ai = intent_engine.get_active_provider()
                reply_text = active_ai.generate_response(prompt=parsed.cleaned_query)
            except Exception as e:
                logger.error(f"AI response generation error: {e}")
                reply_text = f"Maaf kijiye, mujhe response generate karne mein samasya aayi: {e}"

        # 5. Persist to Conversation History
        try:
            self.conv_repo.log_message(
                session_id=self.session_id,
                role="user",
                content=user_text,
                intent=parsed.action_name
            )
            self.conv_repo.log_message(
                session_id=self.session_id,
                role="assistant",
                content=reply_text,
                intent=parsed.action_name,
                tool_used=plugin.name if plugin else "ai_chat"
            )
        except Exception as e:
            logger.error(f"Failed to log conversation message: {e}")

        # 6. Notify UI response listeners
        for listener in self.response_listeners:
            try:
                listener(user_text, reply_text)
            except Exception as e:
                logger.error(f"Error in response listener: {e}")

        # 7. Voice output (if enabled)
        if speak_output:
            self.set_state(AssistantState.SPEAKING)
            tts_engine.speak(reply_text, non_blocking=True)

        self.set_state(AssistantState.IDLE)
        return reply_text


# Global engine instance
core_engine = SoundaryaEngine()
