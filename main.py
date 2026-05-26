import time
import logging
import os

from streamlit import form

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

position = None

# =========================================================
# LOGGING
# =========================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
    # =====================================================
    # LOAD SAVED POSITION
    # =====================================================
position = load_position()
if position:

        logging.info(
            "Restored saved position."
        )

else:

        logging.info(
            "No saved position found."
        )

logging.info(
    "Trading bot started."
)
# =========================================================
# LIVE TRADING LOOP
# =========================================================
def run_bot():

    global position

    # =====================================================
    # CREATE EXCHANGE
    # =====================================================
    exchange = get_exchange()

    if not exchange:

        logging.error("CONNECTION FAILED")

        return

    logging.info("CONNECTED SUCCESSFULLY")

    # =====================================================
    # FETCH FUTURES BALANCE
    # =====================================================
    try:

        balance = exchange.fetch_balance({
            "type": "swap"
        })

        logging.info(
            "Balance fetched successfully"
        )

        print(balance)

        if config.USE_TELEGRAM:

            send_telegram_message(
                f"💰 *LIVE BALANCE*\n\n"
                f"`{balance}`"
            )

    except Exception as e:

        logging.error(
            f"Balance Error: {e}"
        )

    # =====================================================
    # CREATE RISK MANAGER
    # =====================================================
    rm = RiskManager(
        config.INITIAL_CAPITAL
    )

    # =====================================================
    # TELEGRAM START MESSAGE
    # =====================================================
    if config.USE_TELEGRAM:

        send_telegram_message(
            "🟢 *TRADING BOT ONLINE*\n\n"
            "✅ Exchange Connected\n"
            "✅ Strategy Loaded\n"
            "✅ Risk Manager Active\n"
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
                limit=300
            )

            # =================================================
            # EMPTY DATA CHECK
            # =================================================
            if df is None or df.empty:

                logging.warning(
                    "No market data received."
                )

                time.sleep(5)

                continue

            # =================================================
            # SAVE MARKET DATA
            # =================================================
            df.to_csv(
                "market_data.csv",
                index=False
            )

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
            if position is not None:

                position = update_trailing_stop(
                    position,
                    price
                )

                position = handle_exit(
                    position,
                    price,
                    rm
                )

            # =================================================
            # RISK MANAGER CHECK
            # =================================================
            if not rm.can_trade():

                logging.warning(
                    "Cooldown active. Waiting..."
                )

                time.sleep(5)

                continue

            # =================================================
            # SLIPPAGE PROTECTION
            # =================================================
            if not check_slippage(
                exchange,
                config.SYMBOL
            ):

                logging.warning(
                    "Slippage protection blocked trade."
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

                order = None

                # =============================================
                # LIVE TRADING SAFETY
                # =============================================
                if not config.ENABLE_LIVE_TRADING:

                    logging.warning(
                        "LIVE TRADING DISABLED"
                    )

                    time.sleep(5)

                    continue

                # =============================================
                # PAPER TRADING MODE
                # =============================================
                if config.PAPER_TRADING:

                    logging.info(
                        "PAPER TRADE EXECUTED"
                    )

                    order = {
                        "paper_trade": True,
                        "side": side,
                        "price": price,
                        "amount": amount
                    }

                # =============================================
                # LIVE TRADING MODE
                # =============================================
                else:

                    if side == "long":

                        order = place_market_order(
                            exchange,
                            config.SYMBOL,
                            "buy",
                            amount
                        )

                    elif side == "short":

                        order = place_market_order(
                            exchange,
                            config.SYMBOL,
                            "sell",
                            amount
                        )

                # =============================================
                # ORDER SUCCESS
                # =============================================
                if order is not None:

                    position = new_position

                    trade_logger.log_trade(
                        side=side,
                        price=price,
                        amount=amount
                    )

                    rm.record_trade()

                    send_equity_update(
                        rm.capital
                    )

                    # =========================================
                    # TELEGRAM PHOTO
                    # =========================================
                    if os.path.exists(
                        "trade_chart.png"
                    ):

                        send_telegram_photo(
                            "trade_chart.png",
                            caption=(
                                f"📸 Trade Screenshot\n\n"
                                f"📈 Pair: {config.SYMBOL}\n"
                                f"📊 Side: {side.upper()}\n"
                                f"💰 Price: {price}"
                            )
                        )

                    # =========================================
                    # TELEGRAM ALERT
                    # =========================================
                    if config.USE_TELEGRAM:

                        trade_type = (
                            "🚀 LIVE TRADE"
                        )

                        if config.PAPER_TRADING:

                            trade_type = (
                                "🧪 PAPER TRADE"
                            )

                        send_telegram_message(
                            f"{trade_type}\n\n"
                            f"📈 Pair: `{config.SYMBOL}`\n"
                            f"📊 Side: *{side.upper()}*\n"
                            f"💰 Entry Price: `{price}`\n"
                            f"📦 Amount: `{amount}`"
                        )

                else:

                    logging.error(
                        "Order placement failed"
                    )

            # =================================================
            # STATUS LOGGING
            # =================================================
            logging.info(
                f"Price: {price:.2f} | "
                f"Capital: {rm.capital:.2f}"
            )

            if position is not None:

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

                send_error_alert(
                    str(e),
                    severity="HIGH"
                )

            time.sleep(5)