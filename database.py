import sqlite3
from datetime import datetime

# =====================================================
# DATABASE NAME
# =====================================================
DB_NAME = "trading_bot.db"

# =====================================================
# CONNECTION
# =====================================================
def get_connection():

    return sqlite3.connect(
        DB_NAME,
        check_same_thread=False
    )

# =====================================================
# INITIALIZE DATABASE
# =====================================================
def initialize_database():

    conn = get_connection()

    cursor = conn.cursor()

    # =================================================
    # TRADES TABLE
    # =================================================
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

            status TEXT,

            timestamp TEXT
        )
        """
    )

    # =================================================
    # POSITIONS TABLE
    # =================================================
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

            stop_loss REAL,
            take_profit REAL,

            status TEXT,

            timestamp TEXT
        )
        """
    )

    conn.commit()

    conn.close()

# =====================================================
# LOG TRADE
# =====================================================
def log_trade(
    symbol,
    side,
    entry_price,
    exit_price,
    pnl,
    amount,
    status="CLOSED"
):

    try:

        conn = get_connection()

        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO trades (

                symbol,
                side,
                entry_price,
                exit_price,
                pnl,
                amount,
                status,
                timestamp

            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                symbol,
                side,
                entry_price,
                exit_price,
                pnl,
                amount,
                status,
                datetime.utcnow().isoformat(),
            ),
        )

        conn.commit()

        conn.close()

        print(
            f"Trade logged for {symbol}"
        )

    except Exception as e:

        print(
            f"Trade logging error: {e}"
        )

# =====================================================
# SAVE POSITION
# =====================================================
def save_position(
    symbol,
    side,
    entry_price,
    current_price,
    pnl,
    amount,
    stop_loss=0,
    take_profit=0,
):

    try:

        conn = get_connection()

        cursor = conn.cursor()

        # =============================================
        # REMOVE OLD POSITION FOR SAME SYMBOL
        # =============================================
        cursor.execute(
            """
            DELETE FROM positions
            WHERE symbol = ?
            """,
            (symbol,)
        )

        # =============================================
        # INSERT NEW POSITION
        # =============================================
        cursor.execute(
            """
            INSERT INTO positions (

                symbol,
                side,
                entry_price,
                current_price,
                pnl,
                amount,
                stop_loss,
                take_profit,
                status,
                timestamp

            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                symbol,
                side,
                entry_price,
                current_price,
                pnl,
                amount,
                stop_loss,
                take_profit,
                "OPEN",
                datetime.utcnow().isoformat(),
            ),
        )

        conn.commit()

        conn.close()

        print(
            f"Position saved for {symbol}"
        )

    except Exception as e:

        print(
            f"Save position error: {e}"
        )

# =====================================================
# CLOSE POSITION
# =====================================================
def close_position(symbol):

    try:

        conn = get_connection()

        cursor = conn.cursor()

        cursor.execute(
            """
            DELETE FROM positions
            WHERE symbol = ?
            """,
            (symbol,)
        )

        conn.commit()

        conn.close()

        print(
            f"Position closed for {symbol}"
        )

    except Exception as e:

        print(
            f"Close position error: {e}"
        )

# =====================================================
# LOAD OPEN POSITIONS
# =====================================================
def load_positions():

    try:

        conn = get_connection()

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT * FROM positions
            """
        )

        rows = cursor.fetchall()

        conn.close()

        return rows

    except Exception as e:

        print(
            f"Load positions error: {e}"
        )

        return []

# =====================================================
# AUTO INITIALIZE
# =====================================================
initialize_database()

print(
    "Database initialized successfully."
)