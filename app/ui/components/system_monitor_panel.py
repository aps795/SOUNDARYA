"""Real-time System Monitoring telemetry panel for SOUNDARYA."""

from __future__ import annotations
from typing import Optional

try:
    from PySide6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QLabel,
        QProgressBar, QFrame, QGridLayout
    )
    from PySide6.QtCore import QTimer
    HAS_PYSIDE = True
except ImportError:
    HAS_PYSIDE = False
    QWidget = object  # type: ignore

from app.system.monitor import system_monitor, SystemMetrics


class SystemMonitorPanel(QWidget if HAS_PYSIDE else object):  # type: ignore
    """Live hardware performance HUD widget."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        if not HAS_PYSIDE:
            return
        super().__init__(parent)
        self._init_ui()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_metrics)
        self.timer.start(1000)
        self.refresh_metrics()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        # Title
        title_lbl = QLabel("LIVE TELEMETRY")
        title_lbl.setStyleSheet("font-weight: bold; color: #9d4edd; letter-spacing: 1px; font-size: 11px;")
        layout.addWidget(title_lbl)

        grid = QGridLayout()
        grid.setSpacing(8)

        # 1. CPU Bar
        self.lbl_cpu = QLabel("CPU: 0%")
        self.lbl_cpu.setStyleSheet("color: #8e9aaf; font-size: 11px;")
        self.bar_cpu = QProgressBar()
        self.bar_cpu.setRange(0, 100)
        grid.addWidget(self.lbl_cpu, 0, 0)
        grid.addWidget(self.bar_cpu, 0, 1)

        # 2. RAM Bar
        self.lbl_ram = QLabel("RAM: 0%")
        self.lbl_ram.setStyleSheet("color: #8e9aaf; font-size: 11px;")
        self.bar_ram = QProgressBar()
        self.bar_ram.setRange(0, 100)
        grid.addWidget(self.lbl_ram, 1, 0)
        grid.addWidget(self.bar_ram, 1, 1)

        # 3. Disk Bar
        self.lbl_disk = QLabel("DISK: 0%")
        self.lbl_disk.setStyleSheet("color: #8e9aaf; font-size: 11px;")
        self.bar_disk = QProgressBar()
        self.bar_disk.setRange(0, 100)
        grid.addWidget(self.lbl_disk, 2, 0)
        grid.addWidget(self.bar_disk, 2, 1)

        layout.addLayout(grid)

        # Secondary info box
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: #0d101a;
                border: 1px solid rgba(157, 78, 221, 0.2);
                border-radius: 6px;
                padding: 6px;
            }
        """)
        info_layout = QVBoxLayout(info_frame)
        info_layout.setSpacing(4)
        info_layout.setContentsMargins(6, 6, 6, 6)

        self.lbl_battery = QLabel("BATTERY: Detecting...")
        self.lbl_battery.setStyleSheet("color: #00e5ff; font-size: 11px;")
        info_layout.addWidget(self.lbl_battery)

        self.lbl_uptime = QLabel("UPTIME: Calculating...")
        self.lbl_uptime.setStyleSheet("color: #8e9aaf; font-size: 10px;")
        info_layout.addWidget(self.lbl_uptime)

        layout.addWidget(info_frame)
        layout.addStretch()

    def refresh_metrics(self) -> None:
        metrics: SystemMetrics = system_monitor.get_metrics()

        self.bar_cpu.setValue(int(metrics.cpu_percent))
        self.lbl_cpu.setText(f"CPU: {metrics.cpu_percent}%")

        self.bar_ram.setValue(int(metrics.ram_percent))
        self.lbl_ram.setText(f"RAM: {metrics.ram_percent}% ({metrics.ram_used_gb}/{metrics.ram_total_gb} GB)")

        self.bar_disk.setValue(int(metrics.disk_percent))
        self.lbl_disk.setText(f"DISK: {metrics.disk_percent}% ({metrics.disk_free_gb} GB free)")

        if metrics.battery_percent is not None:
            plug_str = " (Plugged In)" if metrics.battery_plugged else " (On Battery)"
            self.lbl_battery.setText(f"BATTERY: {metrics.battery_percent}%{plug_str}")
        else:
            self.lbl_battery.setText("POWER: AC / Desktop")

        self.lbl_uptime.setText(f"UPTIME: {metrics.uptime_hours} hrs | OS: {metrics.os_name}")
