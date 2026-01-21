from decimal import Decimal
from typing import List, Optional
from execution.broker import Broker, OrderRequest, OrderResult, Position, OrderType, OrderSide

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
            unrealized_pnl=Decimal("0")
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
    
    def cancel_order(self, order_id: str) -> bool:
        return True

    def update_positions(self, current_price: Decimal):
        """Simulate TP/SL logic with exit fees."""
        remaining = []
        for pos in self.positions:
            # Find the original order for SL/TP
            order = [o for o in self.orders if o.symbol == pos.symbol][-1]
            closed = False
            exit_price = Decimal("0")
            
            if pos.side == OrderSide.BUY:
                if order.stop_loss and current_price <= order.stop_loss:
                    exit_price = order.stop_loss
                    closed = True
                elif order.take_profit and current_price >= order.take_profit:
                    exit_price = order.take_profit
                    closed = True
            elif pos.side == OrderSide.SELL:
                if order.stop_loss and current_price >= order.stop_loss:
                    exit_price = order.stop_loss
                    closed = True
                elif order.take_profit and current_price <= order.take_profit:
                    exit_price = order.take_profit
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
                self._balance += gross_pnl - exit_fee
                self.total_fees_paid += exit_fee
                self.equity_curve.append(self._balance)
                self.trade_history.append({"pnl": gross_pnl - exit_fee, "fee": exit_fee})
            else:
                remaining.append(pos)
        self.positions = remaining
