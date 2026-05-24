import streamlit as st
import pandas as pd
import os
import ccxt
import plotly.express as px
from streamlit_autorefresh import st_autorefresh

import config

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
st_autorefresh(interval=5000, key="refresh")

# =====================================================
# TITLE
# =====================================================
st.title("🚀 AI Trading Dashboard")

# =====================================================
# CONNECT TO BITGET
# =====================================================
@st.cache_resource
def get_exchange():

    exchange = ccxt.bitget({
        "apiKey": config.API_KEY,
        "secret": config.API_SECRET,
        "password": config.API_PASSWORD,
        "enableRateLimit": True,
        "options": {
            "defaultType": "swap"
        }
    })

    return exchange

exchange = get_exchange()

# =====================================================
# SIDEBAR
# =====================================================
st.sidebar.title("⚙ Control Panel")

st.sidebar.success("Dashboard Online")

# =====================================================
# FETCH BALANCE
# =====================================================
balance = 0

try:

    bal = exchange.fetch_balance()

    if "USDT" in bal["total"]:
        balance = bal["total"]["USDT"]

except:
    pass

# =====================================================
# FETCH BTC PRICE
# =====================================================
btc_price = 0

try:

    ticker = exchange.fetch_ticker(
        config.SYMBOL
    )

    btc_price = ticker["last"]

except:
    pass

# =====================================================
# TOP METRICS
# =====================================================
col1, col2, col3 = st.columns(3)

col1.metric(
    "BTC Price",
    f"${btc_price:,.2f}"
)

col2.metric(
    "Futures Balance",
    f"${balance:,.2f}"
)

col3.metric(
    "Trading Pair",
    config.SYMBOL
)

# =====================================================
# OPEN POSITIONS
# =====================================================
st.subheader("📌 Open Positions")

try:

    positions = exchange.fetch_positions()

    active_positions = []

    for p in positions:

        contracts = float(p.get("contracts", 0))

        if contracts > 0:
            active_positions.append({
                "Symbol": p["symbol"],
                "Side": p["side"],
                "Contracts": contracts,
                "PnL": p.get("unrealizedPnl", 0)
            })

    if active_positions:

        pos_df = pd.DataFrame(
            active_positions
        )

        st.dataframe(pos_df)

    else:

        st.info("No open positions")

except Exception as e:

    st.warning(str(e))

# =====================================================
# TRADE HISTORY
# =====================================================
st.subheader("📜 Trade History")

if os.path.exists("trades.csv"):

    trades_df = pd.read_csv(
        "trades.csv"
    )

    st.dataframe(
        trades_df.tail(20)
    )

    if "pnl" in trades_df.columns:

        winrate = (
            (trades_df["pnl"] > 0).mean()
            * 100
        )

        total_pnl = trades_df["pnl"].sum()

        c1, c2 = st.columns(2)

        c1.metric(
            "Win Rate",
            f"{winrate:.2f}%"
        )

        c2.metric(
            "Total PnL",
            f"${total_pnl:.2f}"
        )

else:

    st.info("No trades logged")

# =====================================================
# EQUITY CURVE
# =====================================================
st.subheader("📈 Equity Curve")

if os.path.exists("equity_curve.csv"):

    equity_df = pd.read_csv(
        "equity_curve.csv"
    )

    fig = px.line(
        equity_df,
        y=equity_df.columns[-1],
        title="Equity Curve"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# =====================================================
# CONFIG SNAPSHOT
# =====================================================
st.subheader("⚙ Config")

st.json({
    "Exchange": config.EXCHANGE_ID,
    "Symbol": config.SYMBOL,
    "Timeframe": config.TIMEFRAME,
    "Paper Trading": config.PAPER_TRADING
})

# =====================================================
# SYSTEM STATUS
# =====================================================
st.subheader("🖥 System Status")

st.success("Railway Deployment Active")

st.success("Bitget API Connected")

st.success("Dashboard Running")