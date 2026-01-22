# Massive Optimization System

This system allows for parallel execution of backtests across a grid of parameters to find the optimal configuration for the TJR Strategy.

## Usage

### 1. Configuration
Edit `optimizer_config.yaml` to define your search space:
```yaml
timeframes: ["15m", "1h", "4h"]
stop_losses: [0, 500, 1000] # 0 = Structural
fee_rates: [0.001, 0.0004]
# ...
```

### 2. Run Optimization
```bash
python3 scripts/optimizer.py --config optimizer_config.yaml
```
- This will use all available CPU cores.
- Progress is shown via a progress bar.
- Results are saved to `results/optimizer_results.csv`.
- Checkpoints are saved every 10 runs (resumes automatically).

### 3. Analyze Results
The script automatically generates a summary at the end. To re-run analysis:
```bash
python3 scripts/optimizer.py --analyze
```
Check `results/summary.txt` for the Top 10 configurations.

## Output Format
`results/optimizer_results.csv` columns:
- `config_id`: Unique ID
- `net_profit`: The main metric
- `profit_factor`: Gross Profit / Gross Loss
- `win_rate`: 0.0 - 1.0
