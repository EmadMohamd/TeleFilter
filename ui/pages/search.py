from datetime import datetime, timedelta, timezone

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QAbstractItemView, QFrame, QGridLayout, QHBoxLayout, QHeaderView, QLabel,
    QLineEdit, QProgressBar, QPushButton, QSizePolicy, QStackedWidget,
    QTableWidgetItem, QVBoxLayout, QWidget,
)

from ..helpers import error_label, field_label
from ..icons import make_icon
from ..theme import T
from ..widgets import ChipInput, ResultsTable, Segmented, ToggleSwitch

PRESETS = ["Yesterday", "Last Week", "Last Month", "Last Year", "Custom"]


class SearchPage(QWidget):
    """Search form, live status, and the results table."""
    startRequested = Signal()
    stopRequested = Signal()
    exportRequested = Signal()
    openRequested = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(14)
        root.addWidget(self._build_form_card())
        root.addLayout(self._build_status_row())
        root.addWidget(self._build_results_card(), 1)

        self.preset_menu.set("Last Week")
        self.on_date_preset_selected("Last Week")

    # ---- layout -----------------------------------------------------------
    def _build_form_card(self):
        card = QFrame()
        card.setObjectName("card")
        cl = QVBoxLayout(card)
        cl.setContentsMargins(22, 20, 22, 20)
        cl.setSpacing(16)
        h = QLabel("New search")
        h.setObjectName("h2")
        sub = QLabel("Separate keywords with a comma or Enter. Arabic and English both work.")
        sub.setObjectName("sub")
        hb = QVBoxLayout()
        hb.setSpacing(2)
        hb.addWidget(h)
        hb.addWidget(sub)
        cl.addLayout(hb)

        grid = QGridLayout()
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(6)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        grid.addWidget(field_label("Keywords"), 0, 0)
        grid.addWidget(field_label("Channels (empty = all)"), 0, 1)
        self.terms_entry = ChipInput("keyword1, keyword2, كلمة مفتاحية")
        self.channels_entry = ChipInput("@example, @channel_name")
        grid.addWidget(self.terms_entry, 1, 0)
        grid.addWidget(self.channels_entry, 1, 1)
        self.terms_err = error_label()
        grid.addWidget(self.terms_err, 2, 0)
        cl.addLayout(grid)

        opts = QHBoxLayout()
        opts.setSpacing(10)
        self.preset_menu = Segmented(PRESETS)
        self.preset_menu.selected.connect(self.on_date_preset_selected)
        opts.addWidget(self.preset_menu)
        opts.addSpacing(6)
        lf = QLabel("From")
        lf.setObjectName("sub")
        self.from_entry = self._date_entry()
        lt = QLabel("to")
        lt.setObjectName("sub")
        self.to_entry = self._date_entry()
        self.from_entry.textEdited.connect(lambda _t: self.preset_menu.set("Custom"))
        self.to_entry.textEdited.connect(lambda _t: self.preset_menu.set("Custom"))
        opts.addWidget(lf)
        opts.addWidget(self.from_entry)
        opts.addWidget(lt)
        opts.addWidget(self.to_entry)
        opts.addStretch(1)
        self.case_switch = ToggleSwitch()
        cs_label = QLabel("Match case")
        cs_label.setObjectName("sub")
        opts.addWidget(self.case_switch)
        opts.addWidget(cs_label)
        cl.addLayout(opts)

        btns = QHBoxLayout()
        btns.setSpacing(10)
        self.run_btn = QPushButton("  Start search")
        self.run_btn.setObjectName("primary")
        self.run_btn.setIcon(make_icon("play", "#ffffff", 16))
        self.run_btn.clicked.connect(lambda: self.startRequested.emit())
        self.stop_btn = QPushButton("  Stop")
        self.stop_btn.setObjectName("danger")
        self.stop_btn.setIcon(make_icon("stop", "#ff9aa0", 16))
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(lambda: self.stopRequested.emit())
        self.export_btn = QPushButton("  Export results")
        self.export_btn.setIcon(make_icon("download", T["text"], 16))
        self.export_btn.setEnabled(False)
        self.export_btn.clicked.connect(lambda: self.exportRequested.emit())
        for b in (self.run_btn, self.stop_btn, self.export_btn):
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            btns.addWidget(b)
        btns.addStretch(1)
        cl.addLayout(btns)
        return card

    def _date_entry(self):
        e = QLineEdit()
        e.setObjectName("date")
        e.setFixedWidth(120)
        e.setPlaceholderText("YYYY-MM-DD")
        return e

    def _build_status_row(self):
        status = QHBoxLayout()
        status.setContentsMargins(4, 0, 4, 0)
        status.setSpacing(14)
        self.status_label = QLabel("System Ready")
        self.status_label.setObjectName("sub")
        self.status_label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        self.progress = QProgressBar()
        self.progress.setTextVisible(False)
        self.progress.setFixedWidth(240)
        self.progress.hide()
        status.addWidget(self.status_label, 1)
        status.addWidget(self.progress)
        return status

    def _build_results_card(self):
        results = QFrame()
        results.setObjectName("card")
        rl = QVBoxLayout(results)
        rl.setContentsMargins(8, 8, 8, 8)
        rl.setSpacing(0)
        rh = QHBoxLayout()
        rh.setContentsMargins(14, 8, 14, 8)
        rh.setSpacing(10)
        rt = QLabel("Results")
        rt.setObjectName("h3")
        self.count_label = QLabel("")
        self.count_label.setObjectName("sub")
        rh.addWidget(rt)
        rh.addWidget(self.count_label)
        rh.addStretch(1)
        hint = QLabel("Double-click a row to read the message")
        hint.setObjectName("sub")
        rh.addWidget(hint)
        rl.addLayout(rh)

        self.results_stack = QStackedWidget()
        empty = QWidget()
        el = QVBoxLayout(empty)
        el.setAlignment(Qt.AlignmentFlag.AlignCenter)
        el.setSpacing(8)
        icon = QLabel()
        icon.setPixmap(make_icon("search", T["mute"], 28).pixmap(QSize(28, 28)))
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_title = QLabel("No results yet")
        self.empty_title.setObjectName("h3")
        self.empty_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_text = QLabel("Run a search and matching messages will appear here.")
        self.empty_text.setObjectName("sub")
        self.empty_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        el.addWidget(icon)
        el.addWidget(self.empty_title)
        el.addWidget(self.empty_text)
        self.results_stack.addWidget(empty)

        cols = ["No.", "Channel Name", "Matched Keywords", "Date & Time", "Msg ID"]
        self.tree = ResultsTable(0, len(cols))
        self.tree.setHorizontalHeaderLabels(cols)
        # Header text follows the same alignment as its column's cells (see fill_results).
        for col in range(len(cols)):
            align = Qt.AlignmentFlag.AlignCenter if col in (0, 3, 4) else (
                Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            self.tree.horizontalHeaderItem(col).setTextAlignment(align)
        self.tree.verticalHeader().hide()
        self.tree.verticalHeader().setDefaultSectionSize(46)
        self.tree.setShowGrid(False)
        self.tree.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tree.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tree.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tree.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        hdr = self.tree.horizontalHeader()
        hdr.setHighlightSections(False)
        hdr.setStretchLastSection(False)
        hdr.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        hdr.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        hdr.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        hdr.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        hdr.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self.tree.setColumnWidth(0, 70)
        self.tree.setColumnWidth(3, 170)
        self.tree.setColumnWidth(4, 110)
        self.tree.cellDoubleClicked.connect(lambda row, _col: self.openRequested.emit(row))
        self.tree.openRequested.connect(lambda row: self.openRequested.emit(row))
        self.results_stack.addWidget(self.tree)
        rl.addWidget(self.results_stack, 1)
        return results

    # ---- dates ------------------------------------------------------------
    def on_date_preset_selected(self, choice):
        now = datetime.now(timezone.utc)
        self.to_entry.setText(now.strftime("%Y-%m-%d"))

        if choice == "Yesterday":
            start_date = now - timedelta(days=1)
        elif choice == "Last Week":
            start_date = now - timedelta(days=7)
        elif choice == "Last Month":
            start_date = now - timedelta(days=30)
        elif choice == "Last Year":
            start_date = now - timedelta(days=365)
        else:
            return  # Custom

        self.from_entry.setText(start_date.strftime("%Y-%m-%d"))

    # ---- state ------------------------------------------------------------
    def show_terms_error(self, message):
        self.terms_entry.set_invalid(True)
        self.terms_err.setText(message)
        self.terms_err.show()

    def clear_terms_error(self):
        self.terms_err.hide()

    def set_running(self, running):
        self.run_btn.setEnabled(not running)
        self.stop_btn.setEnabled(running)
        if running:
            self.export_btn.setEnabled(False)
            self.progress.setRange(0, 0)
            self.progress.show()
        else:
            self.progress.hide()

    def set_export_enabled(self, flag):
        self.export_btn.setEnabled(flag)

    def set_status(self, text):
        self.status_label.setText(text)

    def set_progress(self, done, total):
        self.progress.setRange(0, max(total, 1))
        self.progress.setValue(done)

    def set_count(self, text):
        self.count_label.setText(text)

    def show_empty(self, title, text):
        self.empty_title.setText(title)
        self.empty_text.setText(text)
        self.results_stack.setCurrentIndex(0)

    def clear_results(self, title, text):
        self.tree.setRowCount(0)
        self.count_label.setText("")
        self.show_empty(title, text)

    def fill_results(self, results):
        self.tree.setRowCount(0)
        for index, r in enumerate(results):
            terms_str = "  ·  ".join(r["matched_terms"])
            self.tree.insertRow(index)
            cells = [str(index + 1), r["channel"], terms_str, r["date"], str(r["msg_id"])]
            for col, text in enumerate(cells):
                item = QTableWidgetItem(text)
                if col in (0, 3, 4):
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    item.setForeground(QColor(T["mute"]))
                elif col == 2:
                    item.setForeground(QColor(T["warn"]))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
                else:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
                self.tree.setItem(index, col, item)
        if results:
            self.results_stack.setCurrentIndex(1)
            self.tree.selectRow(0)
