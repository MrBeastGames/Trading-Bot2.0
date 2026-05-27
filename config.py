import os
from dotenv import load_dotenv

# =====================================================
# LOAD ENV VARIABLES
# =====================================================
load_dotenv()

# =====================================================
# EXCHANGE
# =====================================================
EXCHANGE_ID = "bitget"

# =====================================================
# PRIMARY SYMBOL
# =====================================================
SYMBOL = "SOL/USDT"

# =====================================================
# MULTI PAIR TRADING
# =====================================================
SYMBOLS = [

    "BTC/USDT",
    "ETH/USDT",
    "SOL/USDT",
    "XRP/USDT",

]

# =====================================================
# STAGGER PAIR STARTUP
# Prevents Bitget API burst / 429 errors
# =====================================================
PAIR_STARTUP_DELAY = 10

# =====================================================
# TIMEFRAME
# =====================================================
TIMEFRAME = "1m"

# =====================================================
# CAPITAL
# =====================================================
INITIAL_CAPITAL = 50

# =====================================================
# RISK MANAGEMENT
# =====================================================
RISK_PER_TRADE_USD = 2

MAX_DAILY_LOSS_USD = 10

MAX_TRADES_PER_DAY = 10

LEVERAGE = 5

TRADE_COOLDOWN_SECONDS = 300

# =====================================================
# STRATEGY SETTINGS
# =====================================================
STOP_LOSS_PCT = 0.015

TAKE_PROFIT_PCT = 0.045

TRAILING_STOP_PCT = 0.02

# =====================================================
# SLIPPAGE PROTECTION
# =====================================================
MAX_SPREAD_PCT = 0.15

MAX_VOLATILITY_PCT = 1.0

# =====================================================
# MODES
# =====================================================
PAPER_TRADING = True

BACKTESTING = False

USE_TELEGRAM = True

USE_DASHBOARD = True

USE_TESTNET = False

# =====================================================
# LIVE TRADING SAFETY
# =====================================================
ENABLE_LIVE_TRADING = True

# =====================================================
# OUTPUT FILES
# =====================================================
EQUITY_CSV_PATH = "equity_curve.csv"

EQUITY_PNG_PATH = "equity_curve.png"

# =====================================================
# DATABASE
# =====================================================
DATABASE_ENABLED = True

# =====================================================
# DASHBOARD AUTH
# =====================================================
DASHBOARD_USERNAME = "admin"

DASHBOARD_PASSWORD = "changeme"

# =====================================================
# TELEGRAM
# =====================================================
TELEGRAM_BOT_TOKEN = os.getenv(
    "TELEGRAM_BOT_TOKEN"
)

TELEGRAM_CHAT_ID = os.getenv(
    "TELEGRAM_CHAT_ID"
)

# =====================================================
# BITGET API
# =====================================================
# Use Railway Variables
# NEVER hardcode real API keys
# =====================================================
API_KEY = os.getenv(
    "BITGET_API_KEY"
)

API_SECRET = os.getenv(
    "BITGET_API_SECRET"
)

API_PASSWORD = os.getenv(
    "BITGET_API_PASSWORD"
)

# =====================================================
# API VALIDATION
# =====================================================
if not API_KEY:

    print(
        "WARNING: BITGET_API_KEY missing."
    )

if not API_SECRET:

    print(
        "WARNING: BITGET_API_SECRET missing."
    )

if not API_PASSWORD:

    print(
        "WARNING: BITGET_API_PASSWORD missing."
    )

# =====================================================
# RATE LIMIT PROTECTION
# =====================================================
ENABLE_RATE_LIMIT = True

API_TIMEOUT = 30000

REQUEST_RETRY_DELAY = 15

# =====================================================
# LOOP DELAYS
# =====================================================
MAIN_LOOP_SLEEP = 15

ERROR_SLEEP = 30

# =====================================================
# RAILWAY SETTINGS
# =====================================================
PORT = int(
    os.environ.get(
        "PORT",
        8080
    )
)

# =====================================================
# LOGGING
# =====================================================
LOG_LEVEL = "INFO"

# =====================================================
# DEBUG MODE
# =====================================================
DEBUG = False