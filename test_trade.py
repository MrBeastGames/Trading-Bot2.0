import MetaTrader5 as mt5
import config

mt5.initialize(

    login=config.MT5_LOGIN,
    password=config.MT5_PASSWORD,
    server=config.MT5_SERVER

)

symbol = "EURUSD"

lot = 0.01

tick = mt5.symbol_info_tick(symbol)

request = {

    "action": mt5.TRADE_ACTION_DEAL,
    "symbol": symbol,
    "volume": lot,
    "type": mt5.ORDER_TYPE_BUY,
    "price": tick.ask,
    "deviation": 20,
    "magic": 100,
    "comment": "AI Forex Bot",
    "type_time": mt5.ORDER_TIME_GTC,
    "type_filling": mt5.ORDER_FILLING_IOC,

}

result = mt5.order_send(request)

print(result)