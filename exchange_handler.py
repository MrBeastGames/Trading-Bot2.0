import ccxt
import pandas as pd
import logging
import config


# =========================================================
# LOGGING
# =========================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


# =========================================================
# CREATE EXCHANGE
# =========================================================
def get_exchange():

    print("STARTING EXCHANGE CONNECTION")

    try:
        exchange = ccxt.bitget({
            "apiKey": config.API_KEY,
            "secret": config.API_SECRET,
            "password": config.API_PASSWORD,
            "enableRateLimit": True,
            "options": {
                "defaultType": "swap",
            }
        })

        print("EXCHANGE OBJECT CREATED")

        exchange.load_markets()
        print("MARKETS LOADED")

        balance = exchange.fetch_balance()
        print("BALANCE FETCHED")
        print(balance)

        return exchange

    except Exception as e:
        print("FULL ERROR:")
        print(e)
        return None


# =========================================================
# FETCH OHLCV
# =========================================================
def fetch_ohlcv(exchange, symbol, timeframe, limit=100):

    try:
        data = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)

        df = pd.DataFrame(
            data,
            columns=["timestamp", "open", "high", "low", "close", "volume"]
        )

        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df.set_index("timestamp", inplace=True)

        return df

    except Exception as e:
        logging.error(f"OHLCV ERROR: {e}")
        return None


# =========================================================
# PLACE MARKET ORDER
# =========================================================
def place_market_order(exchange, symbol, side, amount):

    try:

        order = exchange.create_order(
            symbol=symbol,
            type="market",
            side=side,
            amount=amount
        )


        return order

    except Exception as e:

        logging.error(f"ORDER ERROR: {e}")

        return None


# =========================================================
# FETCH BALANCE
# =========================================================
def fetch_balance(exchange):

    try:
        return exchange.fetch_balance()

    except Exception as e:
        logging.error(f"BALANCE ERROR: {e}")
        return None


# =========================================================
# TEST CONNECTION + TEST ORDER
# =========================================================
if __name__ == "__main__":

    exchange = get_exchange()

    if exchange:
        print("CONNECTED SUCCESSFULLY")

        # Test order
        try:
            test_order = place_market_order(
                exchange,
                config.SYMBOL,
                "buy",
                0.001
            )

            if test_order:
                logging.info("Test order placed successfully")
            else:
                logging.error("Test order failed")

        except Exception as e:
            logging.error(f"Test Order Error: {e}")

    else:
        print("CONNECTION FAILED")
