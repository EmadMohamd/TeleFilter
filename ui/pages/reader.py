import html
import re

from PySide6.QtCore import Qt, QUrl, Signal
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QApplication, QFrame, QGridLayout, QHBoxLayout, QLabel, QPushButton,
    QTextBrowser, QVBoxLayout, QWidget,
)

from ..helpers import has_arabic
from ..icons import make_icon
from ..theme import T


class ReaderPage(QWidget):
    """Shows one matched message with its metadata, highlighted keywords and quick actions."""
    backRequested = Signal()
    stepRequested = Signal(int)
    notify = Signal(str, str, str)  # kind, title, message

    def __init__(self, parent=None):
        super().__init__(parent)
        self._msg = None
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(14)
        root.addLayout(self._build_top_bar())
        root.addWidget(self._build_card(), 1)

    # ---- layout -----------------------------------------------------------
    def _build_top_bar(self):
        top = QHBoxLayout()
        top.setSpacing(10)
        self.back_btn = QPushButton("  Back to results")
        self.back_btn.setIcon(make_icon("back", T["text"], 16))
        self.back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.back_btn.clicked.connect(lambda: self.backRequested.emit())
        self.pos_label = QLabel("")
        self.pos_label.setObjectName("sub")
        self.prev_btn = QPushButton()
        self.prev_btn.setIcon(make_icon("left", T["text"], 16))
        self.prev_btn.setObjectName("small")
        self.prev_btn.setToolTip("Previous result")
        self.prev_btn.clicked.connect(lambda: self.stepRequested.emit(-1))
        self.next_btn = QPushButton()
        self.next_btn.setIcon(make_icon("right", T["text"], 16))
        self.next_btn.setObjectName("small")
        self.next_btn.setToolTip("Next result")
        self.next_btn.clicked.connect(lambda: self.stepRequested.emit(1))
        esc = QLabel("Esc to go back")
        esc.setObjectName("mono")
        top.addWidget(self.back_btn)
        top.addWidget(self.pos_label)
        top.addStretch(1)
        top.addWidget(esc)
        top.addSpacing(8)
        top.addWidget(self.prev_btn)
        top.addWidget(self.next_btn)
        return top

    def _build_card(self):
        card = QFrame()
        card.setObjectName("card")
        cl = QVBoxLayout(card)
        cl.setContentsMargins(24, 22, 24, 24)
        cl.setSpacing(12)
        self.channel_label = QLabel("")
        self.channel_label.setObjectName("h2")
        self.channel_label.setWordWrap(True)
        self.user_label = QLabel("")
        self.user_label.setObjectName("mono")
        cl.addWidget(self.channel_label)
        cl.addWidget(self.user_label)

        meta = QGridLayout()
        meta.setHorizontalSpacing(18)
        meta.setVerticalSpacing(6)
        meta.setColumnStretch(1, 1)
        self.meta_date = QLabel()
        self.meta_id = QLabel()
        self.meta_terms = QLabel()
        self.meta_link = QLabel()
        for r, (name, w) in enumerate((("Date", self.meta_date), ("Message ID", self.meta_id),
                                       ("Matched", self.meta_terms), ("Link", self.meta_link))):
            k = QLabel(name)
            k.setObjectName("sub")
            meta.addWidget(k, r, 0, Qt.AlignmentFlag.AlignTop)
            meta.addWidget(w, r, 1)
            w.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.meta_link.setOpenExternalLinks(True)
        # Absolute left alignment keeps Arabic text from jumping to the right edge.
        left = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignAbsolute | Qt.AlignmentFlag.AlignVCenter
        for w in (self.meta_terms, self.meta_date, self.meta_id, self.meta_link,
                  self.channel_label, self.user_label):
            w.setAlignment(left)
        self.meta_terms.setTextFormat(Qt.TextFormat.RichText)
        self.meta_link.setTextFormat(Qt.TextFormat.RichText)
        cl.addLayout(meta)

        actions = QHBoxLayout()
        actions.setSpacing(10)
        self.copy_text_btn = QPushButton("  Copy text")
        self.copy_text_btn.setIcon(make_icon("copy", T["text"], 16))
        self.copy_text_btn.clicked.connect(self._copy_text)
        self.copy_link_btn = QPushButton("  Copy link")
        self.copy_link_btn.setIcon(make_icon("copy", T["text"], 16))
        self.copy_link_btn.clicked.connect(self._copy_link)
        self.open_btn = QPushButton("  Open in Telegram")
        self.open_btn.setIcon(make_icon("external", T["text"], 16))
        self.open_btn.clicked.connect(self._open_link)
        for b in (self.copy_text_btn, self.copy_link_btn, self.open_btn):
            b.setObjectName("small")
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            actions.addWidget(b)
        actions.addStretch(1)
        cl.addLayout(actions)

        self.msg_viewer = QTextBrowser()
        self.msg_viewer.setOpenExternalLinks(True)
        cl.addWidget(self.msg_viewer, 1)
        return card

    # ---- public API -------------------------------------------------------
    def show_message(self, msg_obj, index, total, case_sensitive):
        self._msg = msg_obj
        self.channel_label.setText(msg_obj["channel"])
        self.user_label.setText(msg_obj["username"])
        self.meta_date.setText(msg_obj["date"])
        self.meta_id.setText(str(msg_obj["msg_id"]))
        tags = "".join(
            f'<span style="background-color:{T["warn_soft"]}; color:{T["warn"]};">&nbsp;{html.escape(t)}&nbsp;</span>&nbsp; '
            for t in msg_obj["matched_terms"])
        self.meta_terms.setText(f'<p dir="ltr" align="left" style="margin:0;">{tags}</p>')
        link = msg_obj["link"]
        if link:
            self.meta_link.setText(f'<a href="{html.escape(link)}" style="color:{T["accent"]};">{html.escape(link)}</a>')
        else:
            self.meta_link.setText("Not available for private channels")
        self.copy_link_btn.setEnabled(bool(link))
        self.open_btn.setEnabled(bool(link))
        self.msg_viewer.setHtml(self._render_html(msg_obj["text"], msg_obj["matched_terms"], case_sensitive))
        self.pos_label.setText(f"Result {index + 1} of {total}")
        self.prev_btn.setEnabled(index > 0)
        self.next_btn.setEnabled(index < total - 1)

    # ---- helpers ----------------------------------------------------------
    @staticmethod
    def _render_html(text, terms, case_sensitive):
        """Escapes the message, highlights matched terms, and sets direction per line."""
        terms = [t for t in dict.fromkeys(terms) if t]
        parts, pos = [], 0
        if terms:
            flags = 0 if case_sensitive else re.IGNORECASE
            rx = re.compile("|".join(re.escape(t) for t in sorted(terms, key=len, reverse=True)), flags)
            for m in rx.finditer(text):
                parts.append(html.escape(text[pos:m.start()]))
                parts.append(f'<span style="background-color:#5b4a1e; color:#ffd88a;">{html.escape(m.group(0))}</span>')
                pos = m.end()
        parts.append(html.escape(text[pos:]))
        paragraphs = []
        for line in "".join(parts).split("\n"):
            direction = "rtl" if has_arabic(re.sub(r"<[^>]+>", "", line)) else "ltr"
            paragraphs.append(f'<p dir="{direction}" style="margin:0 0 8px 0;">{line or "&nbsp;"}</p>')
        return f'<div style="font-size:15px; line-height:150%; color:{T["text"]};">{"".join(paragraphs)}</div>'

    def _copy_text(self):
        if self._msg:
            QApplication.clipboard().setText(self._msg["text"])
            self.notify.emit("ok", "Copied", "Message text copied.")

    def _copy_link(self):
        if self._msg and self._msg["link"]:
            QApplication.clipboard().setText(self._msg["link"])
            self.notify.emit("ok", "Copied", "Link copied.")

    def _open_link(self):
        if self._msg and self._msg["link"]:
            QDesktopServices.openUrl(QUrl(self._msg["link"]))
