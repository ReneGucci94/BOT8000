from dataclasses import dataclass
from decimal import Decimal

@dataclass(frozen=True)
class RiskConfig:
    risk_percentage: Decimal = Decimal("0.01") # 1% default

class RiskManager:
    def __init__(self, config: RiskConfig):
        self.config = config

    def calculate_position_size(self, account_balance: Decimal, entry_price: Decimal, stop_loss: Decimal) -> Decimal:
        """
        Calculates position size based on fixed % risk of account balance.
        Formula: Qty = (Balance * Risk%) / |Entry - SL|
        """
        if entry_price == stop_loss:
            raise ValueError("Stop Loss cannot be equal to Entry")
            
        risk_amount = account_balance * self.config.risk_percentage
        price_diff = abs(entry_price - stop_loss)
        
        quantity = risk_amount / price_diff
        
        # Rounding? For crypto usually 8 decimals for BTC, but exchange dependent.
        # For now, let's keep high precision or normalize to reasonable standard (e.g. 6 places).
        # TJR Strategy focuses on precision.
        
        return quantity
