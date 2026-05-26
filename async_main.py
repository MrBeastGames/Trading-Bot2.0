import asyncio
import logging

import config
from exchange_handler import get_exchange, fetch_ohlcv, place_order
from strategy import add_indicators, update_trailing_stop, handle_entry, handle_exit
from risk_manager import RiskManager
from telegram_utils import send_telegram_message


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


# =========================================================
# ASYNC BOT LOOP
# =========================================================
async def run_bot_async():
    exchange = get_exchange()
    if exchange is None:
        logging.error("Could not initialize exchange.")
        return

    rm = RiskManager(config.INITIAL_CAPITAL)
    position = None

    logging.info("Async bot started successfully.")

    if config.USE_TELEGRAM:
        send_telegram_message("🟢 Async bot started.")

    while True:
        try:
            # -------------------------------------------------
            # FETCH LATEST DATA
            # -------------------------------------------------
            df = fetch_ohlcv(exchange, config.SYMBOL, config.TIMEFRAME, limit=50)
            if df is None or df.empty:
                logging.warning("No OHLCV data. Retrying...")
                await asyncio.sleep(2)
                continue

            df = add_indicators(df).dropna()
            if df.empty:
                logging.warning("Indicator calculation failed. Retrying...")
                await asyncio.sleep(2)
                continue

            price = df["close"].iloc[-1]
            window_df = df.iloc[-3:]

            # -------------------------------------------------
            # STRATEGY LOGIC
            # -------------------------------------------------
            position = update_trailing_stop(position, price)
            position = handle_exit(position, price, rm)
            position = handle_entry(window_df, price, rm, position)

            # -------------------------------------------------
            # EXECUTE LIVE ORDERS (OPTIONAL)
            # -------------------------------------------------
            if not config.PAPER_TRADING and position:
                side = position["side"]
                amount = position["amount"]
                place_order(exchange, config.SYMBOL, side, amount)

            # -------------------------------------------------
            # LOGGING
            # -------------------------------------------------
            logging.info(
                f"[ASYNC] Price: {price:.2f} | Capital: {rm.capital:.2f} | "
                f"Position: {position}"
            )

            await asyncio.sleep(1)

        except Exception as e:
            logging.error(f"Async loop error: {e}")
            await asyncio.sleep(2)


# =========================================================
# ENTRY POINT
# =========================================================
if __name__ == "__main__":
    try:
        asyncio.run(run_bot_async())
    except KeyboardInterrupt:
        logging.info("Async bot stopped manually.")
        if config.USE_TELEGRAM:
            send_telegram_message("🔴 Async bot stopped manually.")
