"""Personal Memory and Knowledge Management UI Panel for SOUNDARYA."""

from __future__ import annotations
from typing import Optional

try:
    from PySide6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QLabel,
        QLineEdit, QTextEdit, QPushButton, QListWidget, QListWidgetItem,
        QComboBox, QMessageBox
    )
    from PySide6.QtCore import Qt
    HAS_PYSIDE = True
except ImportError:
    HAS_PYSIDE = False
    QWidget = object  # type: ignore

from app.database.repositories import PersonalMemoryRepository
from app.memory.memory_manager import memory_manager


class MemoryPanel(QWidget if HAS_PYSIDE else object):  # type: ignore
    """Interface to inspect, add, and query private personal memories and knowledge."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        if not HAS_PYSIDE:
            return
        super().__init__(parent)
        self.repo = PersonalMemoryRepository()
        self._init_ui()
        self.reload_memories()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        # Header
        header = QLabel("PERSONAL MEMORY VAULT")
        header.setStyleSheet("font-weight: bold; color: #9d4edd; letter-spacing: 1px; font-size: 11px;")
        layout.addWidget(header)

        # Add Memory Form
        form_layout = QVBoxLayout()
        form_layout.setSpacing(6)

        title_row = QHBoxLayout()
        self.input_title = QLineEdit()
        self.input_title.setPlaceholderText("Memory title or subject...")
        title_row.addWidget(self.input_title, stretch=2)

        self.combo_category = QComboBox()
        self.combo_category.addItems(["note", "fact", "goal", "instruction"])
        self.combo_category.setStyleSheet("background-color: #191f33; padding: 6px; border-radius: 6px;")
        title_row.addWidget(self.combo_category, stretch=1)
        form_layout.addLayout(title_row)

        self.input_content = QLineEdit()
        self.input_content.setPlaceholderText("Detailed memory information...")
        form_layout.addWidget(self.input_content)

        btn_save = QPushButton("SAVE TO MEMORY")
        btn_save.setProperty("class", "btn-primary")
        btn_save.clicked.connect(self._save_memory)
        form_layout.addWidget(btn_save)

        layout.addLayout(form_layout)

        # Search Bar
        search_row = QHBoxLayout()
        self.input_search = QLineEdit()
        self.input_search.setPlaceholderText("Search personal notes and facts...")
        self.input_search.textChanged.connect(self._search_memories)
        search_row.addWidget(self.input_search)
        layout.addLayout(search_row)

        # Memories List
        self.list_memories = QListWidget()
        self.list_memories.setStyleSheet("""
            QListWidget {
                background-color: #0d101a;
                border: 1px solid rgba(157, 78, 221, 0.25);
                border-radius: 8px;
                padding: 6px;
            }
            QListWidget::item {
                padding: 8px 10px;
                border-bottom: 1px solid rgba(0, 229, 255, 0.15);
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.list_memories, stretch=1)

    def reload_memories(self) -> None:
        self.memories = self.repo.list_memories(limit=50)
        self._display_memories(self.memories)

    def _display_memories(self, items: list[dict]) -> None:
        self.list_memories.clear()
        for m in items:
            cat = m["category"].upper()
            title = m["title"]
            content = m["content"]
            display_text = f"[{cat}] {title}\n{content}"
            item = QListWidgetItem(display_text)
            self.list_memories.addItem(item)

    def _save_memory(self) -> None:
        title = self.input_title.text().strip()
        content = self.input_content.text().strip()
        cat = self.combo_category.currentText()

        if not content:
            return

        memory_manager.remember_fact(content=content, category=cat, title=title or None)
        self.input_title.clear()
        self.input_content.clear()
        self.reload_memories()

    def _search_memories(self, query: str) -> None:
        q = query.strip()
        if not q:
            self._display_memories(self.memories)
        else:
            results = self.repo.search_memories(q, limit=20)
            self._display_memories(results)
