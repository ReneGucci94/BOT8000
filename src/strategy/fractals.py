from core.series import MarketSeries

def is_valid_high(series: MarketSeries, index: int) -> bool:
    """
    TJR Definition for Valid Swing High:
    A GREEN candle followed by a RED candle.
    """
    if index < 0 or index + 1 >= len(series):
        return False
    
    current = series.get(index)
    next_candle = series.get(index + 1)
    
    # Green: Close > Open
    is_green = current.close > current.open
    # Red: Close < Open
    next_is_red = next_candle.close < next_candle.open
    
    return is_green and next_is_red

def is_valid_low(series: MarketSeries, index: int) -> bool:
    """
    TJR Definition for Valid Swing Low:
    A RED candle followed by a GREEN candle.
    """
    if index < 0 or index + 1 >= len(series):
        return False
        
    current = series.get(index)
    next_candle = series.get(index + 1)
    
    # Red: Close < Open
    is_red = current.close < current.open
    # Green: Close > Open
    next_is_green = next_candle.close > next_candle.open
    
    return is_red and next_is_green
