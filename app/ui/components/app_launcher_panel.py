"""Application Registry and Quick Launcher UI Panel for SOUNDARYA."""

from __future__ import annotations
import json
from typing import Optional, Callable

try:
    from PySide6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QLabel,
        QLineEdit, QPushButton, QListWidget, QListWidgetItem, QFrame
    )
    from PySide6.QtCore import Qt
    HAS_PYSIDE = True
except ImportError:
    HAS_PYSIDE = False
    QWidget = object  # type: ignore

from app.database.repositories import AppRegistryRepository
from app.system.app_launcher import app_launcher


class AppLauncherPanel(QWidget if HAS_PYSIDE else object):  # type: ignore
    """Interactive application directory and one-click launcher."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        if not HAS_PYSIDE:
            return
        super().__init__(parent)
        self.repo = AppRegistryRepository()
        self.on_launch_requested: Optional[Callable[[str], None]] = None
        self._init_ui()
        self.reload_apps()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        header_layout = QHBoxLayout()
        title_lbl = QLabel("APPLICATION REGISTRY")
        title_lbl.setStyleSheet("font-weight: bold; color: #00e5ff; letter-spacing: 1px; font-size: 11px;")
        header_layout.addWidget(title_lbl)
        header_layout.addStretch()

        self.btn_rescan = QPushButton("SCAN APPS")
        self.btn_rescan.setStyleSheet("font-size: 10px; padding: 4px 8px;")
        self.btn_rescan.clicked.connect(self._rescan_apps)
        header_layout.addWidget(self.btn_rescan)
        layout.addLayout(header_layout)

        # Search bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Filter apps or aliases...")
        self.search_input.textChanged.connect(self._filter_apps)
        layout.addWidget(self.search_input)

        # App list
        self.app_list = QListWidget()
        self.app_list.setStyleSheet("""
            QListWidget {
                background-color: #0d101a;
                border: 1px solid rgba(0, 229, 255, 0.2);
                border-radius: 8px;
                padding: 6px;
            }
            QListWidget::item {
                padding: 8px 10px;
                border-bottom: 1px solid rgba(157, 78, 221, 0.15);
                border-radius: 4px;
            }
            QListWidget::item:hover {
                background-color: rgba(0, 229, 255, 0.1);
            }
            QListWidget::item:selected {
                background-color: rgba(0, 229, 255, 0.2);
                border: 1px solid #00e5ff;
            }
        """)
        self.app_list.itemDoubleClicked.connect(self._on_item_double_clicked)
        layout.addWidget(self.app_list, stretch=1)

        # Launch Button
        self.btn_launch = QPushButton("LAUNCH SELECTED")
        self.btn_launch.setProperty("class", "btn-primary")
        self.btn_launch.clicked.connect(self._launch_selected)
        layout.addWidget(self.btn_launch)

    def _rescan_apps(self) -> None:
        app_launcher.scan_installed_applications()
        self.reload_apps()

    def reload_apps(self) -> None:
        self.apps = self.repo.list_apps()
        self._filter_apps(self.search_input.text())

    def _filter_apps(self, filter_text: str) -> None:
        self.app_list.clear()
        query = filter_text.lower().strip()

        for a in self.apps:
            name = a["name"]
            cat = a["category"]
            try:
                aliases = json.loads(a["aliases"])
            except Exception:
                aliases = []

            alias_str = ", ".join(aliases[:3])
            display_text = f"{name}  [{cat.upper()}]\nAliases: {alias_str}"

            if not query or query in name.lower() or any(query in al.lower() for al in aliases):
                item = QListWidgetItem(display_text)
                item.setData(Qt.UserRole, a["name"])
                self.app_list.addItem(item)

    def _on_item_double_clicked(self, item: QListWidgetItem) -> None:
        app_name = item.data(Qt.UserRole)
        if app_name and self.on_launch_requested:
            self.on_launch_requested(app_name)

    def _launch_selected(self) -> None:
        item = self.app_list.currentItem()
        if item:
            self._on_item_double_clicked(item)
