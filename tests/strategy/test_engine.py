import pytest
from decimal import Decimal
from core.candle import Candle
from core.market import MarketState
from core.timeframe import Timeframe
from core.series import MarketSeries
from execution.executor import TradeSignal
from execution.broker import OrderSide
from strategy.engine import TJRStrategy

# Helper to create candle sequence
def create_candle(open_p, close_p, high_p, low_p, timestamp=1000) -> Candle:
    return Candle(
        timestamp=timestamp,
        open=Decimal(str(open_p)),
        close=Decimal(str(close_p)),
        high=Decimal(str(high_p)),
        low=Decimal(str(low_p)),
        volume=Decimal("100"),
        timeframe=Timeframe.M5
    )

def test_strategy_detects_long_setup_on_retest():
    """
    Scenario:
    1. Form Bullish OB (Sweep Low -> BOS High).
    2. Price moves away.
    3. Price returns to OB (Retest/Mitigation).
    4. Expect Signal.
    """
    # 1. Setup Market Sequence
    series = MarketSeries([])
    ts = 1000
    
    # A. Pre-Liquidity Low (99)
    # Red candle High 103, Low 99.
    series = series.add(create_candle(102, 100, 103, 99, ts)); ts+=60
    # Green candle High 103, Low 100. (Validates Low at 99)
    series = series.add(create_candle(100, 103, 104, 100, ts)); ts+=60
    
    # B. Sweep (Drop to 97) - This is our OB candidate
    ob_candle = create_candle(102, 98, 103, 97, ts) # Low 97 sweeps 99.
    series = series.add(ob_candle) # Index 2
    ts+=60
    
    # C. Expansion & BOS (Break Pre-High 104?)
    series = series.add(create_candle(98, 104, 105, 98, ts)); ts+=60
    series = series.add(create_candle(104, 108, 110, 104, ts)); ts+=60 # BOS (Close 108 > 104)
    
    # At this point (Index 4), we have a confirmed OB at Index 2.
    # Range: High 103, Low 97.
    
    # D. Retracement (move back to 100, inside OB)
    series = series.add(create_candle(108, 100, 108, 99, ts)); ts+=60 # Close 100. Inside 97-103.
    
    # Build MarketState
    # Build MarketState
    market = MarketState.empty("BTCUSDT")
    for c in series.candles:
        market = market.update(c)
        
    # 2. Analyze
    strategy = TJRStrategy()
    signal = strategy.analyze(market, Timeframe.M5)
    
    # 3. Assert
    assert signal is not None
    assert signal.side == OrderSide.BUY
    assert signal.symbol == "BTCUSDT" # Default or passed? Strategy usually agnostic or config.
    assert signal.entry_price == Decimal("100") # Current close
    assert signal.stop_loss == Decimal("97") # OB Bottom
    # TP = Entry + 2 * (Entry - SL) = 100 + 2*(3) = 106
    assert signal.take_profit == Decimal("106") 

def test_strategy_no_signal_if_no_ob():
    series = MarketSeries([])
    series = series.add(create_candle(100, 105, 110, 100))
    
    market = MarketState.empty("BTCUSDT").update(series.candles[0])
    strategy = TJRStrategy()
    signal = strategy.analyze(market, Timeframe.M5)
    
    assert signal is None
