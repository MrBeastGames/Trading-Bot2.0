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
            "enableRateLimit": True,

            "options": {
                "defaultType": "swap",
                "defaultSubType": "linear"
            }
        })

        exchange.load_markets()
        exchange.set_leverage(
    10,
    config.SYMBOL
)

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
def place_market_order(
    exchange,
    symbol,
    side,
    amount
):

    try:

        params = {
            "marginMode": "cross",
            "tradeSide": "open"
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