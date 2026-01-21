from dataclasses import dataclass
from enum import Enum
from typing import Optional
from decimal import Decimal
from core.series import MarketSeries

class FVGType(Enum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"

@dataclass(frozen=True)
class FVG:
    type: FVGType
    top: Decimal
    bottom: Decimal
    index: int # Index of the 2nd candle (the middle of the gap)

def detect_fvg(series: MarketSeries, index: int) -> Optional[FVG]:
    """
    Detects if there is a Fair Value Gap triggered by the candle at `index`.
    A FVG is formed by the relationship between candles i-2, i-1, i.
    Uses TJR definition:
    Bullish: High(i-2) < Low(i). Gap is [High(i-2), Low(i)]
    Bearish: Low(i-2) > High(i). Gap is [High(i), Low(i-2)] - Wait, standard is [Low(i-2), High(i)]. 
    Let's check TJR doc:
    Msg: "Espacio donde las mechas de vela 1 y vela 3 NO se tocan"
    Length: 3 candles.
    We check at index `index` (which is candle 3).
    """
    if index < 2:
        return None
        
    c1 = series.get(index - 2)
    # c2 = series.get(index - 1) # Middle candle usually big
    c3 = series.get(index)
    
    # Bullish FVG
    # C1 High < C3 Low
    if c1.high < c3.low:
        return FVG(
            type=FVGType.BULLISH,
            top=c3.low,
            bottom=c1.high,
            index=index - 1
        )
        
    # Bearish FVG
    # C1 Low > C3 High
    if c1.low > c3.high:
        return FVG(
            type=FVGType.BEARISH,
            top=c1.low,
            bottom=c3.high,
            index=index - 1
        )
        
    return None
