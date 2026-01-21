from dataclasses import dataclass
from typing import List, cast
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


