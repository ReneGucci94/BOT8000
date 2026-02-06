import pandas as pd
from pathlib import Path
from src.core.market import calculate_rsi, calculate_adx
from src.core.series import MarketSeries
from src.core.candle import Candle
from src.core.timeframe import Timeframe
from src.data.downloader import download_binance_data

def load_candles(pair, timeframe_str, year, month):
    data_dir = Path("data/raw")
    filename = f"{pair}-{timeframe_str}-{year}-{month:02d}.csv"
    filepath = data_dir / filename
    
    if not filepath.exists():
        print(f"Downloading {filename}...")
        download_binance_data([pair], [timeframe_str], [year], [month], str(data_dir))
    
    # Binance columns: Open time, Open, High, Low, Close, Volume, ...
    # We only need the first 6 columns
    print(f"Reading {filepath}...")
    df = pd.read_csv(filepath, header=None)
    
    candles = []
    # Enum creation
    tf_enum = Timeframe(timeframe_str)

    for _, row in df.iterrows():
        try:
            c = Candle(
                timestamp=int(row[0]),
                open=float(row[1]),
                high=float(row[2]),
                low=float(row[3]),
                close=float(row[4]),
                volume=float(row[5]),
                timeframe=tf_enum, 
                complete=True
            )
            candles.append(c)
        except Exception as e:
            print(f"Error parsing row: {e}")
            continue
        
    return MarketSeries(candles)

def test_indicators_change():
    """Verify indicators return different values for different data."""
    
    # Data de Mayo
    print("Loading May data...")
    series_may = load_candles('BTCUSDT', '4h', 2024, 5)
    
    # Data de Junio  
    print("Loading June data...")
    series_jun = load_candles('BTCUSDT', '4h', 2024, 6)
    
    print(f"Loaded {len(series_may)} candles for May and {len(series_jun)} for June.")
    
    print("Calculating indicators...")
    rsi_may = calculate_rsi(series_may)[-1]
    rsi_jun = calculate_rsi(series_jun)[-1]
    
    adx_may = calculate_adx(series_may)
    adx_jun = calculate_adx(series_jun)
    
    print(f"RSI Mayo: {rsi_may}, RSI Junio: {rsi_jun}")
    print(f"ADX Mayo: {adx_may}, ADX Junio: {adx_jun}")
    
    # Deben ser diferentes
    assert rsi_may != 50.0, "RSI still placeholder"
    assert rsi_may != rsi_jun, "RSI should vary between months"
    assert adx_may != 25.0, "ADX still placeholder"
    assert adx_may != adx_jun, "ADX should vary between months"
    
    print("✅ Indicators are REAL now")

if __name__ == "__main__":
    test_indicators_change()
