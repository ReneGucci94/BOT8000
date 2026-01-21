# Trading Bot v2 - Architectural Design Document

**Status:** Approved
**Date:** 2026-01-20
**Strategy:** TJR Price Action
**Architecture:** Hexagonal (Ports & Adapters) + Functional Domain

## 1. Design Philosophy
- **Immutability First:** All domain models are immutable (frozen dataclasses).
- **Fail Fast:** Invariants validated at instantiation time.
- **Strict Typing:** No generic `float` or `dict`. Use `Decimal` and Typed Domain Objects.
- **Ports & Adapters:** Logic isolated from infra (Binance/Internet).

## 2. Core Domain Models (`src/core/`)

### 2.1 Primitives (`types.py`)
```python
from decimal import Decimal
Price = Decimal      # Precision is critical for "Equal Highs"
Volume = Decimal
Timestamp = int      # Unix ms
```

### 2.2 Timeframe (`timeframe.py`)
Strict Enum to prevent string magic.
- `M5`, `M15`: Entry & Refinement
- `H1`: Alignment
- `H4`: Structural Bias

### 2.3 Candle (`candle.py`)
Immutable atomic unit of truth.
**Invariants:**
- `high >= low`
- `high >= max(open, close)`
- `low <= min(open, close)`
- `volume >= 0`

### 2.4 MarketSeries (`series.py`)
Immutable-ish collection of candles.
- **Storage:** Internal list/deque.
- **Mutation:** Methods like `add(candle)` return a NEW instance (Functional style).
- **Access:** `get(index)`, `last_closed()`.

### 2.5 MarketState (`market.py`)
The "God Object" representing total market reality at `t`.
- Contains `MarketSeries` for all 4 timeframes.
- Synchronized update mechanism.

## 3. Interfaces (Ports)

### 3.1 Data Source Protocol
Abstracts where data comes from (CSV, API, Websocket).
```python
class DataSource(Protocol):
    def get_history(self, symbol: str, timeframe: Timeframe) -> MarketSeries: ...
    def stream(self, symbol: str) -> Iterator[Candle]: ...
```

### 3.2 Broker Protocol
Abstracts execution (Paper, Live, Backtest).
```python
class Broker(Protocol):
    def place_order(self, order: Order) -> OrderResult: ...
    def get_balance(self) -> Decimal: ...
```

## 4. Directory Structure
```
src/
├── core/           # Pure Domain (Rules, Models)
│   ├── types.py
│   ├── candle.py
│   ├── series.py
│   └── timeframe.py
├── infrastructure/ # External World (Binance, CSV)
├── strategies/     # TJR Logic
└── main.py         # Wiring (Dependency Injection)
```
