# src/core/classifier.py
from src.core.regime import MarketRegime
from src.core.market import MarketState

def classify_regime(market_state: MarketState) -> MarketRegime:
    """
    Classifies the current market state into a specific MarketRegime.
    
    Logic hierarchy:
    1. High Volatility (ATR expansion)
    2. Trending (ADX and EMA alignment)
    3. Sideways (Low ADX)
    4. Breakout Pending (Extreme low vol + no trend)
    """
    adx = market_state.adx
    # Use last value of ATR series
    current_atr = market_state.atr[-1] if market_state.atr else 1.0
    atr_avg = market_state.atr_avg_14
    ema_alignment = market_state.ema_alignment
    
    # 1. High volatility priority
    if current_atr > (atr_avg * 1.5):
        return MarketRegime.HIGH_VOLATILITY
        
    # 2. Strong trend
    if adx > 25:
        if ema_alignment == 'bullish':
            return MarketRegime.TRENDING_BULLISH
        elif ema_alignment == 'bearish':
            return MarketRegime.TRENDING_BEARISH
            
    # 3. Consolidation (Low vol + No trend) -> Priority over generic Sideways
    if current_atr < (atr_avg * 0.7) and adx < 25:
        return MarketRegime.BREAKOUT_PENDING

    # 4. Sideways range
    if adx < 20:
        return MarketRegime.SIDEWAYS_RANGE
        
    # 5. Default
    return MarketRegime.SIDEWAYS_RANGE
