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
            self._cache['rsi'] = calculate_rsi(self.h4)
        return self._cache['rsi']

    @property
    def atr(self):
        """Lazy cached ATR calculation (placeholder)."""
        if 'atr' not in self._cache:
            self._cache['atr'] = calculate_atr(self.h4)
        return self._cache['atr']

    @property
    def adx(self) -> float:
        """Lazy cached ADX calculation."""
        if 'adx' not in self._cache:
            self._cache['adx'] = calculate_adx(self.h4)
        return self._cache['adx']

    @property
    def atr_avg_14(self) -> float:
        """Lazy cached ATR average (14 periods)."""
        if 'atr_avg_14' not in self._cache:
            # Note: For simplicity, we calculate it from the atr series
            atr_series = self.atr
            if len(atr_series) >= 14:
                self._cache['atr_avg_14'] = sum(atr_series[-14:]) / 14.0
            else:
                self._cache['atr_avg_14'] = sum(atr_series) / len(atr_series) if atr_series else 1.0
        return self._cache['atr_avg_14']

    @property
    def ema_alignment(self) -> str:
        """Lazy cached EMA alignment (20 vs 50)."""
        if 'ema_alignment' not in self._cache:
            ema_20 = calculate_ema(self.h4, 20)
            ema_50 = calculate_ema(self.h4, 50)
            
            if ema_20 > ema_50:
                alignment = 'bullish'
            elif ema_20 < ema_50:
                alignment = 'bearish'
            else:
                alignment = 'neutral'
            
            self._cache['ema_alignment'] = alignment
        return self._cache['ema_alignment']

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

def calculate_adx(series: MarketSeries) -> float:
    """Placeholder for ADX calculation."""
    # Real ADX would involve smoothed DMS/TR
    return 25.0

def calculate_ema(series: MarketSeries, period: int) -> float:
    """Placeholder for EMA calculation."""
    if len(series) == 0:
        return 0.0
    return float(series.get(-1).close)


