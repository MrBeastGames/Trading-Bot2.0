import time
import logging
import config


class RiskManager:

    # =====================================================
    # INIT
    # =====================================================
    def __init__(self, capital):

        self.capital = capital

        self.last_trade_time = 0

        self.trade_count = 0

        self.daily_loss = 0

    # =====================================================
    # CHECK COOLDOWN + RISK LIMITS
    # =====================================================
    def can_trade(self):

        current_time = time.time()

        cooldown_passed = (
            current_time
            - self.last_trade_time
        ) > config.TRADE_COOLDOWN_SECONDS

        if not cooldown_passed:

            logging.warning(
                "Trade cooldown active."
            )

            return False

        if (
            self.daily_loss
            >= config.MAX_DAILY_LOSS_USD
        ):

            logging.warning(
                "Max daily loss reached."
            )

            return False

        if (
            self.trade_count
            >= config.MAX_TRADES_PER_DAY
        ):

            logging.warning(
                "Max trades reached."
            )

            return False

        return True

    # =====================================================
    # POSITION SIZE
    # =====================================================
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

        size = (
            position_value
            / entry_price
        )

        size = round(size, 4)

        # =================================================
        # MINIMUM SIZE
        # =================================================
        if size < 0.0001:

            size = 0.0001

        return size

    # =====================================================
    # RECORD TRADE
    # =====================================================
    def record_trade(self):

        self.trade_count += 1

        self.last_trade_time = time.time()

        logging.info(
            f"Trade Recorded | Count: {self.trade_count}"
        )

    # =====================================================
    # RECORD LOSS
    # =====================================================
    def record_loss(
        self,
        pnl
    ):

        if pnl < 0:

            self.daily_loss += abs(pnl)

            logging.warning(
                f"Daily Loss Updated: "
                f"{self.daily_loss:.2f}"
            )

    # =====================================================
    # REALIZE PNL
    # =====================================================
    def realize(
        self,
        pnl
    ):

        self.capital += pnl

        logging.info(
            f"PNL Realized: {pnl:.2f}"
        )

        logging.info(
            f"Updated Capital: "
            f"{self.capital:.2f}"
        )

        # RECORD LOSS
        self.record_loss(pnl)