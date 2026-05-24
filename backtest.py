import logging
import matplotlib.pyplot as plt
import config
from exchange_handler import fetch_ohlcv
from risk_manager import RiskManager
from strategy import add_indicators, update_trailing_stop, handle_exit, handle_entry


def backtest(exchange):
    df = fetch_ohlcv(exchange, config.SYMBOL, config.TIMEFRAME, limit=1000)
    df = add_indicators(df).dropna()

    rm = RiskManager(config.INITIAL_CAPITAL)
    position = None
    equity_curve = []

    for ts, row in df.iterrows():
        price = row["close"]

        if position:
            if position["side"] == "long":
                unrealized = position["amount"] * (price - position["entry_price"])
            else:
                unrealized = position["amount"] * (position["entry_price"] - price)
            rm.update(rm.capital + unrealized)
        else:
            rm.update(rm.capital)

        window_df = df.loc[:ts].iloc[-3:]
        if len(window_df) < 3:
            continue

        position = update_trailing_stop(position, price)
        position = handle_exit(position, price, rm)
        position = handle_entry(window_df, price, rm, position)

        equity_curve.append(rm.capital)

    logging.info(f"Backtest finished. Final capital: {rm.capital:.2f}")
    logging.info(f"Max drawdown: {rm.max_dd*100:.2f}%")

    # Save equity curve
    import pandas as pd

    eq_df = pd.DataFrame({"equity": equity_curve})
    eq_df.to_csv(config.EQUITY_CSV_PATH, index=False)

    plt.figure(figsize=(10, 5))
    plt.plot(eq_df["equity"])
    plt.title("Equity Curve")
    plt.xlabel("Step")
    plt.ylabel("Equity")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(config.EQUITY_PNG_PATH)
    plt.close()

    print(f"Backtest Final Capital: {rm.capital:.2f}")
    print(f"Backtest Max DD: {rm.max_dd*100:.2f}%")
    print(f"Equity CSV: {config.EQUITY_CSV_PATH}")
    print(f"Equity PNG: {config.EQUITY_PNG_PATH}")
