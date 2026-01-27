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
