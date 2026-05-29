#!/usr/bin/env python3
"""
AXTEA CNC HMI  –  3-Axis CNC Human Machine Interface
Windows 11 · OSAI C07/C11 · 7 Languages
Corporate palette: #535DDC (blue) · #141E23 (navy) · #E3E6FF (light)
"""

import sys
import math
import time
import random
from datetime import datetime

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFrame, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QGridLayout, QStackedWidget, QSlider,
    QProgressBar, QDialog, QLineEdit, QComboBox, QScrollArea,
    QSizePolicy, QGraphicsDropShadowEffect, QCheckBox, QTextEdit,
    QSpacerItem, QToolButton, QButtonGroup,
)
from PyQt5.QtCore import (
    Qt, QTimer, QPropertyAnimation, QEasingCurve, QSize,
    pyqtSignal, QThread, QObject, QPoint, QRect,
)
from PyQt5.QtGui import (
    QColor, QFont, QPainter, QPen, QBrush, QLinearGradient,
    QPixmap, QPainterPath, QIcon, QFontDatabase, QPolygonF,
    QKeySequence, QPalette,
)
from PyQt5.QtChart import (
    QChart, QChartView, QLineSeries, QAreaSeries, QValueAxis,
    QBarSeries, QBarSet, QBarCategoryAxis,
)

# ── Local imports ──────────────────────────────────────────────────────────────
import os, sys
sys.path.insert(0, os.path.dirname(__file__))

from osai.client import OSAIClient, MachineState, MachineData
from i18n.translations import t, LANGUAGES

# ═══════════════════════════════════════════════════════════════════════════════
# THEME
# ═══════════════════════════════════════════════════════════════════════════════

C = {
    "bg":           "#0D1117",   # page background
    "surface":      "#141E23",   # card / panel background  (Axtea Navy)
    "surface2":     "#1A2730",   # slightly lighter surface
    "border":       "#232F38",   # subtle borders
    "primary":      "#535DDC",   # Axtea Blue
    "primary_dim":  "#3A44B0",
    "primary_light":"#E3E6FF",
    "accent":       "#00B581",   # green accent
    "warn":         "#F5A623",   # amber
    "error":        "#E84040",   # red
    "text":         "#FFFFFF",
    "text_dim":     "#8899AA",
    "text_muted":   "#4A5A6A",
    "wood":         "#D8AD7D",   # Axtea warm
}

STYLESHEET = f"""
QMainWindow, QWidget#root {{
    background: {C['bg']};
}}
QWidget {{
    color: {C['text']};
    font-family: 'Segoe UI', sans-serif;
    font-size: 13px;
}}
QLabel {{
    background: transparent;
}}
QPushButton {{
    background: {C['surface2']};
    color: {C['text']};
    border: 1px solid {C['border']};
    border-radius: 8px;
    padding: 8px 16px;
    font-size: 13px;
}}
QPushButton:hover {{
    background: {C['primary_dim']};
    border-color: {C['primary']};
}}
QPushButton:pressed {{
    background: {C['primary']};
}}
QPushButton#primary {{
    background: {C['primary']};
    border: none;
    font-weight: bold;
}}
QPushButton#primary:hover {{
    background: {C['primary_dim']};
}}
QPushButton#success {{
    background: {C['accent']};
    border: none;
    font-weight: bold;
}}
QPushButton#danger {{
    background: {C['error']};
    border: none;
    font-weight: bold;
}}
QPushButton#warn {{
    background: {C['warn']};
    border: none;
    color: #111;
    font-weight: bold;
}}
QSlider::groove:horizontal {{
    height: 4px;
    background: {C['border']};
    border-radius: 2px;
}}
QSlider::sub-page:horizontal {{
    background: {C['primary']};
    border-radius: 2px;
}}
QSlider::handle:horizontal {{
    width: 16px;
    height: 16px;
    margin: -6px 0;
    background: {C['primary']};
    border-radius: 8px;
    border: 2px solid {C['text']};
}}
QScrollBar:vertical {{
    background: {C['surface']};
    width: 6px;
}}
QScrollBar::handle:vertical {{
    background: {C['border']};
    border-radius: 3px;
}}
QLineEdit {{
    background: {C['surface2']};
    border: 1px solid {C['border']};
    border-radius: 6px;
    padding: 6px 10px;
    color: {C['text']};
}}
QLineEdit:focus {{
    border-color: {C['primary']};
}}
QComboBox {{
    background: {C['surface2']};
    border: 1px solid {C['border']};
    border-radius: 6px;
    padding: 6px 10px;
    color: {C['text']};
}}
QComboBox::drop-down {{
    border: none;
    width: 24px;
}}
QComboBox QAbstractItemView {{
    background: {C['surface']};
    selection-background-color: {C['primary']};
    border: 1px solid {C['border']};
}}
QProgressBar {{
    background: {C['surface2']};
    border: none;
    border-radius: 4px;
    height: 8px;
    text-align: center;
}}
QProgressBar::chunk {{
    background: {C['primary']};
    border-radius: 4px;
}}
QChartView {{
    background: transparent;
}}
"""


def shadow(widget, blur=20, color="#535DDC", alpha=60):
    fx = QGraphicsDropShadowEffect()
    fx.setBlurRadius(blur)
    fx.setOffset(0, 4)
    fx.setColor(QColor(color))
    fx.color().setAlpha(alpha)
    widget.setGraphicsEffect(fx)
    return widget


# ═══════════════════════════════════════════════════════════════════════════════
# CUSTOM WIDGETS
# ═══════════════════════════════════════════════════════════════════════════════

class Card(QFrame):
    def __init__(self, parent=None, radius=12):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background: {C['surface']};
                border: 1px solid {C['border']};
                border-radius: {radius}px;
            }}
        """)

    def set_layout(self, layout):
        layout.setContentsMargins(16, 14, 16, 14)
        self.setLayout(layout)


class NavButton(QPushButton):
    def __init__(self, icon_char, label, parent=None):
        super().__init__(parent)
        self._icon_char = icon_char
        self._label     = label
        self._active    = False
        self.setCheckable(True)
        self.setFixedHeight(62)
        self.setMinimumWidth(90)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("border:none; background:transparent;")

    def setLabel(self, text):
        self._label = text
        self.update()

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        if self.isChecked():
            p.fillRect(0, h - 3, w, 3, QColor(C['primary']))
            text_col = QColor(C['primary'])
        else:
            text_col = QColor(C['text_dim'])
        if self.underMouse():
            p.fillRect(0, 0, w, h, QColor(255, 255, 255, 8))

        p.setPen(text_col)
        f = QFont("Segoe UI", 18)
        p.setFont(f)
        p.drawText(QRect(0, 6, w, 24), Qt.AlignHCenter, self._icon_char)
        f2 = QFont("Segoe UI", 9)
        p.setFont(f2)
        p.drawText(QRect(0, 30, w, 20), Qt.AlignHCenter, self._label)


class AxisDisplay(Card):
    def __init__(self, axis: str, color: str = C['primary'], parent=None):
        super().__init__(parent)
        self.axis  = axis
        self.color = color
        self._machine = 0.0
        self._work    = 0.0
        self._build()

    def _build(self):
        vl = QVBoxLayout()
        vl.setContentsMargins(14, 10, 14, 10)
        vl.setSpacing(4)

        # Axis label
        lbl = QLabel(self.axis)
        lbl.setStyleSheet(f"color:{self.color}; font-size:22px; font-weight:900;")
        vl.addWidget(lbl)

        # Machine position
        self._mach_val = QLabel("0.000")
        self._mach_val.setStyleSheet(f"color:{C['text']}; font-size:28px; font-weight:700; font-family:'Consolas';")
        self._mach_unit = QLabel("mm")
        self._mach_unit.setStyleSheet(f"color:{C['text_dim']}; font-size:11px;")
        hl = QHBoxLayout()
        hl.addWidget(self._mach_val)
        hl.addWidget(self._mach_unit)
        hl.addStretch()
        vl.addLayout(hl)

        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background:{C['border']};")
        vl.addWidget(sep)

        # Work position
        self._work_val = QLabel("0.000")
        self._work_val.setStyleSheet(f"color:{C['text_dim']}; font-size:16px; font-family:'Consolas';")
        vl.addWidget(self._work_val)

        self.setLayout(vl)

    def update_values(self, machine: float, work: float):
        self._machine = machine
        self._work    = work
        self._mach_val.setText(f"{machine:+.3f}")
        self._work_val.setText(f"W {work:+.3f}")


class LoadBar(QWidget):
    def __init__(self, label: str, color: str = C['primary'], parent=None):
        super().__init__(parent)
        self._label = label
        self._color = color
        self._value = 0
        self.setFixedHeight(38)

    def setValue(self, v: float):
        self._value = max(0, min(100, v))
        self.update()

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()

        # Label
        p.setPen(QColor(C['text_dim']))
        f = QFont("Segoe UI", 9)
        p.setFont(f)
        p.drawText(0, 0, 28, h, Qt.AlignVCenter | Qt.AlignLeft, self._label)

        # Track
        bar_x = 32
        bar_w = w - bar_x - 44
        bar_h = 8
        bar_y = (h - bar_h) // 2
        p.setBrush(QColor(C['border']))
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(bar_x, bar_y, bar_w, bar_h, 4, 4)

        # Fill – colour changes: green→amber→red
        if self._value < 60:
            col = QColor(C['accent'])
        elif self._value < 85:
            col = QColor(C['warn'])
        else:
            col = QColor(C['error'])
        fill_w = int(bar_w * self._value / 100)
        if fill_w:
            p.setBrush(col)
            p.drawRoundedRect(bar_x, bar_y, fill_w, bar_h, 4, 4)

        # Value
        p.setPen(QColor(C['text']))
        f2 = QFont("Consolas", 10)
        p.setFont(f2)
        p.drawText(w - 42, 0, 42, h, Qt.AlignVCenter | Qt.AlignRight,
                   f"{self._value:.0f}%")


class SpeedGauge(QWidget):
    def __init__(self, label: str, max_val: float, unit: str, color: str = C['primary'], parent=None):
        super().__init__(parent)
        self._label   = label
        self._max_val = max_val
        self._unit    = unit
        self._color   = color
        self._value   = 0.0
        self.setFixedSize(120, 120)

    def setValue(self, v: float):
        self._value = max(0, min(self._max_val, v))
        self.update()

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        cx, cy = w // 2, h // 2
        R = min(w, h) // 2 - 8

        # Arc background
        p.setPen(QPen(QColor(C['border']), 6, Qt.SolidLine, Qt.RoundCap))
        p.drawArc(cx - R, cy - R, 2*R, 2*R, 225*16, -270*16)

        # Arc value
        pct = self._value / self._max_val if self._max_val else 0
        span = int(-270 * 16 * pct)
        p.setPen(QPen(QColor(self._color), 6, Qt.SolidLine, Qt.RoundCap))
        p.drawArc(cx - R, cy - R, 2*R, 2*R, 225*16, span)

        # Value text
        p.setPen(QColor(C['text']))
        f = QFont("Consolas", 13, QFont.Bold)
        p.setFont(f)
        val_str = f"{int(self._value)}"
        p.drawText(0, cy - 18, w, 22, Qt.AlignHCenter, val_str)

        # Unit
        f2 = QFont("Segoe UI", 8)
        p.setFont(f2)
        p.setPen(QColor(C['text_dim']))
        p.drawText(0, cy + 4, w, 16, Qt.AlignHCenter, self._unit)

        # Label
        p.drawText(0, cy + 20, w, 16, Qt.AlignHCenter, self._label)


class MiniChart(QWidget):
    """Sparkline chart for energy/feed history."""
    def __init__(self, color: str = C['primary'], parent=None):
        super().__init__(parent)
        self._color  = color
        self._data: list[float] = [0.0] * 60
        self.setMinimumHeight(60)

    def push(self, value: float):
        self._data.append(value)
        if len(self._data) > 60:
            self._data.pop(0)
        self.update()

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        if not self._data or max(self._data) == 0:
            return
        mx = max(self._data) or 1
        pts = []
        n = len(self._data)
        for i, v in enumerate(self._data):
            x = int(i * (w - 1) / (n - 1)) if n > 1 else 0
            y = int(h - v / mx * (h - 4) - 2)
            pts.append(QPoint(x, y))

        path = QPainterPath()
        path.moveTo(pts[0])
        for pt in pts[1:]:
            path.lineTo(pt)

        # Fill
        fill = QPainterPath(path)
        fill.lineTo(w, h)
        fill.lineTo(0, h)
        fill.closeSubpath()
        grad = QLinearGradient(0, 0, 0, h)
        c = QColor(self._color)
        c.setAlpha(120)
        grad.setColorAt(0, c)
        c2 = QColor(self._color)
        c2.setAlpha(0)
        grad.setColorAt(1, c2)
        p.fillPath(fill, QBrush(grad))

        # Line
        p.setPen(QPen(QColor(self._color), 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        p.drawPath(path)


class NoteCard(Card):
    deleteRequested = pyqtSignal(object)

    def __init__(self, text: str, author: str, ts: str, color: str = C['primary'], parent=None):
        super().__init__(parent)
        self.setStyleSheet(self.styleSheet() + f"QFrame {{ border-left: 3px solid {color}; }}")
        vl = QVBoxLayout()
        vl.setContentsMargins(12, 10, 12, 10)
        vl.setSpacing(4)

        hdr = QHBoxLayout()
        ts_lbl = QLabel(ts)
        ts_lbl.setStyleSheet(f"color:{C['text_muted']}; font-size:10px;")
        hdr.addWidget(ts_lbl)
        hdr.addStretch()
        del_btn = QPushButton("✕")
        del_btn.setFixedSize(20, 20)
        del_btn.setStyleSheet("background:transparent; border:none; color:#4A5A6A; font-size:11px;")
        del_btn.clicked.connect(lambda: self.deleteRequested.emit(self))
        hdr.addWidget(del_btn)
        vl.addLayout(hdr)

        body = QLabel(text)
        body.setWordWrap(True)
        body.setStyleSheet(f"color:{C['text']}; font-size:12px;")
        vl.addWidget(body)

        auth = QLabel(author)
        auth.setStyleSheet(f"color:{C['text_dim']}; font-size:10px;")
        vl.addWidget(auth)

        self.setLayout(vl)


# ═══════════════════════════════════════════════════════════════════════════════
# SCREENS
# ═══════════════════════════════════════════════════════════════════════════════

class HomeScreen(QWidget):
    def __init__(self, client: OSAIClient, lang_fn, parent=None):
        super().__init__(parent)
        self._client  = client
        self._lang    = lang_fn
        self._notes   = []
        self._energy_hist: list[float] = [random.uniform(2, 5) for _ in range(40)]
        self._build()

    # ── Layout ────────────────────────────────────────────────────────────────
    def _build(self):
        root = QHBoxLayout(self)
        root.setSpacing(12)
        root.setContentsMargins(12, 12, 12, 12)

        # ── LEFT PANEL ────────────────────────────────────────────────────────
        left = QVBoxLayout()
        left.setSpacing(10)

        # Axis positions
        self._axis_x = AxisDisplay("X", "#535DDC")
        self._axis_y = AxisDisplay("Y", "#00B581")
        self._axis_z = AxisDisplay("Z", "#D8AD7D")
        for ax in (self._axis_x, self._axis_y, self._axis_z):
            left.addWidget(ax)

        # Load bars
        load_card = Card()
        load_vl   = QVBoxLayout()
        load_vl.setContentsMargins(14, 12, 14, 12)
        load_vl.setSpacing(6)
        self._load_lbl = QLabel("LOAD")
        self._load_lbl.setStyleSheet(f"color:{C['text_dim']}; font-size:10px; font-weight:600; letter-spacing:2px;")
        load_vl.addWidget(self._load_lbl)
        self._bar_x = LoadBar("X", C['primary'])
        self._bar_y = LoadBar("Y", C['accent'])
        self._bar_z = LoadBar("Z", C['wood'])
        self._bar_s = LoadBar("S", C['warn'])
        for b in (self._bar_x, self._bar_y, self._bar_z, self._bar_s):
            load_vl.addWidget(b)
        load_card.setLayout(load_vl)
        left.addWidget(load_card)

        # Gauges (feed + spindle)
        gauge_card = Card()
        gauge_hl   = QHBoxLayout()
        gauge_hl.setContentsMargins(10, 8, 10, 8)
        self._gauge_feed    = SpeedGauge("FEED", 20000, "mm/min", C['primary'])
        self._gauge_spindle = SpeedGauge("SPINDLE", 24000, "RPM", C['wood'])
        gauge_hl.addWidget(self._gauge_feed)
        gauge_hl.addStretch()
        gauge_hl.addWidget(self._gauge_spindle)
        gauge_card.setLayout(gauge_hl)
        left.addWidget(gauge_card)

        left.addStretch()
        root.addLayout(left, 2)

        # ── CENTER PANEL ──────────────────────────────────────────────────────
        center = QVBoxLayout()
        center.setSpacing(10)

        # Notes header
        notes_hdr = QHBoxLayout()
        self._notes_lbl = QLabel()
        self._notes_lbl.setStyleSheet(f"color:{C['text']}; font-size:14px; font-weight:700;")
        notes_hdr.addWidget(self._notes_lbl)
        notes_hdr.addStretch()
        self._add_note_btn = QPushButton("＋")
        self._add_note_btn.setFixedSize(32, 32)
        self._add_note_btn.setObjectName("primary")
        self._add_note_btn.setStyleSheet(self._add_note_btn.styleSheet())
        self._add_note_btn.clicked.connect(self._add_note)
        notes_hdr.addWidget(self._add_note_btn)
        center.addLayout(notes_hdr)

        # Notes grid
        self._notes_area = QWidget()
        self._notes_grid = QGridLayout(self._notes_area)
        self._notes_grid.setSpacing(8)
        self._notes_grid.setContentsMargins(0, 0, 0, 0)
        center.addWidget(self._notes_area)

        # Seed two demo notes
        self._add_note_item("Grinder dressing scheduling", "Charlie – Operator Shift 2",
                            "10/01/25 15:06", C['primary'])
        self._add_note_item("Machine maintenance scheduled\n10/04/2025 – 09:00-12:00",
                            "John – Operator Shift 1", "10/01/25 15:10", C['warn'])

        # Monitoring cards
        self._mon_lbl = QLabel()
        self._mon_lbl.setStyleSheet(f"color:{C['text']}; font-size:14px; font-weight:700;")
        center.addWidget(self._mon_lbl)

        mon_grid = QGridLayout()
        mon_grid.setSpacing(8)
        self._mon_pieces   = self._mon_card("⬛", "0", "+0%", C['primary'])
        self._mon_errors   = self._mon_card("⚠", "0", "+0%", C['error'])
        self._mon_warnings = self._mon_card("△", "0", "0", C['warn'])
        self._mon_avail    = self._mon_card("◎", "0%", "+0%", C['accent'])
        mon_grid.addWidget(self._mon_pieces[0],   0, 0)
        mon_grid.addWidget(self._mon_errors[0],   0, 1)
        mon_grid.addWidget(self._mon_warnings[0], 0, 2)
        mon_grid.addWidget(self._mon_avail[0],    0, 3)
        center.addLayout(mon_grid)

        # Energy chart
        energy_card = Card()
        energy_vl   = QVBoxLayout()
        energy_vl.setContentsMargins(14, 12, 14, 12)
        self._energy_lbl = QLabel()
        self._energy_lbl.setStyleSheet(f"color:{C['text']}; font-size:13px; font-weight:700;")
        energy_vl.addWidget(self._energy_lbl)
        self._energy_chart = MiniChart(C['primary'])
        energy_vl.addWidget(self._energy_chart)
        energy_card.setLayout(energy_vl)
        center.addWidget(energy_card)

        center.addStretch()
        root.addLayout(center, 3)

        # ── RIGHT PANEL ───────────────────────────────────────────────────────
        right = QVBoxLayout()
        right.setSpacing(10)

        # Smart Links
        self._links_lbl = QLabel()
        self._links_lbl.setStyleSheet(f"color:{C['text']}; font-size:14px; font-weight:700;")
        right.addWidget(self._links_lbl)

        self._link_keys = [
            ("homing","⌖"), ("detections","◈"), ("manuals","📖"),
            ("issues","⚑"), ("task","✓"), ("worklist","☰"),
            ("functions","⚙"), ("machine_data","📊"),
        ]
        for key, icon in self._link_keys:
            btn = self._smart_link_btn(icon, key)
            right.addWidget(btn)

        right.addStretch()

        # Override sliders
        ovr_card = Card()
        ovr_vl   = QVBoxLayout()
        ovr_vl.setContentsMargins(14, 12, 14, 12)
        ovr_vl.setSpacing(12)

        self._ovr_title = QLabel("OVERRIDE")
        self._ovr_title.setStyleSheet(f"color:{C['text_dim']}; font-size:10px; font-weight:600; letter-spacing:2px;")
        ovr_vl.addWidget(self._ovr_title)

        # Feed override
        self._feed_ovr_lbl = QLabel()
        self._feed_ovr_lbl.setStyleSheet(f"color:{C['text_dim']}; font-size:10px;")
        ovr_vl.addWidget(self._feed_ovr_lbl)
        self._feed_ovr_val = QLabel("100 %")
        self._feed_ovr_val.setStyleSheet(f"color:{C['primary']}; font-size:14px; font-weight:700; font-family:'Consolas';")
        ovr_vl.addWidget(self._feed_ovr_val)
        self._feed_slider = QSlider(Qt.Horizontal)
        self._feed_slider.setRange(0, 200)
        self._feed_slider.setValue(100)
        self._feed_slider.valueChanged.connect(self._feed_ovr_changed)
        ovr_vl.addWidget(self._feed_slider)

        # Spindle override
        self._spn_ovr_lbl = QLabel()
        self._spn_ovr_lbl.setStyleSheet(f"color:{C['text_dim']}; font-size:10px;")
        ovr_vl.addWidget(self._spn_ovr_lbl)
        self._spn_ovr_val = QLabel("100 %")
        self._spn_ovr_val.setStyleSheet(f"color:{C['wood']}; font-size:14px; font-weight:700; font-family:'Consolas';")
        ovr_vl.addWidget(self._spn_ovr_val)
        self._spn_slider = QSlider(Qt.Horizontal)
        self._spn_slider.setRange(0, 200)
        self._spn_slider.setValue(100)
        self._spn_slider.valueChanged.connect(self._spn_ovr_changed)
        ovr_vl.addWidget(self._spn_slider)

        ovr_card.setLayout(ovr_vl)
        right.addWidget(ovr_card)

        # Tool card
        self._tool_card = Card()
        tool_vl = QVBoxLayout()
        tool_vl.setContentsMargins(14, 12, 14, 12)
        tool_vl.setSpacing(4)
        self._tool_lbl  = QLabel()
        self._tool_lbl.setStyleSheet(f"color:{C['text_dim']}; font-size:10px; font-weight:600; letter-spacing:2px;")
        tool_vl.addWidget(self._tool_lbl)
        self._tool_name = QLabel("TP1 700")
        self._tool_name.setStyleSheet(f"color:{C['text']}; font-size:16px; font-weight:700;")
        tool_vl.addWidget(self._tool_name)
        self._tool_card.setLayout(tool_vl)
        right.addWidget(self._tool_card)

        root.addLayout(right, 1)

    # ── Notes helpers ─────────────────────────────────────────────────────────
    def _add_note(self):
        dlg = NoteDialog(self._lang, self)
        if dlg.exec_() == QDialog.Accepted:
            text = dlg.text()
            ts   = datetime.now().strftime("%d/%m/%y %H:%M")
            self._add_note_item(text, "Operator", ts, C['primary'])

    def _add_note_item(self, text, author, ts, color):
        card = NoteCard(text, author, ts, color)
        card.deleteRequested.connect(self._remove_note)
        self._notes.append(card)
        self._relayout_notes()

    def _remove_note(self, card):
        self._notes.remove(card)
        card.deleteLater()
        self._relayout_notes()

    def _relayout_notes(self):
        while self._notes_grid.count():
            item = self._notes_grid.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
        for i, c in enumerate(self._notes[:4]):
            self._notes_grid.addWidget(c, i // 2, i % 2)

    # ── Smart link button ─────────────────────────────────────────────────────
    def _smart_link_btn(self, icon, key) -> QPushButton:
        btn = QPushButton()
        btn.setFixedHeight(36)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setProperty("link_key", key)
        btn.setProperty("link_icon", icon)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: {C['surface2']};
                border: 1px solid {C['border']};
                border-radius: 8px;
                text-align: left;
                padding-left: 12px;
                color: {C['text']};
            }}
            QPushButton:hover {{
                border-color: {C['primary']};
                color: {C['primary']};
            }}
        """)
        btn.setText(f"  {icon}   {self._lang(key)}")
        self._link_btns = getattr(self, "_link_btns", [])
        self._link_btns.append((btn, key, icon))
        return btn

    # ── Monitoring mini cards ─────────────────────────────────────────────────
    def _mon_card(self, icon, value, delta, color):
        card = Card()
        vl = QVBoxLayout()
        vl.setContentsMargins(12, 10, 12, 10)
        vl.setSpacing(2)
        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet(f"color:{C['text_dim']}; font-size:11px;")
        vl.addWidget(icon_lbl)
        val_lbl = QLabel(value)
        val_lbl.setStyleSheet(f"color:{C['text']}; font-size:24px; font-weight:700; font-family:'Consolas';")
        vl.addWidget(val_lbl)
        delta_lbl = QLabel(delta)
        delta_lbl.setStyleSheet(f"color:{color}; font-size:11px; font-weight:600;")
        vl.addWidget(delta_lbl)
        sub_lbl = QLabel()
        sub_lbl.setStyleSheet(f"color:{C['text_muted']}; font-size:9px;")
        vl.addWidget(sub_lbl)
        card.setLayout(vl)
        return card, val_lbl, delta_lbl, sub_lbl

    # ── Override handlers ─────────────────────────────────────────────────────
    def _feed_ovr_changed(self, v):
        self._feed_ovr_val.setText(f"{v} %")
        self._client.set_feed_override(v)

    def _spn_ovr_changed(self, v):
        self._spn_ovr_val.setText(f"{v} %")
        self._client.set_spindle_override(v)

    # ── Data update ───────────────────────────────────────────────────────────
    def on_data(self, d: MachineData):
        self._axis_x.update_values(d.machine_pos.x, d.work_pos.x)
        self._axis_y.update_values(d.machine_pos.y, d.work_pos.y)
        self._axis_z.update_values(d.machine_pos.z, d.work_pos.z)
        self._bar_x.setValue(d.load_x)
        self._bar_y.setValue(d.load_y)
        self._bar_z.setValue(d.load_z)
        self._bar_s.setValue(d.load_spindle)
        self._gauge_feed.setValue(d.feed_rate)
        self._gauge_spindle.setValue(d.spindle_speed)
        self._energy_chart.push(d.power_kw)
        # monitoring
        self._mon_pieces[1].setText(str(d.pieces_today))
        self._mon_errors[1].setText(str(len(d.alarms)))
        # sync overrides (external changes)
        if self._feed_slider.value() != d.feed_override:
            self._feed_slider.blockSignals(True)
            self._feed_slider.setValue(d.feed_override)
            self._feed_slider.blockSignals(False)
            self._feed_ovr_val.setText(f"{d.feed_override} %")

    def retranslate(self, lang: str):
        self._notes_lbl.setText(t("notes", lang).upper())
        self._mon_lbl.setText(t("monitoring", lang).upper())
        self._links_lbl.setText(t("smart_links", lang).upper())
        self._energy_lbl.setText(t("energy_management", lang).upper())
        self._feed_ovr_lbl.setText(t("feed_override", lang).upper())
        self._spn_ovr_lbl.setText(t("spindle_override", lang).upper())
        self._tool_lbl.setText(t("tool", lang).upper())
        self._mon_pieces[3].setText(t("last_24h", lang))
        self._mon_errors[3].setText(t("last_24h", lang))
        self._mon_warnings[3].setText(t("last_24h", lang))
        self._mon_avail[3].setText(t("last_24h", lang))
        # smart link labels
        for btn, key, icon in getattr(self, "_link_btns", []):
            btn.setText(f"  {icon}   {t(key, lang)}")


class WorkScreen(QWidget):
    def __init__(self, client: OSAIClient, lang_fn, parent=None):
        super().__init__(parent)
        self._client = client
        self._lang   = lang_fn
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setSpacing(12)
        root.setContentsMargins(16, 16, 16, 16)

        # Program info card
        prog_card = Card()
        prog_vl   = QVBoxLayout()
        prog_vl.setContentsMargins(16, 14, 16, 14)
        prog_vl.setSpacing(8)
        self._prog_name_lbl = QLabel("—")
        self._prog_name_lbl.setStyleSheet(f"color:{C['text']}; font-size:20px; font-weight:700;")
        prog_vl.addWidget(self._prog_name_lbl)
        self._prog_bar = QProgressBar()
        self._prog_bar.setRange(0, 100)
        self._prog_bar.setValue(0)
        self._prog_bar.setFixedHeight(10)
        prog_vl.addWidget(self._prog_bar)
        self._prog_line_lbl = QLabel("Line 0 / 0")
        self._prog_line_lbl.setStyleSheet(f"color:{C['text_dim']}; font-size:11px;")
        prog_vl.addWidget(self._prog_line_lbl)
        prog_card.setLayout(prog_vl)
        root.addWidget(prog_card)

        # Control buttons
        btn_hl = QHBoxLayout()
        btn_hl.setSpacing(10)
        self._btn_start = QPushButton("▶  START")
        self._btn_start.setObjectName("success")
        self._btn_start.setFixedHeight(52)
        self._btn_start.clicked.connect(self._client.program_start)

        self._btn_pause = QPushButton("⏸  PAUSE")
        self._btn_pause.setObjectName("warn")
        self._btn_pause.setFixedHeight(52)
        self._btn_pause.clicked.connect(self._client.program_pause)

        self._btn_stop = QPushButton("⏹  STOP")
        self._btn_stop.setObjectName("danger")
        self._btn_stop.setFixedHeight(52)
        self._btn_stop.clicked.connect(self._client.program_stop)

        self._btn_reset = QPushButton("↺  RESET")
        self._btn_reset.setFixedHeight(52)
        self._btn_reset.clicked.connect(self._client.program_reset)

        self._btn_home = QPushButton("⌖  HOMING")
        self._btn_home.setObjectName("primary")
        self._btn_home.setFixedHeight(52)
        self._btn_home.clicked.connect(self._client.homing)

        for b in (self._btn_start, self._btn_pause, self._btn_stop, self._btn_reset, self._btn_home):
            b.setFont(QFont("Segoe UI", 12, QFont.Bold))
            btn_hl.addWidget(b)
        root.addLayout(btn_hl)

        # Status + axis side by side
        lower = QHBoxLayout()
        lower.setSpacing(12)

        # State card
        state_card = Card()
        state_vl   = QVBoxLayout()
        state_vl.setContentsMargins(16, 14, 16, 14)
        self._state_lbl = QLabel("IDLE")
        self._state_lbl.setAlignment(Qt.AlignCenter)
        self._state_lbl.setStyleSheet(f"color:{C['accent']}; font-size:36px; font-weight:900; letter-spacing:4px;")
        state_vl.addWidget(self._state_lbl)
        self._tool_info = QLabel("Tool: —    Feed: — mm/min    Spindle: — RPM")
        self._tool_info.setAlignment(Qt.AlignCenter)
        self._tool_info.setStyleSheet(f"color:{C['text_dim']}; font-size:12px;")
        state_vl.addWidget(self._tool_info)
        state_card.setLayout(state_vl)
        lower.addWidget(state_card, 2)

        # Axis compact
        ax_card = Card()
        ax_vl   = QVBoxLayout()
        ax_vl.setContentsMargins(16, 14, 16, 14)
        ax_vl.setSpacing(4)
        self._ax_labels = {}
        for ax, col in [("X", C['primary']), ("Y", C['accent']), ("Z", C['wood'])]:
            hl = QHBoxLayout()
            albl = QLabel(ax)
            albl.setStyleSheet(f"color:{col}; font-size:16px; font-weight:700; min-width:20px;")
            hl.addWidget(albl)
            vlbl = QLabel("0.000")
            vlbl.setStyleSheet(f"color:{C['text']}; font-size:20px; font-family:'Consolas'; font-weight:600;")
            hl.addWidget(vlbl)
            hl.addStretch()
            mm = QLabel("mm")
            mm.setStyleSheet(f"color:{C['text_dim']}; font-size:11px;")
            hl.addWidget(mm)
            ax_vl.addLayout(hl)
            self._ax_labels[ax] = vlbl
        ax_card.setLayout(ax_vl)
        lower.addWidget(ax_card, 1)

        root.addLayout(lower)
        root.addStretch()

    def on_data(self, d: MachineData):
        # Program bar
        if d.program_total:
            pct = int(d.program_line * 100 / d.program_total)
            self._prog_bar.setValue(pct)
            self._prog_line_lbl.setText(f"Line {d.program_line} / {d.program_total}")
        self._prog_name_lbl.setText(d.program_name or "—")

        # State
        state_colors = {
            MachineState.IDLE:         C['text_dim'],
            MachineState.RUNNING:      C['accent'],
            MachineState.PAUSED:       C['warn'],
            MachineState.ALARM:        C['error'],
            MachineState.HOMING:       C['primary'],
            MachineState.DISCONNECTED: C['error'],
        }
        col = state_colors.get(d.state, C['text'])
        self._state_lbl.setText(d.state.value)
        self._state_lbl.setStyleSheet(f"color:{col}; font-size:36px; font-weight:900; letter-spacing:4px;")
        self._tool_info.setText(
            f"Tool: T{d.tool_number}    Feed: {d.feed_rate:.0f} mm/min    Spindle: {d.spindle_speed:.0f} RPM"
        )
        self._ax_labels["X"].setText(f"{d.machine_pos.x:+.3f}")
        self._ax_labels["Y"].setText(f"{d.machine_pos.y:+.3f}")
        self._ax_labels["Z"].setText(f"{d.machine_pos.z:+.3f}")

    def retranslate(self, lang: str):
        self._btn_start.setText(f"▶  {t('program_start', lang)}")
        self._btn_pause.setText(f"⏸  {t('program_pause', lang)}")
        self._btn_stop.setText(f"⏹  {t('program_stop', lang)}")
        self._btn_reset.setText(f"↺  {t('program_reset', lang)}")
        self._btn_home.setText(f"⌖  {t('homing', lang)}")


class InspectScreen(QWidget):
    def __init__(self, client: OSAIClient, lang_fn, parent=None):
        super().__init__(parent)
        self._client = client
        self._lang   = lang_fn
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setSpacing(12)
        root.setContentsMargins(16, 16, 16, 16)

        self._alarm_title = QLabel()
        self._alarm_title.setStyleSheet(f"color:{C['text']}; font-size:16px; font-weight:700;")
        root.addWidget(self._alarm_title)

        alarm_scroll = QScrollArea()
        alarm_scroll.setWidgetResizable(True)
        alarm_scroll.setStyleSheet("QScrollArea{background:transparent; border:none;}")
        self._alarm_inner = QWidget()
        self._alarm_vl    = QVBoxLayout(self._alarm_inner)
        self._alarm_vl.setSpacing(6)
        self._alarm_vl.setAlignment(Qt.AlignTop)
        alarm_scroll.setWidget(self._alarm_inner)
        root.addWidget(alarm_scroll)

        self._no_alarm_lbl = QLabel()
        self._no_alarm_lbl.setAlignment(Qt.AlignCenter)
        self._no_alarm_lbl.setStyleSheet(f"color:{C['text_muted']}; font-size:14px;")
        self._alarm_vl.addWidget(self._no_alarm_lbl)

        root.addStretch()

    def on_data(self, d: MachineData):
        while self._alarm_vl.count():
            item = self._alarm_vl.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        if not d.alarms:
            self._no_alarm_lbl = QLabel(self._lang("no_alarms"))
            self._no_alarm_lbl.setAlignment(Qt.AlignCenter)
            self._no_alarm_lbl.setStyleSheet(f"color:{C['accent']}; font-size:14px;")
            self._alarm_vl.addWidget(self._no_alarm_lbl)
        else:
            for alarm in d.alarms:
                lbl = QLabel(f"⚠  {alarm}")
                lbl.setStyleSheet(f"color:{C['error']}; font-size:13px; background:{C['surface']}; "
                                  f"border:1px solid {C['error']}; border-radius:6px; padding:8px 12px;")
                self._alarm_vl.addWidget(lbl)

    def retranslate(self, lang: str):
        self._alarm_title.setText(t("alarm_title", lang))


class AnalyzeScreen(QWidget):
    def __init__(self, client: OSAIClient, lang_fn, parent=None):
        super().__init__(parent)
        self._client  = client
        self._lang    = lang_fn
        self._pieces  = [random.randint(20, 45) for _ in range(8)]
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setSpacing(12)
        root.setContentsMargins(16, 16, 16, 16)

        # KPI row
        kpi_hl = QHBoxLayout()
        kpi_hl.setSpacing(10)
        self._kpi_cards = {}
        for key, val, color in [
            ("pieces_produced", "247", C['primary']),
            ("errors", "3", C['error']),
            ("availability", "96.4%", C['accent']),
            ("power_kw", "3.8 kW", C['wood']),
        ]:
            c = Card()
            vl = QVBoxLayout()
            vl.setContentsMargins(14, 12, 14, 12)
            lbl = QLabel()
            lbl.setStyleSheet(f"color:{C['text_dim']}; font-size:10px; font-weight:600; letter-spacing:1px;")
            vl.addWidget(lbl)
            val_lbl = QLabel(val)
            val_lbl.setStyleSheet(f"color:{color}; font-size:28px; font-weight:800; font-family:'Consolas';")
            vl.addWidget(val_lbl)
            c.setLayout(vl)
            kpi_hl.addWidget(c)
            self._kpi_cards[key] = (lbl, val_lbl)
        root.addLayout(kpi_hl)

        # Bar chart using PyQt5 Charts
        self._bar_set  = QBarSet("Pieces")
        self._bar_set.setColor(QColor(C['primary']))
        for v in self._pieces:
            self._bar_set.append(v)

        bar_series = QBarSeries()
        bar_series.append(self._bar_set)

        chart = QChart()
        chart.addSeries(bar_series)
        chart.setBackgroundBrush(QBrush(QColor(C['surface'])))
        chart.setBackgroundRoundness(12)
        chart.legend().hide()
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.setPlotAreaBackgroundBrush(QBrush(QColor(C['surface2'])))
        chart.setPlotAreaBackgroundVisible(True)

        cats = QBarCategoryAxis()
        cats.append(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun", "Mon"])
        cats.setLabelsColor(QColor(C['text_dim']))
        chart.addAxis(cats, Qt.AlignBottom)
        bar_series.attachAxis(cats)

        val_axis = QValueAxis()
        val_axis.setRange(0, 60)
        val_axis.setLabelFormat("%d")
        val_axis.setLabelsColor(QColor(C['text_dim']))
        val_axis.setGridLineColor(QColor(C['border']))
        chart.addAxis(val_axis, Qt.AlignLeft)
        bar_series.attachAxis(val_axis)

        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        chart_view.setStyleSheet("background:transparent;")
        root.addWidget(chart_view)

        root.addStretch()

    def on_data(self, d: MachineData):
        self._kpi_cards["pieces_produced"][1].setText(str(d.pieces_today))
        self._kpi_cards["errors"][1].setText(str(len(d.alarms)))

    def retranslate(self, lang: str):
        for key, (lbl, _) in self._kpi_cards.items():
            lbl.setText(t(key, lang).upper())


# ═══════════════════════════════════════════════════════════════════════════════
# CONNECTION DIALOG
# ═══════════════════════════════════════════════════════════════════════════════

class ConnDialog(QDialog):
    def __init__(self, lang: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("OSAI Connection")
        self.setFixedSize(380, 280)
        self.setStyleSheet(STYLESHEET + f"QDialog{{background:{C['surface']};border-radius:12px;}}")

        vl = QVBoxLayout(self)
        vl.setSpacing(14)
        vl.setContentsMargins(24, 24, 24, 24)

        title = QLabel(t("connection", lang))
        title.setStyleSheet(f"color:{C['text']}; font-size:18px; font-weight:700;")
        vl.addWidget(title)

        ip_lbl = QLabel(t("ip_address", lang))
        ip_lbl.setStyleSheet(f"color:{C['text_dim']}; font-size:11px;")
        vl.addWidget(ip_lbl)
        self._ip = QLineEdit("192.168.1.10")
        vl.addWidget(self._ip)

        port_lbl = QLabel(t("port", lang))
        port_lbl.setStyleSheet(f"color:{C['text_dim']}; font-size:11px;")
        vl.addWidget(port_lbl)
        self._port = QLineEdit("5050")
        vl.addWidget(self._port)

        self._sim_cb = QCheckBox(t("simulation", lang))
        self._sim_cb.setChecked(True)
        self._sim_cb.setStyleSheet(f"color:{C['text']};")
        vl.addWidget(self._sim_cb)

        btn_hl = QHBoxLayout()
        ok_btn = QPushButton(t("connect", lang))
        ok_btn.setObjectName("primary")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton(t("cancel", lang))
        cancel_btn.clicked.connect(self.reject)
        btn_hl.addWidget(cancel_btn)
        btn_hl.addWidget(ok_btn)
        vl.addLayout(btn_hl)

    @property
    def host(self): return self._ip.text().strip()
    @property
    def port(self): return int(self._port.text().strip() or "5050")
    @property
    def simulation(self): return self._sim_cb.isChecked()


class NoteDialog(QDialog):
    def __init__(self, lang_fn, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Note")
        self.setFixedSize(340, 200)
        self.setStyleSheet(STYLESHEET + f"QDialog{{background:{C['surface']};border-radius:12px;}}")
        vl = QVBoxLayout(self)
        vl.setSpacing(12)
        vl.setContentsMargins(20, 20, 20, 20)
        lbl = QLabel(lang_fn("add_note"))
        lbl.setStyleSheet(f"color:{C['text']}; font-size:15px; font-weight:700;")
        vl.addWidget(lbl)
        self._edit = QTextEdit()
        self._edit.setStyleSheet(f"background:{C['surface2']}; border:1px solid {C['border']}; border-radius:6px; color:{C['text']}; padding:6px;")
        vl.addWidget(self._edit)
        ok = QPushButton(lang_fn("ok"))
        ok.setObjectName("primary")
        ok.clicked.connect(self.accept)
        vl.addWidget(ok)

    def text(self): return self._edit.toPlainText().strip()


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN WINDOW
# ═══════════════════════════════════════════════════════════════════════════════

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._lang   = "EN"
        self._client = OSAIClient(simulation=True)
        self._client.start()

        self.setWindowTitle("AXTEA CNC HMI")
        self.setMinimumSize(1280, 800)
        self.showMaximized()

        central = QWidget()
        central.setObjectName("root")
        self.setCentralWidget(central)
        main_vl = QVBoxLayout(central)
        main_vl.setSpacing(0)
        main_vl.setContentsMargins(0, 0, 0, 0)

        # ── TOP BAR ───────────────────────────────────────────────────────────
        topbar = QWidget()
        topbar.setFixedHeight(62)
        topbar.setStyleSheet(f"background:{C['surface']}; border-bottom:1px solid {C['border']};")
        tb_hl = QHBoxLayout(topbar)
        tb_hl.setContentsMargins(16, 0, 16, 0)
        tb_hl.setSpacing(0)

        # Logo (ASCII representation of AXTEA symbol + name)
        logo_area = QWidget()
        logo_area.setFixedWidth(160)
        logo_hl = QHBoxLayout(logo_area)
        logo_hl.setContentsMargins(0, 0, 0, 0)
        sym_lbl = QLabel("✦")
        sym_lbl.setStyleSheet(f"color:{C['primary']}; font-size:22px; font-weight:900;")
        name_lbl = QLabel("AXTEA")
        name_lbl.setStyleSheet(f"color:{C['text']}; font-size:20px; font-weight:900; letter-spacing:3px;")
        logo_hl.addWidget(sym_lbl)
        logo_hl.addSpacing(6)
        logo_hl.addWidget(name_lbl)
        tb_hl.addWidget(logo_area)

        # Nav buttons
        nav_frame = QWidget()
        nav_hl    = QHBoxLayout(nav_frame)
        nav_hl.setContentsMargins(20, 0, 20, 0)
        nav_hl.setSpacing(4)

        self._nav_btns = {}
        self._screens  = QStackedWidget()
        nav_icons = [("nav_home","⌂",0), ("nav_design","◧",1),
                     ("nav_work","⚙",2),  ("nav_inspect","◉",3),
                     ("nav_analyze","◈",4)]
        for key, icon, idx in nav_icons:
            btn = NavButton(icon, t(key, self._lang))
            btn.setCheckable(True)
            btn.clicked.connect(lambda _, i=idx, b=btn: self._nav(i))
            nav_hl.addWidget(btn)
            self._nav_btns[idx] = (btn, key)
        tb_hl.addWidget(nav_frame)
        tb_hl.addStretch()

        # Status chip
        self._status_chip = QLabel("● DISCONNECTED")
        self._status_chip.setStyleSheet(f"color:{C['error']}; font-size:11px; font-weight:600;")
        tb_hl.addWidget(self._status_chip)
        tb_hl.addSpacing(16)

        # Language selector
        self._lang_combo = QComboBox()
        self._lang_combo.setFixedWidth(110)
        for code, name in LANGUAGES.items():
            self._lang_combo.addItem(name, code)
        self._lang_combo.currentIndexChanged.connect(self._lang_changed)
        tb_hl.addWidget(self._lang_combo)
        tb_hl.addSpacing(10)

        # Connection button
        self._conn_btn = QPushButton("⟳ Connect")
        self._conn_btn.setObjectName("primary")
        self._conn_btn.setFixedHeight(34)
        self._conn_btn.clicked.connect(self._open_conn_dialog)
        tb_hl.addWidget(self._conn_btn)
        tb_hl.addSpacing(8)

        # Alarm bell
        self._alarm_btn = QPushButton("🔔")
        self._alarm_btn.setFixedSize(34, 34)
        self._alarm_btn.setStyleSheet(f"background:transparent; border:none; font-size:16px; color:{C['text_dim']};")
        tb_hl.addWidget(self._alarm_btn)

        # Clock
        self._clock_lbl = QLabel()
        self._clock_lbl.setStyleSheet(f"color:{C['text_dim']}; font-size:12px; font-family:'Consolas'; min-width:75px;")
        tb_hl.addWidget(self._clock_lbl)

        main_vl.addWidget(topbar)

        # ── SCREENS ───────────────────────────────────────────────────────────
        self._home_screen    = HomeScreen(self._client, lambda k: t(k, self._lang))
        self._design_screen  = self._placeholder_screen("nav_design", "◧")
        self._work_screen    = WorkScreen(self._client, lambda k: t(k, self._lang))
        self._inspect_screen = InspectScreen(self._client, lambda k: t(k, self._lang))
        self._analyze_screen = AnalyzeScreen(self._client, lambda k: t(k, self._lang))

        for s in (self._home_screen, self._design_screen, self._work_screen,
                  self._inspect_screen, self._analyze_screen):
            self._screens.addWidget(s)
        main_vl.addWidget(self._screens)

        # ── STATUS BAR ────────────────────────────────────────────────────────
        status_bar = QWidget()
        status_bar.setFixedHeight(28)
        status_bar.setStyleSheet(f"background:{C['surface']}; border-top:1px solid {C['border']};")
        sb_hl = QHBoxLayout(status_bar)
        sb_hl.setContentsMargins(16, 0, 16, 0)
        self._sb_state  = QLabel("OSAI C07")
        self._sb_state.setStyleSheet(f"color:{C['text_dim']}; font-size:10px;")
        self._sb_pos    = QLabel("X: 0.000   Y: 0.000   Z: 0.000")
        self._sb_pos.setStyleSheet(f"color:{C['text_dim']}; font-size:10px; font-family:'Consolas';")
        self._sb_prog   = QLabel("")
        self._sb_prog.setStyleSheet(f"color:{C['primary']}; font-size:10px;")
        sb_hl.addWidget(self._sb_state)
        sb_hl.addStretch()
        sb_hl.addWidget(self._sb_pos)
        sb_hl.addStretch()
        sb_hl.addWidget(self._sb_prog)
        main_vl.addWidget(status_bar)

        # ── Timers ────────────────────────────────────────────────────────────
        self._clock_timer = QTimer(self)
        self._clock_timer.timeout.connect(self._tick_clock)
        self._clock_timer.start(1000)

        # Register data callback
        self._client.on_data_update(self._on_data)

        # Navigate to Home
        self._nav(0)

        # Auto-connect in simulation
        QTimer.singleShot(300, self._auto_connect)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _placeholder_screen(self, title_key: str, icon: str) -> QWidget:
        w = QWidget()
        vl = QVBoxLayout(w)
        vl.setAlignment(Qt.AlignCenter)
        lbl = QLabel(icon)
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet(f"color:{C['primary']}; font-size:64px;")
        vl.addWidget(lbl)
        txt = QLabel(t(title_key, self._lang))
        txt.setAlignment(Qt.AlignCenter)
        txt.setStyleSheet(f"color:{C['text_dim']}; font-size:18px; font-weight:600;")
        vl.addWidget(txt)
        sub = QLabel("Coming soon…")
        sub.setAlignment(Qt.AlignCenter)
        sub.setStyleSheet(f"color:{C['text_muted']}; font-size:13px;")
        vl.addWidget(sub)
        return w

    def _nav(self, idx: int):
        self._screens.setCurrentIndex(idx)
        for i, (btn, _) in self._nav_btns.items():
            btn.setChecked(i == idx)

    def _lang_changed(self, _):
        self._lang = self._lang_combo.currentData()
        self._retranslate()

    def _retranslate(self):
        for i, (btn, key) in self._nav_btns.items():
            btn.setLabel(t(key, self._lang))
            btn.update()
        self._home_screen.retranslate(self._lang)
        self._work_screen.retranslate(self._lang)
        self._inspect_screen.retranslate(self._lang)
        self._analyze_screen.retranslate(self._lang)
        self._update_conn_status(self._client.get_data().state)

    def _tick_clock(self):
        self._clock_lbl.setText(datetime.now().strftime("%H:%M:%S"))

    def _open_conn_dialog(self):
        dlg = ConnDialog(self._lang, self)
        if dlg.exec_() == QDialog.Accepted:
            self._client.stop()
            self._client = OSAIClient(host=dlg.host, port=dlg.port, simulation=dlg.simulation)
            self._client.on_data_update(self._on_data)
            self._client.start()
            ok = self._client.connect()
            if ok:
                self._update_conn_status(MachineState.IDLE)

    def _auto_connect(self):
        self._client.connect()

    def _on_data(self, d: MachineData):
        # This runs in a background thread – use QTimer to marshal to UI thread
        QTimer.singleShot(0, lambda: self._apply_data(d))

    def _apply_data(self, d: MachineData):
        self._home_screen.on_data(d)
        self._work_screen.on_data(d)
        self._inspect_screen.on_data(d)
        self._analyze_screen.on_data(d)
        self._update_conn_status(d.state)
        # Status bar
        self._sb_pos.setText(
            f"X: {d.machine_pos.x:+.3f}   Y: {d.machine_pos.y:+.3f}   Z: {d.machine_pos.z:+.3f}"
        )
        if d.program_name:
            pct = int(d.program_line * 100 / d.program_total) if d.program_total else 0
            self._sb_prog.setText(f"{d.program_name}  {pct}%")

    def _update_conn_status(self, state: MachineState):
        colors = {
            MachineState.DISCONNECTED: C['error'],
            MachineState.IDLE:         C['accent'],
            MachineState.RUNNING:      C['primary'],
            MachineState.PAUSED:       C['warn'],
            MachineState.ALARM:        C['error'],
            MachineState.HOMING:       C['primary'],
        }
        col = colors.get(state, C['text_dim'])
        label = t(state.value.lower() if state.value.lower() in ["idle","running","paused","alarm"] else "connected", self._lang)
        if state == MachineState.DISCONNECTED:
            label = t("disconnected", self._lang)
        self._status_chip.setText(f"● {label.upper()}")
        self._status_chip.setStyleSheet(f"color:{col}; font-size:11px; font-weight:600;")

    def closeEvent(self, e):
        self._client.stop()
        super().closeEvent(e)


# ═══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(STYLESHEET)
    app.setApplicationName("AXTEA CNC HMI")
    app.setOrganizationName("AXTEA")

    # High-DPI support (Windows 11)
    if hasattr(Qt, "AA_EnableHighDpiScaling"):
        app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, "AA_UseHighDpiPixmaps"):
        app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    win = MainWindow()
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
