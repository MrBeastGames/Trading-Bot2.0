import config
import time


class RiskManager:

    def __init__(self, capital):

        self.capital = capital

        self.daily_loss = 0

        self.trade_count = 0

        self.last_trade_time = 0

    # =================================================
    # CHECK COOLDOWN
    # =================================================
    def can_trade(self):

        current_time = time.time()

        cooldown_passed = (
            current_time
            - self.last_trade_time
        ) > config.TRADE_COOLDOWN_SECONDS

        if not cooldown_passed:
            return False

        if self.daily_loss >= config.MAX_DAILY_LOSS_USD:
            return False

        if self.trade_count >= config.MAX_TRADES_PER_DAY:
            return False

        return True

    # =================================================
    # POSITION SIZE
    # =================================================
    def get_position_size(
        self,
        entry_price
    ):

        risk_amount = (
            config.RISK_PER_TRADE_USD
        )

        position_value = (
            risk_amount
            * config.LEVERAGE
        )

        btc_size = (
            position_value
            / entry_price
        )

        btc_size = round(
            btc_size,
            4
        )

        # =================================================
        # MINIMUM BTC SIZE
        # =================================================
        if btc_size < 0.0001:
            btc_size = 0.0001

        return btc_size

    # =================================================
    # RECORD TRADE
    # =================================================
    def record_trade(self):

        self.trade_count += 1

        self.last_trade_time = time.time()

    # =================================================
    # RECORD LOSS
    # =================================================
    def record_loss(self, pnl):

        if pnl < 0:
            self.daily_loss += abs(pnl)