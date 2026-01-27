# tests/agents/test_trading_agents.py
import pytest
from src.agents.trading_agent import TradingAgent
# We will import the implementations once created
from src.agents.trend_hunter import TrendHunterAgent
from src.agents.mean_reversion import MeanReversionAgent
from src.agents.volatility_filter import VolatilityFilterAgent
from src.agents.breakout_hunter import BreakoutHunterAgent
from src.agents.sentiment_scout import SentimentScoutAgent
from src.core.regime import MarketRegime

def test_trend_hunter_initialization():
    """Verificar pesos y regímenes de TrendHunter."""
    agent = TrendHunterAgent()
    
    # Pesos específicos del prompt
    # TrendHunter: Momentum: 3.0, OB: 2.0, Vol: 1.0, ML: 1.0, Liq: 0.8
    weights = {a[0].__class__.__name__: a[1] for a in agent.combiner.alphas}
    
    assert weights['Alpha_Momentum'] == 3.0
    assert weights['Alpha_OB_Quality'] == 2.0
    assert weights['Alpha_Volatility'] == 1.0
    
    # Regímenes
    assert agent.should_activate(MarketRegime.TRENDING_BULLISH)
    assert agent.should_activate(MarketRegime.TRENDING_BEARISH)
    assert not agent.should_activate(MarketRegime.SIDEWAYS_RANGE)

def test_mean_reversion_initialization():
    """Verificar pesos y regímenes de MeanReversion."""
    agent = MeanReversionAgent()
    
    # MeanReversion: OB: 3.0, Momentum: -1.5, Vol: 0.5, ML: 1.0, Liq: 0.8
    weights = {a[0].__class__.__name__: a[1] for a in agent.combiner.alphas}
    
    assert weights['Alpha_OB_Quality'] == 3.0
    assert weights['Alpha_Momentum'] == -1.5
    
    # Regímenes
    assert agent.should_activate(MarketRegime.SIDEWAYS_RANGE)
    assert not agent.should_activate(MarketRegime.TRENDING_BULLISH)

def test_volatility_filter_initialization():
    """Verificar pesos y regímenes de VolatilityFilter."""
    agent = VolatilityFilterAgent()
    weights = {a[0].__class__.__name__: a[1] for a in agent.combiner.alphas}
    assert weights['Alpha_Volatility'] == 4.0
    assert weights['Alpha_Momentum'] == 0.5
    assert agent.should_activate(MarketRegime.HIGH_VOLATILITY)

def test_breakout_hunter_initialization():
    """Verificar pesos y regímenes de BreakoutHunter."""
    agent = BreakoutHunterAgent()
    weights = {a[0].__class__.__name__: a[1] for a in agent.combiner.alphas}
    assert weights['Alpha_Liquidity'] == 3.0
    assert weights['Alpha_OB_Quality'] == 2.0
    assert agent.should_activate(MarketRegime.BREAKOUT_PENDING)

def test_sentiment_scout_initialization():
    """Verificar pesos y regímenes de SentimentScout."""
    agent = SentimentScoutAgent()
    weights = {a[0].__class__.__name__: a[1] for a in agent.combiner.alphas}
    # Todo 1.0
    for val in weights.values():
        assert val == 1.0
    assert agent.should_activate(MarketRegime.NEWS_DRIVEN)
