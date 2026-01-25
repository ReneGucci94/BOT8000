# src/alphas/liquidity.py
from src.alphas.base import Alpha
from src.core.market import MarketState
import statistics

class Alpha_Liquidity(Alpha):
    """
    Alpha based on Volume and Microstructure (Liquidity).
    
    Score reflects relative volume expansion or contraction.
    High Volume Relative to Mean -> Positive score (Suggests strong institutional activity).
    Low Volume Relative to Mean -> Negative score (Suggests low liquidity/trap).
    """
    
    def __init__(self, period: int = 20):
        self.period = period
    
    def get_score(self, market_state: MarketState) -> float:
        series = market_state.h4
        if len(series) < self.period + 1:
            return 0.0
            
        # Extract volumes
        volumes = [float(series.get(i).volume) for i in range(len(series) - self.period, len(series))]
        current_volume = volumes[-1]
        
        # Mean volume of the lookback period
        avg_volume = statistics.mean(volumes[:-1])
        
        if avg_volume == 0:
            return 0.0
            
        # Ratio: (Current / Avg) - 1.0
        # 300 / 100 - 1 = 2.0
        # 20 / 100 - 1 = -0.8
        score = (current_volume / avg_volume) - 1.0
        
        # Scale and clip
        # Max score of 1.0 reached at 2x average volume expansion
        return max(-1.0, min(1.0, score))
