# src/alphas/ob_quality.py
from src.alphas.base import Alpha
from src.core.market import MarketState
from src.strategy.ob import detect_ob, OBType

class Alpha_OB_Quality(Alpha):
    """
    Alpha based on the quality and presence of TJR Order Blocks (OB).
    
    Score is positive for Bullish OBs and negative for Bearish OBs.
    The magnitude reflects the perceived 'strength' or 'quality' of the setup.
    """
    
    def get_score(self, market_state: MarketState) -> float:
        # Use H4 as the primary timeframe for TJR OB detection
        series = market_state.h4
        if len(series) == 0:
            return 0.0
            
        current_idx = len(series) - 1
        
        # 1. Detect OB using existing strategy logic
        ob = detect_ob(series, current_idx)
        
        if not ob:
            return 0.0
            
        # 2. Calculate Directional Base Score
        score = 1.0 if ob.type == OBType.BULLISH else -1.0
        
        # 3. Quality Multiplier (Placeholder for future complexity)
        # For now, we return full strength if detected.
        # Future: factor in sweep volume, BOS displacement, etc.
        quality_multiplier = 1.0
        
        return score * quality_multiplier
