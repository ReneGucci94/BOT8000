from dataclasses import dataclass
from typing import List
from .series import MarketSeries
from .timeframe import Timeframe

@dataclass(frozen=True)
class MarketState:
    symbol: str
    m5: MarketSeries
    m15: MarketSeries
    h1: MarketSeries
    h4: MarketSeries

    @classmethod
    def empty(cls, symbol: str) -> 'MarketState':
        """Factory method to create an empty market state."""
        empty_series = MarketSeries([])
        return cls(
            symbol=symbol,
            m5=empty_series,
            m15=empty_series,
            h1=empty_series,
            h4=empty_series
        )
