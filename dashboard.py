import streamlit as st
import pandas as pd
import os

from telegram_utils import send_telegram_message

# =====================================================
# SAFE CONFIG IMPORT
# =====================================================
try:
    import config
except ModuleNotFoundError:
    config = None


# =====================================================
# PAGE TITLE
# =====================================================
st.title("Trading Bot Dashboard")


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
st.sidebar.header("Telegram Controls")

if st.sidebar.button("Send Test Message"):
    send_telegram_message("📡 Dashboard test message received.")
    st.sidebar.success("Message sent!")


st.sidebar.header("Bot Controls")

if st.sidebar.button("Start Bot"):
    st.session_state["bot_running"] = True
    send_telegram_message("🟢 Bot started from dashboard.")
    st.sidebar.success("Bot started")

if st.sidebar.button("Stop Bot"):
    st.session_state["bot_running"] = False
    send_telegram_message("🔴 Bot stopped from dashboard.")
    st.sidebar.warning("Bot stopped")


# =====================================================
# BOT STATUS
# =====================================================
st.subheader("Bot Status")

if st.session_state["bot_running"]:
    st.success("Bot is RUNNING")
else:
    st.error("Bot is STOPPED")


# =====================================================
# CURRENT POSITION
# =====================================================
st.subheader("Current Position")

position = st.session_state["position"]

if position:
    st.write(position)
else:
    st.write("No open position.")


# =====================================================
# EQUITY CURVE
# =====================================================
st.subheader("Equity Curve")

csv_path = "equity_curve.csv"

if os.path.exists(csv_path):
    try:
        equity_df = pd.read_csv(csv_path)

        if "Date" in equity_df.columns:
            equity_df["Date"] = pd.to_datetime(equity_df["Date"])
            equity_df.set_index("Date", inplace=True)

        if "equity" in equity_df.columns:
            st.line_chart(equity_df["equity"])
            st.dataframe(equity_df.tail(20))
        else:
            st.warning("CSV found but no 'equity' column exists.")
            st.write("Columns:", equity_df.columns.tolist())

    except Exception as e:
        st.error(f"Could not load equity data: {e}")

else:
    st.info("No equity_curve.csv found yet.")


# =====================================================
# CONFIG SNAPSHOT
# =====================================================
st.subheader("Config Snapshot")

if config is None:
    st.warning("config.py could not be loaded.")
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

    if hasattr(config, "API_KEY"):
        snapshot["API_KEY"] = "****"

    if hasattr(config, "API_SECRET"):
        snapshot["API_SECRET"] = "****"

    if hasattr(config, "API_PASSWORD"):
        snapshot["API_PASSWORD"] = "****"

    st.json(snapshot)
    st.subheader("Trade History")

if os.path.exists("trades.csv"):
    trades_df = pd.read_csv("trades.csv")
    st.dataframe(trades_df.tail(20))
else:
    st.info("No trades logged yet.")
if os.path.exists("trades.csv"):
    df = pd.read_csv("trades.csv")

    st.metric("Total Trades", len(df))
    st.metric("Winrate", f"{(df['pnl'] > 0).mean() * 100:.2f}%")
    st.metric("Total PnL", f"{df['pnl'].sum():.2f}")

