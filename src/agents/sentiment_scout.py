# src/agents/sentiment_scout.py
from src.agents.trading_agent import TradingAgent
from src.core.regime import MarketRegime

class SentimentScoutAgent(TradingAgent):
    """
    Agent specialized in news-driven or sentiment-based regimes.
    Currently acts as a balanced baseline.
    """
    
    def __init__(self):
        super().__init__(
            alpha_weights={
                'ob_quality': 1.0,
                'momentum': 1.0,
                'volatility': 1.0,
                'ml_confidence': 1.0,
                'liquidity': 1.0
            },
            active_regimes=[
                MarketRegime.NEWS_DRIVEN
            ]
        )
