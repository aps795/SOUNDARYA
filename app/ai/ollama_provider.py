"""Local LLM provider using Ollama REST API for SOUNDARYA."""

from __future__ import annotations
import json
import logging
import urllib.request
import urllib.error
from typing import List, Dict, Optional
from app.core.config import config
from app.ai.provider_base import BaseAIProvider

logger = logging.getLogger("Soundarya.AI.Ollama")


class OllamaProvider(BaseAIProvider):
    def __init__(self, base_url: Optional[str] = None, model: Optional[str] = None) -> None:
        self.base_url = (base_url or config.ollama_base_url).rstrip("/")
        self.model = model or config.ollama_model
        self.endpoint = f"{self.base_url}/api/chat"

    def is_available(self) -> bool:
        try:
            req = urllib.request.Request(f"{self.base_url}/api/tags")
            with urllib.request.urlopen(req, timeout=2) as resp:
                return resp.status == 200
        except Exception:
            return False

    def generate_response(self, prompt: str, system_prompt: Optional[str] = None, history: Optional[List[Dict[str, str]]] = None) -> str:
        messages: List[Dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False
        }
        data_bytes = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            self.endpoint,
            data=data_bytes,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=45) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["message"]["content"].strip()
        except Exception as e:
            logger.error(f"Ollama request error: {e}")
            raise
