import time
import logging
import config


class RiskManager:

    # =====================================================
    # INIT
    # =====================================================
    def __init__(self, capital):

        self.capital = capital

        self.starting_capital = capital

        self.last_trade_time = 0

        self.trade_count = 0

        self.daily_loss = 0

    # =====================================================
    # CHECK IF BOT CAN TRADE
    # =====================================================
    def can_trade(self):

        current_time = time.time()

        # =================================================
        # COOLDOWN
        # =================================================
        cooldown_passed = (
            current_time
            - self.last_trade_time
        ) > config.TRADE_COOLDOWN_SECONDS

        if not cooldown_passed:

            logging.warning(
                "Trade cooldown active."
            )

            return False

        # =================================================
        # DAILY LOSS LIMIT
        # =================================================
        if (
            self.daily_loss
            >= config.MAX_DAILY_LOSS_USD
        ):

            logging.warning(
                "Max daily loss reached."
            )

            return False

        # =================================================
        # MAX TRADES
        # =================================================
        if (
            self.trade_count
            >= config.MAX_TRADES_PER_DAY
        ):

            logging.warning(
                "Max trades per day reached."
            )

            return False

        # =================================================
        # LOW CAPITAL PROTECTION
        # =================================================
        if self.capital <= 5:

            logging.error(
                "Capital too low."
            )

            return False

        return True

    # =====================================================
    # FOREX POSITION SIZE
    # =====================================================
    def get_position_size(
        self,
        entry_price
    ):

        try:

            # =============================================
            # SAFE FIXED LOTS FOR EXNESS DEMO
            # =============================================
            # VERY IMPORTANT:
            # Start small until bot is stable
            # =============================================

            fixed_lot = 0.1

            logging.info(
                f"Using fixed lot size: {fixed_lot}"
            )

            return fixed_lot

        except Exception as e:

            logging.error(
                f"Position size error: {e}"
            )

            return 0.1

    # =====================================================
    # RECORD TRADE
    # =====================================================
    def record_trade(self):

        self.trade_count += 1

        self.last_trade_time = time.time()

        logging.info(
            f"Trade Recorded | "
            f"Count: {self.trade_count}"
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

        # =============================================
        # RECORD LOSSES
        # =============================================
        self.record_loss(pnl)

    # =====================================================
    # RESET DAILY STATS
    # =====================================================
    def reset_daily_stats(self):

        self.trade_count = 0

        self.daily_loss = 0

        logging.info(
            "Daily stats reset."
        )