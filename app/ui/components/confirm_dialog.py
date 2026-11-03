"""Security Confirmation Modal Dialog for Level 2 Operations."""

from __future__ import annotations
import json
from typing import Optional

try:
    from PySide6.QtWidgets import (
        QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
    )
    from PySide6.QtCore import Qt
    HAS_PYSIDE = True
except ImportError:
    HAS_PYSIDE = False
    QDialog = object  # type: ignore

from app.core.state import ActionRequest


class SecurityConfirmDialog(QDialog if HAS_PYSIDE else object):  # type: ignore
    """Prompts the user for explicit authorization before executing sensitive operations."""

    def __init__(self, request: ActionRequest, parent: Optional[QDialog] = None) -> None:
        if not HAS_PYSIDE:
            return
        super().__init__(parent)
        self.request = request
        self.setWindowTitle("SECURITY AUTHORIZATION REQUIRED")
        self.setFixedSize(480, 260)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # Warning Header
        header = QLabel("⚠️ LEVEL 2 AUTHORIZATION REQUIRED")
        header.setStyleSheet("color: #ffb703; font-weight: bold; font-size: 14px; letter-spacing: 1px;")
        layout.addWidget(header)

        # Details box
        box = QFrame()
        box.setStyleSheet("""
            QFrame {
                background-color: #121624;
                border: 1px solid rgba(255, 183, 3, 0.4);
                border-radius: 8px;
                padding: 12px;
            }
        """)
        box_layout = QVBoxLayout(box)
        box_layout.setSpacing(6)

        lbl_action = QLabel(f"ACTION: {self.request.action_name}")
        lbl_action.setStyleSheet("color: #00e5ff; font-weight: bold; font-size: 12px;")
        box_layout.addWidget(lbl_action)

        params_str = json.dumps(self.request.parameters, indent=2)
        lbl_params = QLabel(f"PARAMETERS:\n{params_str}")
        lbl_params.setStyleSheet("color: #f0f4fc; font-family: monospace; font-size: 11px;")
        box_layout.addWidget(lbl_params)

        layout.addWidget(box)

        # Warning Text
        lbl_desc = QLabel("This action requires explicit user authorization before execution.")
        lbl_desc.setStyleSheet("color: #8e9aaf; font-size: 11px;")
        layout.addWidget(lbl_desc)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.btn_reject = QPushButton("ABORT / REJECT")
        self.btn_reject.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 0, 84, 0.2);
                border: 1px solid #ff0054;
                color: #ff0054;
                font-weight: bold;
                padding: 10px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: rgba(255, 0, 84, 0.4);
            }
        """)
        self.btn_reject.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_reject)

        self.btn_accept = QPushButton("AUTHORIZE & EXECUTE")
        self.btn_accept.setStyleSheet("""
            QPushButton {
                background-color: rgba(0, 245, 212, 0.2);
                border: 1px solid #00f5d4;
                color: #00f5d4;
                font-weight: bold;
                padding: 10px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: rgba(0, 245, 212, 0.4);
            }
        """)
        self.btn_accept.clicked.connect(self.accept)
        btn_layout.addWidget(self.btn_accept)

        layout.addLayout(btn_layout)
