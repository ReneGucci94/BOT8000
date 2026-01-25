# tests/test_analyzer.py
import pytest
import pandas as pd
import numpy as np
import shutil
from pathlib import Path
from src.ml.analyzer import PatternAnalyzer

@pytest.fixture
def sample_data():
    # 1. Velas OHLCV
    dates = pd.date_range(start='2024-01-01', periods=200, freq='4h')
    df_candles = pd.DataFrame({
        'timestamp': dates,
        'open': np.random.rand(200)*100,
        'high': np.random.rand(200)*100 + 1,
        'low': np.random.rand(200)*100 - 1,
        'close': np.random.rand(200)*100,
        'volume': np.random.rand(200)*1000
    })
    
    # 2. Trades históricos
    # Tomamos 50 timestamps aleatorios de las velas
    trade_dates = np.random.choice(dates[50:], 100, replace=False) # Empezar después de 50 para tener features previas
    df_trades = pd.DataFrame({
        'timestamp': trade_dates,
        'result': np.random.choice(['WIN', 'LOSS'], 100),
        'pair': 'BTCUSDT',
        'side': 'LONG'
    })
    
    return df_candles, df_trades

def test_analyzer_training(sample_data):
    candles, trades = sample_data
    
    # Usar path temporal
    model_path = "tests/temp_models/test_rf.pkl"
    analyzer = PatternAnalyzer(model_path=model_path)
    
    # Train
    metrics = analyzer.train(candles, trades)
    
    assert 'accuracy' in metrics
    assert metrics['samples'] > 0
    assert analyzer.is_trained
    assert Path(model_path).exists()
    
    # Limpieza
    shutil.rmtree("tests/temp_models", ignore_errors=True)

def test_analyzer_prediction(sample_data):
    candles, trades = sample_data
    model_path = "tests/temp_models/test_rf_pred.pkl"
    analyzer = PatternAnalyzer(model_path=model_path)
    
    # Train primero
    analyzer.train(candles, trades)
    
    # Predecir con las últimas features calculadas
    # Simular DataFrame de entrada (solo features)
    from src.ml.features import FeatureExtractor
    fe = FeatureExtractor()
    features = fe.add_all_features(candles)
    
    prob = analyzer.predict_proba(features)
    
    assert 0.0 <= prob <= 1.0
    
    shutil.rmtree("tests/temp_models", ignore_errors=True)
