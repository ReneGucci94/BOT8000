import pytest
from decimal import Decimal
from core.timeframe import Timeframe
from utils.data_loader import parse_binance_line, load_binance_csv

def test_parse_binance_line():
    # Example line from BTCUSDT-5m-2024-12.csv
    line = "1733011200000,96407.99,96524.00,96350.13,96508.29,35.87706,1733011499999,3459760.39953790,10233,19.01492000,1833852.07539100,0"
    
    candle = parse_binance_line(line, Timeframe.M5)
    
    assert candle.timestamp == 1733011200000
    assert candle.open == Decimal("96407.99")
    assert candle.high == Decimal("96524.00")
    assert candle.low == Decimal("96350.13")
    assert candle.close == Decimal("96508.29")
    assert candle.volume == Decimal("35.87706")
    assert candle.timeframe == Timeframe.M5
    assert candle.complete is True

def test_parse_invalid_line_throws():
    line = "invalid,data,line"
    with pytest.raises(ValueError):
        parse_binance_line(line, Timeframe.M5)

def test_parse_broken_prices_throws():
    # High < Low
    line = "1733011200000,100,90,110,100,10,1733011499999,0,0,0,0,0"
    with pytest.raises(ValueError):
        parse_binance_line(line, Timeframe.M5)
