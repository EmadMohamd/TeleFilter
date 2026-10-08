# TeleFilter

A modern desktop app built with Python that searches the Telegram channels and groups you follow for keywords, lets you read matching messages in full, and exports the results. Arabic and other right-to-left text displays correctly everywhere, including the input fields.

---

## Requirements

* Python 3.9+
* A Telegram account
* Telegram API credentials

---

## Installation

1. **Clone or download the application files**
2. **Install dependencies**
```bash
pip install -r requirements.txt
```
or install them directly:
```bash
pip install PySide6 telethon
```
3. **Get Telegram API credentials**
   * Go to [my.telegram.org](https://my.telegram.org)
   * Log in with your phone number
   * Click **API development tools**
   * Fill in the form (app name and short name can be anything)
   * Platform: **Other**
   * URL: leave **blank**
   * Click **Create application**
   * Copy your `api_id` and `api_hash`


---

## Usage

Launch the desktop application:

```bash
python main.py
```

### First run

1. The **Connect your account** screen opens. Enter your **API ID** and **API Hash** and click **Connect**. They are saved to `user_config.json` next to the app.
2. Click **Start search**. Telegram sends a verification code to your Telegram app. A dialog asks for your phone number (with country code, for example `+1234567890`), then the code, then your two-step verification password if you have one.
3. This happens once. Your session is saved locally as `telefilter_session.session` next to the app.

To change the credentials later, click **Credentials** in the sidebar.

### Search form

* **Keywords:** Type a keyword and press Enter or a comma to turn it into a chip. Arabic and English both work, and the Arabic comma `،` also separates keywords. Press Backspace in an empty field to remove the last chip.
* **Channels:** Channel usernames or titles, entered the same way. Leave empty to search **all** channels and groups you follow.
* **Time range:** Pick **Yesterday**, **Last Week**, **Last Month** or **Last Year**, or edit the **From** and **to** dates (`YYYY-MM-DD`) to switch to **Custom**.
* **Match case:** Turn on for case-sensitive matching.

### Actions

* **Start search:** Runs the search in the background so the window stays responsive. A progress bar shows which channel is being scanned.
* **Stop:** Cancels a running search. Results found so far are kept.
* **Export results:** Opens a save dialog and writes the results as a `.txt` or `.json` file. The same action is in the sidebar.

### Keyboard shortcuts

* **F11:** toggle fullscreen
* **Esc:** go back from the message reader, or leave fullscreen
* **Enter:** open the selected result
* **Double-click** a row: open the selected result

---

## Features

### 1. Results table

* Dark-themed table of matched channels, matched keywords, date and time, and message ID, newest first.
* Empty, searching and no-results states tell you what to do next.

### 2. Message reader

* Open any result to see the full message with matched keywords highlighted, the channel, date, message ID and direct link.
* Step through results with the previous and next buttons, copy the text or the link, or open the message in Telegram.
* Arabic paragraphs are laid out right-to-left automatically.

### 3. Clear errors

* Invalid credentials show next to the field that needs fixing.
* Network problems, wrong phone numbers, wrong codes and Telegram rate limits appear as short notifications that say what to do.

---

## Notes

* **Session file:** `telefilter_session.session` stores your login so you do not have to sign in again. Keep it private.
* **Performance:** Each channel is read from the newest message backwards and stops once it passes your **From** date, so shorter time ranges and specific channels finish faster. Matching is done on your computer.
* **Group channels:** Both channels and groups you are a member of are searched.

---

## Where your data is stored

Credentials and the Telegram login are created when the app runs, in the same folder as `TeleFilter.exe` (or in the project folder when run from source):

* `user_config.json` holds the API ID and hash
* `telefilter_session.session` holds the Telegram login


---

## Verify your download

TeleFilter asks for your Telegram API credentials and creates a Telegram login on your computer, so it is worth checking that the program you run really comes from this source code.

**Where to download:** only from this repository's **Releases** page. Anything else, including a copy with the same name on another site or fork, is not the official build.

**Check a download** (takes under a minute):

1. Install the [GitHub CLI](https://cli.github.com). It may ask you to sign in once with `gh auth login`.
2. In the folder with the download, run:

   ```
   gh attestation verify TeleFilter-win64.zip --repo EmadMohamd/TeleFilter
   ```

   A successful result names this repository and the commit the file was built from. If it fails, do not run the file.
3. Optional: compare the file's SHA-256 hash with `SHA256SUMS.txt` from the same release:

   ```
   Get-FileHash TeleFilter-win64.zip -Algorithm SHA256
   ```

   A matching hash only shows the download is intact. The attestation in step 2 is the stronger check.

**Read the code:** the app talks only to Telegram. The network code is in `telegram_worker.py` and the sign-in flow is in `ui/main_window.py`. The release workflow shows exactly how the program is built.

**Build it yourself:** if you prefer not to trust a prebuilt file, follow **Building a Windows exe** below, or run `python main.py` from source. Note that rebuilding produces a working but not byte-identical file, so the hashes will differ from the release.

**Keep your login private:** `telefilter_session.session` gives full access to your Telegram account. Never share it, attach it to a bug report, or commit it to Git. If you ever shared it, log out of that session in Telegram (Settings, Devices) and delete the file. If you want extra caution, use a separate Telegram account.

**Found a security problem?** Please report it privately using this repository's Security tab ("Report a vulnerability") instead of a public issue.

---




## File Structure

```
TeleFilter/
├── main.py               # Starts the application
├── app_paths.py          # Where credentials and session are saved
├── TeleFilter.ico        # Icon for the exe
├── config.py             # Loads and saves API credentials (user_config.json)
├── telegram_worker.py    # Telegram search and export logic
├── requirements.txt
├── ui/
│   ├── main_window.py    # Window, sign-in flow and search thread
│   ├── pages/
│   │   ├── credentials.py  # Sign-in screen
│   │   ├── search.py       # Search form and results table
│   │   └── reader.py       # Message reader
│   ├── sidebar.py        # Left navigation and session status
│   ├── widgets.py        # Chip input, toggle, segmented control, table
│   ├── overlays.py       # Notifications and sign-in dialogs
│   ├── theme.py          # Colors and stylesheet
│   ├── icons.py          # Drawn icons and logo loaders
│   ├── assets/           # logo_full.png, logo_mark.png
│   ├── helpers.py        # Shared helpers, error wording
│   └── bridge.py         # Passes updates from the search thread to the UI
└── 
```
