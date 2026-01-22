from dataclasses import dataclass
from decimal import Decimal
from typing import List, Optional
from core.market import MarketState
from core.timeframe import Timeframe
from core.candle import Candle
from execution.broker import Broker, OrderRequest, OrderResult, Position, OrderType, OrderSide
from execution.risk import RiskManager, RiskConfig
from execution.executor import TradeExecutor
from strategy.engine import TJRStrategy

@dataclass(frozen=True)
class BacktestReport:
    initial_balance: Decimal
    final_balance: Decimal
    net_profit: Decimal
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    gross_profit: Decimal
    gross_loss: Decimal
    max_drawdown: Decimal

class Backtester:
    @staticmethod
    def calculate_report(initial_balance: Decimal, equity_curve: List[Decimal], trade_history: List[dict]) -> BacktestReport:
        final_balance = equity_curve[-1]
        net_profit = final_balance - initial_balance
        
        total_trades = len(trade_history)
        winning_trades = 0
        losing_trades = 0
        gross_profit = Decimal("0")
        gross_loss = Decimal("0")
        
        for trade in trade_history:
            pnl = trade.get('pnl', Decimal("0"))
            if pnl > 0:
                winning_trades += 1
                gross_profit += pnl
            else:
                losing_trades += 1
                gross_loss += abs(pnl)
                
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0.0
        
        # Max Drawdown calculation
        max_dd = Decimal("0")
        peak = initial_balance
        for val in equity_curve:
            if val > peak:
                peak = val
            dd = peak - val
            if dd > max_dd:
                max_dd = dd
                
        return BacktestReport(
            initial_balance=initial_balance,
            final_balance=final_balance,
            net_profit=net_profit,
            total_trades=total_trades,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            win_rate=win_rate,
            gross_profit=gross_profit,
            gross_loss=gross_loss,
            max_drawdown=max_dd
        )

    def run(self, candles: List[Candle], broker: Broker, strategy: TJRStrategy, executor: TradeExecutor, timeframe: Timeframe) -> BacktestReport:
        initial_balance = broker.get_balance()
        market = MarketState.empty("BTCUSDT") # Symbol generic for now
        total_trades = 0
        
        # Note: We need a way to track equity over time in the broker or here
        # Let's assume the broker has an equity_curve list (like our InMemoryBroker)
        
        for candle in candles:
            market = market.update(candle)
            
            # 1. Update positions (Check SL/TP)
            # This requires the broker to have an update_positions method
            if hasattr(broker, 'update_positions'):
                broker.update_positions(candle.close)
            
            # 2. Analyze & Execute
            # Only trade if no open positions
            if not broker.get_positions():
                signal = strategy.analyze(market, timeframe)
                if signal:
                    result = executor.execute_trade(signal)
                    if result and result.status == "FILLED":
                        total_trades += 1
        
        # Re-access equity curve from broker if possible
        equity_curve = getattr(broker, 'equity_curve', [broker.get_balance()])
        trade_history = getattr(broker, 'trade_history', [])
        
        return self.calculate_report(initial_balance, equity_curve, trade_history)
