# src/core/regime.py
from enum import Enum

class MarketRegime(Enum):
    TRENDING_BULLISH = "trending_bullish"
    TRENDING_BEARISH = "trending_bearish"
    SIDEWAYS_RANGE = "sideways_range"
    HIGH_VOLATILITY = "high_volatility"
    BREAKOUT_PENDING = "breakout_pending"
    NEWS_DRIVEN = "news_driven"
