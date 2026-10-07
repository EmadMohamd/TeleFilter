"""Reusable input widgets: toggle switch, segmented control, chip input, results table."""
import re

from PySide6.QtCore import QEvent, QRectF, QSize, Qt, Signal
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import (
    QAbstractButton, QButtonGroup, QFrame, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QSizePolicy, QTableWidget, QToolButton,
)

from .helpers import set_prop
from .theme import T


class ToggleSwitch(QAbstractButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(36, 20)

    def paintEvent(self, _event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        on = self.isChecked()
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(T["accent"] if on else "#2a3550"))
        p.drawRoundedRect(QRectF(0, 0, 36, 20), 10, 10)
        p.setBrush(QColor("#ffffff" if on else "#aab4cc"))
        p.drawEllipse(QRectF(18 if on else 2, 2, 16, 16))


class Segmented(QFrame):
    selected = Signal(str)

    def __init__(self, options, parent=None):
        super().__init__(parent)
        self.setObjectName("seg")
        lay = QHBoxLayout(self)
        lay.setContentsMargins(3, 3, 3, 3)
        lay.setSpacing(2)
        self.group = QButtonGroup(self)
        self.group.setExclusive(True)
        self.buttons = {}
        for name in options:
            b = QPushButton(name)
            b.setObjectName("segbtn")
            b.setCheckable(True)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            self.group.addButton(b)
            lay.addWidget(b)
            self.buttons[name] = b
            b.clicked.connect(lambda _checked=False, n=name: self.selected.emit(n))

    def set(self, name):
        self.buttons[name].setChecked(True)


class ChipInput(QFrame):
    """Keyword entry that turns comma / Enter separated words into chips.
    text() returns the same comma separated string a plain Entry would."""

    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setObjectName("chipbox")
        self.setMinimumHeight(48)
        self._placeholder = placeholder
        self._chips = []  # list of (text, frame)
        self._lay = QHBoxLayout(self)
        self._lay.setContentsMargins(8, 4, 8, 4)
        self._lay.setSpacing(6)
        self.edit = QLineEdit()
        self.edit.setPlaceholderText(placeholder)
        self.edit.installEventFilter(self)
        self.edit.textEdited.connect(self._on_text)
        self.edit.returnPressed.connect(self._commit)
        self._lay.addWidget(self.edit, 1)

    def minimumSizeHint(self):
        return QSize(120, 48)

    def _on_text(self, t):
        self.set_invalid(False)
        if "," in t or "،" in t:
            for part in re.split("[,،]", t):
                self._add_chip(part)
            self.edit.clear()

    def _commit(self):
        self._add_chip(self.edit.text())
        self.edit.clear()

    def _add_chip(self, text):
        text = text.strip()
        if not text or any(text == c for c, _ in self._chips):
            return
        frame = QFrame()
        frame.setObjectName("chip")
        fl = QHBoxLayout(frame)
        fl.setContentsMargins(10, 3, 4, 3)
        fl.setSpacing(4)
        fl.addWidget(QLabel(text))
        x = QToolButton()
        x.setObjectName("chipx")
        x.setText("×")
        x.setCursor(Qt.CursorShape.PointingHandCursor)
        x.clicked.connect(lambda _=False, f=frame: self._remove(f))
        fl.addWidget(x)
        frame.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self._lay.insertWidget(self._lay.count() - 1, frame)
        self._chips.append((text, frame))
        self.edit.setPlaceholderText("")
        self.set_invalid(False)

    def _remove(self, frame):
        for i, (_, f) in enumerate(self._chips):
            if f is frame:
                self._chips.pop(i)
                break
        self._lay.removeWidget(frame)
        frame.deleteLater()
        if not self._chips:
            self.edit.setPlaceholderText(self._placeholder)

    def text(self):
        items = [c for c, _ in self._chips]
        pending = self.edit.text().strip()
        if pending:
            items.append(pending)
        return ", ".join(items)

    def setText(self, s):
        for _, f in list(self._chips):
            self._remove(f)
        for part in re.split("[,،]", s or ""):
            self._add_chip(part)

    def set_invalid(self, flag):
        if bool(self.property("invalid")) != flag:
            set_prop(self, "invalid", flag)

    def eventFilter(self, obj, event):
        if obj is self.edit:
            et = event.type()
            if et == QEvent.Type.FocusIn:
                set_prop(self, "focus", True)
            elif et == QEvent.Type.FocusOut:
                set_prop(self, "focus", False)
                self._commit()
            elif et == QEvent.Type.KeyPress and event.key() == Qt.Key.Key_Backspace \
                    and not self.edit.text() and self._chips:
                self._remove(self._chips[-1][1])
                return True
        return super().eventFilter(obj, event)


class ResultsTable(QTableWidget):
    openRequested = Signal(int)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter) and self.currentRow() >= 0:
            self.openRequested.emit(self.currentRow())
            return
        super().keyPressEvent(event)
