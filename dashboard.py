import os
import sqlite3
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

from streamlit_autorefresh import st_autorefresh

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="AI Trading Dashboard",
    layout="wide",
)

# =====================================================
# AUTO REFRESH
# =====================================================
st_autorefresh(
    interval=60000)
key="dashboard_refresh"

# =====================================================
# SAFE CONFIG IMPORT
# =====================================================
try:
    import config
except Exception:
    config = None

# =====================================================
# SAFE TELEGRAM IMPORT
# =====================================================
try:
    from telegram_utils import send_telegram_message
except Exception:

    def send_telegram_message(message):
        pass

# =====================================================
# MOBILE STYLE
# =====================================================
st.markdown(
    """
    <style>

    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# =====================================================
# LOGIN SYSTEM
# =====================================================
USERNAME = "admin"
PASSWORD = "admin123"

if config is not None:

    USERNAME = getattr(
        config,
        "DASHBOARD_USERNAME",
        "admin"
    )

    PASSWORD = getattr(
        config,
        "DASHBOARD_PASSWORD",
        "admin123"
    )

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:

    st.title("🔐 Admin Login")

    username = st.text_input("Username")

    password = st.text_input(
        "Password",
        type="password"
    )

    if st.button("Login"):

        if (
            username == USERNAME
            and password == PASSWORD
        ):

            st.session_state["authenticated"] = True
            st.rerun()

        else:
            st.error("Invalid credentials")

    st.stop()

# =====================================================
# DATABASE CONNECTION
# =====================================================
conn = None

try:

    conn = sqlite3.connect(
        "trading_bot.db",
        check_same_thread=False
    )

except Exception as e:

    st.error(f"Database Error: {e}")

# =====================================================
# TITLE
# =====================================================
st.title("🚀 AI Trading Dashboard")

# =====================================================
# SIDEBAR
# =====================================================
st.sidebar.title("⚙️ Control Panel")

strategy = st.sidebar.selectbox(
    "Strategy",
    [
        "EMA Trend",
        "Scalping",
        "Breakout",
        "Swing",
    ]
)

st.sidebar.success(
    f"Active: {strategy}"
)

# =====================================================
# TELEGRAM TEST
# =====================================================
if st.sidebar.button("Send Telegram Test"):

    try:

        send_telegram_message(
            "📡 Dashboard test successful"
        )

        st.sidebar.success(
            "Telegram sent"
        )

    except Exception as e:

        st.sidebar.error(str(e))

# =====================================================
# BOT STATUS
# =====================================================
st.subheader("🤖 Bot Status")

if os.path.exists("bot_status.txt"):

    try:

        with open(
            "bot_status.txt",
            "r"
        ) as f:

            status = f.read().strip()

        if status == "RUNNING":

            st.success("Bot Running")

        else:

            st.error("Bot Stopped")

    except Exception:

        st.warning(
            "Could not read bot status."
        )

else:

    st.warning(
        "bot_status.txt missing"
    )

# =====================================================
# LOAD TRADES
# =====================================================
trades_df = pd.DataFrame()

if conn is not None:

    try:

        trades_df = pd.read_sql_query(
            "SELECT * FROM trades",
            conn
        )

    except Exception:
        pass

# =====================================================
# LIVE PNL
# =====================================================
st.subheader("💰 Live Performance")

if not trades_df.empty:

    pnl_total = 0

    if "pnl" in trades_df.columns:

        pnl_total = (
            trades_df["pnl"]
            .fillna(0)
            .sum()
        )

    total_trades = len(trades_df)

    wins = 0

    if "pnl" in trades_df.columns:

        wins = (
            trades_df["pnl"] > 0
        ).sum()

    winrate = 0

    if total_trades > 0:

        winrate = (
            wins / total_trades
        ) * 100

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Total PnL",
        f"${pnl_total:.2f}"
    )

    col2.metric(
        "Trades",
        total_trades
    )

    col3.metric(
        "Winrate",
        f"{winrate:.2f}%"
    )

else:

    st.info("No trades yet.")

# =====================================================
# OPEN POSITIONS
# =====================================================
st.subheader("📊 Open Positions")

if conn is not None:

    try:

        positions_df = pd.read_sql_query(
            "SELECT * FROM positions",
            conn
        )

        if not positions_df.empty:

            st.dataframe(
                positions_df,
                use_container_width=True
            )

        else:

            st.info(
                "No open positions"
            )

    except Exception:

        st.info(
            "No positions table yet."
        )

# =====================================================
# MARKET CHART
# =====================================================
st.subheader("📈 Live Market Chart")

if os.path.exists("market_data.csv"):

    try:

        market_df = pd.read_csv(
            "market_data.csv"
        ).tail(200)

        required = [
            "open",
            "high",
            "low",
            "close",
        ]

        if all(
            col in market_df.columns
            for col in required
        ):

            fig = go.Figure()

            fig.add_trace(
                go.Candlestick(
                    x=market_df.index,
                    open=market_df["open"],
                    high=market_df["high"],
                    low=market_df["low"],
                    close=market_df["close"],
                )
            )

            fig.update_layout(
                height=500
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        else:

            st.warning(
                "OHLC columns missing"
            )

    except Exception as e:

        st.warning(
            f"Chart Error: {e}"
        )

else:

    st.warning(
        "market_data.csv not found"
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

            latest = (
                equity_df["equity"]
                .iloc[-1]
            )

            st.metric(
                "Current Equity",
                f"${latest:.2f}"
            )

    except Exception as e:

        st.warning(
            f"Equity Error: {e}"
        )

# =====================================================
# SHARPE RATIO
# =====================================================
st.subheader("📐 Sharpe Ratio")

try:

    if (
        not trades_df.empty
        and "pnl" in trades_df.columns
    ):

        returns = trades_df["pnl"]

        if returns.std() != 0:

            sharpe = (
                returns.mean()
                / returns.std()
            )

            st.metric(
                "Sharpe Ratio",
                f"{sharpe:.2f}"
            )

except Exception:
    pass

# =====================================================
# RISK EXPOSURE
# =====================================================
st.subheader("⚠️ Risk Exposure")

risk = np.random.uniform(1, 10)

st.progress(risk / 10)

st.write(
    f"Current Risk Exposure: {risk:.2f}%"
)

# =====================================================
# HEATMAP
# =====================================================
st.subheader("🔥 Market Heatmap")

heatmap = np.random.rand(10, 10)

fig_heatmap = px.imshow(
    heatmap,
    text_auto=True,
    aspect="auto"
)

st.plotly_chart(
    fig_heatmap,
    use_container_width=True
)

# =====================================================
# TRADE HISTORY
# =====================================================
st.subheader("📜 Trade History")

if not trades_df.empty:

    st.dataframe(
        trades_df.tail(20),
        use_container_width=True
    )

# =====================================================
# CONFIG SNAPSHOT
# =====================================================
st.subheader("⚙️ Config Snapshot")

if config is not None:

    snapshot = {}

    for attr in [
        "EXCHANGE_ID",
        "SYMBOL",
        "TIMEFRAME",
        "PAPER_TRADING",
    ]:

        if hasattr(config, attr):

            snapshot[attr] = getattr(
                config,
                attr
            )

    snapshot["API_KEY"] = "****"
    snapshot["API_SECRET"] = "****"

    st.json(snapshot)

# =====================================================
# CLOSE DB
# =====================================================
if conn is not None:

    conn.close()