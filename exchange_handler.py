import ccxt
import config
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)

# =====================================================
# CONNECT EXCHANGE
# =====================================================

def get_exchange():

    try:

        exchange = ccxt.bitget({
            "apiKey": config.API_KEY,
            "secret": config.API_SECRET,
            "password": config.API_PASSWORD,

            "options": {
                "defaultType": "swap",
                "defaultMarginMode": "cross",
                "defaultMarginCoin": "USDT",
                "createMarketBuyOrderRequiresPrice": False
            }
        })

        exchange.load_markets()

        # ⚠️ IMPORTANT FIX: set swap-specific params
        exchange.options["defaultMarginCoin"] = "USDT"

        logging.info("BITGET CONNECTED")

        return exchange

    except Exception as e:

        logging.error(f"CONNECTION FAILED: {e}")
        return None

# =====================================================
# FETCH OHLCV
# =====================================================
def fetch_ohlcv(
    exchange,
    symbol,
    timeframe,
    limit=100
):

    try:

        candles = exchange.fetch_ohlcv(
            symbol,
            timeframe,
            limit=limit
        )

        df = pd.DataFrame(
            candles,
            columns=[
                "timestamp",
                "open",
                "high",
                "low",
                "close",
                "volume"
            ]
        )

        return df

    except Exception as e:

        logging.error(f"OHLCV ERROR: {e}")

        return None


# =====================================================
# PLACE MARKET ORDER
# =====================================================
def place_market_order(exchange, symbol, side, amount):

    try:

        params = {
            "marginCoin": "USDT",   # 🔥 MUST BE HERE
            "marginMode": "cross"
        }

        order = exchange.create_order(
            symbol=symbol,
            type="market",
            side=side,
            amount=amount,
            params=params
        )

        print("ORDER SUCCESS")
        print(order)

        return order

    except Exception as e:

        print("ORDER ERROR")
        print(e)
        return None

# =====================================================
# TEST CONNECTION
# =====================================================
if __name__ == "__main__":

    exchange = get_exchange()

    if exchange:

        print(exchange.fetch_balance())
# =====================================================
# CHECK SLIPPAGE CONDITIONS
# =====================================================
def check_slippage(
    exchange,
    symbol
):

    try:

        orderbook = exchange.fetch_order_book(
            symbol
        )

        bid = orderbook["bids"][0][0]

        ask = orderbook["asks"][0][0]

        spread_pct = (
            (ask - bid)
            / bid
        ) * 100

        if spread_pct > config.MAX_SPREAD_PCT:

            print(
                f"Spread too high: "
                f"{spread_pct:.4f}%"
            )

            return False

        return True

    except Exception as e:

        print(
            f"Slippage check error: {e}"
        )

        return False