# styles.py — 统一样式配置，gui.py 中直接导入使用

from PyQt5.QtGui import QFont, QColor
from PyQt5.QtWidgets import QGraphicsDropShadowEffect

# ── 颜色常量 ──────────────────────────────────────────────────────
BG          = "#F0F4F8"
CARD_BG     = "#FFFFFF"
BORDER      = "#D9E2EC"
ACCENT      = "#2563EB"
ACCENT_DARK = "#1D4ED8"
ACCENT_LITE = "#EFF6FF"
TEXT_MAIN   = "#1E293B"
TEXT_SUB    = "#64748B"
INPUT_BG    = "#F8FAFC"
SUCCESS     = "#059669"
WARN        = "#D97706"
HEADER_BG   = "#1E40AF"

# ── 字体常量 ──────────────────────────────────────────────────────
FONT_BODY  = QFont("Microsoft YaHei UI", 14)
FONT_BOLD  = QFont("Microsoft YaHei UI", 14, QFont.Bold)
FONT_TITLE = QFont("Microsoft YaHei UI", 20, QFont.Bold)
FONT_SUB   = QFont("Microsoft YaHei UI", 12)
FONT_MONO  = QFont("Consolas", 14)

# ── 组件样式 ──────────────────────────────────────────────────────
CARD_STYLE = f"""
    QFrame {{
        background-color: {CARD_BG};
        border-radius: 14px;
        border: 1px solid {BORDER};
    }}
"""

COMBO_STYLE = f"""
    QComboBox {{
        background: {INPUT_BG};
        color: {TEXT_MAIN};
        border: 1.5px solid {BORDER};
        border-radius: 8px;
        padding: 0 14px;
        font-size: 15px;
    }}
    QComboBox:hover {{ border-color: {ACCENT}; }}
    QComboBox:focus {{ border-color: {ACCENT}; background: #FFFFFF; }}
    QComboBox::drop-down {{ border: none; width: 32px; }}
    QComboBox::down-arrow {{
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 6px solid {TEXT_SUB};
        width: 0; height: 0; margin-right: 10px;
    }}
    QComboBox QAbstractItemView {{
        background: {CARD_BG};
        border: 1px solid {BORDER};
        border-radius: 8px;
        color: {TEXT_MAIN};
        selection-background-color: {ACCENT_LITE};
        selection-color: {ACCENT};
        padding: 4px;
        font-size: 15px;
    }}
"""

INPUT_STYLE = f"""
    QLineEdit {{
        background: {INPUT_BG};
        color: {TEXT_MAIN};
        border: 1.5px solid {BORDER};
        border-radius: 8px;
        padding: 0 12px;
        font-size: 15px;
    }}
    QLineEdit:hover {{ border-color: {ACCENT}; }}
    QLineEdit:focus {{ border-color: {ACCENT}; background: #FFFFFF; }}
"""

BUTTON_STYLE = f"""
    QPushButton {{
        background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
            stop:0 {ACCENT}, stop:1 #3B82F6);
        color: white;
        border: none;
        border-radius: 10px;
        font-size: 16px;
        font-weight: bold;
        letter-spacing: 1px;
    }}
    QPushButton:hover {{
        background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
            stop:0 {ACCENT_DARK}, stop:1 {ACCENT});
    }}
    QPushButton:pressed {{
        background: {ACCENT_DARK};
        padding-top: 3px;
    }}
    QPushButton:disabled {{
        background: #CBD5E1;
        color: #94A3B8;
    }}
"""

RESULT_STYLE = f"""
    QTextEdit {{
        background: {INPUT_BG};
        color: {TEXT_MAIN};
        border: 1.5px solid {BORDER};
        border-radius: 8px;
        padding: 14px;
        font-size: 15px;
    }}
"""

SCROLL_STYLE = f"""
    QScrollArea {{ border: none; background: transparent; }}
    QScrollBar:vertical {{ background: {BG}; width: 7px; border-radius: 4px; }}
    QScrollBar::handle:vertical {{ background: {BORDER}; border-radius: 4px; }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
"""

HEADER_STYLE = f"""
    background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
        stop:0 {HEADER_BG}, stop:1 #3B82F6);
    border-radius: 16px;
"""

DIVIDER_STYLE = f"background: {BORDER}; max-height: 1px; border: none;"

# ── Badge 状态样式 ────────────────────────────────────────────────
_BADGE_BASE = "border-radius: 10px; padding: 3px 12px; font-size: 13px; font-weight: bold;"
BADGE_READY   = _BADGE_BASE + f"background: {ACCENT_LITE}; color: {ACCENT};"
BADGE_RUNNING = _BADGE_BASE + f"background: #FEF3C7; color: {WARN};"
BADGE_DONE    = _BADGE_BASE + f"background: #ECFDF5; color: {SUCCESS};"

# ── 工具函数 ──────────────────────────────────────────────────────
def add_shadow(widget, r=18, c="#B0BEC5", dy=3):
    e = QGraphicsDropShadowEffect()
    e.setBlurRadius(r)
    e.setColor(QColor(c))
    e.setOffset(0, dy)
    widget.setGraphicsEffect(e)