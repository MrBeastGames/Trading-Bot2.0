import logging
from exchange_handler import get_exchange, fetch_ohlcv
import config


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def test_connection():
    """
    Tests Bitget connection, OHLCV fetch, and account info.
    """

    print("\n===== TESTING BITGET CONNECTION =====")

    exchange = get_exchange()
    if exchange is None:
        print("❌ Failed to initialize exchange.")
        return

    print("✅ Exchange initialized successfully.")

    # -----------------------------------------------------
    # TEST OHLCV FETCH
    # -----------------------------------------------------
    print("\n===== TESTING OHLCV FETCH =====")

    df = fetch_ohlcv(exchange, config.SYMBOL, config.TIMEFRAME, limit=20)

    if df is None or df.empty:
        print("❌ Failed to fetch OHLCV.")
    else:
        print("✅ OHLCV fetched successfully.")
        print(df.tail())

    # -----------------------------------------------------
    # TEST BALANCE
    # -----------------------------------------------------
    print("\n===== TESTING ACCOUNT BALANCE =====")

    try:
        balance = exchange.fetch_balance()
        print("✅ Balance fetched successfully.")
        print(balance)
    except Exception as e:
        print(f"❌ Failed to fetch balance: {e}")

    # -----------------------------------------------------
    # TEST OPEN POSITIONS (if futures)
    # -----------------------------------------------------
    print("\n===== TESTING OPEN POSITIONS =====")

    try:
        positions = exchange.fetch_positions()
        print("✅ Positions fetched successfully.")
        print(positions)
    except Exception as e:
        print(f"❌ Failed to fetch positions: {e}")

    print("\n===== TEST COMPLETE =====")


if __name__ == "__main__":
    test_connection()
