# src/agents/trading_agent.py
from abc import ABC
from typing import List, Dict, Optional
from src.alphas.combiner import AlphaCombiner
from src.alphas.ob_quality import Alpha_OB_Quality
from src.alphas.momentum import Alpha_Momentum
from src.alphas.volatility import Alpha_Volatility
from src.alphas.ml_confidence import Alpha_ML_Confidence
from src.alphas.liquidity import Alpha_Liquidity
from src.core.regime import MarketRegime
from src.core.market import MarketState
from src.execution.executor import TradeSignal

class TradingAgent(ABC):
    """
    Base class for specialized trading agents in the MSC Layer 2.
    Each agent has a specific Alpha personality (weights) and target regimes.
    """
    
    def __init__(self, alpha_weights: Dict[str, float], active_regimes: List[MarketRegime]):
        """
        Initialize the agent with its alpha weights and activation regimes.
        """
        alphas = [
            (Alpha_OB_Quality(), alpha_weights.get('ob_quality', 1.0)),
            (Alpha_Momentum(), alpha_weights.get('momentum', 1.0)),
            (Alpha_Volatility(), alpha_weights.get('volatility', 1.0)),
            (Alpha_ML_Confidence(), alpha_weights.get('ml_confidence', 1.0)),
            (Alpha_Liquidity(), alpha_weights.get('liquidity', 1.0))
        ]
        self.combiner = AlphaCombiner(alphas)
        self.active_regimes = active_regimes

    def should_activate(self, regime: MarketRegime) -> bool:
        """Determines if the agent should operate in the current market regime."""
        return regime in self.active_regimes

    def generate_signal(self, market_state: MarketState) -> Optional[TradeSignal]:
        """Generates a trading signal using the agent's unique alpha combination."""
        return self.combiner.get_signal(market_state, threshold=0.6)
