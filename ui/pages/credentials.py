from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget

from ..helpers import error_label, field_label, made_by_label, set_prop
from ..icons import make_full_logo, make_icon
from ..theme import T


class CredentialsPage(QWidget):
    """Split-screen sign-in: product pitch on the left, API credentials form on the right."""
    submitted = Signal()
    backRequested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        lay.addWidget(self._build_hero(), 1)
        lay.addWidget(self._build_form_side(), 1)

    # ---- layout -----------------------------------------------------------
    def _build_hero(self):
        hero = QFrame()
        hero.setObjectName("hero")
        hl = QVBoxLayout(hero)
        hl.setContentsMargins(56, 48, 56, 48)
        hl.setSpacing(16)
        logo = QLabel()
        logo.setPixmap(make_full_logo(190))
        logo.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        hl.addWidget(logo)
        hl.addStretch(1)
        title = QLabel("Search every channel\nyou follow.")
        title.setObjectName("heroTitle")
        text = QLabel("Find messages by keyword across channels and groups, in English or Arabic, within any date range.")
        text.setObjectName("heroText")
        text.setWordWrap(True)
        text.setMaximumWidth(420)
        hl.addWidget(title)
        hl.addWidget(text)
        hl.addStretch(1)
        for n, s in enumerate(["Paste your API ID and hash from my.telegram.org",
                               "Sign in once with your phone number",
                               "Search. Your session stays on this computer"], 1):
            r = QHBoxLayout()
            r.setSpacing(12)
            num = QLabel(str(n))
            num.setObjectName("stepNum")
            num.setAlignment(Qt.AlignmentFlag.AlignCenter)
            st = QLabel(s)
            st.setObjectName("stepText")
            r.addWidget(num)
            r.addWidget(st, 1)
            hl.addLayout(r)
        return hero

    def _build_form_side(self):
        right = QWidget()
        rl = QHBoxLayout(right)
        rl.setContentsMargins(40, 40, 40, 40)
        rl.addStretch(1)
        form = QWidget()
        form.setFixedWidth(420)
        fl = QVBoxLayout(form)
        fl.setContentsMargins(0, 0, 0, 0)
        fl.setSpacing(8)

        self.back_btn = QPushButton("  Back to search")
        self.back_btn.setObjectName("ghost")
        self.back_btn.setIcon(make_icon("back", T["mute"], 16))
        self.back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.back_btn.clicked.connect(lambda: self.backRequested.emit())
        self.back_btn.hide()
        back_row = QHBoxLayout()
        back_row.addWidget(self.back_btn)
        back_row.addStretch(1)
        fl.addLayout(back_row)

        h = QLabel("Connect your account")
        h.setObjectName("h2")
        sub = QLabel("Credentials are saved locally in user_config.json.")
        sub.setObjectName("sub")
        fl.addWidget(h)
        fl.addWidget(sub)
        fl.addSpacing(14)

        fl.addWidget(field_label("API ID"))
        self.api_id_entry = QLineEdit()
        self.api_id_entry.setPlaceholderText("12345678")
        self.api_id_entry.textChanged.connect(lambda: self.clear_error("id"))
        self.api_id_entry.returnPressed.connect(lambda: self.submitted.emit())
        fl.addWidget(self.api_id_entry)
        self.api_id_err = error_label()
        fl.addWidget(self.api_id_err)
        fl.addSpacing(6)

        fl.addWidget(field_label("API Hash"))
        hash_row = QHBoxLayout()
        hash_row.setSpacing(8)
        self.api_hash_entry = QLineEdit()
        self.api_hash_entry.setPlaceholderText("abc123xyz...")
        self.api_hash_entry.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_hash_entry.textChanged.connect(lambda: self.clear_error("hash"))
        self.api_hash_entry.returnPressed.connect(lambda: self.submitted.emit())
        self.show_hash_btn = QPushButton("Show")
        self.show_hash_btn.setObjectName("small")
        self.show_hash_btn.setCheckable(True)
        self.show_hash_btn.setFixedHeight(44)
        self.show_hash_btn.toggled.connect(self._toggle_hash)
        hash_row.addWidget(self.api_hash_entry, 1)
        hash_row.addWidget(self.show_hash_btn)
        fl.addLayout(hash_row)
        self.api_hash_err = error_label()
        fl.addWidget(self.api_hash_err)
        fl.addSpacing(14)

        connect_btn = QPushButton("Connect   →")
        connect_btn.setObjectName("primary")
        connect_btn.setFixedHeight(46)
        connect_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        connect_btn.clicked.connect(lambda: self.submitted.emit())
        fl.addWidget(connect_btn)
        fl.addSpacing(6)
        note = QLabel("Stored on this device only. Never sent anywhere except Telegram.")
        note.setObjectName("sub")
        note.setWordWrap(True)
        fl.addWidget(note)

        col = QVBoxLayout()
        col.addStretch(1)
        col.addWidget(form)
        col.addStretch(1)
        credit = made_by_label()  # pinned to the bottom of the right-hand panel
        if credit:
            col.addWidget(credit, 0, Qt.AlignmentFlag.AlignHCenter)
        rl.addLayout(col)
        rl.addStretch(1)
        return right

    # ---- public API -------------------------------------------------------
    def values(self):
        return self.api_id_entry.text().strip(), self.api_hash_entry.text().strip()

    def set_values(self, api_id, api_hash):
        self.api_id_entry.setText(api_id)
        self.api_hash_entry.setText(api_hash)

    def set_back_visible(self, flag):
        self.back_btn.setVisible(flag)

    def _field(self, which):
        return (self.api_id_entry, self.api_id_err) if which == "id" else (self.api_hash_entry, self.api_hash_err)

    def set_error(self, which, message):
        entry, err = self._field(which)
        err.setText(message)
        err.show()
        set_prop(entry, "invalid", True)

    def clear_error(self, which):
        entry, err = self._field(which)
        err.hide()
        set_prop(entry, "invalid", False)

    def _toggle_hash(self, shown):
        self.api_hash_entry.setEchoMode(QLineEdit.EchoMode.Normal if shown else QLineEdit.EchoMode.Password)
        self.show_hash_btn.setText("Hide" if shown else "Show")
