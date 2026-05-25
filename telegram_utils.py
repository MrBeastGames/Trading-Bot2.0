import requests
import config
import pandas as pd
import os
from datetime import datetime


# =========================================================
# SEND TEXT MESSAGE
# =========================================================
def send_telegram_message(message):

    if not config.USE_TELEGRAM:
        return

    url = (
        f"https://api.telegram.org/bot"
        f"{config.TELEGRAM_BOT_TOKEN}/sendMessage"
    )

    payload = {
        "chat_id": config.TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }

    try:

        requests.post(
            url,
            json=payload,
            timeout=10
        )

    except Exception as e:

        print(
            f"Telegram Error: {e}"
        )


# =========================================================
# SEND PHOTO
# =========================================================
def send_telegram_photo(
    image_path,
    caption=""
):

    if not os.path.exists(image_path):
        return

    url = (
        f"https://api.telegram.org/bot"
        f"{config.TELEGRAM_BOT_TOKEN}/sendPhoto"
    )

    try:

        with open(image_path, "rb") as photo:

            requests.post(
                url,
                data={
                    "chat_id": config.TELEGRAM_CHAT_ID,
                    "caption": caption,
                    "parse_mode": "Markdown"
                },
                files={
                    "photo": photo
                },
                timeout=20
            )

    except Exception as e:

        print(
            f"Telegram Photo Error: {e}"
        )


# =========================================================
# SEND DAILY REPORT
# =========================================================
def send_daily_report():

    if not os.path.exists("trades.csv"):
        return

    try:

        df = pd.read_csv("trades.csv")

        if df.empty:
            return

        total_trades = len(df)

        total_pnl = df["pnl"].sum()

        wins = len(
            df[df["pnl"] > 0]
        )

        winrate = (
            wins / total_trades
        ) * 100

        message = (
            "📅 *DAILY REPORT*\n\n"
            f"📊 Trades: `{total_trades}`\n"
            f"💰 Total PnL: `{total_pnl:.2f}`\n"
            f"🏆 Winrate: `{winrate:.2f}%`\n"
            f"🕒 Time: `{datetime.now()}`"
        )

        send_telegram_message(
            message
        )

    except Exception as e:

        send_telegram_message(
            f"🚨 DAILY REPORT ERROR\n\n`{e}`"
        )


# =========================================================
# SEND EQUITY UPDATE
# =========================================================
def send_equity_update(capital):

    message = (
        "💰 *EQUITY UPDATE*\n\n"
        f"🏦 Current Equity: `{capital:.2f} USDT`"
    )

    send_telegram_message(message)


# =========================================================
# SEND ERROR ALERT
# =========================================================
def send_error_alert(
    error,
    severity="LOW"
):

    emoji = "⚠️"

    if severity == "HIGH":
        emoji = "🚨"

    elif severity == "CRITICAL":
        emoji = "🔥"

    message = (
        f"{emoji} *BOT ERROR*\n\n"
        f"Severity: `{severity}`\n"
        f"Error: `{error}`"
    )

    send_telegram_message(message)