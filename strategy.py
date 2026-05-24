import logging
import requests
import pandas as pd
import numpy as np

import config

from exchange_handler import (
    place_market_order,
    get_exchange
)

# =========================================================
# CREATE EXCHANGE
# =========================================================
exchange = get_exchange()


# =========================================================
# TELEGRAM
# =========================================================
def send_telegram_message(message: str):

    if not config.USE_TELEGRAM:
        return

    if not config.TELEGRAM_BOT_TOKEN:
        logging.error("Telegram bot token missing")
        return

    if not config.TELEGRAM_CHAT_ID:
        logging.error("Telegram chat ID missing")
        return

    url = (
        f"https://api.telegram.org/bot"
        f"{config.TELEGRAM_BOT_TOKEN}/sendMessage"
    )

    payload = {
        "chat_id": config.TELEGRAM_CHAT_ID,
        "text": message,
    }

    try:

        response = requests.post(
            url,
            json=payload
        )

        if response.status_code != 200:

            logging.error(
                f"Telegram Error: {response.text}"
            )

    except Exception as e:

        logging.error(
            f"Telegram Exception: {e}"
        )


# =========================================================
# INDICATORS
# =========================================================
def add_indicators(df: pd.DataFrame):

    df = df.copy()

    # SMA
    df["short_sma"] = (
        df["close"]
        .rolling(9)
        .mean()
    )

    df["long_sma"] = (
        df["close"]
        .rolling(21)
        .mean()
    )

    # RSI
    delta = df["close"].diff()

    gain = (
        delta.where(delta > 0, 0)
        .rolling(14)
        .mean()
    )

    loss = (
        -delta.where(delta < 0, 0)
        .rolling(14)
        .mean()
    )

    rs = gain / loss.replace(0, np.nan)

    df["rsi"] = 100 - (
        100 / (1 + rs)
    )

    # ATR
    high_low = (
        df["high"] - df["low"]
    )

    high_close = (
        df["high"] - df["close"].shift()
    ).abs()

    low_close = (
        df["low"] - df["close"].shift()
    ).abs()

    tr = pd.concat(
        [high_low, high_close, low_close],
        axis=1
    ).max(axis=1)

    df["atr"] = (
        tr.rolling(14).mean()
    )

    # Higher timeframe SMA
    df["htf_sma"] = (
        df["close"]
        .rolling(50)
        .mean()
    )

    return df


# =========================================================
# TRAILING STOP
# =========================================================
def update_trailing_stop(position, price):

    if position is None:
        return position

    if position["side"] == "long":

        new_stop = (
            price *
            (1 - config.TRAILING_STOP_PCT)
        )

        if new_stop > position["stop"]:
            position["stop"] = new_stop

    elif position["side"] == "short":

        new_stop = (
            price *
            (1 + config.TRAILING_STOP_PCT)
        )

        if new_stop < position["stop"]:
            position["stop"] = new_stop

    return position


# =========================================================
# EXIT LOGIC
# =========================================================
def handle_exit(position, price, rm):

    if position is None:
        return None

    side = position["side"]
    entry = position["entry_price"]
    amount = position["amount"]

    stop = position["stop"]
    tp = position["take_profit"]

    closed = False

    # LONG EXIT
    if side == "long":

        if price <= stop or price >= tp:

            pnl = amount * (
                price - entry
            )

            if config.PAPER_TRADING:
                rm.capital += pnl

            logging.info(
                f"LONG EXIT at {price:.2f} | "
                f"PnL: {pnl:.2f}"
            )

            send_telegram_message(
                f"📉 LONG EXIT at "
                f"{price:.2f} | "
                f"PnL: {pnl:.2f}"
            )

            closed = True

    # SHORT EXIT
    elif side == "short":

        if price >= stop or price <= tp:

            pnl = amount * (
                entry - price
            )

            if config.PAPER_TRADING:
                rm.capital += pnl

            logging.info(
                f"SHORT EXIT at {price:.2f} | "
                f"PnL: {pnl:.2f}"
            )

            send_telegram_message(
                f"📈 SHORT EXIT at "
                f"{price:.2f} | "
                f"PnL: {pnl:.2f}"
            )

            closed = True

    return None if closed else position


# =========================================================
# FILTERS
# =========================================================
def _passes_filters(row_now):

    if pd.isna(row_now["atr"]):
        return False

    if pd.isna(row_now["htf_sma"]):
        return False

    atr_ratio = (
        row_now["atr"] /
        row_now["close"]
    )

    if atr_ratio < 0.002:
        return False

    return True


# =========================================================
# ENTRY LOGIC
# =========================================================
def handle_entry(df, price, rm, position):

    if position is not None:
        return position

    row_now = df.iloc[-1]
    row_prev = df.iloc[-2]

    short_now = row_now["short_sma"]
    long_now = row_now["long_sma"]

    short_prev = row_prev["short_sma"]
    long_prev = row_prev["long_sma"]

    rsi_now = row_now["rsi"]
    htf_sma_now = row_now["htf_sma"]

    if any(pd.isna([
        short_now,
        long_now,
        short_prev,
        long_prev,
        rsi_now,
        htf_sma_now
    ])):
        return None

    if not _passes_filters(row_now):
        return None

    # =====================================================
    # LONG ENTRY
    # =====================================================
    if (
        short_now > long_now
        and short_prev <= long_prev
        and rsi_now < 70
        and price > htf_sma_now
    ):

        stop = (
            price *
            (1 - config.STOP_LOSS_PCT)
        )

        amount = rm.get_position_size(
            price,
            stop
        )

        if amount > 0:

            if config.PAPER_TRADING:
                rm.capital -= amount * price

            # REAL BUY ORDER
            if not config.PAPER_TRADING:

                place_market_order(
                    exchange,
                    config.SYMBOL,
                    "buy",
                    amount
                )

            pos = {
                "side": "long",
                "entry_price": price,
                "amount": amount,
                "stop": stop,
                "take_profit": (
                    price *
                    (1 + config.TAKE_PROFIT_PCT)
                ),
            }

            logging.info(
                f"LONG ENTRY at "
                f"{price:.2f} | "
                f"Size: {amount}"
            )

            send_telegram_message(
                f"📈 LONG ENTRY at "
                f"{price:.2f} | "
                f"Size: {amount}"
            )

            return pos

    # =====================================================
    # SHORT ENTRY
    # =====================================================
    if (
        short_now < long_now
        and short_prev >= long_prev
        and rsi_now > 30
        and price < htf_sma_now
    ):

        stop = (
            price *
            (1 + config.STOP_LOSS_PCT)
        )

        amount = rm.get_position_size(
            price,
            stop
        )

        if amount > 0:

            if config.PAPER_TRADING:
                rm.capital -= amount * price

            # REAL SELL ORDER
            if not config.PAPER_TRADING:

                place_market_order(
                    exchange,
                    config.SYMBOL,
                    "sell",
                    amount
                )

            pos = {
                "side": "short",
                "entry_price": price,
                "amount": amount,
                "stop": stop,
                "take_profit": (
                    price *
                    (1 - config.TAKE_PROFIT_PCT)
                ),
            }

            logging.info(
                f"SHORT ENTRY at "
                f"{price:.2f} | "
                f"Size: {amount}"
            )

            send_telegram_message(
                f"📉 SHORT ENTRY at "
                f"{price:.2f} | "
                f"Size: {amount}"
            )

            return pos

    return None