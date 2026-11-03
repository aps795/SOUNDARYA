"""Multi-lingual Intent Recognition and Entity Extraction Engine (English, Hindi, Hinglish)."""

from __future__ import annotations
import re
import logging
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from app.core.config import config
from app.ai.provider_base import BaseAIProvider
from app.ai.openai_provider import OpenAIProvider
from app.ai.ollama_provider import OllamaProvider
from app.ai.rule_fallback_provider import RuleFallbackProvider

logger = logging.getLogger("Soundarya.AI.Intent")


@dataclass
class ParsedIntent:
    """Classified intent with action target and extracted entities."""
    raw_query: str
    cleaned_query: str
    intent_category: str # 'app', 'folder', 'system', 'memory', 'task', 'file', 'chat'
    action_name: str # e.g. 'app:open', 'folder:open', 'system:status', 'memory:search', etc.
    parameters: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0


class IntentEngine:
    """Parses user input into structured computer operating actions and conversational responses."""

    def __init__(self) -> None:
        self.fallback_provider = RuleFallbackProvider()
        self.openai_provider = OpenAIProvider()
        self.ollama_provider = OllamaProvider()

    def get_active_provider(self) -> BaseAIProvider:
        """Select best available AI provider based on configuration and connectivity."""
        pref = config.ai_provider.lower()
        if pref == "openai" and self.openai_provider.is_available():
            return self.openai_provider
        if pref == "ollama" and self.ollama_provider.is_available():
            return self.ollama_provider
        return self.fallback_provider

    def strip_wake_word(self, text: str) -> str:
        """Clean leading/trailing wake words and polite prefixes."""
        patterns = [
            r"^(hey|suno|arre|hello|namaste)?\s*soundarya[,:\s]*",
            r"[,:\s]*soundarya\s*$"
        ]
        cleaned = text.strip()
        for pat in patterns:
            cleaned = re.sub(pat, "", cleaned, flags=re.IGNORECASE).strip()
        return cleaned

    def clean_filler_words(self, text: str) -> str:
        """Remove extraneous politeness and filler words."""
        cleaned = re.sub(r"\b(please|plz|zara|turant|bhi|kripya)\b", "", text, flags=re.IGNORECASE)
        return re.sub(r"\s+", " ", cleaned).strip()

    def parse(self, text: str) -> ParsedIntent:
        """Analyze user query and return parsed intent with extracted parameters."""
        cleaned = self.strip_wake_word(text)
        cleaned_no_filler = self.clean_filler_words(cleaned)
        lower = cleaned_no_filler.lower()

        # 1. Folder Opening Intent (checked before generic app launch)
        # Examples: "meri Downloads folder open karo", "open documents folder", "desktop kholo"
        folder_match = re.search(r"\b(downloads|documents|desktop|pictures|music)\b(?:\s*folder)?", lower)
        if folder_match and any(w in lower for w in ("open", "kholo", "chalao", "dikhao", "browse")):
            folder_name = folder_match.group(1).strip()
            return ParsedIntent(
                raw_query=text,
                cleaned_query=cleaned,
                intent_category="folder",
                action_name="folder:open",
                parameters={"folder_name": folder_name},
                confidence=0.98
            )

        # 2. System Status Telemetry
        # Examples: "system status batao", "battery kitni hai", "cpu usage check karo"
        if any(w in lower for w in [
            "system status", "telemetry", "hardware status", "cpu usage",
            "ram usage", "battery kitni", "battery status", "system info"
        ]):
            return ParsedIntent(
                raw_query=text,
                cleaned_query=cleaned,
                intent_category="system",
                action_name="system:status",
                parameters={},
                confidence=0.99
            )

        # 3. Personal Memory / Notes Search
        # Examples: "meri personal notes mein AI project search karo", "search notes for meeting"
        mem_search = re.search(
            r"(?:meri\s+)?(?:personal\s+)?(?:notes|memory|memories|yaadon)\s*(?:mein|for)?\s*(.+?)\s*(?:search karo|dhoondo|find|batao)",
            lower
        ) or re.search(
            r"(?:search|find)\s+(?:in\s+)?(?:notes|memory)\s+(?:for\s+)?(.+)",
            lower
        )
        if mem_search:
            search_query = mem_search.group(1).strip()
            search_query = re.sub(r"^(mein|for|about)\s+", "", search_query).strip()
            return ParsedIntent(
                raw_query=text,
                cleaned_query=cleaned,
                intent_category="memory",
                action_name="memory:search",
                parameters={"query": search_query},
                confidence=0.95
            )

        # 4. Personal Memory / Note Add
        # Examples: "remember that my passport expires next year", "note down that meeting at 4pm", "yaad rakhna ki..."
        mem_add = re.search(
            r"(?:remember\s+(?:that)?|note\s+down\s+(?:that)?|yaad\s+rakhna\s+(?:ki)?|save\s+note)\s+(.+)",
            lower
        )
        if mem_add:
            content = mem_add.group(1).strip()
            return ParsedIntent(
                raw_query=text,
                cleaned_query=cleaned,
                intent_category="memory",
                action_name="memory:add",
                parameters={"content": content, "category": "note", "title": content[:40]},
                confidence=0.95
            )

        # 5. Schedule & Tasks List
        # Examples: "aaj ka schedule batao", "show today's schedule", "pending tasks dikhao"
        if any(w in lower for w in [
            "aaj ka schedule", "today's schedule", "schedule batao", "show tasks",
            "mera schedule", "pending tasks", "tasks dikhao", "to-do list"
        ]):
            return ParsedIntent(
                raw_query=text,
                cleaned_query=cleaned,
                intent_category="task",
                action_name="task:list",
                parameters={"filter": "pending"},
                confidence=0.95
            )

        # 6. Add Task
        # Examples: "add task buy groceries", "schedule reminder pay electricity bill"
        task_add = re.search(r"(?:add\s+task|schedule\s+reminder|task\s+add\s+karo)\s+(.+)", lower)
        if task_add:
            task_title = task_add.group(1).strip()
            return ParsedIntent(
                raw_query=text,
                cleaned_query=cleaned,
                intent_category="task",
                action_name="task:add",
                parameters={"title": task_title, "priority": "medium"},
                confidence=0.95
            )

        # 7. File Search
        # Examples: "search files named report", "find file project.pdf", "file dhoondo invoice"
        file_search = re.search(r"(?:search\s+files?\s+(?:named)?|find\s+file|file\s+dhoondo)\s+(.+)", lower)
        if file_search:
            file_query = file_search.group(1).strip()
            return ParsedIntent(
                raw_query=text,
                cleaned_query=cleaned,
                intent_category="file",
                action_name="file:search",
                parameters={"query": file_query},
                confidence=0.95
            )

        # 8. Screenshot
        if any(w in lower for w in ["screenshot", "screen capture", "screen snapshot"]):
            return ParsedIntent(
                raw_query=text,
                cleaned_query=cleaned,
                intent_category="system",
                action_name="system:screenshot",
                parameters={},
                confidence=0.99
            )

        # 9. Application Launch Intent
        # Examples: "Chrome kholo", "open VS Code", "launch Spotify", "Terminal start karo", "kholo Calculator"
        app_match = None
        # Pattern A: <verb> <app> (e.g., "open VS Code", "kholo Calculator")
        match_a = re.match(r"^(?:open|launch|start|kholo|chalao)\s+([a-zA-Z0-9_\-\s]+?)(?:\s+(?:app|application|karo))?$", lower)
        if match_a:
            app_match = match_a.group(1).strip()

        # Pattern B: <app> <verb> (e.g., "Chrome kholo", "Spotify open karo")
        if not app_match:
            match_b = re.match(r"^([a-zA-Z0-9_\-\s]+?)\s+(?:kholo|chalao|open karo|start karo|open)$", lower)
            if match_b:
                app_match = match_b.group(1).strip()

        if app_match:
            app_candidate = re.sub(r"^(the|an|a|application|app)\s+", "", app_match).strip()
            if app_candidate:
                return ParsedIntent(
                    raw_query=text,
                    cleaned_query=cleaned,
                    intent_category="app",
                    action_name="app:open",
                    parameters={"app_name": app_candidate},
                    confidence=0.95
                )

        # 10. Default General Conversation / Chat
        return ParsedIntent(
            raw_query=text,
            cleaned_query=cleaned,
            intent_category="chat",
            action_name="chat:respond",
            parameters={"query": cleaned},
            confidence=0.8
        )


# Global instance
intent_engine = IntentEngine()
