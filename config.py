import os
import json

CONFIG_FILE = "user_config.json"

def load_config():
    """Loads Telegram API configuration from local JSON file."""
    if not os.path.exists(CONFIG_FILE):
        return {}
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_config(api_id, api_hash, session_name="telethon_session"):
    """Saves Telegram API configuration to local JSON file."""
    try:
        data = {
            "api_id": str(api_id).strip(),
            "api_hash": str(api_hash).strip(),
            "session_name": str(session_name).strip()
        }
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        return True
    except Exception:
        return False

def validate_config(config):
    """Checks if the config contains valid non-empty credentials."""
    api_id = config.get("api_id")
    api_hash = config.get("api_hash")
    if not api_id or not api_hash:
        return False
    try:
        int(api_id)
        return len(str(api_hash).strip()) > 5
    except ValueError:
        return False