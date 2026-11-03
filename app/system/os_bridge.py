"""Operating System abstraction bridge for cross-platform automation."""

from __future__ import annotations
import os
import sys
import platform
import subprocess
import logging
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger("Soundarya.OSBridge")


class OSBridge:
    """Provides native OS interactions for macOS, Windows, and Linux."""

    def __init__(self) -> None:
        self.system = platform.system().lower() # 'darwin', 'windows', 'linux'

    @property
    def is_mac(self) -> bool:
        return self.system == "darwin"

    @property
    def is_windows(self) -> bool:
        return self.system == "windows"

    @property
    def is_linux(self) -> bool:
        return self.system == "linux"

    def open_item(self, target_path: str | Path) -> bool:
        """Open a file or folder using the default system handler."""
        path_str = str(target_path)
        try:
            if self.is_mac:
                subprocess.run(["open", path_str], check=True)
            elif self.is_windows:
                os.startfile(path_str) # type: ignore
            else:
                subprocess.run(["xdg-open", path_str], check=True)
            return True
        except Exception as e:
            logger.error(f"Failed to open item '{path_str}': {e}")
            return False

    def launch_binary(self, executable_path: str, args: Optional[List[str]] = None) -> bool:
        """Launch an executable application."""
        cmd = [executable_path] + (args or [])
        try:
            if self.is_mac and executable_path.endswith(".app"):
                subprocess.run(["open", "-a", executable_path], check=True)
            elif self.is_windows:
                subprocess.Popen(cmd, creationflags=subprocess.DETACHED_PROCESS if hasattr(subprocess, 'DETACHED_PROCESS') else 0)
            else:
                subprocess.Popen(cmd)
            return True
        except Exception as e:
            logger.error(f"Failed to launch binary '{executable_path}': {e}")
            return False

    def get_user_directories(self) -> dict[str, Path]:
        """Resolve standard user directories."""
        home = Path.home()
        return {
            "home": home,
            "downloads": home / "Downloads",
            "documents": home / "Documents",
            "desktop": home / "Desktop",
            "pictures": home / "Pictures",
            "music": home / "Music"
        }

    def open_folder(self, folder_name: str) -> bool:
        """Open standard user folder by key or custom path."""
        dirs = self.get_user_directories()
        target = dirs.get(folder_name.lower())
        if target and target.exists():
            return self.open_item(target)
        # Attempt direct path
        path = Path(folder_name).expanduser().resolve()
        if path.exists():
            return self.open_item(path)
        return False


# Global singleton instance
os_bridge = OSBridge()
