# src/agents/trend_hunter.py
from src.agents.trading_agent import TradingAgent
from src.core.regime import MarketRegime

class TrendHunterAgent(TradingAgent):
    """
    Agent specialized in following strong trends.
    Bias: High Momentum and OB Quality.
    """
    
    def __init__(self):
        super().__init__(
            alpha_weights={
                'momentum': 3.0,
                'ob_quality': 2.0,
                'volatility': 1.0,
                'ml_confidence': 1.0,
                'liquidity': 0.8
            },
            active_regimes=[
                MarketRegime.TRENDING_BULLISH,
                MarketRegime.TRENDING_BEARISH
            ]
        )
