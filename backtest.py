import pandas as pd
import matplotlib.pyplot as plt

import config

from strategy import (
    add_indicators,
    handle_entry,
    handle_exit,
    update_trailing_stop,
)

from risk_manager import RiskManager


# =========================================================
# LOAD HISTORICAL DATA
# =========================================================
import os

if not os.path.exists("market_data.csv"):

    print(
        "ERROR: market_data.csv not found."
    )

    print(
        "Run main.py first to generate market data."
    )

    exit()

df = pd.read_csv("market_data.csv")

# =========================================================
# CLEAN DATA
# =========================================================
df["timestamp"] = pd.to_datetime(
    df["timestamp"]
)

df = add_indicators(df)

df = df.dropna().reset_index(drop=True)

# =========================================================
# RISK MANAGER
# =========================================================
rm = RiskManager(
    config.INITIAL_CAPITAL
)

# =========================================================
# VARIABLES
# =========================================================
position = None

equity_curve = []

trade_count = 0

wins = 0

losses = 0

# =========================================================
# MAIN BACKTEST LOOP
# =========================================================
for i in range(50, len(df)):

    window_df = df.iloc[i-3:i]

    price = df["close"].iloc[i]

    # =====================================================
    # UPDATE TRAILING STOP
    # =====================================================
    position = update_trailing_stop(
        position,
        price
    )

    # =====================================================
    # HANDLE EXIT
    # =====================================================
    old_capital = rm.capital

    position = handle_exit(
        position,
        price,
        rm
    )

    # =====================================================
    # CLOSED TRADE DETECTED
    # =====================================================
    if rm.capital != old_capital:

        trade_count += 1

        pnl = rm.capital - old_capital

        if pnl > 0:
            wins += 1
        else:
            losses += 1

    # =====================================================
    # HANDLE ENTRY
    # =====================================================
    new_position = handle_entry(
        window_df,
        price,
        rm,
        position
    )

    if (
        new_position is not None
        and position is None
    ):

        position = new_position

    # =====================================================
    # EQUITY CURVE
    # =====================================================
    equity_curve.append(
        rm.capital
    )

# =========================================================
# RESULTS
# =========================================================
print("\n========== BACKTEST RESULTS ==========\n")

print(f"Initial Capital: {config.INITIAL_CAPITAL}")

print(f"Final Capital: {rm.capital:.2f}")

print(f"Total Trades: {trade_count}")

# =========================================================
# WINRATE
# =========================================================
if trade_count > 0:

    winrate = (
        wins / trade_count
    ) * 100

else:

    winrate = 0

print(f"Winrate: {winrate:.2f}%")

# =========================================================
# TOTAL RETURN
# =========================================================
total_return = (
    (
        rm.capital
        - config.INITIAL_CAPITAL
    )
    / config.INITIAL_CAPITAL
) * 100

print(f"Total Return: {total_return:.2f}%")

# =========================================================
# MAX DRAWDOWN
# =========================================================
equity_series = pd.Series(
    equity_curve
)

rolling_max = equity_series.cummax()

drawdown = (
    equity_series - rolling_max
) / rolling_max

max_drawdown = drawdown.min() * 100

print(f"Max Drawdown: {max_drawdown:.2f}%")

# =========================================================
# SHARPE RATIO
# =========================================================
returns = equity_series.pct_change().dropna()

if returns.std() != 0:

    sharpe = (
        returns.mean()
        / returns.std()
    ) * (252 ** 0.5)

else:

    sharpe = 0

print(f"Sharpe Ratio: {sharpe:.2f}")

print("\n======================================\n")

# =========================================================
# SAVE EQUITY CURVE
# =========================================================
equity_df = pd.DataFrame({
    "equity": equity_curve
})

equity_df.to_csv(
    "equity_curve.csv",
    index=False
)

# =========================================================
# PLOT EQUITY CURVE
# =========================================================
plt.figure(figsize=(12, 6))

plt.plot(equity_curve)

plt.title("Backtest Equity Curve")

plt.xlabel("Trades")

plt.ylabel("Capital")

plt.grid(True)

plt.show()