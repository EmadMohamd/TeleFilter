"""Transient UI on top of the app: toast notifications and the sign-in prompt dialog."""
from PySide6.QtCore import QSize, Qt, QTimer
from PySide6.QtWidgets import QDialog, QFrame, QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout

from .icons import make_icon
from .theme import T


class Toast(QFrame):
    STYLE = {
        "error": ("x", T["bad"], T["bad_soft"]),
        "warn": ("alert", T["warn"], T["warn_soft"]),
        "ok": ("check", T["ok"], T["ok_soft"]),
        "info": ("info", T["accent"], T["accent_soft"]),
    }
    WIDTH = 380

    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("toast")
        self.hide()
        lay = QHBoxLayout(self)
        lay.setContentsMargins(14, 12, 14, 12)
        lay.setSpacing(12)
        self.icon = QLabel()
        self.icon.setFixedSize(28, 28)
        self.icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(self.icon, 0, Qt.AlignmentFlag.AlignTop)
        col = QVBoxLayout()
        col.setSpacing(2)
        self.title = QLabel()
        self.title.setObjectName("toastTitle")
        self.body = QLabel()
        self.body.setObjectName("toastBody")
        self.body.setWordWrap(True)
        col.addWidget(self.title)
        col.addWidget(self.body)
        lay.addLayout(col, 1)
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.hide)

    def popup(self, kind, title, message, ms=4500):
        icon, color, soft = self.STYLE.get(kind, self.STYLE["info"])
        self.icon.setPixmap(make_icon(icon, color, 16).pixmap(QSize(16, 16)))
        self.icon.setStyleSheet(f"background:{soft}; border-radius:8px;")
        self.setStyleSheet(f"QFrame#toast {{ border: 1px solid {color}; }}")
        self.title.setText(title)
        self.body.setText(message)
        self.body.setVisible(bool(message))
        self.setFixedWidth(self.WIDTH)
        text_w = self.WIDTH - 14 * 2 - 28 - 12
        body_h = self.body.heightForWidth(text_w) if message else 0
        self.setFixedHeight(max(12 * 2 + self.title.sizeHint().height() + (2 + body_h if message else 0), 56))
        self.reposition()
        self.show()
        self.raise_()
        self.timer.start(ms)

    def reposition(self):
        p = self.parentWidget()
        if p:
            self.move(max(p.width() - self.width() - 24, 8), 16)


class PromptDialog(QDialog):
    """Styled replacement for the plain input box used during Telegram sign-in."""

    def __init__(self, parent, title, text, mode="text"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(460)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 24, 24, 20)
        lay.setSpacing(14)
        h = QLabel(title)
        h.setObjectName("h2")
        sub = QLabel(text)
        sub.setObjectName("sub")
        sub.setWordWrap(True)
        self.edit = QLineEdit()
        if mode == "secret":
            self.edit.setEchoMode(QLineEdit.EchoMode.Password)
        elif mode == "code":
            self.edit.setProperty("code", True)
            self.edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.edit.returnPressed.connect(self.accept)
        row = QHBoxLayout()
        row.addStretch(1)
        cancel = QPushButton("Cancel")
        cancel.clicked.connect(self.reject)
        ok = QPushButton("Continue")
        ok.setObjectName("primary")
        ok.setDefault(True)
        ok.clicked.connect(self.accept)
        row.addWidget(cancel)
        row.addWidget(ok)
        lay.addWidget(h)
        lay.addWidget(sub)
        lay.addWidget(self.edit)
        lay.addSpacing(4)
        lay.addLayout(row)
        self.edit.setFocus()

    def get_input(self):
        if self.exec() == QDialog.DialogCode.Accepted:
            return self.edit.text()
        return None
