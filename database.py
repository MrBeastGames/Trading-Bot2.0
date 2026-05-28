import sqlite3

DB_NAME = "trading_bot.db"

def initialize_database():

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    # =====================================================
    # TRADES TABLE
    # =====================================================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS trades (

        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT,
        side TEXT,
        price REAL,
        amount REAL,
        pnl REAL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP

    )
    """)

    # =====================================================
    # POSITIONS TABLE
    # =====================================================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS positions (

        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT,
        side TEXT,
        entry_price REAL,
        amount REAL,
        pnl REAL,
        status TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP

    )
    """)

    conn.commit()

    conn.close()

if __name__ == "__main__":

    initialize_database()

    print("Database initialized.")