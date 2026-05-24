import os
from dotenv import load_dotenv

# LOAD .ENV FILE
load_dotenv()


# =========================================================
# EXCHANGE
# =========================================================
EXCHANGE_ID = "bitget"

SYMBOL = "BTC/USDT:USDT"

TIMEFRAME = "1m"


# =========================================================
# CAPITAL
# =========================================================
INITIAL_CAPITAL = 50

MAX_RISK_PER_TRADE = 0.0001


# =========================================================
# STRATEGY
# =========================================================
STOP_LOSS_PCT = 0.015

TAKE_PROFIT_PCT = 0.045

TRAILING_STOP_PCT = 0.02


# =========================================================
# MODES
# =========================================================
PAPER_TRADING = False

BACKTESTING = True

USE_TELEGRAM = True

USE_DASHBOARD = True

USE_TESTNET = False


# =========================================================
# OUTPUT FILES
# =========================================================
EQUITY_CSV_PATH = "equity_curve.csv"

EQUITY_PNG_PATH = "equity_curve.png"


# =========================================================
# BITGET API
# =========================================================
API_KEY = "bg_d3fd832cb78a15cb25853a905920e697"

API_SECRET = "8a8cec56de5d3b3896bfd17fcf34d9c72fa5d871e7600957762000a9460f8fb5"

API_PASSWORD = "1274712747"

# =========================================================
# TELEGRAM
# =========================================================
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")