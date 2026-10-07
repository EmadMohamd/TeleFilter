import logging
import sys

from app_paths import use_data_dir

# Must run before anything reads user_config.json or opens a Telegram session.
DATA_DIR = use_data_dir()

from PySide6.QtWidgets import QApplication  # noqa: E402

from ui import APP_STYLESHEET, TeleFilterApp  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(APP_STYLESHEET)
    window = TeleFilterApp()
    window.showMaximized()
    sys.exit(app.exec())
