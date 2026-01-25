# tests/test_features.py
import pytest
import pandas as pd
import numpy as np
from src.ml.features import FeatureExtractor

@pytest.fixture
def sample_data():
    """Genera datos OHLCV sintéticos para tests."""
    dates = pd.date_range(start='2024-01-01', periods=100, freq='4h')
    np.random.seed(42)
    
    # Random walk para precios
    close = np.cumprod(1 + np.random.normal(0, 0.01, 100)) * 100
    high = close * (1 + np.abs(np.random.normal(0, 0.005, 100)))
    low = close * (1 - np.abs(np.random.normal(0, 0.005, 100)))
    open_p = close * (1 + np.random.normal(0, 0.002, 100))
    volume = np.random.randint(100, 1000, 100).astype(float)
    
    # Asegurar consitencia H/L
    high = np.maximum(high, np.maximum(open_p, close))
    low = np.minimum(low, np.minimum(open_p, close))
    
    df = pd.DataFrame({
        'timestamp': dates,
        'open': open_p,
        'high': high,
        'low': low,
        'close': close,
        'volume': volume
    })
    return df

def test_feature_extractor_initialization():
    fe = FeatureExtractor()
    assert fe.include_patterns is True

def test_add_all_features_columns(sample_data):
    fe = FeatureExtractor()
    df_features = fe.add_all_features(sample_data)
    
    expected_cols = [
        'ema_9', 'ema_200', 'rsi_14', 'macd', 
        'atr_14', 'bb_upper', 'obv', 'body_ratio'
    ]
    
    for col in expected_cols:
        assert col in df_features.columns
        
    # Verificar que no hay NaNs (debería haber droppeado las primeras filas)
    assert not df_features.isnull().values.any()
    # Debería tener menos filas que el original por el dropna (EMA 200 requiere 200 periodos? No, span=200 ajusta desde el principio pero necesita datos, la rolling window de 20 en BB elimina 19)
    # MACD necesita 26 iniciales.
    assert len(df_features) < len(sample_data)

def test_rsi_calculation(sample_data):
    fe = FeatureExtractor()
    df = fe.add_momentum_features(sample_data)
    
    assert 'rsi_14' in df.columns
    # RSI debe estar entre 0 y 100
    assert df['rsi_14'].min() >= 0
    assert df['rsi_14'].max() <= 100

def test_bollinger_bands(sample_data):
    fe = FeatureExtractor()
    df = fe.add_volatility_features(sample_data)
    
    # Upper debe ser mayor que Lower (ignoring NaNs from rolling window)
    df = df.dropna()
    assert (df['bb_upper'] > df['bb_lower']).all()
    # Close suele estar dentro, pero no siempre.
    
def test_input_validation():
    fe = FeatureExtractor()
    bad_df = pd.DataFrame({'a': [1, 2], 'b': [3, 4]})
    
    with pytest.raises(ValueError, match="must contain columns"):
        fe.add_all_features(bad_df)
