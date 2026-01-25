# src/alphas/volatility.py
from src.alphas.base import Alpha
from src.core.market import MarketState
import statistics

class Alpha_Volatility(Alpha):
    """
    Alpha based on Volatility Regime Detection using ATR.
    
    Score reflects ATR expansion or contraction relative to its average.
    Positive score -> Volatility is expanding (favorable for trend/TJR).
    Negative score -> Volatility is contracting (risk of chop/range).
    """
    
    def __init__(self, period: int = 14):
        self.period = period
    
    def get_score(self, market_state: MarketState) -> float:
        # Use cached ATR series
        atr_series = market_state.atr
        if len(atr_series) < self.period + 1:
            return 0.0
            
        current_atr = atr_series[-1]
        # Calculate moving average of ATR
        avg_atr = statistics.mean(atr_series[-self.period:])
        
        if avg_atr == 0:
            return 0.0
            
        # Ratio: Current / Average - 1.0
        # Expansion (2.0 / 1.0) - 1.0 = 1.0
        # Contraction (0.5 / 1.0) - 1.0 = -0.5
        score = (current_atr / avg_atr) - 1.0
        
        # Scale and clip
        # Assume a ratio of 2.0 (100% increase) is the max score of 1.0
        return max(-1.0, min(1.0, score))
