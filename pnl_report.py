import pandas as pd
import os


def generate_report():
    # Check if file exists
    if not os.path.exists("trades.csv"):
        print("No trades.csv file found.")
        return

    df = pd.read_csv("trades.csv")

    if df.empty:
        print("No trades logged.")
        return

    total_trades = len(df)
    wins = (df["pnl"] > 0).sum()
    losses = (df["pnl"] < 0).sum()
    winrate = (wins / total_trades) * 100 if total_trades > 0 else 0

    total_pnl = df["pnl"].sum()
    avg_win = df[df["pnl"] > 0]["pnl"].mean() if wins > 0 else 0
    avg_loss = df[df["pnl"] < 0]["pnl"].mean() if losses > 0 else 0

    # Max drawdown from equity_after column
    if "equity_after" in df.columns:
        max_drawdown = (df["equity_after"].cummax() - df["equity_after"]).max()
    else:
        max_drawdown = 0

    print("\n===== PnL REPORT =====")
    print(f"Total Trades: {total_trades}")
    print(f"Wins: {wins} | Losses: {losses}")
    print(f"Winrate: {winrate:.2f}%")
    print(f"Total PnL: {total_pnl:.2f}")
    print(f"Avg Win: {avg_win:.2f}")
    print(f"Avg Loss: {avg_loss:.2f}")
    print(f"Max Drawdown: {max_drawdown:.2f}")
    print("======================\n")


if __name__ == "__main__":
    generate_report()
