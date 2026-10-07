from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from .helpers import set_prop
from .icons import make_icon, make_logo
from .theme import T


class Sidebar(QFrame):
    searchClicked = Signal()
    exportClicked = Signal()
    credentialsClicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("side")
        self.setFixedWidth(220)
        sl = QVBoxLayout(self)
        sl.setContentsMargins(14, 20, 14, 16)
        sl.setSpacing(4)

        brand = QHBoxLayout()
        brand.setContentsMargins(2, 0, 0, 12)
        logo = QLabel()
        logo.setPixmap(make_logo(40))
        logo.setFixedSize(40, 40)
        bt = QLabel("TeleFilter")
        bt.setObjectName("brand")
        brand.addWidget(logo)
        brand.addWidget(bt)
        brand.addStretch(1)
        sl.addLayout(brand)

        self.nav_search = self._nav_button("Search", "search", self.searchClicked.emit)
        self.nav_export = self._nav_button("Export", "download", self.exportClicked.emit)
        self.nav_creds = self._nav_button("Credentials", "key", self.credentialsClicked.emit)
        self.nav_export.setEnabled(False)
        for b in (self.nav_search, self.nav_export, self.nav_creds):
            sl.addWidget(b)
        sl.addStretch(1)

        acct = QFrame()
        acct.setObjectName("acct")
        al = QHBoxLayout(acct)
        al.setContentsMargins(12, 10, 12, 10)
        al.setSpacing(10)
        self.acct_dot = QLabel()
        self.acct_dot.setFixedSize(8, 8)
        self.acct_title = QLabel("Not signed in")
        self.acct_title.setObjectName("h3")
        self.acct_title.setStyleSheet("font-size:12px;")
        self.acct_sub = QLabel("Sign in when you start a search")
        self.acct_sub.setObjectName("sub")
        self.acct_sub.setStyleSheet("font-size:11px;")
        self.acct_sub.setWordWrap(True)
        tl = QVBoxLayout()
        tl.setSpacing(0)
        tl.addWidget(self.acct_title)
        tl.addWidget(self.acct_sub)
        al.addWidget(self.acct_dot, 0, Qt.AlignmentFlag.AlignTop)
        al.addLayout(tl, 1)
        sl.addWidget(acct)

    def _nav_button(self, text, icon, slot):
        b = QPushButton("  " + text)
        b.setObjectName("nav")
        b.setIcon(make_icon(icon, T["mute"], 18))
        b.setIconSize(QSize(18, 18))
        b.setCursor(Qt.CursorShape.PointingHandCursor)
        b.clicked.connect(lambda _checked=False: slot())
        return b

    def set_active(self, name):
        for key, b in (("search", self.nav_search), ("creds", self.nav_creds)):
            set_prop(b, "active", key == name)

    def set_export_enabled(self, flag):
        self.nav_export.setEnabled(flag)

    def set_signed_in(self, ok):
        color = T["ok"] if ok else "#4a5570"
        self.acct_dot.setStyleSheet(f"background:{color}; border-radius:4px;")
        self.acct_title.setText("Signed in" if ok else "Not signed in")
        self.acct_sub.setText("Session saved on this computer" if ok else "Sign in when you start a search")
