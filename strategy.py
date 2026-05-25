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

    if position is not None:
        return position

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
        return position

    if pd.isna(atr_now):
        return position

    if pd.isna(volume_avg):
        return position

    if atr_now <= 0:
        return position

    # =====================================================
    # VOLUME FILTER
    # =====================================================
    high_volume = (
        volume_now > volume_avg
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
        45 <= rsi_now <= 70
    )

    # =====================================================
    # FINAL LONG ENTRY
    # =====================================================
    if (
        bullish_cross
        and bullish_trend
        and good_rsi
        and high_volume
    ):

        amount = rm.get_position_size(
            price
        )

        if amount <= 0:
            return position

        atr_mult_sl = 1.5

        atr_mult_tp = 3.0

        return {
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

    return position


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
    pnl = amount * (
        price - entry
    )

    # =====================================================
    # BREAK EVEN PROTECTION
    # =====================================================
    risk_distance = (
        entry - stop_loss
    )

    reward_distance = (
        price - entry
    )

    if reward_distance >= risk_distance:

        position["stop_loss"] = max(
            stop_loss,
            entry
        )

    # =====================================================
    # STOP LOSS
    # =====================================================
    if (
        side == "long"
        and price <= position["stop_loss"]
    ):

        rm.realize(pnl)

        log_trade(
            side=side,
            entry_price=entry,
            exit_price=price,
            amount=amount,
            pnl=pnl,
            equity=rm.capital,
        )

        clear_position()

        return None

    # =====================================================
    # TAKE PROFIT
    # =====================================================
    if (
        side == "long"
        and price >= take_profit
    ):

        rm.realize(pnl)

        log_trade(
            side=side,
            entry_price=entry,
            exit_price=price,
            amount=amount,
            pnl=pnl,
            equity=rm.capital,
        )

        clear_position()

        return None

    # =====================================================
    # TRAILING STOP
    # =====================================================
    if (
        trail is not None
        and price <= trail
    ):

        pnl = amount * (
            trail - entry
        )

        rm.realize(pnl)

        log_trade(
            side=side,
            entry_price=entry,
            exit_price=trail,
            amount=amount,
            pnl=pnl,
            equity=rm.capital,
        )

        clear_position()

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

    return position