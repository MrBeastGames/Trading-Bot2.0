import streamlit as st
import pandas as pd
import numpy as np
import os
import plotly.graph_objects as go
import plotly.express as px

from streamlit_autorefresh import st_autorefresh

# =====================================================
# SAFE TELEGRAM IMPORT
# =====================================================
try:
    from telegram_utils import send_telegram_message
except Exception:
    def send_telegram_message(message):
        return None

# =====================================================
# SAFE CONFIG IMPORT
# =====================================================
try:
    import config
except ModuleNotFoundError:
    config = None

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="Trading Bot Dashboard",
    layout="wide"
)

# =====================================================
# AUTO REFRESH
# =====================================================
st_autorefresh(
    interval=15000,
    key="dashboard_refresh"
)

# =====================================================
# TITLE
# =====================================================
st.title("🚀 AI Trading Dashboard")

# =====================================================
# SESSION STATE
# =====================================================
if "bot_running" not in st.session_state:
    st.session_state["bot_running"] = False

if "position" not in st.session_state:
    st.session_state["position"] = None

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
    ]
)

st.sidebar.success(f"Active Strategy: {strategy}")

# =====================================================
# TELEGRAM TEST
# =====================================================
if st.sidebar.button("Send Telegram Test"):
    try:
        send_telegram_message("📡 Dashboard test message")
        st.sidebar.success("Telegram message sent")
    except Exception as e:
        st.sidebar.error(f"Telegram Error: {e}")

# =====================================================
# BOT STATUS
# =====================================================
st.subheader("🤖 Bot Status")

if st.session_state["bot_running"]:
    st.success("Bot is RUNNING")
else:
    st.error("Bot is STOPPED")

# =====================================================
# LIVE MARKET CHART
# =====================================================
st.subheader("📈 Live Market Chart")

# =====================================================
# MARKET DATA
# =====================================================
if os.path.exists("market_data.csv"):

    market_df = pd.read_csv(
        "market_data.csv"
    ).tail(300)

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

        fig = go.Figure(
            data=[
                go.Candlestick(
                    x=market_df.index,
                    open=market_df["open"],
                    high=market_df["high"],
                    low=market_df["low"],
                    close=market_df["close"]
                )
            ]
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:

        st.warning(
            "market_data.csv is missing OHLC columns"
        )

else:

    st.warning(
        "No market_data.csv found."
    )


# =====================================================
# OPEN POSITION
# =====================================================
st.subheader("📊 Current Position")

position = st.session_state["position"]

if position:
    st.json(position)
else:
    st.info("No open position.")

# =====================================================
# EQUITY CURVE
# =====================================================
st.subheader("💰 Equity Curve")

if os.path.exists("equity_curve.csv"):

    equity_df = pd.read_csv(
        "equity_curve.csv"
    ).tail(300)

else:

    equity_df = pd.DataFrame() 

    if "equity" in equity_df.columns:

        st.line_chart(equity_df["equity"])

        latest_equity = equity_df["equity"].iloc[-1]

        st.metric(
            "Current Equity",
            f"{latest_equity:.2f}"
        )

    else:
        st.warning("No equity data found.")

# =====================================================
# TRADE HISTORY
# =====================================================
st.subheader("📜 Trade History")

if os.path.exists("trades.csv"):

    trades_df = pd.read_csv(
        "trades.csv"
    ).tail(100)

else:

    trades_df = pd.DataFrame()

    st.dataframe(trades_df.tail(20))

    if "pnl" in trades_df.columns:

        total_pnl = trades_df["pnl"].sum()
        total_trades = len(trades_df)
        winrate = ((trades_df["pnl"] > 0).mean()) * 100

        col1, col2, col3 = st.columns(3)

        col1.metric("Total Trades", total_trades)
        col2.metric("Winrate", f"{winrate:.2f}%")
        col3.metric("Total PnL", f"{total_pnl:.2f}")

    else:
     st.info("No trades logged yet.")

# =====================================================
# RISK EXPOSURE
# =====================================================
st.subheader("⚠️ Risk Exposure")

risk_value = np.random.uniform(1, 10)

st.progress(risk_value / 10)

st.write(f"Current Risk Exposure: {risk_value:.2f}%")

# =====================================================
# SHARPE RATIO
# =====================================================
st.subheader("📐 Sharpe Ratio")

if os.path.exists("trades.csv"):

    trades_df = pd.read_csv("trades.csv")

    if "pnl" in trades_df.columns:

        returns = trades_df["pnl"]

        if returns.std() != 0:

            sharpe = returns.mean() / returns.std()

            st.metric(
                "Sharpe Ratio",
                f"{sharpe:.2f}"
            )

        else:
            st.metric("Sharpe Ratio", "0.00")

# =====================================================
# HEATMAP
# =====================================================
st.subheader("🔥 Market Heatmap")

heatmap_data = np.random.rand(10, 10)

fig_heatmap = px.imshow(
    heatmap_data,
    text_auto=True,
    aspect="auto"
)

st.plotly_chart(fig_heatmap, use_container_width=True)

# =====================================================
# CONFIG SNAPSHOT
# =====================================================
st.subheader("⚙️ Config Snapshot")

if config is None:
    st.warning("config.py could not be loaded")
else:

    snapshot = {}

    if hasattr(config, "EXCHANGE_ID"):
        snapshot["EXCHANGE_ID"] = config.EXCHANGE_ID

    if hasattr(config, "SYMBOL"):
        snapshot["SYMBOL"] = config.SYMBOL

    if hasattr(config, "TIMEFRAME"):
        snapshot["TIMEFRAME"] = config.TIMEFRAME

    if hasattr(config, "PAPER_TRADING"):
        snapshot["PAPER_TRADING"] = config.PAPER_TRADING

    snapshot["API_KEY"] = "****"
    snapshot["API_SECRET"] = "****"
    snapshot["API_PASSWORD"] = "****"

    st.json(snapshot)