"""Futuristic Theme and Stylesheet (QSS) for SOUNDARYA Desktop Assistant."""

from __future__ import annotations

# Color Palette Constants
COLOR_BG = "#0a0c14"
COLOR_PANEL_BG = "rgba(18, 22, 36, 0.90)"
COLOR_PANEL_SOLID = "#121624"
COLOR_CARD_BG = "#191f33"
COLOR_CYAN_PRIMARY = "#00e5ff"
COLOR_CYAN_GLOW = "rgba(0, 229, 255, 0.4)"
COLOR_VIOLET_ACCENT = "#9d4edd"
COLOR_VIOLET_GLOW = "rgba(157, 78, 221, 0.4)"
COLOR_TEXT_PRIMARY = "#f0f4fc"
COLOR_TEXT_MUTED = "#8e9aaf"
COLOR_SUCCESS = "#00f5d4"
COLOR_WARNING = "#ffb703"
COLOR_DANGER = "#ff0054"

STYLESHEET = f"""
QMainWindow {{
    background-color: {COLOR_BG};
}}

QWidget {{
    color: {COLOR_TEXT_PRIMARY};
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    font-size: 13px;
}}

/* Glassmorphic Cards and Panels */
QFrame.glass-panel {{
    background-color: {COLOR_PANEL_BG};
    border: 1px solid rgba(0, 229, 255, 0.25);
    border-radius: 12px;
}}

QFrame.card-panel {{
    background-color: {COLOR_CARD_BG};
    border: 1px solid rgba(157, 78, 221, 0.2);
    border-radius: 8px;
    padding: 10px;
}}

/* Status Badge */
QLabel#statusBadge {{
    background-color: rgba(0, 229, 255, 0.15);
    border: 1px solid {COLOR_CYAN_PRIMARY};
    border-radius: 6px;
    padding: 4px 12px;
    font-weight: bold;
    color: {COLOR_CYAN_PRIMARY};
    text-transform: uppercase;
    letter-spacing: 1px;
}}

/* Inputs */
QLineEdit {{
    background-color: {COLOR_CARD_BG};
    border: 1px solid rgba(0, 229, 255, 0.3);
    border-radius: 8px;
    padding: 10px 14px;
    color: {COLOR_TEXT_PRIMARY};
    font-size: 14px;
}}

QLineEdit:focus {{
    border: 1px solid {COLOR_CYAN_PRIMARY};
    background-color: #1c233a;
}}

/* Buttons */
QPushButton {{
    background-color: {COLOR_CARD_BG};
    border: 1px solid rgba(0, 229, 255, 0.4);
    border-radius: 8px;
    padding: 9px 16px;
    font-weight: 600;
    color: {COLOR_CYAN_PRIMARY};
}}

QPushButton:hover {{
    background-color: rgba(0, 229, 255, 0.15);
    border: 1px solid {COLOR_CYAN_PRIMARY};
}}

QPushButton:pressed {{
    background-color: rgba(0, 229, 255, 0.3);
}}

QPushButton.btn-primary {{
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00b4d8, stop:1 #9d4edd);
    border: none;
    color: #ffffff;
    font-weight: bold;
}}

QPushButton.btn-primary:hover {{
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00e5ff, stop:1 #b5179e);
}}

QPushButton.btn-mic {{
    background-color: rgba(0, 229, 255, 0.12);
    border: 1px solid {COLOR_CYAN_PRIMARY};
    border-radius: 22px;
    min-width: 44px;
    min-height: 44px;
    font-size: 18px;
}}

QPushButton.btn-mic:hover {{
    background-color: rgba(0, 229, 255, 0.3);
}}

/* ScrollBars */
QScrollBar:vertical {{
    background: {COLOR_BG};
    width: 6px;
    margin: 0px;
}}

QScrollBar::handle:vertical {{
    background: rgba(0, 229, 255, 0.3);
    border-radius: 3px;
    min-height: 20px;
}}

QScrollBar::handle:vertical:hover {{
    background: {COLOR_CYAN_PRIMARY};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

/* Progress Bars */
QProgressBar {{
    background-color: #141928;
    border: 1px solid rgba(0, 229, 255, 0.2);
    border-radius: 4px;
    text-align: center;
    color: #ffffff;
    font-size: 11px;
    font-weight: bold;
    height: 12px;
}}

QProgressBar::chunk {{
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {COLOR_CYAN_PRIMARY}, stop:1 {COLOR_VIOLET_ACCENT});
    border-radius: 3px;
}}

/* Tab Widget */
QTabWidget::pane {{
    border: 1px solid rgba(0, 229, 255, 0.2);
    border-radius: 8px;
    background-color: {COLOR_PANEL_BG};
}}

QTabBar::tab {{
    background-color: {COLOR_CARD_BG};
    border: 1px solid rgba(0, 229, 255, 0.15);
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    padding: 8px 16px;
    margin-right: 4px;
    color: {COLOR_TEXT_MUTED};
    font-weight: 600;
}}

QTabBar::tab:selected {{
    background-color: {COLOR_PANEL_SOLID};
    border: 1px solid {COLOR_CYAN_PRIMARY};
    border-bottom: 2px solid {COLOR_CYAN_PRIMARY};
    color: {COLOR_CYAN_PRIMARY};
}}
"""
