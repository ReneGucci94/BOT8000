from typing import Optional, List
from decimal import Decimal
from core.market import MarketState
from core.timeframe import Timeframe
from execution.executor import TradeSignal
from execution.broker import OrderSide
from .ob import detect_ob, OrderBlock, OBType

class TJRStrategy:
    """
    Orchestrator for TJR Price Action Strategy.
    Scans for Setups (OBs formed by Sweep+BOS) and triggers on Retest.
    """
    def __init__(self):
        # In a real system, we'd persist active POIs (Points of Interest)
        # For simulation, we scan recent history for active OBs.
        pass

    def analyze(self, market: MarketState, timeframe: Timeframe = Timeframe.M5) -> Optional[TradeSignal]:
        series = market.get_series(timeframe)
        if len(series) < 5:
            return None
            
        current_candle = series.current
        current_idx = len(series) - 1
        
        # 1. Scan for recent Order Blocks (e.g., look back 50 candles)
        # We need an OB that was formed RECENTLY, but NOT by the current candle itself.
        # And the price must be returning to it now.
        
        valid_setup = None
        
        # Optimize: Scan backwards for OBs
        for i in range(current_idx - 1, max(-1, current_idx - 50), -1):
            ob = detect_ob(series, i)
            if ob:
                # 2. Check overlap with current price
                # If Bullish OB: Current Low <= OB.Top and Current High >= OB.Bottom?
                # Actually retest means we dip into it.
                # Simplification: If current Close is inside OB range? 
                # Or Low touched it.
                
                if ob.type == OBType.BULLISH:
                    # Check if mitigation happened
                    # If current low touched valid zone [Bottom, Top]
                    if current_candle.low <= ob.top and current_candle.close >= ob.bottom:
                         # Potential Entry
                         # Ensure we are not the OB candle itself (ob.index != current_idx)
                         if ob.index < current_idx:
                             valid_setup = ob
                             break
                
                elif ob.type == OBType.BEARISH:
                    if current_candle.high >= ob.bottom and current_candle.close <= ob.top:
                        if ob.index < current_idx:
                             valid_setup = ob
                             break
                             
        if not valid_setup:
            return None
            
        # 3. Generate Signal
        if valid_setup.type == OBType.BULLISH:
            entry = current_candle.close # Market entry on close
            sl = valid_setup.bottom
            risk = entry - sl
            if risk <= 0: return None # Safety
            tp = entry + (risk * Decimal("2"))
            
            return TradeSignal(
                symbol="BTCUSDT", # Configurable
                side=OrderSide.BUY,
                entry_price=entry,
                stop_loss=sl,
                take_profit=tp
            )
            
        elif valid_setup.type == OBType.BEARISH:
            entry = current_candle.close
            sl = valid_setup.top
            risk = sl - entry
            if risk <= 0: return None
            tp = entry - (risk * Decimal("2"))
            
            return TradeSignal(
                symbol="BTCUSDT",
                side=OrderSide.SELL,
                entry_price=entry,
                stop_loss=sl,
                take_profit=tp
            )
            
        return None
