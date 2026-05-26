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
ENABLE_LIVE_TRADING = False


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
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
API_PASSWORD = os.getenv("API_PASSWORD")


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