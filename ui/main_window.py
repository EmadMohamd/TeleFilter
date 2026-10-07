"""Main window: wires the pages together and runs the Telegram search on a worker thread."""
import asyncio
import logging
import re
import threading
from datetime import datetime, timezone
from pathlib import Path

from PySide6.QtGui import QIcon, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QFileDialog, QHBoxLayout, QMainWindow, QStackedWidget, QVBoxLayout, QWidget,
)
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

from config import load_config, save_config, validate_config
from telegram_worker import TelegramWorker

from .bridge import Bridge
from .helpers import friendly_error
from .icons import make_logo
from .overlays import PromptDialog, Toast
from .pages import CredentialsPage, ReaderPage, SearchPage
from .sidebar import Sidebar

logger = logging.getLogger("TeleFilterUI")


class TeleFilterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TeleFilter 2026")
        self.setWindowIcon(QIcon(make_logo(64)))
        self.resize(1280, 800)
        self.setMinimumSize(1000, 680)

        self.results_data = []
        self.is_searching = False
        self._last_case = False
        self._reader_index = -1
        self._prompt_event = threading.Event()
        self._prompt_result = None

        self.bridge = Bridge()
        self.bridge.status.connect(self._on_status)
        self.bridge.done.connect(self.populate_results)
        self.bridge.failed.connect(self._on_failed)
        self.bridge.reset.connect(self.reset_buttons)
        self.bridge.auth.connect(self._on_auth)
        self.bridge.ask.connect(self._show_prompt)

        central = QWidget()
        central.setObjectName("root")
        self.setCentralWidget(central)
        outer = QVBoxLayout(central)
        outer.setContentsMargins(0, 0, 0, 0)
        self.root_stack = QStackedWidget()
        outer.addWidget(self.root_stack)

        self.cred_page = CredentialsPage()
        self.cred_page.submitted.connect(self.submit_credentials)
        self.cred_page.backRequested.connect(self.show_search_view)
        self.root_stack.addWidget(self.cred_page)
        self.root_stack.addWidget(self._build_workspace())
        self.toast = Toast(central)

        QShortcut(QKeySequence("F11"), self, activated=self.toggle_fullscreen)
        QShortcut(QKeySequence("Esc"), self, activated=self._on_escape)

        config = load_config()
        if validate_config(config):
            self.cred_page.set_values(config.get("api_id", ""), config.get("api_hash", ""))
            self.show_search_view()
        else:
            self.show_credentials_view()
        session = Path(str(config.get("session_name", "telefilter_session")) + ".session")
        self._on_auth(session.exists())

    def _build_workspace(self):
        page = QWidget()
        lay = QHBoxLayout(page)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        self.sidebar = Sidebar()
        self.sidebar.searchClicked.connect(self.show_search_view)
        self.sidebar.exportClicked.connect(self.export_results)
        self.sidebar.credentialsClicked.connect(self.show_credentials_view)
        lay.addWidget(self.sidebar)

        self.search_page = SearchPage()
        self.search_page.startRequested.connect(self.start_search_thread)
        self.search_page.stopRequested.connect(self.stop_search)
        self.search_page.exportRequested.connect(self.export_results)
        self.search_page.openRequested.connect(self.on_select_message)

        self.reader_page = ReaderPage()
        self.reader_page.backRequested.connect(self.show_search_view)
        self.reader_page.stepRequested.connect(self._step_reader)
        self.reader_page.notify.connect(lambda kind, title, msg: self.show_toast(msg, kind=kind, title=title))

        self.inner_stack = QStackedWidget()
        self.inner_stack.addWidget(self.search_page)
        self.inner_stack.addWidget(self.reader_page)
        lay.addWidget(self.inner_stack, 1)
        return page

    # ---- window behaviour -------------------------------------------------
    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.exit_fullscreen()
        else:
            self.showFullScreen()

    def exit_fullscreen(self):
        self.showNormal()
        self.showMaximized()

    def _on_escape(self):
        if self.root_stack.currentIndex() == 1 and self.inner_stack.currentIndex() == 1:
            self.show_search_view()
        elif self.isFullScreen():
            self.exit_fullscreen()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "toast") and self.toast.isVisible():
            self.toast.reposition()

    def show_toast(self, message, is_error=False, title=None, kind=None):
        kind = kind or ("error" if is_error else "info")
        if title is None:
            title = {"error": "Something went wrong", "ok": "Done", "warn": "Heads up"}.get(kind, "TeleFilter")
        self.toast.popup(kind, title, message)

    # ---- view switching ---------------------------------------------------
    def show_credentials_view(self):
        self.cred_page.set_back_visible(validate_config(load_config()))
        self.root_stack.setCurrentIndex(0)

    def show_search_view(self):
        self.root_stack.setCurrentIndex(1)
        self.inner_stack.setCurrentIndex(0)
        self.sidebar.set_active("search")

    def show_detail_view(self):
        self.root_stack.setCurrentIndex(1)
        self.inner_stack.setCurrentIndex(1)
        self.sidebar.set_active("search")

    def _on_auth(self, ok):
        self.sidebar.set_signed_in(ok)

    # ---- credentials ------------------------------------------------------
    def submit_credentials(self):
        api_id, api_hash = self.cred_page.values()
        session_name = "telefilter_session"

        ok = True
        if not api_id:
            self.cred_page.set_error("id", "API ID is required.")
            ok = False
        else:
            try:
                int(api_id)
            except ValueError:
                self.cred_page.set_error("id", "API ID must be a number, like 12345678.")
                ok = False
        if not api_hash:
            self.cred_page.set_error("hash", "API Hash is required.")
            ok = False
        if not ok:
            return

        if save_config(api_id, api_hash, session_name):
            self.show_search_view()
            self.show_toast("Your API credentials were saved on this computer.", kind="ok", title="Credentials saved")
        else:
            self.show_toast("Could not write user_config.json. Check that the folder is writable.",
                            kind="error", title="Could not save credentials")

    # ---- sign-in prompts (called from the worker thread) -------------------
    def prompt_for_input(self, prompt_text, title_text, mode="text"):
        self._prompt_event.clear()
        self._prompt_result = None
        self.bridge.ask.emit(prompt_text, title_text, mode)
        self._prompt_event.wait()
        return self._prompt_result

    def _show_prompt(self, prompt_text, title_text, mode):
        dialog = PromptDialog(self, title_text, prompt_text, mode)
        self._prompt_result = dialog.get_input()
        self._prompt_event.set()

    # ---- search -----------------------------------------------------------
    def parse_date(self, value):
        if not value:
            return None
        try:
            return datetime.strptime(value.strip(), "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except ValueError:
            return None

    def start_search_thread(self):
        sp = self.search_page
        sp.clear_terms_error()
        search_terms = [t.strip() for t in sp.terms_entry.text().split(",") if t.strip()]
        if not search_terms:
            sp.show_terms_error("Add at least one keyword to search.")
            return

        target_channels = [c.strip() for c in sp.channels_entry.text().split(",") if c.strip()]
        date_from = self.parse_date(sp.from_entry.text())
        date_to = self.parse_date(sp.to_entry.text()) or datetime.now(timezone.utc)
        case_sensitive = sp.case_switch.isChecked()
        self._last_case = case_sensitive

        self.is_searching = True
        sp.set_running(True)
        self.sidebar.set_export_enabled(False)
        sp.set_status("Connecting to Telegram...")
        sp.clear_results("Searching your channels", "Matches will appear here when the scan finishes.")
        self.results_data.clear()

        threading.Thread(
            target=lambda: asyncio.run(
                self.run_search_async(search_terms, target_channels, date_from, date_to, case_sensitive)),
            daemon=True
        ).start()

    async def run_search_async(self, search_terms, target_channels, date_from, date_to, case_sensitive):
        client = None
        try:
            config = load_config()
            client = TelegramClient(config.get("session_name", "telefilter_session"),
                                    int(config["api_id"]),
                                    config["api_hash"])
            await client.connect()

            if not await client.is_user_authorized():
                self.bridge.status.emit("Authentication required...")
                phone = self.prompt_for_input("Enter your phone number with country code, for example +1234567890.",
                                              "Sign in to Telegram")
                if not phone:
                    await client.disconnect()
                    self.bridge.reset.emit()
                    return

                await client.send_code_request(phone.strip())
                code = self.prompt_for_input("Enter the verification code Telegram just sent you.",
                                             "Verification code", mode="code")
                if not code:
                    await client.disconnect()
                    self.bridge.reset.emit()
                    return

                try:
                    await client.sign_in(phone.strip(), code.strip())
                except SessionPasswordNeededError:
                    pwd = self.prompt_for_input("Enter your Two-Step Verification password.",
                                                "Two-step verification", mode="secret")
                    if not pwd:
                        await client.disconnect()
                        self.bridge.reset.emit()
                        return
                    await client.sign_in(password=pwd.strip())

            self.bridge.auth.emit(True)
            await client.disconnect()

            check_cancelled = lambda: not self.is_searching
            update_status = lambda msg: self.bridge.status.emit(msg)

            results = await TelegramWorker.search_channels(
                search_terms, target_channels, date_from, date_to, check_cancelled, update_status, case_sensitive
            )

            results.sort(key=lambda x: x["date"], reverse=True)
            self.results_data = results
            self.bridge.done.emit()

        except Exception as e:
            logger.error("Search error: %s", e, exc_info=True)
            self.bridge.failed.emit(friendly_error(e))
            if client and client.is_connected():
                await client.disconnect()

    def _on_status(self, msg):
        self.search_page.set_status(msg)
        m = re.match(r"Scanning \((\d+)/(\d+)\)", msg)
        if m:
            self.search_page.set_progress(int(m.group(1)), int(m.group(2)))

    def _on_failed(self, message):
        self.search_page.set_status("Operation failed.")
        self.reset_buttons()
        self.search_page.show_empty("The search did not finish", "Fix the issue shown above and start again.")
        self.show_toast(message, kind="error", title="Search failed")

    def stop_search(self):
        self.is_searching = False
        self.search_page.set_status("Aborting operation...")

    def reset_buttons(self):
        self.is_searching = False
        self.search_page.set_running(False)

    def populate_results(self):
        sp = self.search_page
        cancelled = not self.is_searching
        sp.fill_results(self.results_data)

        count = len(self.results_data)
        plural = "s" if count != 1 else ""
        sp.set_status(f"Stopped. Found {count} matching items." if cancelled
                      else f"Completed. Found {count} matching items.")
        sp.set_count(f"{count} matching message{plural}")
        self.reset_buttons()
        if count > 0:
            sp.set_export_enabled(True)
            self.sidebar.set_export_enabled(True)
            if not cancelled:
                self.show_toast(f"Found {count} message{plural}.", kind="ok", title="Search complete")
        else:
            sp.show_empty("No messages found", "Try a wider date range or fewer keywords.")

    # ---- export -----------------------------------------------------------
    def export_results(self):
        if not self.results_data:
            return
        path, selected = QFileDialog.getSaveFileName(
            self, "Export results", "telefilter_results.txt",
            "Text file (*.txt);;JSON file (*.json)")
        if not path:
            return
        if not path.lower().endswith((".txt", ".json")):
            path += ".json" if "json" in selected.lower() else ".txt"
        try:
            TelegramWorker.export_to_file(path, self.results_data)
            self.show_toast(f"Saved {len(self.results_data)} results to {Path(path).name}.",
                            kind="ok", title="Export complete")
        except Exception as e:
            logger.error("Export error: %s", e, exc_info=True)
            self.show_toast(friendly_error(e), kind="error", title="Export failed")

    # ---- reader -----------------------------------------------------------
    def on_select_message(self, index):
        if index < 0 or index >= len(self.results_data):
            return
        self._reader_index = index
        self.reader_page.show_message(self.results_data[index], index, len(self.results_data), self._last_case)
        self.show_detail_view()

    def _step_reader(self, delta):
        new = self._reader_index + delta
        if 0 <= new < len(self.results_data):
            self.search_page.tree.selectRow(new)
            self.on_select_message(new)
