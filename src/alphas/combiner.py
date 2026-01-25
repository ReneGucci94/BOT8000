# src/alphas/combiner.py
from typing import List, Tuple, Optional, Any
from src.alphas.base import Alpha
from src.core.market import MarketState
from src.execution.executor import TradeSignal
from src.execution.broker import OrderSide

class AlphaCombiner:
    """
    Combines multiple Alpha signals into a single aggregate score and trade decision.
    
    Implements the weighted average of independent opinions (Pure Alpha philosophy).
    """
    
    def __init__(self, alphas_with_weights: List[Tuple[Alpha, float]]):
        """
        Args:
            alphas_with_weights: List of (AlphaInstance, weight)
        """
        self.alphas = alphas_with_weights
        
    def get_aggregate_score(self, market_state: MarketState) -> float:
        """
        Calculates the weighted average score of all alphas.
        
        Returns:
            float: Normalized score in range [-1.0, 1.0]
        """
        if not self.alphas:
            return 0.0
            
        total_score = 0.0
        total_weight = 0.0
        
        for alpha, weight in self.alphas:
            score = alpha.get_score(market_state)
            total_score += score * weight
            total_weight += weight
            
        if total_weight == 0:
            return 0.0
            
        return total_score / total_weight
        
    def get_signal(self, market_state: MarketState, threshold: float = 0.6) -> Optional[TradeSignal]:
        """
        Generates a trade signal if the aggregate score exceeds the threshold.
        
        Note: SL/TP should be determined by RiskManager, this provides direction & confidence.
        """
        score = self.get_aggregate_score(market_state)
        
        if abs(score) < threshold:
            return None
            
        # Direction
        side = OrderSide.BUY if score > 0 else OrderSide.SELL
        
        # We return a TradeSignal object. 
        # For compatibility with legacy system, we might need to fill entry_price.
        # But per requirements, direction is the key.
        
        # Accessing symbol from market_state
        symbol = getattr(market_state, 'symbol', 'BTCUSDT')
        
        # Note: In a full integration, SL/TP would be calculated outside or here 
        # using ATR, but for this task we focus on the combiner architecture.
        # We fill them with 0.0 here, expecting the RiskManager to override or 
        # the executor to handle them.
        
        return TradeSignal(
            symbol=symbol,
            side=side,
            entry_price=0.0, # Placeholder
            stop_loss=0.0,    # Placeholder
            take_profit=0.0,  # Placeholder
            confidence=abs(score) # Custom field added to TradeSignal if possible, or just used in logs
        )
