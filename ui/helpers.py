"""Small shared helpers: text utilities, error wording and tiny widget factories."""
import html

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel
from telethon.errors import FloodWaitError, PhoneCodeInvalidError, PhoneNumberInvalidError


AUTHOR_NAME = "Emad Mohamed"
AUTHOR_URL = "https://github.com/EmadMohamd"



def has_arabic(text):
    return any("؀" <= c <= "ۿ" or "ݐ" <= c <= "ݿ" for c in str(text or ""))


def set_prop(widget, name, value):
    """Sets a dynamic property and re-applies the stylesheet so [prop="..."] selectors update."""
    widget.setProperty(name, value)
    widget.style().unpolish(widget)
    widget.style().polish(widget)


def friendly_error(e):
    """Turns an exception into a message a person can act on."""
    if isinstance(e, FloodWaitError):
        return f"Telegram asked us to wait {e.seconds} seconds before trying again."
    if isinstance(e, PhoneNumberInvalidError):
        return "That phone number is not valid. Include the country code, like +1234567890."
    if isinstance(e, PhoneCodeInvalidError):
        return "That login code is not correct. Start the search again to get a new code."
    if isinstance(e, (ConnectionError, TimeoutError)):
        return "Could not reach Telegram. Check your internet connection and try again."
    return str(e) or e.__class__.__name__


def field_label(text):
    lbl = QLabel(text.upper())
    lbl.setObjectName("fieldLabel")
    return lbl


def error_label():
    lbl = QLabel("")
    lbl.setObjectName("err")
    lbl.setWordWrap(True)
    lbl.hide()
    return lbl


def made_by_label():
    """Small "Made by <name>" credit that opens AUTHOR_URL in the browser. Returns None if no name is set."""
    if not AUTHOR_NAME.strip():
        return None
    name = html.escape(AUTHOR_NAME.strip())
    url = html.escape(AUTHOR_URL.strip(), quote=True)
    body = f'<a href="{url}" style="color:#5b8cff; text-decoration:none;">{name}</a>' if url else name
    lbl = QLabel(f"Made by {body}")
    lbl.setObjectName("sub")
    lbl.setTextFormat(Qt.TextFormat.RichText)
    lbl.setOpenExternalLinks(True)
    lbl.setToolTip(AUTHOR_URL.strip())
    return lbl
