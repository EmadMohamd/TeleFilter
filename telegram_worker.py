import os
import json
import logging
from datetime import datetime, timezone
from telethon import TelegramClient

# Configure logging format and stream output
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("TelegramWorker")

CONFIG_FILE = "user_config.json"

def load_config():
    """Loads user configuration from a local JSON file."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.error("Failed to parse config file: %s", e)
    return {}


class TelegramWorker:
    @staticmethod
    async def get_client():
        # Load config dynamically every time the client is requested
        config = load_config()
        api_id = config.get("api_id")
        api_hash = config.get("api_hash")
        session_name = config.get("session_name", "my_session")

        if not api_id or not api_hash:
            logger.error("API_ID and API_HASH are missing from user_config.json.")
            raise ValueError("API_ID and API_HASH must be configured in the app settings.")

        logger.info("Initializing TelegramClient session: %s", session_name)
        client = TelegramClient(session_name, int(api_id), api_hash)
        await client.connect()

        if not await client.is_user_authorized():
            logger.error("Telegram session is unauthorized.")
            raise Exception(
                "Telegram session is unauthorized. Please log in interactively."
            )

        logger.info("Telegram client successfully connected and authorized.")
        return client

    @staticmethod
    async def search_channels(search_terms, target_channels, date_from, date_to, check_cancelled, update_status,
                              case_sensitive=False):
        """
        Searches subscribed channels with optimized filters, supporting case sensitivity,
        date ranges, and interruption checks.
        """
        logger.info("Starting channel search workflow with terms: %s", search_terms)
        
        try:
            client = await TelegramWorker.get_client()
        except Exception as e:
            logger.exception("Failed to initialize Telegram client during search: %s", e)
            raise

        matched_results = []

        try:
            update_status("Fetching subscribed dialogs...")
            logger.info("Fetching subscribed dialogs from Telegram...")
            dialogs = []
            async for dialog in client.iter_dialogs():
                if dialog.is_channel or dialog.is_group:
                    dialogs.append(dialog)

            # Filter dialogs if specific channels are requested
            if target_channels:
                logger.info("Filtering dialogs against target channels: %s", target_channels)
                filtered_dialogs = []
                normalized_targets = [tc.lower().replace("@", "") for tc in target_channels]

                for d in dialogs:
                    title_lower = d.title.lower()
                    username_lower = (getattr(d.entity, 'username', None) or "").lower()

                    if any(nt in title_lower or (username_lower and nt in username_lower) for nt in normalized_targets):
                        filtered_dialogs.append(d)
                dialogs = filtered_dialogs

            total_channels = len(dialogs)
            logger.info("Found %d matching channels/groups to scan.", total_channels)
            
            if total_channels == 0:
                logger.warning("No channels matched the filter criteria.")
                return []

            for index, dialog in enumerate(dialogs):
                if check_cancelled():
                    logger.info("Search operation cancelled by user.")
                    break

                channel_name = dialog.title
                ent_username = getattr(dialog.entity, 'username', None)
                channel_username = f"@{ent_username}" if ent_username else "Private/No Username"

                status_msg = f"Scanning ({index + 1}/{total_channels}): {channel_name}"
                update_status(status_msg)
                logger.debug(status_msg)

                # Iterate through messages in the channel/group efficiently
                async for message in client.iter_messages(dialog.entity):
                    if check_cancelled():
                        break

                    if not message.text:
                        continue

                    # Handle message dates with timezone awareness
                    msg_date = message.date
                    if msg_date.tzinfo is None:
                        msg_date = msg_date.replace(tzinfo=timezone.utc)

                    # Stop looking if messages are older than the 'from' limit
                    if date_from and msg_date < date_from:
                        break

                    # Skip messages newer than 'to' limit
                    if date_to and msg_date > date_to:
                        continue

                    # Check keyword matches based on case-sensitivity choice
                    msg_text = message.text
                    matched_terms_found = []

                    for term in search_terms:
                        if case_sensitive:
                            if term in msg_text:
                                matched_terms_found.append(term)
                        else:
                            if term.lower() in msg_text.lower():
                                matched_terms_found.append(term)

                    if matched_terms_found:
                        link = ""
                        if ent_username:
                            link = f"https://t.me/{ent_username}/{message.id}"

                        matched_results.append({
                            "matched_terms": matched_terms_found,
                            "channel": channel_name,
                            "username": channel_username,
                            "date": msg_date.strftime("%Y-%m-%d %H:%M"),
                            "text": msg_text,
                            "link": link,
                            "msg_id": message.id
                        })

            logger.info("Search completed successfully. Total matches found: %d", len(matched_results))

        except Exception as e:
            logger.error("An error occurred during channel search execution: %s", e, exc_info=True)
            raise
        finally:
            logger.info("Disconnecting Telegram client.")
            await client.disconnect()

        return matched_results

    @staticmethod
    def export_to_file(file_path, results_data):
        """Backwards compatibility helper for file export."""
        logger.info("Exporting %d results to file: %s", len(results_data), file_path)
        try:
            if file_path.lower().endswith(".txt"):
                with open(file_path, "w", encoding="utf-8") as f:
                    for r in results_data:
                        f.write(f"[{r['date']}] {r['channel']} ({r['username']})\n")
                        f.write(f"Matched    : {', '.join(r['matched_terms'])}\n")
                        f.write(f"Link       : {r['link']}\n")
                        f.write("-" * 60 + "\n")
                        f.write(f"{r['text']}\n")
                        f.write("=" * 60 + "\n\n")
            else:
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(results_data, f, ensure_ascii=False, indent=2)
            logger.info("File export completed successfully.")
        except Exception as e:
            logger.error("Failed to export results to file %s: %s", file_path, e, exc_info=True)
            raise