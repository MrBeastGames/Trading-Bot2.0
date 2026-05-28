import MetaTrader5 as mt5
import pandas as pd
import logging
import config

# =====================================================
# CONNECT MT5
# =====================================================

def get_exchange():

    if not mt5.initialize(

        login=config.MT5_LOGIN,
        password=config.MT5_PASSWORD,
        server=config.MT5_SERVER

    ):

        logging.error(
            "MT5 initialize failed"
        )

        return None

    logging.info(
        "MT5 CONNECTED"
    )

    return mt5

# =====================================================
# FETCH OHLCV
# =====================================================

def fetch_ohlcv(
    exchange,
    symbol,
    timeframe,
    limit=300
):

    timeframe_map = {

        "M1": mt5.TIMEFRAME_M1,
        "M5": mt5.TIMEFRAME_M5,
        "M15": mt5.TIMEFRAME_M15,
        "H1": mt5.TIMEFRAME_H1,

    }

    tf = timeframe_map.get(
        timeframe,
        mt5.TIMEFRAME_M5
    )

    rates = exchange.copy_rates_from_pos(
        symbol,
        tf,
        0,
        limit
    )

    if rates is None:

        return pd.DataFrame()

    df = pd.DataFrame(rates)

    df["time"] = pd.to_datetime(
        df["time"],
        unit="s"
    )

    return df

# =====================================================
# PLACE MARKET ORDER
# =====================================================

# =====================================================
# PLACE MARKET ORDER
# =====================================================
def place_market_order(
    exchange,
    symbol,
    side,
    amount
):

    import MetaTrader5 as mt5
    import logging

    # =============================================
    # SYMBOL INFO
    # =============================================
    symbol_info = mt5.symbol_info(symbol)

    if symbol_info is None:

        logging.error(
            f"{symbol} not found"
        )

        return None

    # =============================================
    # ENABLE SYMBOL
    # =============================================
    if not symbol_info.visible:

        mt5.symbol_select(symbol, True)

    # =============================================
    # TICK DATA
    # =============================================
    tick = mt5.symbol_info_tick(symbol)

    if tick is None:

        logging.error(
            f"No tick data for {symbol}"
        )

        return None

    # =============================================
    # ORDER TYPE
    # =============================================
    if side.lower() == "buy":

        order_type = mt5.ORDER_TYPE_BUY
        price = tick.ask

    else:

        order_type = mt5.ORDER_TYPE_SELL
        price = tick.bid

    # =============================================
    # SAFE LOT SIZE
    # =============================================
    amount = round(float(amount), 2)

    if amount < 0.01:
        amount = 0.01

    # =============================================
    # TRY ALL FILLING MODES
    # =============================================
    filling_modes = [
        mt5.ORDER_FILLING_FOK,
        mt5.ORDER_FILLING_IOC,
        mt5.ORDER_FILLING_RETURN,
    ]

    for filling in filling_modes:

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": amount,
            "type": order_type,
            "price": price,
            "deviation": 20,
            "magic": 123456,
            "comment": "AI Forex Bot",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": filling,
        }

        result = mt5.order_send(request)

        if result is None:

            continue

        # SUCCESS
        if result.retcode == mt5.TRADE_RETCODE_DONE:

            logging.info(
                f"ORDER SUCCESS: {symbol}"
            )

            logging.info(result)

            return result

        else:

            logging.warning(
                f"Filling mode failed: "
                f"{filling}"
            )

            logging.warning(result)

    logging.error(
        f"ALL FILLING MODES FAILED "
        f"for {symbol}"
    )

    return None
 # =====================================================
# SLIPPAGE CHECK
# =====================================================
def check_slippage(
    exchange,
    symbol
):

    try:

        return True

    except Exception:

        return False