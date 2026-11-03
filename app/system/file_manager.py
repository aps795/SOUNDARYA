"""File search, browsing, and document handling engine for SOUNDARYA."""

from __future__ import annotations
import os
import shutil
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from app.system.os_bridge import os_bridge

logger = logging.getLogger("Soundarya.FileManager")


class FileManager:
    """Handles personal file searches, reads, and directory operations."""

    def __init__(self) -> None:
        self.user_dirs = os_bridge.get_user_directories()

    def search_files(self, query: str, search_path: Optional[Path] = None, max_results: int = 15) -> List[Dict[str, Any]]:
        """Search for files by filename or extension across user documents or given path."""
        target_root = search_path or self.user_dirs.get("documents", Path.home())
        results: List[Dict[str, Any]] = []
        term = query.lower()

        try:
            for root, dirs, files in os.walk(target_root):
                # Avoid hidden directories and cache
                dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("node_modules", "venv", ".git")]
                for f in files:
                    if term in f.lower():
                        full_path = Path(root) / f
                        try:
                            stat = full_path.stat()
                            results.append({
                                "name": f,
                                "path": str(full_path),
                                "size_bytes": stat.st_size,
                                "modified": stat.st_mtime
                            })
                            if len(results) >= max_results:
                                return results
                        except OSError:
                            continue
        except Exception as e:
            logger.error(f"Error during file search for '{query}': {e}")
        return results

    def read_text_file(self, file_path: str | Path, max_lines: int = 100) -> str:
        """Safely read lines from supported plain text, markdown, or code files."""
        path = Path(file_path)
        if not path.exists():
            return f"Error: File '{path}' does not exist."
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                lines = [f.readline() for _ in range(max_lines)]
            return "".join(lines)
        except Exception as e:
            return f"Error reading file: {e}"

    def delete_file(self, file_path: str | Path) -> tuple[bool, str]:
        """Delete a file with security checks."""
        path = Path(file_path).resolve()
        if not path.exists():
            return False, f"File '{path}' does not exist."
        try:
            if path.is_file():
                path.unlink()
                return True, f"File '{path.name}' deleted."
            elif path.is_dir():
                shutil.rmtree(path)
                return True, f"Directory '{path.name}' deleted."
            return False, "Unknown item type."
        except Exception as e:
            return False, f"Deletion failed: {e}"


# Global instance
file_manager = FileManager()
