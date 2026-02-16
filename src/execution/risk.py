from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

@dataclass(frozen=True)
class RiskConfig:
    risk_percentage: Decimal = Decimal("0.01") # 1% default
    max_portfolio_risk: Optional[Decimal] = None
    use_dd_scaling: bool = False

class RiskManager:
    def __init__(self, config: RiskConfig):
        self.config = config

    def calculate_position_size(
        self, 
        account_balance: Decimal, 
        entry_price: Decimal, 
        stop_loss: Decimal,
        current_open_risk: Decimal = Decimal("0"),
        current_drawdown_pct: Decimal = Decimal("0")
    ) -> Decimal:
        """
        Calculates position size based on fixed % risk of account balance.
        Formula: Qty = (Balance * Risk%) / |Entry - SL|
        
        Applies Risk Overlay:
        1. Portfolio Heat: Caps total risk exposure if max_portfolio_risk is set.
        2. DD Scaling: Reduces risk during drawdowns if use_dd_scaling is True.
        """
        # Auto-cast for robustness
        current_open_risk = Decimal(str(current_open_risk))
        current_drawdown_pct = Decimal(str(current_drawdown_pct))

        if entry_price == stop_loss:
            raise ValueError("Stop Loss cannot be equal to Entry")
            
        risk_amount = account_balance * self.config.risk_percentage
        
        # 1. Drawdown Scaling
        if self.config.use_dd_scaling and current_drawdown_pct > 0:
            # Formula: multiplier = max(0.5, 1.0 - (dd * 2))
            multiplier = max(Decimal("0.5"), Decimal("1.0") - (current_drawdown_pct * Decimal("2.0")))
            risk_amount *= multiplier
            
        # 2. Portfolio Heat
        if self.config.max_portfolio_risk:
            max_risk_amt = account_balance * self.config.max_portfolio_risk
            available_risk = max_risk_amt - current_open_risk
            
            if available_risk <= 0:
                return Decimal("0")
            
            if risk_amount > available_risk:
                risk_amount = available_risk
        
        price_diff = abs(entry_price - stop_loss)
        
        quantity = risk_amount / price_diff
        
        # Rounding? For crypto usually 8 decimals for BTC, but exchange dependent.
        # For now, let's keep high precision or normalize to reasonable standard (e.g. 6 places).
        # TJR Strategy focuses on precision.
        
        return quantity
