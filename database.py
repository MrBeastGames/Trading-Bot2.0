import sqlite3
from datetime import datetime

DB_NAME = "trading_bot.db"


def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)


conn = get_connection()
cursor = conn.cursor()

# =====================================================
# TRADES TABLE
# =====================================================
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS trades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT,
        side TEXT,
        entry_price REAL,
        exit_price REAL,
        pnl REAL,
        amount REAL,
        timestamp TEXT
    )
    """
)

# =====================================================
# POSITIONS TABLE
# =====================================================
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS positions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT,
        side TEXT,
        entry_price REAL,
        current_price REAL,
        pnl REAL,
        amount REAL,
        status TEXT,
        timestamp TEXT
    )
    """
)

conn.commit()


def log_trade(symbol, side, entry_price, exit_price, pnl, amount):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO trades
        (symbol, side, entry_price, exit_price, pnl, amount, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            symbol,
            side,
            entry_price,
            exit_price,
            pnl,
            amount,
            datetime.utcnow().isoformat(),
        ),
    )

    conn.commit()
    conn.close()


def save_position(symbol, side, entry_price, current_price, pnl, amount):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM positions")

    cursor.execute(
        """
        INSERT INTO positions
        (symbol, side, entry_price, current_price, pnl, amount, status, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            symbol,
            side,
            entry_price,
            current_price,
            pnl,
            amount,
            "OPEN",
            datetime.utcnow().isoformat(),
        ),
    )

    conn.commit()
    conn.close()
