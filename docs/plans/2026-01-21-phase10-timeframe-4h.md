# Phase 10: Timeframe Optimization (4H)

> **Hypothesis:** 4H timeframe will provide a Stop Loss range wide enough that the fixed 0.1% fee is a negligible percentage of the risk (e.g., fee < 10% of 1R), potentially solving the "Scalper's Trap".

---

### Task 1: Data Preparation
- [x] Download 4H BTCUSDT data for Jan, Feb, Mar, Jun, Sep, Nov, Dec 2024. [DONE]

---

### Task 2: Script Configuration (4H)
- **Target File:** `scripts/run_multi_month_backtest.py`
- **Change:** 
    - Set `TARGET_TIMEFRAME = Timeframe.H4`
    - Set `GLO_PATTERN = "*-4h-*.csv"`
    - Run the script.

---

### Task 3: Analysis
- **Execution:** Run the script and capture the table.
- **Metrics to Evaluate:**
    - **Trade Frequency:** Is it > 0? (Unlike 1H which had 229 trades in fix, wait did 1H have trades? Yes 229 trades in 7 months after fix).
    - **Net Profit:** Is it positive?
    - **Win Rate:** Does it maintain > 40%?

### Verification
- **Automated:** `python3 scripts/run_multi_month_backtest.py`
- **Manual:** Review output table and compare `Fees` vs `Net Profit` column.
