import sqlite3
import logging
from datetime import datetime

DB_NAME = "trading_bot.db"


# =====================================================
# CREATE DATABASE
# =====================================================
def initialize_database():

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    # =================================================
    # TRADES TABLE
    # =================================================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS trades (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        symbol TEXT,

        side TEXT,

        price REAL,

        amount REAL,

        pnl REAL,

        timestamp TEXT
    )
    """)

    # =================================================
    # POSITIONS TABLE
    # =================================================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS positions (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        symbol TEXT,

        side TEXT,

        entry_price REAL,

        amount REAL,

        timestamp TEXT
    )
    """)

    conn.commit()

    conn.close()


# =====================================================
# LOG TRADE
# =====================================================
def log_trade(
    symbol,
    side,
    price,
    amount,
    pnl=0
):

    try:

        conn = sqlite3.connect(DB_NAME)

        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO trades (

            symbol,
            side,
            price,
            amount,
            pnl,
            timestamp

        ) VALUES (?, ?, ?, ?, ?, ?)
        """, (

            symbol,
            side,
            float(price),
            float(amount),
            float(pnl),
            str(datetime.now())

        ))

        conn.commit()

        conn.close()

        logging.info(
            f"Trade logged: {symbol}"
        )

    except Exception as e:

        logging.error(
            f"Trade logging failed: {e}"
        )


# =====================================================
# SAVE POSITION
# =====================================================
def save_position(
    symbol,
    side,
    entry_price,
    amount
):

    try:

        conn = sqlite3.connect(DB_NAME)

        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO positions (

            symbol,
            side,
            entry_price,
            amount,
            timestamp

        ) VALUES (?, ?, ?, ?, ?)
        """, (

            symbol,
            side,
            float(entry_price),
            float(amount),
            str(datetime.now())

        ))

        conn.commit()

        conn.close()

        logging.info(
            f"Position saved: {symbol}"
        )

    except Exception as e:

        logging.error(
            f"Position save failed: {e}"
        )


# =====================================================
# CLEAR POSITIONS
# =====================================================
def clear_positions():

    try:

        conn = sqlite3.connect(DB_NAME)

        cursor = conn.cursor()

        cursor.execute(
            "DELETE FROM positions"
        )

        conn.commit()

        conn.close()

    except Exception as e:

        logging.error(
            f"Clear positions failed: {e}"
        )


# =====================================================
# INIT DB
# =====================================================
initialize_database()