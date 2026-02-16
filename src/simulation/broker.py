from decimal import Decimal
from typing import List, Optional, Any
from src.execution.broker import Broker, OrderRequest, OrderResult, Position, OrderType, OrderSide

class InMemoryBroker(Broker):
    """
    Simulation Broker with realistic 0.1% Fees.
    """
    def __init__(self, balance: Decimal = Decimal("10000"), fee_rate: Decimal = Decimal("0.001")):
        self._balance = balance
        self._fee_rate = fee_rate
        self.orders: List[OrderRequest] = []
        self.positions: List[Position] = []
        self.equity_curve: List[Decimal] = [self._balance]
        self.total_fees_paid = Decimal("0")
        self.trade_history = []
        self.closed_positions = []
        
    def get_balance(self) -> Decimal:
        return self._balance

    def place_order(self, order: OrderRequest) -> OrderResult:
        if self._balance <= 0:
            return OrderResult(order_id="REJECTED", status="FAILED", filled_price=Decimal("0"), filled_quantity=Decimal("0"))
            
        # Simulate Entry Fee
        entry_val = order.quantity * order.price
        fee = entry_val * self._fee_rate
        
        if self._balance < fee:
            # Cannot even pay fee
            return OrderResult(order_id="REJECTED_FEE", status="FAILED", filled_price=Decimal("0"), filled_quantity=Decimal("0"))
            
        self._balance -= fee
        self.total_fees_paid += fee
        
        self.orders.append(order)
        
        pos = Position(
            symbol=order.symbol,
            side=order.side,
            quantity=order.quantity,
            entry_price=order.price,
            unrealized_pnl=Decimal("0"),
            stop_loss=order.stop_loss,
            take_profit=order.take_profit,
            metadata=order.metadata
        )
        self.positions.append(pos)
        
        # Track equity after fee
        self.equity_curve.append(self._balance)
        
        return OrderResult(
            order_id=f"id_{len(self.orders)}",
            status="FILLED",
            filled_price=order.price,
            filled_quantity=order.quantity
        )

    def get_positions(self) -> List[Position]:
        return self.positions
    
    def get_closed_positions(self) -> List[Any]:
        """Returns all positions that have been closed."""
        return self.closed_positions

    def cancel_order(self, order_id: str) -> bool:
        return True

    def update_positions(self, current_price: Decimal):
        """Simulate TP/SL logic with exit fees."""
        remaining = []
        for pos in self.positions:
            closed = False
            exit_price = Decimal("0")
            
            if pos.side == OrderSide.BUY:
                if pos.stop_loss and current_price <= pos.stop_loss:
                    exit_price = pos.stop_loss
                    closed = True
                elif pos.take_profit and current_price >= pos.take_profit:
                    exit_price = pos.take_profit
                    closed = True
            elif pos.side == OrderSide.SELL:
                if pos.stop_loss and current_price >= pos.stop_loss:
                    exit_price = pos.stop_loss
                    closed = True
                elif pos.take_profit and current_price <= pos.take_profit:
                    exit_price = pos.take_profit
                    closed = True
            
            if closed:
                # 1. Calculate Gross PnL
                if pos.side == OrderSide.BUY:
                    gross_pnl = (exit_price - pos.entry_price) * pos.quantity
                else:
                    gross_pnl = (pos.entry_price - exit_price) * pos.quantity
                
                # 2. Calculate Exit Fee
                exit_val = pos.quantity * exit_price
                exit_fee = exit_val * self._fee_rate
                
                # 3. Update Balance
                net_pnl = gross_pnl - exit_fee
                self._balance += net_pnl
                self.total_fees_paid += exit_fee
                self.equity_curve.append(self._balance)
                self.trade_history.append({"pnl": net_pnl, "fee": exit_fee})
                
                # For V3 Data Extraction
                pos_closed = pos.__dict__.copy()
                pos_closed.update({
                    'exit_price': exit_price,
                    'pnl': net_pnl,
                    'closed_at_price': current_price
                })
                # Using a simple namespace/dict wrapper to act like an object in Worker
                from types import SimpleNamespace
                self.closed_positions.append(SimpleNamespace(**pos_closed))
            else:
                remaining.append(pos)
        self.positions = remaining

    def get_current_drawdown_pct(self) -> Decimal:
        """Calculate current drawdown from equity peak."""
        if not self.equity_curve:
            return Decimal("0.0")
        
        # Determine peak equity so far
        # Note: self.equity_curve can grow large, optimization: track peak in _balance update
        # For now, max() is O(N) but safe.
        peak = max(self.equity_curve)
        current = self._balance
        
        if peak <= 0:
            return Decimal("0.0")
            
        return (peak - current) / peak

    def get_open_risk(self) -> Decimal:
        """Calculate total risk of all open positions."""
        total_risk = Decimal("0")
        for pos in self.positions:
            if pos.stop_loss and pos.entry_price:
                risk_per_share = abs(pos.entry_price - pos.stop_loss)
                total_risk += risk_per_share * pos.quantity
            else:
                # Fallback: Full value at risk if no SL
                total_risk += pos.entry_price * pos.quantity
        return total_risk
