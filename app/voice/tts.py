"""Text-to-Speech synthesis coordinator for SOUNDARYA."""

from __future__ import annotations
import os
import sys
import threading
import subprocess
import logging
from typing import Optional
from app.core.config import config
from app.system.os_bridge import os_bridge

logger = logging.getLogger("Soundarya.Voice.TTS")


class TextToSpeechEngine:
    """Manages audible speech synthesis with platform-native high fidelity engines."""

    def __init__(self) -> None:
        self.enabled = config.voice_output_enabled
        self.lock = threading.Lock()
        self._is_speaking = False

    @property
    def is_speaking(self) -> bool:
        return self._is_speaking

    def speak(self, text: str, non_blocking: bool = True) -> None:
        """Synthesize and vocalize the given text."""
        if not self.enabled or not text.strip():
            return

        if non_blocking:
            t = threading.Thread(target=self._synthesize_sync, args=(text,), daemon=True)
            t.start()
        else:
            self._synthesize_sync(text)

    def _synthesize_sync(self, text: str) -> None:
        with self.lock:
            self._is_speaking = True
            try:
                # Clean text of markdown asterisks or code formatting
                cleaned = text.replace("*", "").replace("#", "").replace("`", "")
                
                if os_bridge.is_mac:
                    # High quality native macOS speech synthesis
                    subprocess.run(["say", "-r", "185", cleaned], check=False)
                elif os_bridge.is_windows:
                    # Windows PowerShell Speech Synthesizer or pyttsx3
                    ps_cmd = f"Add-Type -AssemblyName System.Speech; $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer; $synth.Speak('{cleaned}')"
                    subprocess.run(["powershell", "-Command", ps_cmd], check=False)
                else:
                    # Linux espeak fallback
                    subprocess.run(["espeak", cleaned], check=False)
            except Exception as e:
                logger.error(f"TTS vocalization failed: {e}")
            finally:
                self._is_speaking = False


# Global instance
tts_engine = TextToSpeechEngine()
