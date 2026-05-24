import asyncio
import logging
from datetime import datetime

import config
from exchange_handler import get_exchange, fetch_ohlcv
from risk_manager import RiskManager
from strategy import add_indicators, update_trailing_stop, handle_exit, handle_entry


logging.basicConfig(level=logging.INFO)


async def async_live_trading_loop():
    exchange = get_exchange()
    rm = RiskManager(config.INITIAL_CAPITAL)
    position = None

    print(f"⚡ Async Trading Bot | {config.SYMBOL} {config.TIMEFRAME}")

    while True:
        try:
            df = fetch_ohlcv(exchange, config.SYMBOL, config.TIMEFRAME)
            df = add_indicators(df)
            price = df["close"].iloc[-1]

            if position:
                if position["side"] == "long":
                    unrealized = position["amount"] * (price - position["entry_price"])
                else:
                    unrealized = position["amount"] * (position["entry_price"] - price)
                rm.update(rm.capital + unrealized)
            else:
                rm.update(rm.capital)

            position = update_trailing_stop(position, price)
            position = handle_exit(position, price, rm)
            position = handle_entry(df, price, rm, position)

            print(
                f"{datetime.now().strftime('%H:%M:%S')} | "
                f"Price: {price:.2f} | "
                f"Capital: {rm.capital:.2f}"
            )

            await asyncio.sleep(60)

        except Exception as e:
            logging.error(f"Error: {e}")
            await asyncio.sleep(10)


if __name__ == "__main__":
    asyncio.run(async_live_trading_loop())
