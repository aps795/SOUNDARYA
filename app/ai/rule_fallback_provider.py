"""Rule-based offline conversational fallback provider for SOUNDARYA."""

from __future__ import annotations
import random
from typing import List, Dict, Optional
from app.ai.provider_base import BaseAIProvider


class RuleFallbackProvider(BaseAIProvider):
    """Provides high-quality offline conversational responses when cloud/local LLMs are unreachable."""

    def is_available(self) -> bool:
        return True

    def generate_response(self, prompt: str, system_prompt: Optional[str] = None, history: Optional[List[Dict[str, str]]] = None) -> str:
        p = prompt.lower().strip()

        # Greetings
        if any(w in p for w in ["hello", "namaste", "hi", "hey soundarya", "salam"]):
            responses = [
                "Namaste! Main Soundarya hoon. Main aapki kya madad kar sakti hoon?",
                "Hello! Soundarya is online and ready. What system command or inquiry would you like to run?",
                "Namaste Commander! Bataiye, aaj hum kya execute karein?"
            ]
            return random.choice(responses)

        # Identity
        if any(w in p for w in ["who are you", "kaun ho", "tumhara naam", "introduce"]):
            return (
                "Main hoon SOUNDARYA — aapka Personal AI Operating Assistant. "
                "Main aapke applications launch kar sakti hoon, system monitor kar sakti hoon, "
                "personal database aur memory maintain karti hoon, aur Hindi, Hinglish ya English mein baat kar sakti hoon."
            )

        # State / Wellbeing
        if any(w in p for w in ["kaise ho", "how are you", "sab theek"]):
            return "Main bilkul badhiya hoon! Sabhi system subroutines 100% active hain. Aap bataiye, kya karna hai?"

        # Help
        if any(w in p for w in ["help", "madad", "kya kar sakti ho", "features"]):
            return (
                "Aap mujhse ye sab karwa sakte hain:\n"
                "1. Applications kholna: 'Chrome kholo', 'VS Code open karo'\n"
                "2. Folders browse karna: 'Downloads folder open karo'\n"
                "3. System telemetry: 'System status batao', 'Battery kitni hai'\n"
                "4. Personal memories & notes: 'Notes mein AI search karo', 'Note down that meeting is at 5pm'\n"
                "5. Schedule & tasks: 'Aaj ka schedule batao', 'Add task submit report'"
            )

        # Default conversational reply
        return (
            f"Maine aapka request note kar liya hai: '{prompt}'. "
            "Agar ye koi operating system command hai toh main ise turant execute kar sakti hoon."
        )
