"""Unified Voice Interaction Controller for SOUNDARYA."""

from __future__ import annotations
import threading
import logging
from typing import Callable, Optional
from app.core.config import config
from app.voice.stt import stt_engine
from app.voice.tts import tts_engine

logger = logging.getLogger("Soundarya.Voice.Controller")


class VoiceController:
    """Coordinates Push-to-Talk and Continuous Listening modes."""

    def __init__(self) -> None:
        self.push_to_talk_active = False
        self.continuous_mode = False
        self.muted = False
        self.listening = False
        self.on_speech_detected: Optional[Callable[[str], None]] = None
        self._continuous_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

    def set_callback(self, callback: Callable[[str], None]) -> None:
        """Register handler to receive transcribed user commands."""
        self.on_speech_detected = callback

    def toggle_mute(self) -> bool:
        """Toggle microphone mute status."""
        self.muted = not self.muted
        logger.info(f"Microphone mute state: {self.muted}")
        return self.muted

    def start_push_to_talk(self) -> None:
        """Initiate single speech capture session."""
        if self.muted or self.listening:
            return

        def _capture() -> None:
            self.listening = True
            try:
                text = stt_engine.transcribe_from_mic(timeout_sec=5.0)
                if text and self.on_speech_detected:
                    self.on_speech_detected(text)
            finally:
                self.listening = False

        threading.Thread(target=_capture, daemon=True).start()

    def enable_continuous_mode(self, enabled: bool) -> None:
        """Toggle continuous background wake-word listening with explicit user consent."""
        self.continuous_mode = enabled
        if enabled:
            self._stop_event.clear()
            self._continuous_thread = threading.Thread(target=self._continuous_worker, daemon=True)
            self._continuous_thread.start()
            logger.info("Continuous voice listening enabled.")
        else:
            self._stop_event.set()
            logger.info("Continuous voice listening stopped.")

    def _continuous_worker(self) -> None:
        while not self._stop_event.is_set():
            if self.muted or tts_engine.is_speaking:
                self._stop_event.wait(0.5)
                continue
            text = stt_engine.transcribe_from_mic(timeout_sec=4.0)
            if text and self.on_speech_detected:
                self.on_speech_detected(text)


# Global instance
voice_controller = VoiceController()
