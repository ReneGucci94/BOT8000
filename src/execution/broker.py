from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import List, Optional, Protocol

class OrderSide(Enum):
    BUY = "BUY"
    SELL = "SELL"

class OrderType(Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"

@dataclass(frozen=True)
class OrderRequest:
    symbol: str
    side: OrderSide
    type: OrderType
    quantity: Decimal
    price: Optional[Decimal] = None
    stop_loss: Optional[Decimal] = None
    take_profit: Optional[Decimal] = None
    metadata: Optional[dict] = None

@dataclass(frozen=True)
class OrderResult:
    order_id: str
    status: str
    filled_price: Optional[Decimal]
    filled_quantity: Decimal

@dataclass(frozen=True)
class Position:
    symbol: str
    side: OrderSide
    quantity: Decimal
    entry_price: Decimal
    unrealized_pnl: Optional[Decimal] = None
    stop_loss: Optional[Decimal] = None
    take_profit: Optional[Decimal] = None
    metadata: Optional[dict] = None

class Broker(ABC):
    """Abstract interface for Broker implementations (Paper, Live, Backtest)."""
    
    @abstractmethod
    def get_balance(self) -> Decimal:
        """Returns current account balance."""
        pass

    @abstractmethod
    def place_order(self, order: OrderRequest) -> OrderResult:
        """Places a new order."""
        pass

    @abstractmethod
    def get_positions(self) -> List[Position]:
        """Returns list of open positions."""
        pass

    @abstractmethod
    def cancel_order(self, order_id: str) -> bool:
        """Cancels an existing order."""
        pass

    @abstractmethod
    def get_current_drawdown_pct(self) -> Decimal:
        """Returns current drawdown percentage (0.0 to 1.0)."""
        pass

    @abstractmethod
    def get_open_risk(self) -> Decimal:
        """Returns total open risk amount (Sum of |Entry-SL|*Qty)."""
        pass
