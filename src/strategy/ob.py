from dataclasses import dataclass
from enum import Enum
from typing import Optional
from decimal import Decimal
from src.core.series import MarketSeries
from .structure import detect_bos, StructureType
from .fractals import is_valid_low, is_valid_high

class OBType(Enum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"

@dataclass(frozen=True)
class OrderBlock:
    type: OBType
    top: Decimal
    bottom: Decimal
    index: int # Index of the OB candle

def detect_ob(series: MarketSeries, index: int) -> Optional[OrderBlock]:
    """
    TJR Order Block Detection:
    1. Scan for BOS at 'index'.
    2. If BOS detected, trace back the move to find origin.
    3. Verify Origin scanned/swept a previous Swing Point.
    4. If swept, the last contrarian candle is the OB.
    """
    
    # 1. Check BOS
    bos = detect_bos(series, index)
    if not bos:
        return None
        
    current_bos_idx = index
    
    if bos.type == StructureType.BOS_BULLISH:
        # Looking for Bullish OB
        # Logic:
        # a. Find the lowest low between broken_index (Old High) and current_bos_idx?
        #    Actually we need the origin of the move that broke the high.
        #    Usually the lowest point in recent history before the break.
        
        # Scan back for the lowest point since the previous swing high? 
        # Or justscan back for the swing low that initiated this.
        
        # Simple algorithm for MVP:
        # Find the absolute lowest candle index between [index-20, index].
        # Let's say range is 50 to match BOS scanner.
        scan_stop = max(-1, index - 50)
        lowest_idx = -1
        lowest_val = Decimal("1000000000")
        
        for i in range(index, scan_stop, -1):
            c = series.get(i)
            if c.low < lowest_val:
                lowest_val = c.low
                lowest_idx = i
                
        if lowest_idx == -1:
            return None
            
        # The OB is typically the last DOWN candle (Red) at or near this bottom
        # specifically the one responsible for the sweep.
        # Let's look at the bottom candle itself.
        bott_candle = series.get(lowest_idx)
        
        # 3. Verify Sweep
        # Did this bottom sweep a previous low?
        # We need to find a VALID LOW before 'lowest_idx' that is HIGHER than 'lowest_val'.
        # Meaning: Previous Low > Current Low.
        
        swept = False
        for k in range(lowest_idx - 1, scan_stop, -1):
            if is_valid_low(series, k):
                 prev_low_candle = series.get(k)
                 if prev_low_candle.low > lowest_val: # We went lower than strict previous low
                     swept = True
                     break
        
        if not swept:
            return None
            
        # 4. Identify OB Candle
        # TJR: "Ultima vela ROJA antes del movimiento"
        # Search backwards from lowest_idx (inclusive) or forwards?
        # Usually it's the candle AT the bottom or just before the explosive move.
        # If the bottom candle is RED, it is the OB.
        # If the bottom candle is GREEN (hammer?), maybe the red before it.
        # Simplified: Use the candle at lowest_idx if Red, else scan back 1-2 candles for Red.
        
        ob_idx = lowest_idx
        c_ob = series.get(ob_idx)
        if c_ob.close > c_ob.open: # Green
             # Try prev
             if ob_idx > 0:
                 c_prev = series.get(ob_idx - 1)
                 if c_prev.close < c_prev.open:
                     ob_idx = ob_idx - 1
                     c_ob = c_prev
        
        # Construct OB
        return OrderBlock(
            type=OBType.BULLISH,
            top=c_ob.high,
            bottom=c_ob.low,
            index=ob_idx
        )

    elif bos.type == StructureType.BOS_BEARISH:
        # Looking for Bearish OB
        scan_stop = max(-1, index - 50)
        highest_idx = -1
        highest_val = Decimal("-1")
        
        for i in range(index, scan_stop, -1):
            c = series.get(i)
            if c.high > highest_val:
                highest_val = c.high
                highest_idx = i
                
        if highest_idx == -1:
            return None
            
        # Check Sweep
        swept = False
        for k in range(highest_idx - 1, scan_stop, -1):
             if is_valid_high(series, k):
                 prev_high_candle = series.get(k)
                 if prev_high_candle.high < highest_val: # We went higher than previous high
                     swept = True
                     break
        
        if not swept:
            return None
            
        # OB Candle (Green)
        ob_idx = highest_idx
        c_ob = series.get(ob_idx)
        if c_ob.close < c_ob.open: # Red
             if ob_idx > 0:
                 c_prev = series.get(ob_idx - 1)
                 if c_prev.close > c_prev.open:
                     ob_idx = ob_idx - 1
                     c_ob = c_prev
                     
        return OrderBlock(
            type=OBType.BEARISH,
            top=c_ob.high,
            bottom=c_ob.low,
            index=ob_idx
        )

    return None
