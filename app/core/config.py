"""Configuration manager for SOUNDARYA Assistant."""

from __future__ import annotations
import os
import json
from pathlib import Path
from typing import Any, Dict

# Base project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def _parse_simple_yaml(text: str) -> Dict[str, Any]:
    """Fallback simple YAML parser for basic nested key-value structures if PyYAML is unavailable."""
    result: Dict[str, Any] = {}
    current_section: str | None = None
    
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.endswith(":") and not ":" in line[:-1]:
            current_section = line[:-1].strip()
            result[current_section] = {}
        elif ":" in line:
            key, val = line.split(":", 1)
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            if val.lower() == "true":
                typed_val: Any = True
            elif val.lower() == "false":
                typed_val = False
            else:
                try:
                    typed_val = int(val) if val.isdigit() else float(val)
                except ValueError:
                    typed_val = val
            
            if current_section and isinstance(result.get(current_section), dict):
                result[current_section][key] = typed_val
            else:
                result[key] = typed_val
    return result


def load_yaml(file_path: Path) -> Dict[str, Any]:
    """Load YAML file using PyYAML or graceful fallback parser."""
    if not file_path.exists():
        return {}
    content = file_path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore
        return yaml.safe_load(content) or {}
    except ImportError:
        return _parse_simple_yaml(content)


def load_env(env_path: Path) -> None:
    """Load key-value environment variables from .env if python-dotenv is not installed."""
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k = k.strip()
        v = v.strip().strip('"').strip("'")
        if k and k not in os.environ:
            os.environ[k] = v


class AppConfig:
    """Central configuration container for SOUNDARYA."""

    def __init__(self, root_dir: Path | None = None) -> None:
        self.root_dir = root_dir or PROJECT_ROOT
        self.config_dir = self.root_dir / "config"
        self.data_dir = self.root_dir / "data"
        self.documents_dir = self.data_dir / "documents"
        self.vector_store_dir = self.data_dir / "vector_store"
        self.db_path = self.data_dir / "soundarya.db"

        # Ensure essential directories exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.documents_dir.mkdir(parents=True, exist_ok=True)
        self.vector_store_dir.mkdir(parents=True, exist_ok=True)

        # Load environment variables
        load_env(self.root_dir / ".env")

        # Load settings and permissions YAML
        self.settings = load_yaml(self.config_dir / "settings.yaml")
        self.permissions = load_yaml(self.config_dir / "permissions.yaml")

    @property
    def assistant_name(self) -> str:
        return self.settings.get("assistant", {}).get("name", "SOUNDARYA")

    @property
    def default_language(self) -> str:
        return self.settings.get("assistant", {}).get("default_language", "Hinglish")

    @property
    def wake_word(self) -> str:
        return os.getenv("VOICE_WAKE_WORD") or self.settings.get("assistant", {}).get("wake_word", "soundarya")

    @property
    def ai_provider(self) -> str:
        return os.getenv("AI_PROVIDER") or self.settings.get("ai", {}).get("default_provider", "fallback")

    @property
    def openai_api_key(self) -> str:
        return os.getenv("OPENAI_API_KEY", "")

    @property
    def openai_model(self) -> str:
        return os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    @property
    def ollama_base_url(self) -> str:
        return os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    @property
    def ollama_model(self) -> str:
        return os.getenv("OLLAMA_MODEL", "llama3:8b")

    @property
    def voice_input_enabled(self) -> bool:
        val = os.getenv("VOICE_INPUT_ENABLED", "true").lower()
        return val in ("true", "1", "yes")

    @property
    def voice_output_enabled(self) -> bool:
        val = os.getenv("VOICE_OUTPUT_ENABLED", "true").lower()
        return val in ("true", "1", "yes")

    def get_setting(self, section: str, key: str, default: Any = None) -> Any:
        return self.settings.get(section, {}).get(key, default)


# Global singleton instance
config = AppConfig()
