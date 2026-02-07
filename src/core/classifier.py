# src/core/classifier.py
from src.core.regime import MarketRegime
from src.core.market import MarketState

from typing import Dict, Any

def classify_regime(market_state: MarketState, params: Dict[str, Any] = None) -> MarketRegime:
    """
    Classifies the current market state into a specific MarketRegime.
    
    Logic hierarchy:
    1. High Volatility (ATR expansion)
    2. Trending (ADX and EMA alignment)
    3. Sideways (Low ADX)
    4. Breakout Pending (Extreme low vol + no trend)
    """
    # Defaults (si no se pasan params)
    if params is None:
        adx_trend_thresh = 25
        adx_sideways_thresh = 20
        atr_high_mult = 1.5
        atr_low_mult = 0.7
    else:
        adx_trend_thresh = params.get("adx_trend_threshold", 25)
        adx_sideways_thresh = params.get("adx_sideways_threshold", 15)
        atr_high_mult = params.get("atr_high_mult", 1.5)
        atr_low_mult = params.get("atr_low_mult", 0.65)
        
    adx = market_state.adx
    # Use last value of ATR series
    current_atr = market_state.atr[-1] if market_state.atr else 1.0
    atr_avg = market_state.atr_avg_14
    ema_alignment = market_state.ema_alignment
    
    # 1. High volatility priority
    if current_atr > (atr_avg * atr_high_mult):
        return MarketRegime.HIGH_VOLATILITY
        
    # 2. Strong trend
    if adx > adx_trend_thresh:
        if ema_alignment == 'bullish':
            return MarketRegime.TRENDING_BULLISH
        elif ema_alignment == 'bearish':
            return MarketRegime.TRENDING_BEARISH
            
    # 3. Consolidation (Low vol + No trend) -> Priority over generic Sideways
    if current_atr < (atr_avg * atr_low_mult) and adx < adx_trend_thresh:
        return MarketRegime.BREAKOUT_PENDING

    # 4. Sideways range
    if adx < adx_sideways_thresh:
        return MarketRegime.SIDEWAYS_RANGE
        
    # 5. Default
    return MarketRegime.SIDEWAYS_RANGE
