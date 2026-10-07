"""Design tokens and the application-wide Qt stylesheet."""

T = {
    "ink": "#0a0e17", "panel": "#111726", "panel2": "#161d30", "line": "#212b42",
    "text": "#e8edf7", "mute": "#8b97b0", "accent": "#5b8cff", "accent_soft": "#1b2a52",
    "ok": "#3ecf8e", "ok_soft": "#12332a", "warn": "#f5b74a", "warn_soft": "#3a2d14",
    "bad": "#f2646b", "bad_soft": "#3a1a20",
}

_QSS = """
* { font-family: "Segoe UI", "Inter", "Noto Sans", "Noto Sans Arabic", sans-serif; font-size: 13px; color: @text; }
QMainWindow, QWidget#root { background: @ink; }
QDialog { background: @panel; }
QLabel { background: transparent; }
QLabel#h2 { font-size: 18px; font-weight: 700; }
QLabel#h3 { font-size: 15px; font-weight: 700; }
QLabel#sub { color: @mute; }
QLabel#mono { font-family: "Cascadia Mono", "Consolas", "DejaVu Sans Mono", monospace; font-size: 12px; color: @mute; }
QLabel#fieldLabel { color: @mute; font-size: 11px; font-weight: 700; letter-spacing: 1px; }
QLabel#err { color: @bad; font-size: 12px; }
QLabel#brand { font-size: 16px; font-weight: 800; }

QFrame#card { background: @panel; border: 1px solid @line; border-radius: 14px; }
QFrame#side { background: #0d1220; border-right: 1px solid @line; }
QFrame#acct { border: 1px solid @line; border-radius: 10px; }

QPushButton#nav { text-align: left; padding: 0 12px; min-height: 38px; border: none; border-radius: 9px; color: @mute; font-weight: 500; background: transparent; }
QPushButton#nav:hover { color: @text; background: #141b30; }
QPushButton#nav[active="true"] { background: @accent_soft; color: #cfdcff; }
QPushButton#nav:disabled { color: #4a5570; background: transparent; }

QLineEdit { background: @panel2; border: 1px solid @line; border-radius: 10px; padding: 0 12px; min-height: 44px; selection-background-color: @accent; }
QLineEdit:focus { border: 1px solid @accent; }
QLineEdit[invalid="true"] { border: 1px solid @bad; }
QLineEdit[code="true"] { font-family: "Cascadia Mono", "Consolas", monospace; font-size: 22px; letter-spacing: 6px; }
QLineEdit#date { font-family: "Cascadia Mono", "Consolas", "DejaVu Sans Mono", monospace; min-height: 38px; padding: 0 10px; }

QFrame#chipbox { background: @panel2; border: 1px solid @line; border-radius: 10px; }
QFrame#chipbox[focus="true"] { border: 1px solid @accent; }
QFrame#chipbox[invalid="true"] { border: 1px solid @bad; }
QFrame#chipbox QLineEdit { border: none; background: transparent; min-height: 32px; padding: 0 4px; }
QFrame#chip { background: @accent_soft; border-radius: 12px; }
QFrame#chip QLabel { color: #cfdcff; }
QToolButton#chipx { border: none; background: transparent; color: #7f95c9; font-size: 15px; padding: 0 2px; }
QToolButton#chipx:hover { color: @text; }

QPushButton { background: @panel2; border: 1px solid @line; border-radius: 10px; padding: 0 16px; min-height: 40px; font-weight: 600; }
QPushButton:hover { border-color: #34426a; }
QPushButton:disabled { color: #5d6985; background: #10162a; border-color: #1a2236; }
QPushButton#primary { background: @accent; border-color: @accent; color: #ffffff; }
QPushButton#primary:hover { background: #6d9aff; border-color: #6d9aff; }
QPushButton#primary:disabled { background: #25325a; border-color: #25325a; color: #7280a8; }
QPushButton#danger { background: @bad_soft; border-color: #5a2a32; color: #ff9aa0; }
QPushButton#danger:disabled { background: #10162a; border-color: #1a2236; color: #5d6985; }
QPushButton#ghost { background: transparent; border: none; color: @mute; }
QPushButton#ghost:hover { color: @text; }
QPushButton#small { min-height: 34px; padding: 0 12px; }

QFrame#seg { background: @panel2; border: 1px solid @line; border-radius: 10px; }
QPushButton#segbtn { background: transparent; border: none; border-radius: 7px; padding: 0 12px; min-height: 32px; color: @mute; font-weight: 500; }
QPushButton#segbtn:checked { background: @accent_soft; color: #cfdcff; }
QPushButton#segbtn:hover:!checked { color: @text; }

QProgressBar { background: #1d2640; border: none; border-radius: 3px; min-height: 6px; max-height: 6px; }
QProgressBar::chunk { background: @accent; border-radius: 3px; }

QTableWidget { background: transparent; color: @text; border: none; gridline-color: transparent; outline: 0; font-size: 13px; }
QTableWidget::item { padding: 0 12px; border-bottom: 1px solid #1a2236; }
QTableWidget::item:hover { background: #141c33; }
QTableWidget::item:selected { background: #162247; color: @text; }
QHeaderView { background: @panel; border: none; }
QTableCornerButton::section { background: @panel; border: none; }
QHeaderView::section { background: @panel; color: @mute; border: none; border-bottom: 1px solid @line; padding: 10px 12px; font-size: 11px; font-weight: 700; text-align: left; }
QScrollBar:vertical { background: transparent; width: 10px; margin: 2px; }
QScrollBar::handle:vertical { background: #2a3550; border-radius: 3px; min-height: 30px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal { background: transparent; height: 10px; margin: 2px; }
QScrollBar::handle:horizontal { background: #2a3550; border-radius: 3px; min-width: 30px; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }
QTextBrowser { background: @panel2; border: 1px solid @line; border-radius: 12px; padding: 16px; selection-background-color: @accent; }

QFrame#hero { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1a2a5c, stop:0.5 #0f1730, stop:1 #0a0e17); border-right: 1px solid @line; }
QLabel#heroTitle { font-size: 34px; font-weight: 800; }
QLabel#heroText { color: #aab7d6; font-size: 14px; }
QLabel#stepText { color: #aab7d6; }
QLabel#stepNum { border: 1px solid #34426a; border-radius: 12px; color: #cfdcff; font-size: 12px; min-width: 24px; max-width: 24px; min-height: 24px; max-height: 24px; }

QFrame#toast { background: #1a1f31; border: 1px solid @line; border-radius: 12px; }
QLabel#toastTitle { font-weight: 600; }
QLabel#toastBody { color: @mute; font-size: 12px; }
QToolTip { background: #1a1f31; color: @text; border: 1px solid @line; padding: 4px 8px; }
"""

APP_STYLESHEET = _QSS
for _k, _v in sorted(T.items(), key=lambda kv: -len(kv[0])):
    APP_STYLESHEET = APP_STYLESHEET.replace("@" + _k, _v)
