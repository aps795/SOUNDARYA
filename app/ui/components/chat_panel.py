"""Chat Conversation and Command Input Panel for SOUNDARYA."""

from __future__ import annotations
import html
from typing import Optional, Callable

try:
    from PySide6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QTextBrowser,
        QLineEdit, QPushButton, QFrame, QLabel, QScrollArea
    )
    from PySide6.QtCore import Qt, Signal
    from PySide6.QtGui import QIcon, QFont
    HAS_PYSIDE = True
except ImportError:
    HAS_PYSIDE = False
    QWidget = object  # type: ignore


class ChatPanel(QWidget if HAS_PYSIDE else object):  # type: ignore
    """Futuristic conversational terminal displaying command logs and AI responses."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        if not HAS_PYSIDE:
            return
        super().__init__(parent)
        self.on_send_command: Optional[Callable[[str], None]] = None
        self.on_mic_clicked: Optional[Callable[[], None]] = None
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        # Header with Chat Badge
        header_layout = QHBoxLayout()
        header_title = QLabel("SYSTEM TERMINAL & CONVERSATION")
        header_title.setStyleSheet("font-weight: bold; color: #00e5ff; letter-spacing: 1px; font-size: 11px;")
        header_layout.addWidget(header_title)
        header_layout.addStretch()

        self.mic_status = QLabel("MIC: READY")
        self.mic_status.setStyleSheet("color: #8e9aaf; font-size: 10px; font-weight: bold;")
        header_layout.addWidget(self.mic_status)
        layout.addLayout(header_layout)

        # Transcript Display
        self.chat_display = QTextBrowser()
        self.chat_display.setOpenExternalLinks(False)
        self.chat_display.setStyleSheet("""
            QTextBrowser {
                background-color: #0d101a;
                border: 1px solid rgba(0, 229, 255, 0.2);
                border-radius: 8px;
                padding: 12px;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            }
        """)
        layout.addWidget(self.chat_display, stretch=1)

        # Quick Action Pills
        quick_layout = QHBoxLayout()
        quick_layout.setSpacing(6)
        quick_commands = [
            "Chrome kholo",
            "Downloads open karo",
            "System status batao",
            "Aaj ka schedule",
            "Notes search AI"
        ]
        for cmd in quick_commands:
            btn = QPushButton(cmd)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(18, 22, 36, 0.8);
                    border: 1px solid rgba(0, 229, 255, 0.25);
                    border-radius: 12px;
                    padding: 4px 10px;
                    font-size: 11px;
                    color: #8e9aaf;
                }
                QPushButton:hover {
                    color: #00e5ff;
                    border: 1px solid #00e5ff;
                    background-color: rgba(0, 229, 255, 0.1);
                }
            """)
            btn.clicked.connect(lambda _, c=cmd: self._send_quick_command(c))
            quick_layout.addWidget(btn)
        quick_layout.addStretch()
        layout.addLayout(quick_layout)

        # Input Row
        input_layout = QHBoxLayout()
        input_layout.setSpacing(8)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Command or question... (e.g. 'Soundarya, VS Code kholo')")
        self.input_field.returnPressed.connect(self._handle_send)
        input_layout.addWidget(self.input_field, stretch=1)

        self.btn_send = QPushButton("TRANSMIT")
        self.btn_send.setProperty("class", "btn-primary")
        self.btn_send.clicked.connect(self._handle_send)
        input_layout.addWidget(self.btn_send)

        self.btn_mic = QPushButton("🎤")
        self.btn_mic.setToolTip("Push-to-Talk (Hold or Click)")
        self.btn_mic.setStyleSheet("""
            QPushButton {
                background-color: rgba(0, 229, 255, 0.15);
                border: 1px solid #00e5ff;
                border-radius: 6px;
                min-width: 42px;
                min-height: 38px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: rgba(0, 229, 255, 0.3);
            }
        """)
        self.btn_mic.clicked.connect(self._handle_mic)
        input_layout.addWidget(self.btn_mic)

        layout.addLayout(input_layout)

        # Welcome initial message
        self.add_message(
            "SOUNDARYA",
            "Online and operational. Systems calibrated. How may I assist you, Commander?",
            is_assistant=True
        )

    def _handle_send(self) -> None:
        text = self.input_field.text().strip()
        if not text:
            return
        self.input_field.clear()
        if self.on_send_command:
            self.on_send_command(text)

    def _send_quick_command(self, cmd: str) -> None:
        if self.on_send_command:
            self.on_send_command(cmd)

    def _handle_mic(self) -> None:
        if self.on_mic_clicked:
            self.on_mic_clicked()

    def add_message(self, sender: str, message: str, is_assistant: bool = False) -> None:
        """Append formatted bubble to chat transcript."""
        escaped_msg = html.escape(message).replace("\n", "<br>")
        if is_assistant:
            html_block = f"""
            <div style="margin-bottom: 12px; padding: 10px 14px; background: rgba(18, 22, 36, 0.9); border-left: 3px solid #00e5ff; border-radius: 8px;">
                <div style="color: #00e5ff; font-weight: bold; font-size: 11px; margin-bottom: 4px; letter-spacing: 0.5px;">◈ {sender}</div>
                <div style="color: #f0f4fc; font-size: 13px; line-height: 1.4;">{escaped_msg}</div>
            </div>
            """
        else:
            html_block = f"""
            <div style="margin-bottom: 12px; padding: 10px 14px; background: rgba(157, 78, 221, 0.15); border-right: 3px solid #9d4edd; border-radius: 8px; text-align: right;">
                <div style="color: #c77dff; font-weight: bold; font-size: 11px; margin-bottom: 4px;">USER ◈</div>
                <div style="color: #f0f4fc; font-size: 13px; line-height: 1.4;">{escaped_msg}</div>
            </div>
            """
        self.chat_display.append(html_block)
        # Scroll to bottom
        sb = self.chat_display.verticalScrollBar()
        sb.setValue(sb.maximum())
