# src/agents/mean_reversion.py
from src.agents.trading_agent import TradingAgent
from src.core.regime import MarketRegime

class MeanReversionAgent(TradingAgent):
    """
    Agent specialized in identifying overextended moves and mean reversion setups.
    Bias: High OB Quality and Negative Momentum.
    """
    
    def __init__(self):
        super().__init__(
            alpha_weights={
                'ob_quality': 3.0,
                'momentum': -1.5, # Contrarian bias
                'volatility': 0.5,
                'ml_confidence': 1.0,
                'liquidity': 0.8
            },
            active_regimes=[
                MarketRegime.SIDEWAYS_RANGE
            ]
        )
