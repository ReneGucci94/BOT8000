# src/alphas/momentum.py
from src.alphas.base import Alpha
from src.core.market import MarketState

class Alpha_Momentum(Alpha):
    """
    Alpha based on Trend Strength and Momentum using RSI.
    
    Score is normalized from RSI [0, 100] to [-1.0, 1.0].
    RSI > 50 (Bullish) -> Positive score.
    RSI < 50 (Bearish) -> Negative score.
    """
    
    def get_score(self, market_state: MarketState) -> float:
        # Use cached RSI from market state
        rsi_series = market_state.rsi
        if not rsi_series:
            return 0.0
            
        current_rsi = rsi_series[-1]
        
        # Normalize: (RSI - 50) / 50
        # 100 -> 1.0
        # 50  -> 0.0
        # 0   -> -1.0
        score = (current_rsi - 50) / 50.0
        
        # Clip to ensure bounds just in case of rounding or edge cases
        return max(-1.0, min(1.0, score))
