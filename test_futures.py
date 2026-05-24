import ccxt

exchange = ccxt.bitget({
    "enableRateLimit": True,

    "options": {
        "defaultType": "swap"
    }
})

print("CONNECTING TO FUTURES...")

markets = exchange.load_markets()

print("CONNECTED")

symbol = "BTC/USDT:USDT"

ticker = exchange.fetch_ticker(symbol)

print(ticker)