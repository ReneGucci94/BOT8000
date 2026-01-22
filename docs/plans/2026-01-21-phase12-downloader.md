# Phase 12: Automatic Data Downloader Implementation Plan

## 1. Component Design: `src/data/downloader.py`

### Functionality
- **`download_binance_data`**: Main entry point.
- **Logic**:
    - Iterate through specified Year/Months.
    - Construct Binance Vision URL.
    - Check if `data/raw/{pair}-{tf}-{year}-{month}.csv` exists.
    - If not, download ZIP, extract CSV, rename/move, cleanup ZIP.
    - Handling `HTTP 404` (graceful skip for future months not yet available).

### Error Handling
- Retries for network issues.
- Verification of downloaded file size (basic check).

## 2. Configuration Updates
To know *what* to download, we need to add fields to `OptimizerConfig`:
- `download_years`: List[int] (e.g., [2024])
- `download_months`: List[int] (e.g., [1, 2, ... 12])

### Files to Modify
- `src/optimization/types.py`: Add fields to `OptimizerConfig`.
- `optimizer_config.yaml`: Add default values.
- `scripts/optimizer.py`: parsing logic.

## 3. Integration
In `scripts/optimizer.py`:
1. Load Config.
2. `print("Verifying Data...")`
3. Function call:
   ```python
   for pair in config.pairs:
       for tf in config.timeframes:
           download_binance_data(pair, tf, config.download_years, config.download_months)
   ```
4. Proceed to optimization.

## 4. Verification
- **Run**: `python3 scripts/optimizer.py --config dry_run_config.yaml`
- **Expectation**: Should attempt to download missing files (or skip existing ones) before running the dry run.

## 5. Dependencies
- `requests` (Need to install if missing).
- `tqdm` (Already installed).
