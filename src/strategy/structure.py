from dataclasses import dataclass
from enum import Enum
from typing import Optional
from decimal import Decimal
from core.series import MarketSeries
from .fractals import is_valid_high, is_valid_low

class StructureType(Enum):
    BOS_BULLISH = "BOS_BULLISH"
    BOS_BEARISH = "BOS_BEARISH"

@dataclass(frozen=True)
class StructureEvent:
    type: StructureType
    price: Decimal # The price level that was broken (High/Low)
    broken_index: int # Index of the candle that formed the High/Low
    breakout_index: int # Index of the candle causing the break

def detect_bos(series: MarketSeries, index: int) -> Optional[StructureEvent]:
    """
    Scans for the most recent valid fractal and checks if the current candle
    breaks it with a BODY CLOSE.
    
    LIMITATION: For MVP, scans back up to 50 candles.
    """
    if index < 2:
        return None
        
    current = series.get(index)
    
    # Check for Bullish BOS (Breaking a recent High)
    # Scan backwards for the most recent valid high
    last_high_idx = -1
    for i in range(index - 1, max(-1, index - 50), -1):
        if is_valid_high(series, i):
            last_high_idx = i
            break
            
    if last_high_idx != -1:
        high_candle = series.get(last_high_idx)
        # Check if we CLOSED above the high
        if current.close > high_candle.high:
            # Verify that intermediate candles didn't already break it?
            # For simplicity/MVP, we just check if THIS candle broke it.
            # In a real scanner, you'd track state consistently.
            # Assuming this is called sequentially or we just want signal at this bar.
            return StructureEvent(
                type=StructureType.BOS_BULLISH,
                price=high_candle.high,
                broken_index=last_high_idx,
                breakout_index=index
            )

    # Check for Bearish BOS (Breaking a recent Low)
    last_low_idx = -1
    for i in range(index - 1, max(-1, index - 50), -1):
        if is_valid_low(series, i):
            last_low_idx = i
            break
            
    if last_low_idx != -1:
        low_candle = series.get(last_low_idx)
        # Check if we CLOSED below the low
        if current.close < low_candle.low:
            return StructureEvent(
                type=StructureType.BOS_BEARISH,
                price=low_candle.low,
                broken_index=last_low_idx,
                breakout_index=index
            )
            
    return None
