
import streamlit as st
import pandas as pd
import numpy as np
import os
import sqlite3
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

sqlite3.enable_callback_tracebacks(True)

try:
    import config
except Exception:
    config = None

st.set_page_config(
    page_title="AI Trading Dashboard",
    layout="wide"
)

st_autorefresh(
    interval=10000,
    key="dashboard_refresh"
)

st.title("🚀 AI Trading Dashboard")

conn = sqlite3.connect(
    "trading_bot.db",
    check_same_thread=False,
    timeout=30
)

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

st.subheader("💰 Live PnL")

try:

    trades_df = pd.read_sql_query(
        "SELECT * FROM trades LIMIT 100",
        conn
    )

    if not trades_df.empty and "pnl" in trades_df.columns:

        total_pnl = trades_df["pnl"].fillna(0).sum()

        total_trades = len(trades_df)

        winrate = (
            (trades_df["pnl"] > 0).mean()
        ) * 100

        c1, c2, c3 = st.columns(3)

        c1.metric("Total PnL", f"${total_pnl:.2f}")
        c2.metric("Trades", total_trades)
        c3.metric("Winrate", f"{winrate:.2f}%")

        st.dataframe(
            trades_df.tail(20),
            use_container_width=True
        )

    else:

        st.info("No trades logged yet.")

except Exception as e:

    st.warning(f"Trades Error: {e}")

st.subheader("📊 Open Positions")

try:

    positions_df = pd.read_sql_query(
        "SELECT * FROM positions LIMIT 50",
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

    st.warning(f"Positions Error: {e}")

st.subheader("📈 Live Market Chart")

if os.path.exists("market_data.csv"):

    try:

        market_df = pd.read_csv(
            "market_data.csv"
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
                "OHLC columns missing."
            )

    except Exception as e:

        st.warning(
            f"Chart Error: {e}"
        )

else:

    st.warning(
        "No market_data.csv found."
    )

conn.close()
