from dataclasses import dataclass
from .types import Price, Volume, Timestamp
from .timeframe import Timeframe

@dataclass(frozen=True)
class Candle:
    timestamp: Timestamp
    open: Price
    high: Price
    low: Price
    close: Price
    volume: Volume
    timeframe: Timeframe
    complete: bool = False

    def __post_init__(self) -> None:
        # Invariant checks
        if self.high < self.low:
            raise ValueError(f"High ({self.high}) < Low ({self.low})")
        
        if self.volume < 0:
            raise ValueError(f"Volume ({self.volume}) < 0")
            
        # Wick integrity checks
        if self.high < self.open:
            raise ValueError(f"High ({self.high}) < Open ({self.open})")
        if self.high < self.close:
            raise ValueError(f"High ({self.high}) < Close ({self.close})")
            
        if self.low > self.open:
            raise ValueError(f"Low ({self.low}) > Open ({self.open})")
        if self.low > self.close:
            raise ValueError(f"Low ({self.low}) > Close ({self.close})")
