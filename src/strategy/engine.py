from typing import Optional, List
from decimal import Decimal
from src.core.market import MarketState
from src.core.timeframe import Timeframe
from src.execution.executor import TradeSignal
from src.execution.broker import OrderSide
from .ob import detect_ob, OrderBlock, OBType

class TJRStrategy:
    """
    Orchestrator for TJR Price Action Strategy.
    Scans for Setups (OBs formed by Sweep+BOS) and triggers on Retest.
    """
    def __init__(
        self, 
        fixed_stop_loss: Optional[Decimal] = None, 
        take_profit_multiplier: Decimal = Decimal("2.0"),
        stop_loss_atr_multiplier: Optional[Decimal] = None
    ):
        """
        :param fixed_stop_loss: If provided, uses this fixed USD distance for SL instead of structural low.
        :param take_profit_multiplier: R-Multiple for TP (default 2.0).
        :param stop_loss_atr_multiplier: If provided, uses ATR * this multiplier for SL distance.
        """
        self.fixed_stop_loss = fixed_stop_loss
        self.take_profit_multiplier = take_profit_multiplier
        self.stop_loss_atr_multiplier = stop_loss_atr_multiplier

    def _calculate_atr(self, series, period: int = 14) -> Optional[Decimal]:
        """Calculate Average True Range for SL sizing."""
        if len(series) < period + 1:
            return None
        
        tr_values = []
        for i in range(-period, 0):
            candle = series[i]
            prev_candle = series[i - 1]
            high_low = candle.high - candle.low
            high_prev_close = abs(candle.high - prev_candle.close)
            low_prev_close = abs(candle.low - prev_candle.close)
            tr = max(high_low, high_prev_close, low_prev_close)
            tr_values.append(tr)
        
        return sum(tr_values) / len(tr_values)

    def analyze(self, market: MarketState, timeframe: Timeframe = Timeframe.M5) -> Optional[TradeSignal]:
        series = market.get_series(timeframe)
        if len(series) < 5:
            return None
            
        current_candle = series.current
        current_idx = len(series) - 1
        
        # 1. Scan for recent Order Blocks (e.g., look back 50 candles)
        valid_setup = None
        
        # Optimize: Scan backwards for OBs
        for i in range(current_idx - 1, max(-1, current_idx - 50), -1):
            ob = detect_ob(series, i)
            if ob:
                if ob.type == OBType.BULLISH:
                    if current_candle.low <= ob.top and current_candle.close >= ob.bottom:
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
        # Calculate ATR if needed for ATR-based SL
        atr = None
        if self.stop_loss_atr_multiplier:
            atr = self._calculate_atr(series)
        
        if valid_setup.type == OBType.BULLISH:
            entry = current_candle.close
            
            # SL Logic: ATR > Fixed > Structural
            if self.stop_loss_atr_multiplier and atr:
                sl = entry - (atr * self.stop_loss_atr_multiplier)
            elif self.fixed_stop_loss and self.fixed_stop_loss > 0:
                sl = entry - self.fixed_stop_loss
            else:
                sl = valid_setup.bottom
                
            risk = entry - sl
            if risk <= 0: return None
            
            tp = entry + (risk * self.take_profit_multiplier)
            
            return TradeSignal(
                symbol="BTCUSDT",
                side=OrderSide.BUY,
                entry_price=entry,
                stop_loss=sl,
                take_profit=tp
            )
            
        elif valid_setup.type == OBType.BEARISH:
            entry = current_candle.close
            
            # SL Logic: ATR > Fixed > Structural
            if self.stop_loss_atr_multiplier and atr:
                sl = entry + (atr * self.stop_loss_atr_multiplier)
            elif self.fixed_stop_loss and self.fixed_stop_loss > 0:
                sl = entry + self.fixed_stop_loss
            else:
                sl = valid_setup.top
                
            risk = sl - entry
            if risk <= 0: return None
            
            tp = entry - (risk * self.take_profit_multiplier)
            
            return TradeSignal(
                symbol="BTCUSDT",
                side=OrderSide.SELL,
                entry_price=entry,
                stop_loss=sl,
                take_profit=tp
            )
            
        return None
