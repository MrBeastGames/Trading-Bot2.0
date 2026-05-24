import config


class RiskManager:
    def __init__(self, capital: float):
        self.capital = capital
        self.peak = capital
        self.max_dd = 0.0

    def get_position_size(self, entry_price: float, stop_price: float) -> float:
        risk_amount = self.capital * config.MAX_RISK_PER_TRADE
        price_risk = abs(entry_price - stop_price)
        if price_risk <= 0:
            return 0.0
        return risk_amount / price_risk

    def update(self, new_capital: float):
        self.capital = new_capital
        drawdown = (self.peak - new_capital) / self.peak if self.peak > 0 else 0
        self.max_dd = max(self.max_dd, drawdown)
        self.peak = max(self.peak, new_capital)
