import csv
from decimal import Decimal
from typing import List
from src.core.candle import Candle
from src.core.timeframe import Timeframe

def parse_binance_line(line: str, timeframe: Timeframe) -> Candle:
    """
    Parses a single line of Binance CSV kline data.
    Format:
    0: Open time (ms)
    1: Open
    2: High
    3: Low
    4: Close
    5: Volume
    ...
    """
    parts = line.strip().split(",")
    if len(parts) < 6:
        raise ValueError(f"Invalid Binance CSV line (insufficient columns): {line}")
        
    try:
        timestamp = int(parts[0])
        open_p = Decimal(parts[1])
        high_p = Decimal(parts[2])
        low_p = Decimal(parts[3])
        close_p = Decimal(parts[4])
        volume = Decimal(parts[5])
        
        return Candle(
            timestamp=timestamp,
            open=open_p,
            high=high_p,
            low=low_p,
            close=close_p,
            volume=volume,
            timeframe=timeframe,
            complete=True
        )
    except (ValueError, TypeError) as e:
        raise ValueError(f"Error parsing Binance line: {e} | Line: {line}")

def load_binance_csv(file_path: str, timeframe: Timeframe) -> List[Candle]:
    """
    Loads a full Binance CSV file and returns a list of Candles.
    """
    candles = []
    with open(file_path, "r") as f:
        # Binance CSVs sometimes don't have headers.
        # We assume no headers for these monthly kline zips.
        for line in f:
            if not line.strip():
                continue
            candles.append(parse_binance_line(line, timeframe))
            
    return candles
