import os
from dotenv import load_dotenv

# LOAD .ENV FILE
load_dotenv()

# =====================================================
# PAPER TRADING
# =====================================================
PAPER_TRADING = True

# =========================================================
# EXCHANGE
# =========================================================
EXCHANGE_ID = "bitget"

SYMBOL = "SOL/USDT"

TIMEFRAME = "1m"

# =====================================================
# LIVE TRADING SAFETY
# =====================================================
ENABLE_LIVE_TRADING = True


# =========================================================
# CAPITAL
# =========================================================
INITIAL_CAPITAL = 50

# =========================
# RISK MANAGEMENT
# =========================
RISK_PER_TRADE_USD = 2

MAX_DAILY_LOSS_USD = 10

MAX_TRADES_PER_DAY = 10

LEVERAGE = 5

TRADE_COOLDOWN_SECONDS = 300


# =========================================================
# STRATEGY
# =========================================================
STOP_LOSS_PCT = 0.015

TAKE_PROFIT_PCT = 0.045

TRAILING_STOP_PCT = 0.02


# =========================================================
# MODES
# =========================================================
PAPER_TRADING = True

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
import os

API_KEY = "bg_6ef587e9746fdbe465672a2be01681a1"
API_SECRET = "e32e7d3b08063d7f6aff40db6bcbdbcbcaa7376a70586db37ff04c67b12d177e"
API_PASSWORD = "1274712747"


# =========================================================
# TELEGRAM
# =========================================================
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
# =====================================================
# SLIPPAGE PROTECTION
# =====================================================

MAX_SPREAD_PCT = 0.15

MAX_VOLATILITY_PCT = 1.0