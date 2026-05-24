import csv
import os
from datetime import datetime

LOG_FILE = "trades.csv"


def init_trade_log():
    """Create the CSV file with headers if it doesn't exist."""
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "timestamp",
                "side",
                "entry_price",
                "exit_price",
                "amount",
                "pnl",
                "equity_after",
            ])


def log_trade(side, entry_price, exit_price, amount, pnl, equity):
    """Append a completed trade to the CSV."""
    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.utcnow().isoformat(),
            side,
            entry_price,
            exit_price,
            amount,
            pnl,
            equity,
        ])
