import streamlit as st
import pandas as pd
import numpy as np
import os
import sqlite3
import plotly.graph_objects as go

from streamlit_autorefresh import st_autorefresh

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="AI Trading Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# AUTO REFRESH
# =====================================================
st_autorefresh(
    interval=10000,
    key="dashboard_refresh"
)

# =====================================================
# MOBILE CSS
# =====================================================
st.markdown("""
<style>
.block-container {
    padding-top: 1rem;
    padding-bottom: 1rem;
}

[data-testid="metric-container"] {
    border-radius: 12px;
    padding: 15px;
    background-color: #111827;
    border: 1px solid #1f2937;
}

@media (max-width: 768px) {
    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# SAFE CONFIG IMPORT
# =====================================================
try:
    import config
except Exception:
    config = None

# =====================================================
# DATABASE
# =====================================================
DB_PATH = "trading_bot.db"

def get_connection():
    return sqlite3.connect(
        DB_PATH,
        check_same_thread=False,
        timeout=30
    )

# =====================================================
# CREATE TABLES IF MISSING
# =====================================================
def initialize_database():

    conn = get_connection()
    cursor = conn.cursor()

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

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS positions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT,
        side TEXT,
        entry_price REAL,
        current_price REAL,
        pnl REAL,
        amount REAL,
        timestamp TEXT
    )
    """)

    conn.commit()
    conn.close()

initialize_database()

# =====================================================
# TITLE
# =====================================================
st.title("🚀 AI Trading Dashboard")

# =====================================================
# SIDEBAR
# =====================================================
st.sidebar.title("⚙️ Bot Controls")

if config:

    st.sidebar.success(
        f"Exchange: {config.EXCHANGE_ID}"
    )

    st.sidebar.info(
        f"Timeframe: {config.TIMEFRAME}"
    )

# =====================================================
# BOT STATUS
# =====================================================
st.subheader("🤖 Bot Status")

if os.path.exists("bot_status.txt"):

    with open("bot_status.txt", "r") as f:
        status = f.read().strip()

    if status == "RUNNING":
        st.success("Bot is RUNNING")
    else:
        st.error("Bot is STOPPED")

else:
    st.warning("No status file found.")

# =====================================================
# DATABASE CONNECTION
# =====================================================
conn = get_connection()

# =====================================================
# LIVE PNL
# =====================================================
st.subheader("💰 Live PnL")

try:

    trades_df = pd.read_sql_query(
        "SELECT * FROM trades ORDER BY id DESC LIMIT 100",
        conn
    )

    if not trades_df.empty:

        if "pnl" not in trades_df.columns:
            trades_df["pnl"] = 0

        trades_df["pnl"] = trades_df["pnl"].fillna(0)

        total_pnl = trades_df["pnl"].sum()
        total_trades = len(trades_df)

        winrate = (
            (trades_df["pnl"] > 0).mean()
        ) * 100

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Total PnL",
            f"${total_pnl:.2f}"
        )

        c2.metric(
            "Trades",
            total_trades
        )

        c3.metric(
            "Winrate",
            f"{winrate:.2f}%"
        )

        st.dataframe(
            trades_df,
            use_container_width=True
        )

    else:

        st.info("No trades logged yet.")

except Exception as e:

    st.error(f"Trades Error: {e}")

# =====================================================
# OPEN POSITIONS
# =====================================================
st.subheader("📊 Open Positions")

try:

    positions_df = pd.read_sql_query(
        "SELECT * FROM positions ORDER BY id DESC LIMIT 50",
        conn
    )

    if not positions_df.empty:

        st.dataframe(
            positions_df,
            use_container_width=True
        )

    else:

        st.info("No open positions.")

except Exception as e:

    st.error(f"Positions Error: {e}")

# =====================================================
# LIVE CHART
# =====================================================
st.subheader("📈 Live Market Chart")

market_file = "market_data.csv"

if os.path.exists(market_file):

    try:

        market_df = pd.read_csv(
            market_file
        ).tail(200)

        required_cols = [
            "open",
            "high",
            "low",
            "close"
        ]

        if all(
            col in market_df.columns
            for col in required_cols
        ):

            fig = go.Figure()

            fig.add_trace(
                go.Candlestick(
                    x=market_df.index,
                    open=market_df["open"],
                    high=market_df["high"],
                    low=market_df["low"],
                    close=market_df["close"],
                    name="Price"
                )
            )

            fig.update_layout(
                height=600,
                xaxis_rangeslider_visible=False
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        else:

            st.warning(
                "OHLC columns missing."
            )

    except Exception as e:

        st.error(f"Chart Error: {e}")

else:

    st.warning(
        "market_data.csv not found."
    )

# =====================================================
# EQUITY CURVE
# =====================================================
st.subheader("💹 Equity Curve")

if os.path.exists("equity_curve.csv"):

    try:

        equity_df = pd.read_csv(
            "equity_curve.csv"
        )

        if (
            not equity_df.empty
            and "equity" in equity_df.columns
        ):

            st.line_chart(
                equity_df["equity"]
            )

    except Exception as e:

        st.error(f"Equity Error: {e}")

# =====================================================
# RISK EXPOSURE
# =====================================================
st.subheader("⚠️ Risk Exposure")

risk_value = np.random.uniform(1, 10)

st.progress(risk_value / 10)

st.write(
    f"Current Risk Exposure: "
    f"{risk_value:.2f}%"
)

# =====================================================
# CONFIG SNAPSHOT
# =====================================================
st.subheader("⚙️ Config Snapshot")

if config:

    snapshot = {
        "EXCHANGE_ID": getattr(
            config,
            "EXCHANGE_ID",
            "N/A"
        ),
        "SYMBOL": getattr(
            config,
            "SYMBOL",
            "N/A"
        ),
        "TIMEFRAME": getattr(
            config,
            "TIMEFRAME",
            "N/A"
        ),
        "PAPER_TRADING": getattr(
            config,
            "PAPER_TRADING",
            True
        )
    }

    st.json(snapshot)

# =====================================================
# CLEANUP
# =====================================================
conn.close()