# src/agents/orchestrator.py
from typing import Optional, Dict
from src.core.regime import MarketRegime
from src.core.market import MarketState
from src.core.classifier import classify_regime
from src.execution.executor import TradeSignal

# Import Agents
from src.agents.trend_hunter import TrendHunterAgent
from src.agents.mean_reversion import MeanReversionAgent
from src.agents.volatility_filter import VolatilityFilterAgent
from src.agents.breakout_hunter import BreakoutHunterAgent
from src.agents.sentiment_scout import SentimentScoutAgent

class MSCOrchestrator:
    """
    Multi-Strategy Coordinator (MSC) Orchestrator (Layer 1).
    Selects the "Single Winner" specialized agent based on the market regime.
    """
    
    def __init__(self):
        # 1. Map regimes to specialized agents
        self.agents = {
            MarketRegime.TRENDING_BULLISH: TrendHunterAgent(),
            MarketRegime.TRENDING_BEARISH: TrendHunterAgent(),
            MarketRegime.SIDEWAYS_RANGE: MeanReversionAgent(),
            MarketRegime.HIGH_VOLATILITY: VolatilityFilterAgent(),
            MarketRegime.BREAKOUT_PENDING: BreakoutHunterAgent(),
            MarketRegime.NEWS_DRIVEN: SentimentScoutAgent()
        }
    
    def get_signal(self, market_state: MarketState) -> Optional[TradeSignal]:
        """
        Coordinates the brain's decision.
        1. Classifies regime.
        2. Delegates to the specialist.
        3. Injects metadata for audit.
        """
        # 1. Classify Regime (The Brain)
        regime = classify_regime(market_state)
        
        # 2. Select Agent (The specialist)
        agent = self.agents.get(regime)
        if not agent:
            # Fallback to Sentiment Scout (Balanced) if for some reason regime is not mapped
            agent = self.agents[MarketRegime.NEWS_DRIVEN]
            
        # 3. Generate Signal
        signal = agent.generate_signal(market_state)
        
        # 4. Inject Metadata for audit (Layer 1 requirement)
        if signal:
            # We use object.__setattr__ if the dataclass is frozen
            # Checking if TradeSignal is frozen (usually is in this codebase)
            # Actually, our src/execution/executor.py defines it as frozen=True
            object.__setattr__(signal, 'metadata', {
                'agent': agent.__class__.__name__,
                'regime': regime.value,
                'timestamp': getattr(market_state, 'timestamp', 0)
            })
            
        return signal
