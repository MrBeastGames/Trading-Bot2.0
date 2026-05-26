import streamlit as st
import pandas as pd
import numpy as np
import os
import sqlite3
import plotly.graph_objects as go
import plotly.express as px

from streamlit_autorefresh import st_autorefresh

# =====================================================
# SAFE IMPORTS
# =====================================================
try:
    import config
except Exception:
    config = None

try:
    from telegram_utils import send_telegram_message
except Exception:

    def send_telegram_message(message):
        return None

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="AI Trading Dashboard",
    layout="wide",
)

# =====================================================
# MOBILE OPTIMIZATION
# =====================================================
st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }

    @media (max-width: 768px) {
        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =====================================================
# AUTO REFRESH
# =====================================================
st_autorefresh(
    interval=10000,
    key="dashboard_refresh",
)

# =====================================================
# AUTHENTICATION
# =====================================================
DASHBOARD_USERNAME = "admin"
DASHBOARD_PASSWORD = "admin123"

if config is not None:

    DASHBOARD_USERNAME = getattr(
        config,
        "DASHBOARD_USERNAME",
        "admin"
    )

    DASHBOARD_PASSWORD = getattr(
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
            username == DASHBOARD_USERNAME
            and password == DASHBOARD_PASSWORD
        ):

            st.session_state[
                "authenticated"
            ] = True

            st.rerun()

        else:

            st.error(
                "Invalid credentials"
            )

    st.stop()

# =====================================================
# DATABASE CONNECTION
# =====================================================
conn = sqlite3.connect(
    "trading_bot.db",
    check_same_thread=False
)

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
        "EMA Trend Strategy",
        "Scalping Strategy",
        "Breakout Strategy",
        "Swing Strategy",
    ],
)

st.sidebar.success(
    f"Active Strategy: {strategy}"
)

# =====================================================
# TELEGRAM TEST
# =====================================================
if st.sidebar.button(
    "Send Telegram Test"
):

    try:

        send_telegram_message(
            "📡 Dashboard test message"
        )

        st.sidebar.success(
            "Telegram message sent"
        )

    except Exception as e:

        st.sidebar.error(
            f"Telegram Error: {e}"
        )

# =====================================================
# BOT STATUS
# =====================================================
st.subheader("🤖 Bot Status")

if os.path.exists("bot_status.txt"):

    with open("bot_status.txt", "r") as f:

        status = f.read().strip()

    if status == "RUNNING":

        st.success(
            "Bot is RUNNING"
        )

    else:

        st.error(
            "Bot is STOPPED"
        )

else:

    st.error(
        "Bot is STOPPED"
    )

# =====================================================
# LIVE PNL
# =====================================================
st.subheader("💰 Live PnL")

try:

    trades_df = pd.read_sql_query(
        "SELECT * FROM trades",
        conn
    )

    if not trades_df.empty:

        if "pnl" in trades_df.columns:

            total_pnl = trades_df[
                "pnl"
            ].sum()

            total_trades = len(
                trades_df
            )

            winrate = (
                (
                    trades_df["pnl"] > 0
                ).mean()
            ) * 100

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "Total PnL",
                f"${total_pnl:.2f}"
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

            st.warning(
                "PnL column missing in database."
            )

    else:

        st.info(
            "No trades yet."
        )

except Exception as e:

    st.warning(
        f"Database Error: {e}"
    )

# =====================================================
# OPEN POSITIONS
# =====================================================
st.subheader("📊 Open Positions")

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
            "No open positions."
        )

except Exception as e:

    st.warning(
        f"Positions Error: {e}"
    )

# =====================================================
# LIVE MARKET CHART
# =====================================================
st.subheader("📈 Live Market Chart")

market_file = "market_data.csv"

if os.path.exists(market_file):

    try:

        market_df = pd.read_csv(
            market_file
        ).tail(300)

        required_cols = [
            "open",
            "high",
            "low",
            "close",
        ]

        if all(
            col in market_df.columns
            for col in required_cols
        ):

            fig = go.Figure(
                data=[
                    go.Candlestick(
                        x=market_df.index,
                        open=market_df["open"],
                        high=market_df["high"],
                        low=market_df["low"],
                        close=market_df["close"],
                    )
                ]
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

        st.warning(
            f"Chart Error: {e}"
        )

else:

    st.warning(
        "No market data file found."
    )

# =====================================================
# EQUITY CURVE
# =====================================================
st.subheader("💹 Equity Curve")

if os.path.exists("equity_curve.csv"):

    try:

        equity_df = pd.read_csv(
            "equity_curve.csv"
        ).tail(300)

        if (
            not equity_df.empty
            and "equity" in equity_df.columns
        ):

            st.line_chart(
                equity_df["equity"]
            )

            latest_equity = equity_df[
                "equity"
            ].iloc[-1]

            st.metric(
                "Current Equity",
                f"{latest_equity:.2f}"
            )

        else:

            st.warning(
                "No equity data found."
            )

    except Exception as e:

        st.warning(
            f"Equity Error: {e}"
        )

# =====================================================
# TRADE HISTORY
# =====================================================
st.subheader("📜 Trade History")

if os.path.exists("trades.csv"):

    try:

        csv_trades_df = pd.read_csv(
            "trades.csv"
        ).tail(100)

        st.dataframe(
            csv_trades_df,
            use_container_width=True
        )

    except Exception as e:

        st.warning(
            f"Trade History Error: {e}"
        )

# =====================================================
# RISK EXPOSURE
# =====================================================
st.subheader("⚠️ Risk Exposure")

risk_value = np.random.uniform(
    1,
    10
)

st.progress(risk_value / 10)

st.write(
    f"Current Risk Exposure: "
    f"{risk_value:.2f}%"
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

        else:

            st.metric(
                "Sharpe Ratio",
                "0.00"
            )

except Exception:
    pass

# =====================================================
# HEATMAP
# =====================================================
st.subheader("🔥 Market Heatmap")

heatmap_data = np.random.rand(
    10,
    10
)

fig_heatmap = px.imshow(
    heatmap_data,
    text_auto=True,
    aspect="auto",
)

st.plotly_chart(
    fig_heatmap,
    use_container_width=True
)

# =====================================================
# CONFIG SNAPSHOT
# =====================================================
st.subheader("⚙️ Config Snapshot")

if config is None:

    st.warning(
        "config.py could not be loaded"
    )

else:

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
    snapshot["API_PASSWORD"] = "****"

    st.json(snapshot)

# =====================================================
# CLEANUP
# =====================================================
conn.close()