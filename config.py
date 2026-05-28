import os
from dotenv import load_dotenv

load_dotenv()

# =====================================================
# EXCHANGE
# =====================================================
EXCHANGE_ID = "mt5"

# =====================================================
# MT5
# =====================================================

MT5_LOGIN = int(
    os.getenv("MT5_LOGIN")
)

MT5_PASSWORD = os.getenv(
    "MT5_PASSWORD"
)

MT5_SERVER = os.getenv(
    "MT5_SERVER"
)

# =====================================================
# FOREX PAIRS
# =====================================================

SYMBOLS = [

    "EURUSD",
    "GBPUSD",
    "USDJPY",

]

SYMBOL = "EURUSD"

# =====================================================
# STAGGER PAIR STARTUP
# Prevents MT5/API burst connections
# =====================================================

PAIR_STARTUP_DELAY = 10

# =====================================================
# TIMEFRAME
# =====================================================

TIMEFRAME = "M5"

# =====================================================
# RISK
# =====================================================

INITIAL_CAPITAL = 100

RISK_PER_TRADE_USD = 1

MAX_DAILY_LOSS_USD = 10

MAX_TRADES_PER_DAY = 10

LEVERAGE = 10

TRADE_COOLDOWN_SECONDS = 300

# =====================================================
# STRATEGY
# =====================================================

STOP_LOSS_PCT = 0.003

TAKE_PROFIT_PCT = 0.006

TRAILING_STOP_PCT = 0.002

# =====================================================
# MODES
# =====================================================

PAPER_TRADING = False

ENABLE_LIVE_TRADING = False

USE_TELEGRAM = True

USE_DASHBOARD = True

# =====================================================
# DASHBOARD AUTH
# =====================================================

DASHBOARD_USERNAME = "admin"

DASHBOARD_PASSWORD = "changeme"

# ============================================
# LOOP DELAYS
# ============================================
MAIN_LOOP_SLEEP = 15

ERROR_SLEEP = 30