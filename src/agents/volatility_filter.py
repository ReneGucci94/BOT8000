# src/agents/volatility_filter.py
from src.agents.trading_agent import TradingAgent
from src.core.regime import MarketRegime

class VolatilityFilterAgent(TradingAgent):
    """
    Agent specialized in high volatility conditions.
    Bias: High Volatility alpha weight.
    """
    
    def __init__(self):
        super().__init__(
            alpha_weights={
                'ob_quality': 0.5,
                'momentum': 0.5,
                'volatility': 4.0,
                'ml_confidence': 0.5,
                'liquidity': 0.5
            },
            active_regimes=[
                MarketRegime.HIGH_VOLATILITY
            ]
        )
