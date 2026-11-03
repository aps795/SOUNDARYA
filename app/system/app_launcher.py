"""Application Discovery and Launcher Engine for SOUNDARYA."""

from __future__ import annotations
import os
import logging
from pathlib import Path
from typing import Dict, List, Optional
from app.system.os_bridge import os_bridge
from app.database.repositories import AppRegistryRepository

logger = logging.getLogger("Soundarya.AppLauncher")


class AppLauncher:
    """Manages application indexing, alias resolution, and process launching."""

    def __init__(self, repo: Optional[AppRegistryRepository] = None) -> None:
        self.repo = repo or AppRegistryRepository()

    def scan_installed_applications(self) -> int:
        """Scan system directories for installed applications and populate registry."""
        count = 0
        if os_bridge.is_mac:
            count += self._scan_mac_apps()
        elif os_bridge.is_windows:
            count += self._scan_windows_apps()
        else:
            count += self._scan_linux_apps()
        logger.info(f"Discovered and registered {count} system applications.")
        return count

    def _scan_mac_apps(self) -> int:
        count = 0
        search_dirs = [
            Path("/Applications"),
            Path("/System/Applications"),
            Path.home() / "Applications"
        ]

        for app_dir in search_dirs:
            if not app_dir.exists():
                continue
            for item in app_dir.glob("*.app"):
                name = item.stem
                aliases = self._generate_default_aliases(name)
                self.repo.register_app(
                    name=name,
                    executable_path=str(item),
                    aliases=aliases,
                    category=self._categorize_app(name)
                )
                count += 1
        return count

    def _scan_windows_apps(self) -> int:
        count = 0
        start_menus = [
            Path(os.environ.get("APPDATA", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs",
            Path(os.environ.get("ProgramData", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs"
        ]
        for menu in start_menus:
            if not menu.exists():
                continue
            for link in menu.rglob("*.lnk"):
                name = link.stem
                aliases = self._generate_default_aliases(name)
                self.repo.register_app(
                    name=name,
                    executable_path=str(link),
                    aliases=aliases,
                    category=self._categorize_app(name)
                )
                count += 1
        return count

    def _scan_linux_apps(self) -> int:
        count = 0
        desktop_dirs = [
            Path("/usr/share/applications"),
            Path.home() / ".local/share/applications"
        ]
        for dir_path in desktop_dirs:
            if not dir_path.exists():
                continue
            for item in dir_path.glob("*.desktop"):
                name = item.stem
                self.repo.register_app(
                    name=name,
                    executable_path=str(item),
                    aliases=self._generate_default_aliases(name),
                    category=self._categorize_app(name)
                )
                count += 1
        return count

    def _generate_default_aliases(self, app_name: str) -> List[str]:
        name_lower = app_name.lower()
        aliases = [name_lower]
        cleaned = "".join([c for c in name_lower if c.isalnum() or c.isspace()])
        if cleaned != name_lower:
            aliases.append(cleaned)
        
        # Common known mappings
        known = {
            "google chrome": ["chrome", "browser", "google browser"],
            "visual studio code": ["vscode", "code", "editor", "vs code"],
            "terminal": ["term", "console", "command prompt", "shell"],
            "calculator": ["calc"],
            "spotify": ["music", "songs"],
            "safari": ["browser", "mac browser"],
            "finder": ["files", "file manager"],
            "notepad": ["notes", "text editor"],
            "slack": ["chat", "office chat"]
        }
        for k, v in known.items():
            if k in name_lower or name_lower in k:
                aliases.extend(v)
        return list(set(aliases))

    def _categorize_app(self, app_name: str) -> str:
        name_lower = app_name.lower()
        if any(w in name_lower for w in ["chrome", "safari", "firefox", "edge", "brave"]):
            return "browser"
        if any(w in name_lower for w in ["code", "sublime", "pycharm", "intellij", "terminal", "iterm"]):
            return "development"
        if any(w in name_lower for w in ["spotify", "music", "vlc", "quicktime", "media"]):
            return "media"
        if any(w in name_lower for w in ["notes", "word", "excel", "pages", "calc", "calendar"]):
            return "productivity"
        return "general"

    def launch_app(self, query: str) -> tuple[bool, str]:
        """Find an application by query/alias and launch it."""
        app = self.repo.find_app(query)
        if not app:
            # If not in registry, attempt direct launch by name
            if os_bridge.is_mac:
                mac_app = Path(f"/Applications/{query}.app")
                if mac_app.exists():
                    os_bridge.launch_binary(str(mac_app))
                    return True, f"Launched {query}."
            return False, f"Application '{query}' not found in registry."

        path = app["executable_path"]
        success = os_bridge.launch_binary(path)
        if success:
            self.repo.record_launch(app["id"])
            return True, f"Launched {app['name']} successfully."
        return False, f"Failed to launch {app['name']} at path {path}."


# Global instance
app_launcher = AppLauncher()
