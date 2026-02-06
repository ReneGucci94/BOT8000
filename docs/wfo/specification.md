# Walk-Forward Optimization (WFO) Specification

## 1. Overview

Implementation of a robust Walk-Forward Optimization module for BOT8000 v3. The system will use rolling windows to validate strategy performance out-of-sample.

## 2. Window Generation (PARTE 2)

The system must generate train/test windows based on the following rules:

- **Structure**: Rolling windows shifting by `step_months`.
- **Constraint**: `step_months` must equal `test_months` to ensure contiguous testing without overlap or gaps.
- **Labels**: Format `Train:YYYY-MMtoYYYY-MM_Test:YYYY-MM`.

### Dataclass Definition

```python
@dataclass
class Window:
    window_id: int
    label: str
    train_start_month: int
    train_end_month: int
    test_start_month: int
    test_end_month: int
    train_data: List[Candle]
    test_data: List[Candle]
    warmup_data: List[Candle]
```

## 3. Configuration (PARTE 7)

### 7.1 Config Object

```python
@dataclass
class WindowConfig:
    train_months: int
    test_months: int
    step_months: int
    year: int
    warmup_bars: int
```

### 7.2 Example Configuration

For Year 2024:

- `train_months` = 4
- `test_months` = 1
- `step_months` = 1
- `warmup_bars` = 240 (for 4H timeframe)

**Expected Output**: 8 Windows for 2024 (Train Jan-Apr -> Test May ... Train Aug-Nov -> Test Dec).

## 4. Data Requirements (PARTE 4 + 9)

- **Warmup**: Exactly 240 bars (40 days for 4H) prior to the *Test* window start (or Train start? *Clarification: Spec usually implies warmup is available for indicators. In WFO, indicators often need warmup before the execution period. The test `test_warmup_exactly_240_bars` implies warmup is part of the Window object. Usually warmup precedes the data it supports.*)
  - *Correction based on Test:* `win.warmup_data` is checked.
- **Separation**: No data leakage.
  - `max(train_timestamp) < min(test_timestamp)`
  - `max(warmup_timestamp) < min(test_timestamp)`

## 5. Modules

- `windows.py`: Window generation logic.
- `param_space.py`: Parameter definitions.
- `constraints.py`: Logic to validate/project parameters.
- `fitness.py`: Scoring logic (PF, Sharpe, etc.).
- `genetic_algorithm.py`: Optimization core.
- `aggregator.py`: Combining results.
