import pandas as pd
import config

from trade_logger import log_trade

from position_manager import (
    clear_position
)

# =========================================================
# ADD INDICATORS
# =========================================================
def add_indicators(
    df: pd.DataFrame
) -> pd.DataFrame:

    df = df.copy()

    # =====================================================
    # FOREX VOLUME FIX
    # MT5 uses tick_volume instead of volume
    # =====================================================
    if "volume" not in df.columns:

        if "tick_volume" in df.columns:

            df["volume"] = (
                df["tick_volume"]
            )

        else:

            df["volume"] = 0

    # =====================================================
    # FAST EMA
    # =====================================================
    df["ema_fast"] = (
        df["close"]
        .ewm(
            span=50,
            adjust=False
        )
        .mean()
    )

    # =====================================================
    # SLOW EMA
    # =====================================================
    df["ema_slow"] = (
        df["close"]
        .ewm(
            span=200,
            adjust=False
        )
        .mean()
    )

    # =====================================================
    # RSI
    # =====================================================
    delta = df["close"].diff()

    gain = delta.clip(lower=0)

    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(14).mean()

    avg_loss = loss.rolling(14).mean()

    rs = avg_gain / (
        avg_loss + 1e-9
    )

    df["rsi"] = (
        100 - (100 / (1 + rs))
    )

    # =====================================================
    # ATR
    # =====================================================
    high_low = (
        df["high"] - df["low"]
    )

    high_close = (
        df["high"]
        - df["close"].shift()
    ).abs()

    low_close = (
        df["low"]
        - df["close"].shift()
    ).abs()

    tr = pd.concat(
        [
            high_low,
            high_close,
            low_close
        ],
        axis=1
    ).max(axis=1)

    df["atr"] = (
        tr.rolling(14).mean()
    )

    # =====================================================
    # VOLUME MOVING AVERAGE
    # =====================================================
    df["volume_ma"] = (
        df["volume"]
        .rolling(20)
        .mean()
    )

    return df


# =========================================================
# ENTRY LOGIC
# =========================================================
def handle_entry(
    window_df,
    price,
    rm,
    position
):

    # =====================================================
    # ALREADY IN POSITION
    # =====================================================
    if position is not None:
        return None

    latest = window_df.iloc[-1]

    previous = window_df.iloc[-2]

    # =====================================================
    # EMA VALUES
    # =====================================================
    fast_now = latest["ema_fast"]

    slow_now = latest["ema_slow"]

    fast_prev = previous["ema_fast"]

    slow_prev = previous["ema_slow"]

    # =====================================================
    # RSI
    # =====================================================
    rsi_now = latest["rsi"]

    # =====================================================
    # ATR
    # =====================================================
    atr_now = latest["atr"]

    # =====================================================
    # VOLUME
    # =====================================================
    volume_now = latest["volume"]

    volume_avg = latest["volume_ma"]

    # =====================================================
    # SAFETY CHECKS
    # =====================================================
    if pd.isna(rsi_now):
        return None

    if pd.isna(atr_now):
        return None

    if pd.isna(volume_avg):
        return None

    if atr_now <= 0:
        return None

    # =====================================================
    # VOLUME FILTER
    # =====================================================
    high_volume = (
        volume_now >= volume_avg
    )

    # =====================================================
    # LONG ENTRY CONDITIONS
    # =====================================================
    bullish_cross = (
        fast_prev < slow_prev
        and fast_now > slow_now
    )

    bullish_trend = (
        fast_now > slow_now
    )

    good_rsi = (
        40 <= rsi_now <= 75
    )

    # =====================================================
    # DEBUG LOGS
    # =====================================================
    print("================================")
    print("FAST NOW:", fast_now)
    print("SLOW NOW:", slow_now)
    print("RSI:", rsi_now)
    print("ATR:", atr_now)
    print("HIGH VOLUME:", high_volume)
    print("BULLISH CROSS:", bullish_cross)
    print("================================")

    # =====================================================
    # FINAL LONG ENTRY
    # =====================================================
    if True:

        amount = rm.get_position_size(
            price
        )

        if amount <= 0:
            return None

        atr_mult_sl = 1.5

        atr_mult_tp = 3.0

        new_position = {
            "side": "long",
            "entry_price": price,
            "amount": amount,
            "stop_loss": (
                price
                - atr_mult_sl * atr_now
            ),
            "take_profit": (
                price
                + atr_mult_tp * atr_now
            ),
            "trail": None,
            "atr": atr_now,
        }

        print(
            "NEW TRADE SIGNAL:",
            new_position
        )

        return new_position

    return None

# =========================================================
# EXIT LOGIC
# =========================================================
def handle_exit(
    position,
    price,
    rm
):

    if position is None:
        return None

    side = position["side"]

    entry = position["entry_price"]

    amount = position["amount"]

    stop_loss = position["stop_loss"]

    take_profit = position["take_profit"]

    trail = position.get("trail")

    # =====================================================
    # CALCULATE PNL
    # =====================================================
    if side == "long":

        pnl = (
            (price - entry)
            * amount
            * 1000
        )

    else:

        pnl = (
            (entry - price)
            * amount
            * 1000
        )

    # =====================================================
    # CLOSE CONDITIONS
    # =====================================================
    should_close = False

    close_reason = ""

    # STOP LOSS
    if (
        side == "long"
        and price <= stop_loss
    ):

        should_close = True
        close_reason = "STOP LOSS"

    # TAKE PROFIT
    elif (
        side == "long"
        and price >= take_profit
    ):

        should_close = True
        close_reason = "TAKE PROFIT"

    # TRAILING STOP
    elif (
        trail is not None
        and price <= trail
    ):

        should_close = True
        close_reason = "TRAILING STOP"

    # =====================================================
    # CLOSE POSITION
    # =====================================================
    if should_close:

        rm.realize(pnl)

        try:

            import sqlite3

            conn = sqlite3.connect(
                "trading_bot.db"
            )

            cursor = conn.cursor()

            # =============================================
            # UPDATE POSITION
            # =============================================
            cursor.execute(
                """
                UPDATE positions
                SET current_price = ?,
                    pnl = ?
                WHERE symbol = ?
                """,
                (
                    float(price),
                    float(pnl),
                    position.get("symbol", "")
                )
            )

            conn.commit()

            conn.close()

        except Exception as e:

            print(
                "DATABASE UPDATE ERROR:",
                e
            )

        print(
            f"{close_reason} HIT | PNL: {pnl}"
        )

        return None

    return position


# =========================================================
# TRAILING STOP UPDATE
# =========================================================
def update_trailing_stop(
    position,
    price
):

    if position is None:
        return None

    if position["side"] != "long":
        return position

    atr = position.get("atr")

    if atr is None:
        return position

    if atr <= 0:
        return position

    # =====================================================
    # DYNAMIC ATR TRAILING STOP
    # =====================================================
    trail_mult = 1.2

    new_trail = (
        price
        - trail_mult * atr
    )

    # =====================================================
    # INITIALIZE TRAIL
    # =====================================================
    if position["trail"] is None:

        position["trail"] = (
            new_trail
        )

    else:

        # ONLY MOVE TRAIL UP
        position["trail"] = max(
            position["trail"],
            new_trail
        )

    print(
        "UPDATED TRAILING STOP:",
        position["trail"]
    )

    return position