import argparse
import sys
import yaml
import os
from pathlib import Path
from decimal import Decimal

# Ensure src is in path
sys.path.append(os.path.abspath("src"))

from optimization.types import OptimizerConfig
from optimization.engine import OptimizerEngine
from optimization.analyzer import ResultAnalyzer
from data.downloader import download_binance_data

def load_config(config_path: str) -> OptimizerConfig:
    with open(config_path, 'r') as f:
        data = yaml.safe_load(f)
        
    return OptimizerConfig(
        timeframes=data['timeframes'],
        pairs=data['pairs'],
        stop_losses=[Decimal(str(x)) for x in data['stop_losses']],
        take_profit_multiples=[float(x) for x in data['take_profit_multiples']],
        fee_rates=[Decimal(str(x)) for x in data['fee_rates']],
        initial_balance=Decimal(str(data['initial_balance'])),
        risk_percent=Decimal(str(data['risk_percent'])),
        data_path=data['data_path'],
        download_years=data.get('download_years', [2024]),
        download_months=data.get('download_months', list(range(1, 13))),
        parallel=data.get('parallel', True),
        checkpoint_interval=data.get('checkpoint_interval', 10)
    )

def main():
    parser = argparse.ArgumentParser(description="TJR Bot Massive Optimizer")
    parser.add_argument("--config", type=str, default="optimizer_config.yaml", help="Path to config file")
    parser.add_argument("--analyze", action="store_true", help="Run analysis only")
    args = parser.parse_args()
    
    config = load_config(args.config)
    
    if not args.analyze:
        # Automatic Data Download
        download_binance_data(
            pairs=config.pairs,
            timeframes=config.timeframes,
            years=config.download_years,
            months=config.download_months,
            data_dir=config.data_path
        )
        
        print(f"--- Starting Optimization ---")
        print(f"Timeframes: {config.timeframes}")
        print(f"Pairs: {config.pairs}")
        
        engine = OptimizerEngine(config)
        engine.run()
        print("Optimization Complete.")
        
    # Always run analysis after
    results_file = Path("results/optimizer_results.csv")
    if results_file.exists():
        analyzer = ResultAnalyzer(results_file)
        analyzer.load()
        analyzer.save_summary(Path("results/summary.txt"))
        print("\nSummary Report generated in results/summary.txt")
    else:
        print("No results to analyze.")

if __name__ == "__main__":
    main()
