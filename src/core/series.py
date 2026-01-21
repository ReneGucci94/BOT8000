from typing import List, Optional, Iterator
from .candle import Candle

class MarketSeries:
    def __init__(self, candles: List[Candle]):
        # Enforce sorting by timestamp on creation
        self._candles = sorted(candles, key=lambda c: c.timestamp)
    
    @property
    def candles(self) -> List[Candle]:
        return self._candles
    
    @property
    def current(self) -> Candle:
        if not self._candles:
            raise IndexError("Series is empty")
        return self._candles[-1]
    
    @property
    def last_closed(self) -> Optional[Candle]:
        """Returns the last candle where complete=True."""
        for c in reversed(self._candles):
            if c.complete:
                return c
        return None

    def __len__(self) -> int:
        return len(self._candles)
        
    def __iter__(self) -> Iterator[Candle]:
        return iter(self._candles)

    def add(self, candle: Candle) -> 'MarketSeries':
        """
        Functional add: Returns a NEW MarketSeries instance with the new candle.
        Does NOT mutate the current instance.
        """
        # Optimized for readability, not performance (yet)
        return MarketSeries(self._candles + [candle])
    
    def get(self, index: int) -> Candle:
        return self._candles[index]
