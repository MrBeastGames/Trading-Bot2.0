import MetaTrader5 as mt5
import config

connected = mt5.initialize(

    login=config.MT5_LOGIN,
    password=config.MT5_PASSWORD,
    server=config.MT5_SERVER

)

if connected:

    print("MT5 CONNECTED")

    account = mt5.account_info()

    print(account)

else:

    print("MT5 FAILED")