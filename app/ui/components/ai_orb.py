"""Animated Holographic AI Core Orb widget for SOUNDARYA Assistant."""

from __future__ import annotations
import math
import random
from typing import Optional

try:
    from PySide6.QtWidgets import QWidget
    from PySide6.QtCore import Qt, QTimer, QRectF
    from PySide6.QtGui import QPainter, QColor, QPen, QRadialGradient, QBrush, QFont
    HAS_PYSIDE = True
except ImportError:
    HAS_PYSIDE = False
    QWidget = object  # type: ignore

from app.core.state import AssistantState


class SoundaryaOrb(QWidget if HAS_PYSIDE else object):  # type: ignore
    """Procedurally rendered holographic AI core with dynamic state animations."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        if not HAS_PYSIDE:
            return
        super().__init__(parent)
        self.setMinimumSize(220, 220)
        self.setMaximumSize(300, 300)

        self.current_state = AssistantState.IDLE
        self.angle_ring_1 = 0.0
        self.angle_ring_2 = 0.0
        self.pulse_phase = 0.0
        self.waveform_levels = [0.2] * 16

        # 60 FPS animation timer
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self._animate_frame)
        self.anim_timer.start(16)

    def set_state(self, state: AssistantState) -> None:
        """Update the visual mode to match the assistant operational state."""
        self.current_state = state
        self.update()

    def _animate_frame(self) -> None:
        # State-based rotation speeds
        if self.current_state == AssistantState.PROCESSING:
            self.angle_ring_1 += 3.5
            self.angle_ring_2 -= 4.5
        elif self.current_state == AssistantState.EXECUTING:
            self.angle_ring_1 += 2.5
            self.angle_ring_2 -= 3.0
        elif self.current_state == AssistantState.LISTENING:
            self.angle_ring_1 += 1.5
            self.angle_ring_2 -= 1.8
        else:
            self.angle_ring_1 += 0.6
            self.angle_ring_2 -= 0.8

        self.pulse_phase = (self.pulse_phase + 0.05) % (2 * math.pi)

        # Procedural speech waveform fluctuation
        if self.current_state == AssistantState.SPEAKING:
            self.waveform_levels = [random.uniform(0.3, 1.0) for _ in range(16)]
        elif self.current_state == AssistantState.LISTENING:
            self.waveform_levels = [random.uniform(0.1, 0.6) for _ in range(16)]
        else:
            self.waveform_levels = [0.15 for _ in range(16)]

        self.update()

    def paintEvent(self, event) -> None:  # type: ignore
        if not HAS_PYSIDE:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        width = self.width()
        height = self.height()
        center_x = width / 2.0
        center_y = height / 2.0
        base_radius = min(width, height) * 0.38

        # Color schemes mapped to states
        if self.current_state == AssistantState.ERROR:
            primary_color = QColor(255, 0, 84) # Crimson
            secondary_color = QColor(255, 120, 0)
        elif self.current_state == AssistantState.SPEAKING:
            primary_color = QColor(157, 78, 221) # Violet
            secondary_color = QColor(0, 229, 255) # Cyan
        elif self.current_state == AssistantState.PROCESSING:
            primary_color = QColor(114, 9, 183) # Deep Purple
            secondary_color = QColor(76, 201, 240)
        elif self.current_state == AssistantState.LISTENING:
            primary_color = QColor(0, 245, 212) # Bright Emerald / Cyan
            secondary_color = QColor(0, 180, 216)
        elif self.current_state == AssistantState.EXECUTING:
            primary_color = QColor(255, 183, 3) # Cyber Gold
            secondary_color = QColor(157, 78, 221)
        else: # IDLE
            primary_color = QColor(0, 229, 255) # Electric Cyan
            secondary_color = QColor(157, 78, 221)

        pulse_scale = 1.0 + 0.05 * math.sin(self.pulse_phase)
        active_radius = base_radius * pulse_scale

        # 1. Background Glow / Halo
        glow_grad = QRadialGradient(center_x, center_y, active_radius * 1.3)
        glow_primary = QColor(primary_color)
        glow_primary.setAlpha(40)
        glow_grad.setColorAt(0.0, glow_primary)
        glow_grad.setColorAt(1.0, QColor(10, 12, 20, 0))
        painter.setBrush(QBrush(glow_grad))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QRectF(center_x - active_radius * 1.3, center_y - active_radius * 1.3, active_radius * 2.6, active_radius * 2.6))

        # 2. Outer Rotating Cyber Ring
        painter.save()
        painter.translate(center_x, center_y)
        painter.rotate(self.angle_ring_1)
        pen_outer = QPen(primary_color, 2, Qt.DashLine)
        painter.setPen(pen_outer)
        painter.drawEllipse(QRectF(-active_radius * 0.95, -active_radius * 0.95, active_radius * 1.9, active_radius * 1.9))
        painter.restore()

        # 3. Inner Counter-Rotating Arc Ring
        painter.save()
        painter.translate(center_x, center_y)
        painter.rotate(self.angle_ring_2)
        pen_inner = QPen(secondary_color, 3, Qt.SolidLine)
        painter.setPen(pen_inner)
        # Draw broken arcs
        for i in range(4):
            painter.drawArc(QRectF(-active_radius * 0.75, -active_radius * 0.75, active_radius * 1.5, active_radius * 1.5), i * 90 * 16, 55 * 16)
        painter.restore()

        # 4. Radiating Acoustic Waveform Needles (Active when Speaking/Listening)
        if self.current_state in (AssistantState.SPEAKING, AssistantState.LISTENING):
            num_bars = len(self.waveform_levels)
            for idx, level in enumerate(self.waveform_levels):
                angle_rad = (idx / num_bars) * 2 * math.pi
                inner_r = active_radius * 0.55
                outer_r = inner_r + (level * 25)
                x1 = center_x + inner_r * math.cos(angle_rad)
                y1 = center_y + inner_r * math.sin(angle_rad)
                x2 = center_x + outer_r * math.cos(angle_rad)
                y2 = center_y + outer_r * math.sin(angle_rad)
                wave_pen = QPen(primary_color, 2)
                painter.setPen(wave_pen)
                painter.drawLine(int(x1), int(y1), int(x2), int(y2))

        # 5. Core Nucleus (Pulsing glowing center)
        core_radius = active_radius * 0.45
        core_grad = QRadialGradient(center_x, center_y, core_radius)
        c_bright = QColor(255, 255, 255, 220)
        c_edge = QColor(primary_color)
        c_edge.setAlpha(160)
        core_grad.setColorAt(0.0, c_bright)
        core_grad.setColorAt(0.6, c_edge)
        core_grad.setColorAt(1.0, QColor(primary_color.red(), primary_color.green(), primary_color.blue(), 20))
        painter.setBrush(QBrush(core_grad))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QRectF(center_x - core_radius, center_y - core_radius, core_radius * 2, core_radius * 2))

        # 6. Central State Text Label
        painter.setPen(QColor(255, 255, 255, 230))
        font = QFont("Helvetica", 9, QFont.Bold)
        font.setLetterSpacing(QFont.AbsoluteSpacing, 1)
        painter.setFont(font)
        state_label = self.current_state.value.upper()
        painter.drawText(QRectF(center_x - 50, center_y - 10, 100, 20), Qt.AlignCenter, state_label)
