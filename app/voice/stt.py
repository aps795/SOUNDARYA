"""Speech-to-Text audio transcription engine for SOUNDARYA."""

from __future__ import annotations
import logging
from typing import Optional, Callable

logger = logging.getLogger("Soundarya.Voice.STT")

try:
    import speech_recognition as sr
    HAS_SR = True
except ImportError:
    HAS_SR = False


class SpeechToTextEngine:
    """Captures microphone input and transcribes audio to text."""

    def __init__(self) -> None:
        self.recognizer = sr.Recognizer() if HAS_SR else None
        if self.recognizer:
            self.recognizer.energy_threshold = 400
            self.recognizer.dynamic_energy_threshold = True

    def is_available(self) -> bool:
        return HAS_SR

    def transcribe_from_mic(self, timeout_sec: float = 5.0) -> Optional[str]:
        """Record audio from active microphone and transcribe to text."""
        if not HAS_SR or not self.recognizer:
            logger.warning("speech_recognition library is not available.")
            return None

        try:
            with sr.Microphone() as source:
                logger.info("Listening for audio input...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=timeout_sec, phrase_time_limit=10.0)
                # Attempt Google Speech Recognition with Indian English / Hinglish support
                text = self.recognizer.recognize_google(audio, language="en-IN")
                logger.info(f"Transcribed audio: '{text}'")
                return text
        except sr.WaitTimeoutError:
            logger.info("Microphone timed out waiting for speech.")
            return None
        except sr.UnknownValueError:
            logger.info("Speech was unintelligible.")
            return None
        except Exception as e:
            logger.error(f"STT transcription failure: {e}")
            return None


# Global instance
stt_engine = SpeechToTextEngine()
