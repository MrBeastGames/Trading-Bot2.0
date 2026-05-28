import time
import logging
import threading

import config
import trade_logger

from exchange_handler import (
    get_exchange,
    fetch_ohlcv,
    place_market_order,
    check_slippage,
)

from strategy import (
    add_indicators,
    update_trailing_stop,
    handle_entry,
    handle_exit,
)

from risk_manager import RiskManager

from load_position import (
    load_position
)

from telegram_utils import (
    send_telegram_message,
    send_equity_update,
    send_error_alert,
)

# =========================================================
# GLOBAL POSITIONS
# =========================================================
positions = {}

# =========================================================
# LOGGING
# =========================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# =========================================================
# BOT STATUS
# =========================================================
def set_bot_status(status):

    try:

        with open(
            "bot_status.txt",
            "w"
        ) as f:

            f.write(status)

    except Exception as e:

        logging.error(
            f"Status file error: {e}"
        )

# =========================================================
# RESTORE POSITIONS
# =========================================================
def restore_positions():

    try:

        saved_position = load_position()

        if saved_position:

            positions[
                config.SYMBOL
            ] = saved_position

            logging.info(
                "Restored saved position."
            )

        else:

            logging.info(
                "No saved position found."
            )

    except Exception as e:

        logging.error(
            f"Restore position error: {e}"
        )

# =========================================================
# RUN SYMBOL BOT
# =========================================================
def run_symbol_bot(symbol):

    global positions

    logging.info(
        f"Starting bot for {symbol}"
    )

    # =====================================================
    # CONNECT EXCHANGE
    # =====================================================
    exchange = get_exchange()

    if not exchange:

        logging.error(
            f"{symbol} CONNECTION FAILED"
        )

        return

    logging.info(
        f"{symbol} CONNECTED SUCCESSFULLY"
    )

    # =====================================================
    # RISK MANAGER
    # =====================================================
    rm = RiskManager(
        config.INITIAL_CAPITAL
    )

    # =====================================================
    # TELEGRAM STARTUP
    # =====================================================
    if config.USE_TELEGRAM:

        try:

            send_telegram_message(
                f"🟢 BOT ONLINE\n\n"
                f"📈 Symbol: {symbol}"
            )

        except Exception:
            pass

    # =====================================================
    # MAIN LOOP
    # =====================================================
    while True:

        try:

            # =================================================
            # FETCH OHLCV
            # =================================================
            try:

                df = fetch_ohlcv(
                    exchange,
                    symbol,
                    config.TIMEFRAME,
                    limit=300
                )

            except Exception as e:

                logging.error(
                    f"{symbol} fetch error: {e}"
                )

                time.sleep(
                    config.ERROR_SLEEP
                )

                continue

            # =================================================
            # EMPTY CHECK
            # =================================================
            if df is None or df.empty:

                logging.warning(
                    f"{symbol} No market data."
                )

                time.sleep(
                    config.MAIN_LOOP_SLEEP
                )

                continue

            # =================================================
            # SAVE MARKET DATA
            # =================================================
            try:

                safe_symbol = (
                    symbol.replace("/", "_")
                )

                df.to_csv(
                    f"market_data_{safe_symbol}.csv",
                    index=False
                )

                df.to_csv(
                    "market_data.csv",
                    index=False
                )

            except Exception as e:

                logging.error(
                    f"CSV save error: {e}"
                )

            # =================================================
            # ADD INDICATORS
            # =================================================
            df = add_indicators(df)

            df = df.dropna()

            if len(df) < 3:

                logging.warning(
                    f"{symbol} Not enough candles."
                )

                time.sleep(
                    config.MAIN_LOOP_SLEEP
                )

                continue

            # =================================================
            # PRICE
            # =================================================
            price = (
                df["close"].iloc[-1]
            )

            window_df = df.iloc[-3:]

            # =================================================
            # CURRENT POSITION
            # =================================================
            current_position = (
                positions.get(symbol)
            )

            # =================================================
            # UPDATE POSITION
            # =================================================
            if current_position is not None:

                current_position = (
                    update_trailing_stop(
                        current_position,
                        price
                    )
                )

                current_position = (
                    handle_exit(
                        current_position,
                        price,
                        rm
                    )
                )

                positions[symbol] = (
                    current_position
                )

            # =================================================
            # RISK CHECK
            # =================================================
            if not rm.can_trade():

                logging.warning(
                    f"{symbol} Cooldown active."
                )

                time.sleep(
                    config.MAIN_LOOP_SLEEP
                )

                continue

            # =================================================
            # SLIPPAGE CHECK
            # =================================================
            if not check_slippage(
                exchange,
                symbol
            ):

                logging.warning(
                    f"{symbol} Slippage blocked."
                )

                time.sleep(
                    config.MAIN_LOOP_SLEEP
                )

                continue

            # =================================================
            # HANDLE ENTRY
            # =================================================
            new_position = (
                handle_entry(
                    window_df,
                    price,
                    rm,
                    current_position
                )
            )

            # =================================================
            # EXECUTE TRADE
            # =================================================
            if (
                new_position is not None
                and current_position is None
            ):

                side = (
                    new_position["side"]
                )

                amount = (
                    new_position["amount"]
                )

                order = None

                # =============================================
                # PAPER TRADING
                # =============================================
                if config.PAPER_TRADING:

                    logging.info(
                        f"{symbol} PAPER TRADE EXECUTED"
                    )

                    order = {
                        "paper_trade": True
                    }

                # =============================================
                # LIVE TRADING
                # =============================================
                else:

                    try:

                        if side == "long":

                            order = (
                                place_market_order(
                                    exchange,
                                    symbol,
                                    "buy",
                                    amount
                                )
                            )

                        elif side == "short":

                            order = (
                                place_market_order(
                                    exchange,
                                    symbol,
                                    "sell",
                                    amount
                                )
                            )

                    except Exception as e:

                        logging.error(
                            f"{symbol} order error: {e}"
                        )

                # =============================================
                # ORDER SUCCESS
                # =============================================
                if order is not None:

                    new_position["symbol"] = symbol

                    positions[symbol] = new_position

                    try:

                        # =====================================
                        # LOG TRADE
                        # =====================================
                        trade_logger.log_trade(
                            symbol=symbol,
                            side=side,
                            price=price,
                            amount=amount,
                            pnl=0
                        )

                        # =====================================
                        # SAVE POSITION
                        # =====================================
                        trade_logger.save_position(
                            symbol=symbol,
                            side=side,
                            entry_price=price,
                            amount=amount
                        )

                        logging.info(
                            f"{symbol} position saved."
                        )

                    except Exception as e:

                        logging.error(
                            f"Trade logger error: {e}"
                        )

                    # =========================================
                    # RECORD TRADE
                    # =========================================
                    try:

                        rm.record_trade()

                    except Exception:
                        pass

                    # =========================================
                    # EQUITY UPDATE
                    # =========================================
                    try:

                        send_equity_update(
                            rm.capital
                        )

                    except Exception:
                        pass

                    # =========================================
                    # TELEGRAM ALERT
                    # =========================================
                    if config.USE_TELEGRAM:

                        try:

                            send_telegram_message(
                                f"📈 NEW TRADE\n\n"
                                f"Symbol: {symbol}\n"
                                f"Side: {side}\n"
                                f"Price: {price}"
                            )

                        except Exception:
                            pass

            # =================================================
            # STATUS LOG
            # =================================================
            logging.info(
                f"{symbol} | "
                f"Price: {price:.5f}"
            )

            # =================================================
            # WAIT
            # =================================================
            time.sleep(
                config.MAIN_LOOP_SLEEP
            )

        except Exception as e:

            logging.error(
                f"{symbol} Main Loop Error: {e}"
            )

            try:

                send_error_alert(
                    f"{symbol}: {str(e)}",
                    severity="HIGH"
                )

            except Exception:
                pass

            time.sleep(
                config.ERROR_SLEEP
            )

# =========================================================
# START BOT
# =========================================================
def start_bot():

    logging.info(
        "Trading bot starting..."
    )

    set_bot_status("RUNNING")

    restore_positions()

    symbols = getattr(
        config,
        "SYMBOLS",
        [config.SYMBOL]
    )

    threads = []

    for symbol in symbols:

        logging.info(
            f"Launching thread for {symbol}"
        )

        t = threading.Thread(
            target=run_symbol_bot,
            args=(symbol,),
            daemon=True
        )

        t.start()

        threads.append(t)

        logging.info(
            f"Waiting "
            f"{config.PAIR_STARTUP_DELAY}s "
            f"before next pair..."
        )

        time.sleep(
            config.PAIR_STARTUP_DELAY
        )

    logging.info(
        "All trading threads started."
    )

    while True:

        time.sleep(60)

# =========================================================
# MAIN ENTRY
# =========================================================
if __name__ == "__main__":

    try:

        start_bot()

    except KeyboardInterrupt:

        set_bot_status("STOPPED")

        logging.info(
            "Bot stopped manually."
        )

    except Exception as e:

        set_bot_status("STOPPED")

        logging.error(
            f"Fatal Error: {e}"
        )
