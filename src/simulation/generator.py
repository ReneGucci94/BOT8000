from decimal import Decimal
from typing import List, Generator
import random
from core.candle import Candle
from core.timeframe import Timeframe

class MarketGenerator:
    """
    Generates synthetic OHLC data with structural patterns.
    """
    def __init__(self, start_price: int = 50000, start_ts: int = 1000):
        self.current_price = Decimal(str(start_price))
        self.ts = start_ts
        self.timeframe = Timeframe.M5
        
    def _create_candle(self, open_p: Decimal, close_p: Decimal) -> Candle:
        high_p = max(open_p, close_p) + (Decimal("10") * Decimal(random.random()))
        low_p = min(open_p, close_p) - (Decimal("10") * Decimal(random.random()))
        # Ensure minimal volume
        vol = Decimal("100") + Decimal(random.randint(0, 500))
        
        c = Candle(
            timestamp=self.ts,
            open=open_p,
            close=close_p,
            high=high_p,
            low=low_p,
            volume=vol,
            timeframe=self.timeframe
        )
        self.ts += (5 * 60) # 5 min increments
        return c

    def generate_random_walk(self, n: int) -> List[Candle]:
        candles = []
        for _ in range(n):
            open_p = self.current_price
            # Volatility around 0.1%
            change = open_p * Decimal("0.001") * Decimal(2 * (random.random() - 0.5))
            close_p = open_p + change
            
            c = self._create_candle(open_p, close_p)
            candles.append(c)
            self.current_price = close_p
            
        return candles

    def generate_bullish_cycle(self) -> List[Candle]:
        """
        Generates a predefined TJR Bullish Cycle:
        1. Consolidation (Range)
        2. Sweep (Dump below range)
        3. Reversal (Strong Green)
        4. Expansion (Trend Up)
        """
        candles = []
        # 1. Consensus / Range
        for _ in range(5):
             candles.append(self._create_candle(self.current_price, self.current_price + Decimal(random.randint(-10, 10))))
             self.current_price = candles[-1].close

        # 2. Sweep Low (Dump 100 points)
        dump_open = self.current_price
        dump_close = dump_open - Decimal("150")
        candles.append(self._create_candle(dump_open, dump_close))
        self.current_price = dump_close
        
        # 3. Reversal (OB Creation)
        # Strong Buy back up
        pump_open = self.current_price
        pump_close = pump_open + Decimal("200") # Break structure?
        candles.append(self._create_candle(pump_open, pump_close))
        self.current_price = pump_close
        
        # 4. Mitigation / Retest
        # Slow drift down
        for _ in range(3):
            close = self.current_price - Decimal("20")
            candles.append(self._create_candle(self.current_price, close))
            self.current_price = close
            
        # 5. Expansion
        for _ in range(10):
            close = self.current_price + Decimal("50")
            candles.append(self._create_candle(self.current_price, close))
            self.current_price = close
            
        return candles

    def generate_cycle_stream(self, cycles: int = 1) -> Generator[Candle, None, None]:
        for _ in range(cycles):
             # Alternating cycles or just Bullish for MVP
             batch = self.generate_bullish_cycle()
             for c in batch:
                 yield c
                 
