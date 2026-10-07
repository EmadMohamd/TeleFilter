from PySide6.QtCore import QObject, Signal


class Bridge(QObject):
    """Thread-safe channel from the Telegram worker thread to the UI thread."""
    status = Signal(str)
    done = Signal()
    failed = Signal(str)
    reset = Signal()
    auth = Signal(bool)
    ask = Signal(str, str, str)
