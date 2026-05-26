import time
import logging
import os
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
from load_position import load_position

from telegram_utils import (
    send_telegram_message,
    send_telegram_photo,
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
    handlers=[logging.StreamHandler()]
)

# =========================================================
# BOT STATUS FILE
# =========================================================
def set_bot_status(status):

    with open("bot_status.txt", "w") as f:
        f.write(status)

# =========================================================
# STARTUP
# =========================================================
logging.info("Trading bot starting...")

set_bot_status("RUNNING")

# =========================================================
# LOAD SAVED POSITIONS
# =========================================================
saved_position = load_position()

if saved_position:

    positions[config.SYMBOL] = saved_position

    logging.info(
        "Restored saved position."
    )

else:

    logging.info(
        "No saved position found."
    )

# =========================================================
# MULTI SYMBOL TRADING LOOP
# =========================================================
def run_symbol_bot(symbol):

    global positions

    logging.info(f"Starting bot for {symbol}")

    # =====================================================
    # CREATE EXCHANGE
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
    # CREATE RISK MANAGER
    # =====================================================
    rm = RiskManager(
        config.INITIAL_CAPITAL
    )

    # =====================================================
    # TELEGRAM START ALERT
    # =====================================================
    if config.USE_TELEGRAM:

        send_telegram_message(
            f"🟢 *BOT ONLINE*\n\n"
            f"📈 Symbol: `{symbol}`\n"
            f"✅ Exchange Connected\n"
            f"✅ Strategy Loaded\n"
            f"✅ Risk Manager Active"
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
                symbol,
                config.TIMEFRAME,
                limit=300
            )

            # =================================================
            # EMPTY DATA CHECK
            # =================================================
            if df is None or df.empty:

                logging.warning(
                    f"{symbol} No market data received."
                )

                time.sleep(5)
                continue

            # =================================================
            # SAVE MARKET DATA
            # =================================================
            safe_symbol = symbol.replace("/", "_")

            df.to_csv(
                f"market_data_{safe_symbol}.csv",
                index=False
            )

            # =================================================
            # ADD INDICATORS
            # =================================================
            df = add_indicators(df)

            df = df.dropna()

            if len(df) < 3:

                logging.warning(
                    f"{symbol} Not enough candle data."
                )

                time.sleep(5)
                continue

            # =================================================
            # CURRENT PRICE
            # =================================================
            price = df["close"].iloc[-1]

            # =================================================
            # WINDOW DATA
            # =================================================
            window_df = df.iloc[-3:]

            # =================================================
            # CURRENT POSITION
            # =================================================
            current_position = positions.get(symbol)

            # =================================================
            # UPDATE TRAILING STOP
            # =================================================
            if current_position is not None:

                current_position = update_trailing_stop(
                    current_position,
                    price
                )

                current_position = handle_exit(
                    current_position,
                    price,
                    rm
                )

                positions[symbol] = current_position

            # =================================================
            # RISK MANAGER CHECK
            # =================================================
            if not rm.can_trade():

                logging.warning(
                    f"{symbol} Cooldown active."
                )

                time.sleep(5)
                continue

            # =================================================
            # SLIPPAGE PROTECTION
            # =================================================
            if not check_slippage(
                exchange,
                symbol
            ):

                logging.warning(
                    f"{symbol} Slippage protection blocked trade."
                )

                time.sleep(5)
                continue

            # =================================================
            # HANDLE ENTRY
            # =================================================
            new_position = handle_entry(
                window_df,
                price,
                rm,
                current_position
            )

            # =================================================
            # EXECUTE TRADE
            # =================================================
            if (
                new_position is not None
                and current_position is None
            ):

                side = new_position["side"]
                amount = new_position["amount"]

                order = None

                # =============================================
                # LIVE TRADING SAFETY
                # =============================================
                if not config.ENABLE_LIVE_TRADING:

                    logging.warning(
                        f"{symbol} LIVE TRADING DISABLED"
                    )

                    time.sleep(5)
                    continue

                # =============================================
                # PAPER TRADING
                # =============================================
                if config.PAPER_TRADING:

                    logging.info(
                        f"{symbol} PAPER TRADE EXECUTED"
                    )

                    order = {
                        "paper_trade": True,
                        "side": side,
                        "price": price,
                        "amount": amount
                    }

                # =============================================
                # LIVE TRADING
                # =============================================
                else:

                    if side == "long":

                        order = place_market_order(
                            exchange,
                            symbol,
                            "buy",
                            amount
                        )

                    elif side == "short":

                        order = place_market_order(
                            exchange,
                            symbol,
                            "sell",
                            amount
                        )

                # =============================================
                # ORDER SUCCESS
                # =============================================
                if order is not None:

                    positions[symbol] = new_position

                trade_logger.log_trade(
                       symbol=symbol,
                       side=side,
                       price=price,
                       amount=amount,
                       pnl=0
                    )

                rm.record_trade()

                send_equity_update(
                        rm.capital
                    )

                    # =========================================
                    # TELEGRAM ALERT
                    # =========================================
                if config.USE_TELEGRAM:

                        trade_type = "🚀 LIVE TRADE"

                        if config.PAPER_TRADING:
                            trade_type = "🧪 PAPER TRADE"

                        send_telegram_message(
                            f"{trade_type}\n\n"
                            f"📈 Symbol: `{symbol}`\n"
                            f"📊 Side: *{side.upper()}*\n"
                            f"💰 Entry Price: `{price}`\n"
                            f"📦 Amount: `{amount}`"
                        )

                    # =========================================
                    # TRADE SCREENSHOT
                    # =========================================
                if os.path.exists(
                        "trade_chart.png"
                    ):

                        send_telegram_photo(
                            "trade_chart.png",
                            caption=(
                                f"📸 Trade Screenshot\n\n"
                                f"📈 Symbol: {symbol}\n"
                                f"📊 Side: {side.upper()}\n"
                                f"💰 Price: {price}"
                            )
                        )

                else:

                    logging.error(
                        f"{symbol} Order placement failed"
                    )

            # =================================================
            # STATUS LOGGING
            # =================================================
            logging.info(
                f"{symbol} | "
                f"Price: {price:.2f} | "
                f"Capital: {rm.capital:.2f}"
            )

            if positions.get(symbol):

                logging.info(
                    f"{symbol} Open Position: "
                    f"{positions[symbol]}"
                )

            else:

                logging.info(
                    f"{symbol} No open position."
                )

            # =================================================
            # WAIT
            # =================================================
            time.sleep(5)

        except Exception as e:

            logging.error(
                f"{symbol} Main Loop Error: {e}"
            )

            if config.USE_TELEGRAM:

                send_error_alert(
                    f"{symbol}: {str(e)}",
                    severity="HIGH"
                )

            time.sleep(5)

# =========================================================
# START ALL SYMBOL BOTS
# =========================================================
if __name__ == "__main__":

    try:

        symbols = getattr(
            config,
            "SYMBOLS",
            [config.SYMBOL]
        )

        threads = []

        for symbol in symbols:

            t = threading.Thread(
                target=run_symbol_bot,
                args=(symbol,),
                daemon=True
            )

            t.start()

            threads.append(t)

        logging.info(
            "All trading threads started."
        )

        while True:
            time.sleep(60)

    except KeyboardInterrupt:

        set_bot_status("STOPPED")

        logging.info(
            "Bot stopped manually."
        )

        if config.USE_TELEGRAM:

            send_telegram_message(
                "🔴 *BOT STOPPED MANUALLY*"
            )

    except Exception as e:

        set_bot_status("STOPPED")

        logging.error(
            f"Fatal Error: {e}"
        )

        if config.USE_TELEGRAM:

            send_telegram_message(
                f"🔴 *BOT CRASHED*\n\n"
                f"`{e}`"
            )