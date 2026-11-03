"""Flagship Desktop HUD Window for SOUNDARYA Personal AI Operating Assistant."""

from __future__ import annotations
import sys
from typing import Optional

try:
    from PySide6.QtWidgets import (
        QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QTabWidget, QFrame, QPushButton, QCheckBox, QMessageBox
    )
    from PySide6.QtCore import Qt, QTimer, Slot
    from PySide6.QtGui import QIcon
    HAS_PYSIDE = True
except ImportError:
    HAS_PYSIDE = False
    QMainWindow = object  # type: ignore

from app.core.config import config
from app.core.state import AssistantState, ActionRequest
from app.core.security import security_engine
from app.core.engine import core_engine
from app.voice.voice_controller import voice_controller
from app.ui.theme import STYLESHEET, COLOR_CYAN_PRIMARY, COLOR_VIOLET_ACCENT
from app.ui.components.ai_orb import SoundaryaOrb
from app.ui.components.chat_panel import ChatPanel
from app.ui.components.system_monitor_panel import SystemMonitorPanel
from app.ui.components.app_launcher_panel import AppLauncherPanel
from app.ui.components.memory_panel import MemoryPanel
from app.ui.components.confirm_dialog import SecurityConfirmDialog


class SoundaryaMainWindow(QMainWindow if HAS_PYSIDE else object):  # type: ignore
    """Main desktop interface integrating holographic AI orb, voice controls, and system HUD."""

    def __init__(self) -> None:
        if not HAS_PYSIDE:
            return
        super().__init__()
        self.setWindowTitle(f"{config.assistant_name} — Personal AI Operating Assistant")
        self.resize(config.get_setting("ui", "window_width", 1280), config.get_setting("ui", "window_height", 820))
        self.setStyleSheet(STYLESHEET)

        self._init_ui()
        self._wire_engine_events()

    def _init_ui(self) -> None:
        central = QWidget(self)
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(16, 16, 16, 16)
        root_layout.setSpacing(14)

        # 1. Top HUD Status Bar
        top_bar = self._create_top_bar()
        root_layout.addWidget(top_bar)

        # 2. Main Content Area (Split Left/Right)
        main_content = QHBoxLayout()
        main_content.setSpacing(14)

        # Left Column: AI Orb, Voice Controls, Hardware Telemetry
        left_col = QFrame()
        left_col.setProperty("class", "glass-panel")
        left_col.setFixedWidth(340)
        left_layout = QVBoxLayout(left_col)
        left_layout.setContentsMargins(14, 14, 14, 14)
        left_layout.setSpacing(12)

        # Animated AI Core
        self.ai_orb = SoundaryaOrb(self)
        left_layout.addWidget(self.ai_orb, alignment=Qt.AlignCenter)

        # Voice Control Section
        voice_box = self._create_voice_controls()
        left_layout.addWidget(voice_box)

        # Live Hardware Monitor
        self.monitor_panel = SystemMonitorPanel(self)
        left_layout.addWidget(self.monitor_panel, stretch=1)

        main_content.addWidget(left_col)

        # Right Column: Tabbed Workspaces (Chat, App Registry, Memory Vault)
        right_col = QFrame()
        right_col.setProperty("class", "glass-panel")
        right_layout = QVBoxLayout(right_col)
        right_layout.setContentsMargins(8, 8, 8, 8)

        self.tabs = QTabWidget()
        self.chat_panel = ChatPanel(self)
        self.chat_panel.on_send_command = self._handle_user_command
        self.chat_panel.on_mic_clicked = self._toggle_push_to_talk

        self.launcher_panel = AppLauncherPanel(self)
        self.launcher_panel.on_launch_requested = lambda name: self._handle_user_command(f"Open {name}")

        self.memory_panel = MemoryPanel(self)

        self.tabs.addTab(self.chat_panel, "◈ TERMINAL & CHAT")
        self.tabs.addTab(self.launcher_panel, "◈ APP REGISTRY")
        self.tabs.addTab(self.memory_panel, "◈ MEMORY VAULT")

        right_layout.addWidget(self.tabs)
        main_content.addWidget(right_col, stretch=1)

        root_layout.addLayout(main_content)

    def _create_top_bar(self) -> QFrame:
        bar = QFrame()
        bar.setStyleSheet("background-color: #121624; border-radius: 8px; border: 1px solid rgba(0, 229, 255, 0.2);")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(14, 8, 14, 8)

        lbl_logo = QLabel("◈ SOUNDARYA // AI OPERATING SYSTEM")
        lbl_logo.setStyleSheet("font-weight: 800; font-size: 13px; color: #00e5ff; letter-spacing: 2px;")
        layout.addWidget(lbl_logo)

        layout.addStretch()

        self.lbl_ai_provider = QLabel(f"ENGINE: {config.ai_provider.upper()}")
        self.lbl_ai_provider.setStyleSheet("color: #9d4edd; font-weight: bold; font-size: 11px; margin-right: 15px;")
        layout.addWidget(self.lbl_ai_provider)

        self.status_badge = QLabel("STATUS: IDLE")
        self.status_badge.setObjectName("statusBadge")
        layout.addWidget(self.status_badge)

        return bar

    def _create_voice_controls(self) -> QFrame:
        box = QFrame()
        box.setStyleSheet("background-color: #0d101a; border-radius: 8px; border: 1px solid rgba(0, 229, 255, 0.15);")
        layout = QVBoxLayout(box)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        v_title = QLabel("VOICE SUBSYSTEM")
        v_title.setStyleSheet("font-weight: bold; color: #00e5ff; font-size: 10px; letter-spacing: 1px;")
        layout.addWidget(v_title)

        btn_row = QHBoxLayout()
        self.btn_ptt = QPushButton("PUSH TO TALK")
        self.btn_ptt.setProperty("class", "btn-primary")
        self.btn_ptt.clicked.connect(self._toggle_push_to_talk)
        btn_row.addWidget(self.btn_ptt)

        self.btn_mute = QPushButton("MUTE MIC")
        self.btn_mute.clicked.connect(self._toggle_mute)
        btn_row.addWidget(self.btn_mute)
        layout.addLayout(btn_row)

        self.chk_continuous = QCheckBox("Continuous Listening (Consent Required)")
        self.chk_continuous.setStyleSheet("color: #8e9aaf; font-size: 11px;")
        self.chk_continuous.toggled.connect(self._toggle_continuous)
        layout.addWidget(self.chk_continuous)

        return box

    def _wire_engine_events(self) -> None:
        core_engine.add_state_listener(self._on_assistant_state_change)
        security_engine.register_confirmation_handler(self._confirm_security_dialog)
        voice_controller.set_callback(self._on_voice_transcribed)

    def _on_assistant_state_change(self, state: AssistantState) -> None:
        self.ai_orb.set_state(state)
        self.status_badge.setText(f"STATUS: {state.value.upper()}")
        if state == AssistantState.ERROR:
            self.status_badge.setStyleSheet("background: rgba(255, 0, 84, 0.2); border: 1px solid #ff0054; color: #ff0054;")
        elif state == AssistantState.EXECUTING:
            self.status_badge.setStyleSheet("background: rgba(255, 183, 3, 0.2); border: 1px solid #ffb703; color: #ffb703;")
        elif state == AssistantState.SPEAKING:
            self.status_badge.setStyleSheet("background: rgba(157, 78, 221, 0.2); border: 1px solid #9d4edd; color: #c77dff;")
        else:
            self.status_badge.setStyleSheet("background: rgba(0, 229, 255, 0.15); border: 1px solid #00e5ff; color: #00e5ff;")

    def _confirm_security_dialog(self, request: ActionRequest) -> bool:
        """Present modal authorization dialog on UI thread."""
        dialog = SecurityConfirmDialog(request, self)
        return dialog.exec() == SecurityConfirmDialog.Accepted

    def _handle_user_command(self, text: str) -> None:
        self.chat_panel.add_message("USER", text, is_assistant=False)
        # Process command through core engine
        response = core_engine.process_command(text, speak_output=config.voice_output_enabled)
        self.chat_panel.add_message("SOUNDARYA", response, is_assistant=True)

    def _on_voice_transcribed(self, text: str) -> None:
        # Route voice transcription to command handler
        self._handle_user_command(text)

    def _toggle_push_to_talk(self) -> None:
        self.chat_panel.mic_status.setText("MIC: LISTENING...")
        self.chat_panel.mic_status.setStyleSheet("color: #00e5ff; font-weight: bold;")
        core_engine.set_state(AssistantState.LISTENING)
        voice_controller.start_push_to_talk()

    def _toggle_mute(self) -> None:
        is_muted = voice_controller.toggle_mute()
        if is_muted:
            self.btn_mute.setText("UNMUTE MIC")
            self.btn_mute.setStyleSheet("border-color: #ff0054; color: #ff0054;")
            self.chat_panel.mic_status.setText("MIC: MUTED")
            self.chat_panel.mic_status.setStyleSheet("color: #ff0054; font-weight: bold;")
        else:
            self.btn_mute.setText("MUTE MIC")
            self.btn_mute.setStyleSheet("")
            self.chat_panel.mic_status.setText("MIC: READY")
            self.chat_panel.mic_status.setStyleSheet("color: #8e9aaf; font-weight: bold;")

    def _toggle_continuous(self, checked: bool) -> None:
        if checked:
            reply = QMessageBox.question(
                self,
                "Continuous Listening Consent",
                "Continuous listening mode will keep the microphone active in the background to detect wake words.\n\nDo you grant explicit consent for SOUNDARYA to activate continuous listening?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                voice_controller.enable_continuous_mode(True)
            else:
                self.chk_continuous.setChecked(False)
        else:
            voice_controller.enable_continuous_mode(False)
