import streamlit as st
import pandas as pd
import os

# =====================================================
# SAFE TELEGRAM IMPORT
# =====================================================
try:
    from telegram_utils import send_telegram_message
except:
    def send_telegram_message(msg):
        pass

# =====================================================
# SAFE CONFIG IMPORT
# =====================================================
try:
    import config
except:
    config = None

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="Trading Bot Dashboard",
    layout="wide"
)

# =====================================================
# TITLE
# =====================================================
st.title("🚀 Trading Bot Dashboard")

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
st.sidebar.title("⚙ Controls")

# TELEGRAM TEST
if st.sidebar.button("Send Telegram Test"):

    try:
        send_telegram_message(
            "📡 Dashboard test message"
        )
        st.sidebar.success("Message sent")

    except Exception as e:
        st.sidebar.error(str(e))

# START BOT
if st.sidebar.button("Start Bot"):

    st.session_state["bot_running"] = True

    send_telegram_message(
        "🟢 Bot started from dashboard"
    )

# STOP BOT
if st.sidebar.button("Stop Bot"):

    st.session_state["bot_running"] = False

    send_telegram_message(
        "🔴 Bot stopped from dashboard"
    )

# =====================================================
# STATUS SECTION
# =====================================================
st.subheader("🤖 Bot Status")

if st.session_state["bot_running"]:
    st.success("RUNNING")
else:
    st.error("STOPPED")

# =====================================================
# POSITION SECTION
# =====================================================
st.subheader("📌 Current Position")

position = st.session_state["position"]

if position:
    st.write(position)
else:
    st.info("No open position")

# =====================================================
# EQUITY CURVE
# =====================================================
st.subheader("📈 Equity Curve")

if os.path.exists("equity_curve.csv"):

    try:

        equity_df = pd.read_csv(
            "equity_curve.csv"
        )

        st.line_chart(equity_df)

        st.dataframe(
            equity_df.tail(20)
        )

    except Exception as e:

        st.error(
            f"Equity curve error: {e}"
        )

else:
    st.warning(
        "No equity_curve.csv found"
    )

# =====================================================
# TRADE HISTORY
# =====================================================
st.subheader("📜 Trade History")

if os.path.exists("trades.csv"):

    try:

        trades_df = pd.read_csv(
            "trades.csv"
        )

        st.dataframe(
            trades_df.tail(20)
        )

        # METRICS
        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Total Trades",
            len(trades_df)
        )

        if "pnl" in trades_df.columns:

            winrate = (
                (trades_df["pnl"] > 0).mean()
                * 100
            )

            pnl = trades_df["pnl"].sum()

            col2.metric(
                "Win Rate",
                f"{winrate:.2f}%"
            )

            col3.metric(
                "Total PnL",
                f"{pnl:.2f}"
            )

    except Exception as e:

        st.error(
            f"Trade history error: {e}"
        )

else:
    st.info("No trades logged yet")

# =====================================================
# CONFIG SNAPSHOT
# =====================================================
st.subheader("⚙ Config Snapshot")

if config:

    snapshot = {

        "EXCHANGE_ID":
        getattr(config, "EXCHANGE_ID", ""),

        "SYMBOL":
        getattr(config, "SYMBOL", ""),

        "TIMEFRAME":
        getattr(config, "TIMEFRAME", ""),

        "PAPER_TRADING":
        getattr(config, "PAPER_TRADING", "")
    }

    st.json(snapshot)

else:
    st.warning("Config not loaded")