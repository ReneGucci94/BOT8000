import pandas as pd
from pathlib import Path
from typing import List, Dict

class ResultAnalyzer:
    def __init__(self, results_file: Path):
        self.results_file = results_file
        self.df = pd.DataFrame()

    def load(self):
        if self.results_file.exists():
            self.df = pd.read_csv(self.results_file)
            
    def generate_summary(self) -> str:
        if self.df.empty:
            return "No results found."
            
        # Ensure numeric types
        numeric_cols = ['net_profit', 'total_trades', 'win_rate', 'max_drawdown', 'fees_paid']
        for col in numeric_cols:
            if col in self.df.columns:
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
        
        # 1. Top 10 by Net Profit
        top_10 = self.df.sort_values(by='net_profit', ascending=False).head(10)
        
        # 2. Best by Timeframe
        best_by_tf = self.df.loc[self.df.groupby('timeframe')['net_profit'].idxmax()]
        
        # 3. Best by Pair (if multiple pairs)
        best_by_pair = self.df.loc[self.df.groupby('pair')['net_profit'].idxmax()]
        
        summary = []
        summary.append("=== OPTIMIZATION SUMMARY ===\n")
        summary.append(f"Total Configurations: {len(self.df)}")
        summary.append(f"Profitable Configs: {len(self.df[self.df['net_profit'] > 0])} ({len(self.df[self.df['net_profit'] > 0])/len(self.df)*100:.2f}%)")
        
        summary.append("\n--- TOP 10 CONFIGURATIONS ---")
        summary.append(top_10[['config_id', 'timeframe', 'pair', 'stop_loss', 'net_profit', 'total_trades']].to_string(index=False))
        
        summary.append("\n\n--- BEST BY TIMEFRAME ---")
        summary.append(best_by_tf[['timeframe', 'config_id', 'net_profit', 'win_rate', 'total_trades']].to_string(index=False))
        
        return "\n".join(summary)

    def save_summary(self, output_file: Path):
        report = self.generate_summary()
        with open(output_file, 'w') as f:
            f.write(report)
        print(f"Summary saved to {output_file}")
