from dataclasses import dataclass, field
from typing import List, cast, Dict, Any
from .candle import Candle
from .series import MarketSeries
from .timeframe import Timeframe

@dataclass(frozen=True)
class MarketState:
    symbol: str
    m5: MarketSeries
    m15: MarketSeries
    h1: MarketSeries
    h4: MarketSeries
    _cache: Dict[str, Any] = field(default_factory=dict, init=False, repr=False)

    def __post_init__(self):
        # Use object.__setattr__ because the dataclass is frozen
        object.__setattr__(self, '_cache', {})

    @property
    def rsi(self):
        """Lazy cached RSI calculation (placeholder)."""
        if 'rsi' not in self._cache:
            # Note: In a real implementation, we would call an actual indicator lib
            self._cache['rsi'] = calculate_rsi(self.h4)
        return self._cache['rsi']

    @property
    def atr(self):
        """Lazy cached ATR calculation (placeholder)."""
        if 'atr' not in self._cache:
            self._cache['atr'] = calculate_atr(self.h4)
        return self._cache['atr']

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

    def update(self, candle: Candle) -> 'MarketState':
        """
        Returns a NEW MarketState with the candle added to the correct series.
        """
        if candle.timeframe == Timeframe.M5:
            return MarketState(
                symbol=self.symbol,
                m5=self.m5.add(candle),
                m15=self.m15,
                h1=self.h1,
                h4=self.h4
            )
        elif candle.timeframe == Timeframe.M15:
            return MarketState(
                symbol=self.symbol,
                m5=self.m5,
                m15=self.m15.add(candle),
                h1=self.h1,
                h4=self.h4
            )
        elif candle.timeframe == Timeframe.H1:
            return MarketState(
                symbol=self.symbol,
                m5=self.m5,
                m15=self.m15,
                h1=self.h1.add(candle),
                h4=self.h4
            )
        elif candle.timeframe == Timeframe.H4:
            return MarketState(
                symbol=self.symbol,
                m5=self.m5,
                m15=self.m15,
                h1=self.h1,
                h4=self.h4.add(candle)
            )
        else:
            # Should be unreachable if Timeframe enum is exhaustive for this bot
            return self

    def get_series(self, timeframe: Timeframe) -> MarketSeries:
        """Polymorphic access to series by timeframe."""
        if timeframe == Timeframe.M5:
            return self.m5
        elif timeframe == Timeframe.M15:
            return self.m15
        elif timeframe == Timeframe.H1:
            return self.h1
        elif timeframe == Timeframe.H4:
            return self.h4
        else:
            raise ValueError(f"Unsupported timeframe: {timeframe}")


def calculate_rsi(series: MarketSeries) -> List[float]:
    """Placeholder for RSI calculation."""
    # This will be mocked in tests or implemented with a real lib later
    return [50.0] * len(series)

def calculate_atr(series: MarketSeries) -> List[float]:
    """Placeholder for ATR calculation."""
    return [1.0] * len(series)


