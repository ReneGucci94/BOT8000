# Phase 11: Massive Optimization System Implementation Plan

## 1. System Architecture

The system will be composed of three main layers:
1.  **Configuration Layer**: Parsers for YAML config and Data Models for validation.
2.  **Execution Layer (The Optimizer)**: Parallel execution engine with grid search capability, checkpointing, and error handling.
3.  **Analysis Layer**: Post-processing tools to aggregate results, generate proper metrics, and visualize data.

### Directory Structure
```
src/
  optimization/
    __init__.py
    types.py          # OptimizerConfig, BacktestResult, TestConfig
    engine.py         # The Optimizer class (Parallel execution, Checkpointing)
    analyzer.py       # ResultAnalyzer class (Summary, Plots)
scripts/
  optimizer.py        # CLI Entry point
  analyze_results.py  # Standalone analysis script
  optimizer_config.yaml # Default config
tests/
  optimization/
    test_engine.py
    test_types.py
```

## 2. Implementation Steps

### Step 1: Core Types & Configuration [Foundations]
**Goal**: strict typing and validation.
- Create `src/optimization/types.py`:
    - `OptimizerConfig`: Pydantic model or dataclass with validation.
    - `BacktestResult`: Dataclass for metrics.
    - `TestConfig`: Single permutation parameters.
- Dependencies: `pyyaml` for loading config.

### Step 2: The Optimizer Engine [Core]
**Goal**: Robust execution.
- Create `src/optimization/engine.py`.
- **Key Features**:
    - `generate_configurations()`: Cartesian product.
    - `restore_checkpoint()`: Read JSON of completed IDs.
    - `run_parallel()`: Use `ProcessPoolExecutor`.
    - `execute_worker()`: The static function that runs one simulation.
        - **Critical**: Must instantiate a fresh `Backtester` and `Broker` for each run.
        - **Critical**: Exception isolation (one crash shouldn't kill the batch).

### Step 3: Integration with Backtester [Bridge]
**Goal**: Connect the generic Optimizer to our specific `TJRStrategy`.
- The worker function in `src/optimization/engine.py` needs to:
    - Load specific CSV (implement caching/lazy loading logic if needed, or just load per process).
    - Instantiate `TJRStrategy` with the dynamic params (which we need to make configurable if they aren't yet).
    - **Note**: Currently `TJRStrategy` might have hardcoded params (like lookback, risk, etc). We might need to Refactor `TJRStrategy` to accept a config object.
    - **Refactor Task**: Ensure `TJRStrategy` and `RiskManager` accept all optimization parameters.

### Step 4: Result Analyzer [Insights]
**Goal**: Visual and statistical output.
- Create `src/optimization/analyzer.py`.
- Methods to generate:
    - CSV export.
    - Summary textual report (Top 10, correlations).
    - Plots (using `matplotlib` if available, else text-based or skip).

### Step 5: CLI & Entry Points [User Interface]
- Create `scripts/optimizer.py`: Handles args, loading yaml, running engine.
- Create `scripts/analyze_results.py`: Standalone report generation.

## 3. Verification Plan
- **Unit Tests**:
    - Test config generation (cartesian product count).
    - Test checkpoint read/write.
    - Test single worker execution.
- **Integration Test**:
    - Run a "Dry Run" optimization with a tiny config (2 params, 1 timeframe, 2 pairs) to verify end-to-end flow without waiting hours.

## 4. Risks & Mitigations
- **Memory Usage**: Loading 1GB of CSVs in 8 processes simultaneously.
    - *Mitigation*: Load data INSIDE the worker only when needed, or use shared memory if necessary (but likely OS file caching is enough).
- **Process Overhead**: Spawning processes is slow.
    - *Mitigation*: The backtest takes seconds, so overhead is negligible.
- **Strategy Config**: `TJRStrategy` might be rigid.
    - *Mitigation*: Pass `StopLoss` and `TakeProfit` dynamically via the `RiskManager` or Strategy `analyze` method.

## 5. Dependencies
- Standard Lib: `concurrent.futures`, `itertools`, `json`, `dataclasses`.
- External: `pyyaml` (need to check if installed), `tqdm`.
