import time
import logging

import config
import trade_logger

from exchange_handler import (
    get_exchange,
    fetch_ohlcv,
    place_market_order,
)

from strategy import (
    add_indicators,
    update_trailing_stop,
    handle_entry,
    handle_exit,
)

from risk_manager import RiskManager
from telegram_utils import send_telegram_message


# =========================================================
# LOGGING
# =========================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


# =========================================================
# LIVE TRADING LOOP
# =========================================================
def run_bot():

    # =====================================================
    # CREATE EXCHANGE
    # =====================================================
    exchange = get_exchange()

    if not exchange:
        logging.error("CONNECTION FAILED")
        return

    logging.info("CONNECTED SUCCESSFULLY")

    # =====================================================
    # TEST BALANCE
    # =====================================================
    try:
        balance = exchange.fetch_balance()
        logging.info("Balance fetched successfully")
        print(balance)

    except Exception as e:
        logging.error(f"Balance Error: {e}")

    # =====================================================
    # TEST ORDER
    # =====================================================
    try:

        response = place_market_order(
            exchange,
            config.SYMBOL,
            "buy",
            0.001
        )

        if response:
          logging.info(f"Order placed successfully: {response}")
        else:
            logging.error("Order placement failed")

    except Exception as e:

        logging.error("Test Order Error:")
        logging.error(str(e))

        if hasattr(e, "args") and len(e.args) > 0:
            logging.error(
                f"Error details: {e.args[0]}"
            )

    # =====================================================
    # CREATE RISK MANAGER
    # =====================================================
    rm = RiskManager(
        config.INITIAL_CAPITAL
    )

    # =====================================================
    # CURRENT POSITION
    # =====================================================
    position = None

    logging.info("Trading bot started.")

    # =====================================================
    # TELEGRAM START MESSAGE
    # =====================================================
    if config.USE_TELEGRAM:

        send_telegram_message(
            "🟢 Trading bot started."
        )

    # =====================================================
    # MAIN LOOP
    # =====================================================
    while True:

        try:

            # =================================================
            # FETCH MARKET DATA
            # =================================================
            df = fetch_ohlcv(
                exchange,
                config.SYMBOL,
                config.TIMEFRAME,
                limit=100
            )

            if df is None or df.empty:

                logging.warning(
                    "No market data received."
                )

                time.sleep(5)
                continue

            # =================================================
            # ADD INDICATORS
            # =================================================
            df = add_indicators(df)
            df = df.dropna()

            if len(df) < 3:

                logging.warning(
                    "Not enough candle data."
                )

                time.sleep(5)
                continue

            # =================================================
            # CURRENT PRICE
            # =================================================
            price = df["close"].iloc[-1]

            # =================================================
            # LAST 3 CANDLES
            # =================================================
            window_df = df.iloc[-3:]

            # =================================================
            # UPDATE TRAILING STOP
            # =================================================
            position = update_trailing_stop(
                position,
                price
            )

            # =================================================
            # HANDLE EXIT
            # =================================================
            position = handle_exit(
                position,
                price,
                rm
            )

            # =================================================
            # HANDLE ENTRY
            # =================================================
            new_position = handle_entry(
                window_df,
                price,
                rm,
                position
            )

            # =================================================
            # EXECUTE ORDER
            # =================================================
            if (
                new_position is not None
                and position is None
            ):

                side = new_position["side"]
                amount = new_position["amount"]

                # =============================================
                # LONG POSITION
                # =============================================
                if side == "long":

                    place_market_order(
                        exchange,
                        config.SYMBOL,
                        "buy",
                        amount
                    )

                # =============================================
                # SHORT POSITION
                # =============================================
                elif side == "short":

                    place_market_order(
                        exchange,
                        config.SYMBOL,
                        "sell",
                        amount
                    )

                # =============================================
                # LOG TRADE
                # =============================================
                trade_logger.log_trade(
                    side=side,
                    price=price,
                    amount=amount
                )

                # =============================================
                # TELEGRAM ALERT
                # =============================================
                if config.USE_TELEGRAM:

                    send_telegram_message(
                        f"✅ {side.upper()} ORDER EXECUTED\n"
                        f"Price: {price}\n"
                        f"Amount: {amount}"
                    )

                # =============================================
                # SAVE POSITION
                # =============================================
                position = new_position

            # =================================================
            # STATUS LOGGING
            # =================================================
            logging.info(
                f"Price: {price:.2f} | "
                f"Capital: {rm.capital:.2f}"
            )

            if position:

                logging.info(
                    f"Open Position: {position}"
                )

            else:

                logging.info(
                    "No open position."
                )

            # =================================================
            # WAIT
            # =================================================
            time.sleep(5)

        except Exception as e:

            logging.error(
                f"Main Loop Error: {e}"
            )

            if config.USE_TELEGRAM:

                send_telegram_message(
                    f"⚠️ Bot Error:\n{e}"
                )

            time.sleep(5)


# =========================================================
# START BOT
# =========================================================
if __name__ == "__main__":

    try:

        run_bot()

    except KeyboardInterrupt:

        logging.info(
            "Bot stopped manually."
        )

        if config.USE_TELEGRAM:

            send_telegram_message(
                "🔴 Bot stopped manually."
            )

    except Exception as e:

        logging.error(
            f"Fatal Error: {e}"
        )

        if config.USE_TELEGRAM:

            send_telegram_message(
                f"🔴 Bot crashed:\n{e}"
            )