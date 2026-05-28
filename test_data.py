import MetaTrader5 as mt5
import pandas as pd
import config

mt5.initialize(

    login=config.MT5_LOGIN,
    password=config.MT5_PASSWORD,
    server=config.MT5_SERVER

)

rates = mt5.copy_rates_from_pos(
    "EURUSD",
    mt5.TIMEFRAME_M5,
    0,
    10
)

df = pd.DataFrame(rates)

print(df)