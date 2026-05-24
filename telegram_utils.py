import logging
import requests
import config


def send_telegram_message(text: str):
    if not config.USE_TELEGRAM:
        return

    if not config.TELEGRAM_BOT_TOKEN or not config.TELEGRAM_CHAT_ID:
        logging.warning("Telegram enabled but token/chat_id not set.")
        return

    try:
        url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": config.TELEGRAM_CHAT_ID, "text": text}
        requests.post(url, data=payload, timeout=10)
    except Exception as e:
        logging.error(f"Telegram error: {e}")
