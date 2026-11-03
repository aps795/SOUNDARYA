"""OpenAI API provider implementation for SOUNDARYA."""

from __future__ import annotations
import json
import logging
import urllib.request
import urllib.error
from typing import List, Dict, Optional
from app.core.config import config
from app.ai.provider_base import BaseAIProvider

logger = logging.getLogger("Soundarya.AI.OpenAI")


class OpenAIProvider(BaseAIProvider):
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None) -> None:
        self.api_key = api_key or config.openai_api_key
        self.model = model or config.openai_model
        self.api_url = "https://api.openai.com/v1/chat/completions"

    def is_available(self) -> bool:
        return bool(self.api_key and len(self.api_key.strip()) > 10)

    def generate_response(self, prompt: str, system_prompt: Optional[str] = None, history: Optional[List[Dict[str, str]]] = None) -> str:
        if not self.is_available():
            raise RuntimeError("OpenAI API key is missing. Set OPENAI_API_KEY in .env.")

        messages: List[Dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        if history:
            messages.extend(history)

        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.3
        }

        data_bytes = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            self.api_url,
            data=data_bytes,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            logger.error(f"OpenAI completion failed: {e}")
            raise
