"""Main executable entry point for SOUNDARYA — Personal AI Operating Assistant."""

from __future__ import annotations
import sys
import logging
from pathlib import Path
from app.core.config import config
from app.core.engine import core_engine
from app.core.state import AssistantState

# Configure application logging
logging.basicConfig(
    level=logging.INFO if config.get_setting("assistant", "debug", True) else logging.WARNING,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s"
)
logger = logging.getLogger("Soundarya.Main")


def run_cli_mode() -> None:
    """Terminal-based interactive session for SOUNDARYA."""
    print("=" * 65)
    print(f"  ◈ {config.assistant_name} — {config.get_setting('assistant', 'tagline', 'Personal AI Operating Assistant')}")
    print(f"  ◈ Version: {config.get_setting('assistant', 'version', '1.0.0')} | Language: {config.default_language}")
    print("=" * 65)
    print("Commands you can try:")
    print("  • 'Chrome kholo' / 'open VS Code'")
    print("  • 'Downloads folder open karo'")
    print("  • 'System status batao'")
    print("  • 'Aaj ka schedule batao'")
    print("  • 'Note down that meeting is tomorrow at 4 PM'")
    print("  • 'Notes mein meeting search karo'")
    print("  • Type 'exit' or 'quit' to terminate.")
    print("-" * 65)

    while True:
        try:
            user_input = input("\n[COMMANDER] > ").strip()
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit", "q"):
                print(f"\n[SOUNDARYA] > Systems standing down. Goodbye Commander.")
                break

            response = core_engine.process_command(user_input, speak_output=config.voice_output_enabled)
            print(f"\n[SOUNDARYA] > {response}")
        except (KeyboardInterrupt, EOFError):
            print(f"\n[SOUNDARYA] > Interrupted. Shutting down.")
            break


def main() -> None:
    """Launch application in Desktop GUI or CLI mode."""
    # Check if CLI mode explicitly requested or headless
    if "--cli" in sys.argv or "--headless" in sys.argv:
        run_cli_mode()
        return

    # Try PySide6 GUI launch
    try:
        from PySide6.QtWidgets import QApplication
        from app.ui.main_window import SoundaryaMainWindow

        app = QApplication(sys.argv)
        app.setApplicationName(config.assistant_name)
        window = SoundaryaMainWindow()
        window.show()
        sys.exit(app.exec())
    except ImportError:
        logger.warning("PySide6 is not installed or graphical environment unavailable. Launching CLI terminal mode.")
        run_cli_mode()


if __name__ == "__main__":
    main()
