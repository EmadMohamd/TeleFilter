"""Where TeleFilter keeps its files.

user_config.json (API credentials) and the Telegram login (*.session) are created at run time,
in the same folder as TeleFilter.exe. Nothing is bundled into the exe, so every user starts
clean and enters their own details on first launch.

If that folder is read-only (for example the app was installed under C:\\Program Files), the
files go to a per-user folder instead:
  Windows: %APPDATA%\\TeleFilter    macOS: ~/Library/Application Support/TeleFilter
  Linux:   ~/.local/share/TeleFilter
"""
import os
import sys
from pathlib import Path

APP_NAME = "TeleFilter"


def _app_dir() -> Path:
    """Folder holding the exe when packaged, or the project folder when run from source."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def _is_writable(folder: Path) -> bool:
    try:
        folder.mkdir(parents=True, exist_ok=True)
        probe = folder / ".write_test"
        probe.write_text("ok")
        probe.unlink()
        return True
    except OSError:
        return False


def _fallback_dir() -> Path:
    if sys.platform.startswith("win"):
        base = Path(os.environ.get("APPDATA") or Path.home() / "AppData" / "Roaming")
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share")
    path = base / APP_NAME
    path.mkdir(parents=True, exist_ok=True)
    return path


def data_dir() -> Path:
    app_dir = _app_dir()
    return app_dir if _is_writable(app_dir) else _fallback_dir()


def use_data_dir() -> Path:
    """Makes the data folder the working directory.

    config.py and the Telegram client use relative file names, so this one call puts the
    config and session files in that folder without changing either module.
    """
    path = data_dir()
    os.chdir(path)
    return path
