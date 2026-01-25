import pandas as pd
import numpy as np
from typing import List
from src.database.models import Trade

def build_equity_curve(trades: List[Trade], freq: str = '1D') -> pd.DataFrame:
    """
    Convert a list of trades into a time-series equity curve.
    
    Args:
        trades: List of Trade objects.
        freq: Resampling frequency (default '1D').
        
    Returns:
        DataFrame with index 'timestamp' and column 'equity'.
    """
    if not trades:
        return pd.DataFrame(columns=['equity'])
        
    data = []
    for t in trades:
        data.append({
            'timestamp': pd.to_datetime(t.timestamp),
            'pnl': float(t.profit_loss)
        })
    
    df = pd.DataFrame(data)
    # Resample to align grid (e.g., daily) and sum PnL for that period
    df = df.set_index('timestamp').resample(freq).sum().fillna(0)
    # Cumulative sum to get equity curve
    df['equity'] = df['pnl'].cumsum()
    return df

def calculate_correlation(trades_a: List[Trade], trades_b: List[Trade]) -> float:
    """
    Calculate Pearson correlation between the equity curves of two trade lists.
    
    Args:
        trades_a: First list of trades.
        trades_b: Second list of trades.
        
    Returns:
        float: Correlation coefficient between -1 and 1. Returns 0.0 if not enough data.
    """
    if not trades_a or not trades_b:
        return 0.0
        
    equity_a = build_equity_curve(trades_a)
    equity_b = build_equity_curve(trades_b)
    
    if equity_a.empty or equity_b.empty:
        return 0.0
    
    # Merge on timestamp to align the series
    # Use outer join to keep all dates, then forward fill equity
    # (if no trade happened on a day, equity remains same as previous day)
    merged = pd.merge(
        equity_a['equity'], 
        equity_b['equity'], 
        left_index=True, 
        right_index=True, 
        how='outer', 
        suffixes=('_a', '_b')
    )
    
    # Forward fill to propagate equity values
    merged = merged.fillna(method='ffill')
    
    # If starting points differ, fill initial NaNs with 0 (assuming starting equity 0)
    merged = merged.fillna(0)
    
    if len(merged) < 2:
        return 0.0
        
    # Calculate Pearson correlation of the equity levels
    return float(merged['equity_a'].corr(merged['equity_b']))
