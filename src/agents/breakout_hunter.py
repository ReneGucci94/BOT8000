# src/agents/breakout_hunter.py
from src.agents.trading_agent import TradingAgent
from src.core.regime import MarketRegime

class BreakoutHunterAgent(TradingAgent):
    """
    Agent specialized in identifying potential breakouts.
    Bias: High Liquidity and OB Quality.
    """
    
    def __init__(self):
        super().__init__(
            alpha_weights={
                'ob_quality': 2.0,
                'liquidity': 3.0,
                'volatility': 1.5,
                'ml_confidence': 1.0,
                'momentum': 1.0
            },
            active_regimes=[
                MarketRegime.BREAKOUT_PENDING
            ]
        )
