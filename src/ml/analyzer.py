# src/ml/analyzer.py
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_score, recall_score, accuracy_score
import joblib
from pathlib import Path

from src.ml.features import FeatureExtractor

class PatternAnalyzer:
    """
    Motor de Machine Learning para analizar patrones de mercado.
    Entrena modelos para predecir el resultado de trades basados en market features.
    """
    
    def __init__(self, model_path: str = "data/models/rf_model_v1.pkl"):
        self.model_path = Path(model_path)
        self.extractor = FeatureExtractor()
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_leaf=20,
            random_state=42,
            n_jobs=-1
        )
        self.is_trained = False
        self._load_model()

    def _load_model(self):
        if self.model_path.exists():
            try:
                self.model = joblib.load(self.model_path)
                self.is_trained = True
                print(f"Modelo cargado desde {self.model_path}")
            except Exception as e:
                print(f"Error cargando modelo: {e}")

    def prepare_data(self, candles_df: pd.DataFrame, trades_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Prepara dataset uniendo features de velas con etiquetas de trades.
        Args:
            candles_df: OHLCV data
            trades_df: DataFrame con trades históricos (debe tener timestamp de entrada y resultado)
        """
        # 1. Extraer features técnicas
        features_df = self.extractor.add_all_features(candles_df)
        
        # 2. Etiquetado (Labeling)
        # Asumimos que trades_df tiene 'entry_time' y 'result' ('WIN'/'LOSS')
        # Alineamos por timestamp. Como el trade ocurre AL CIERRE de la vela o en la vela siguiente,
        # usaremos features de la vela PREVIA o ACTUAL a la entrada.
        # Simplificación: Features de la vela donde el timestamp coincide con entry_time.
        
        # Asegurar tipos de timestamp
        features_df.index = pd.to_datetime(features_df['timestamp']) if 'timestamp' in features_df.columns else features_df.index
        trades_df['timestamp'] = pd.to_datetime(trades_df['timestamp'])
        
        # Merge asof (cercano) o exacto
        # Unimos trades con features. Usamos features conocidas AL MOMENTO de la entrada.
        # Si trade timestamp es 12:00, usamos features de vela de las 12:00 (si es cierre) o 08:00 (si es open).
        # Asumiremos datos de cierre.
        
        # Requerimos que las features tengan índice por tiempo
        merged = pd.merge_asof(
            trades_df.sort_values('timestamp'),
            features_df.sort_index(),
            left_on='timestamp',
            right_index=True,
            direction='backward', # Features anteriores o iguales al trade
            tolerance=pd.Timedelta('4h') # Max diferencia permitida
        )
        
        merged = merged.dropna()
        
        # Crear target: 1 si WIN, 0 si LOSS
        y = (merged['result'] == 'WIN').astype(int)
        
        # Seleccionar solo columnas numéricas de features
        exclude_cols = ['timestamp', 'pair', 'side', 'result', 'profit_loss', 'entry_price', 'exit_price', 'stop_loss', 'take_profit', 'backtest_run_id', 'id', 'market_state', 'strategy_version', 'profit_loss_pct', 'risk_reward', 'worker_id', 'entry_time']
        
        # Filtrar columnas que vienen de features_df
        feature_cols = [c for c in features_df.columns if c in merged.columns and c not in exclude_cols]
        X = merged[feature_cols].select_dtypes(include=[np.number])
        
        return X, y

    def train(self, candles_df: pd.DataFrame, trades_df: pd.DataFrame) -> Dict[str, float]:
        """Entrena el modelo con nuevos datos."""
        X, y = self.prepare_data(candles_df, trades_df)
        
        if len(X) < 50:
            return {'error': 'Insufficient data (<50 samples)'}
            
        # Split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
        
        # Train
        self.model.fit(X_train, y_train)
        self.is_trained = True
        
        # Evaluacion
        preds = self.model.predict(X_test)
        metrics = {
            'accuracy': accuracy_score(y_test, preds),
            'precision': precision_score(y_test, preds, zero_division=0),
            'recall': recall_score(y_test, preds, zero_division=0),
            'samples': len(X)
        }
        
        # Guardar
        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.model, self.model_path)
        
        return metrics

    def predict_proba(self, candle_features: pd.DataFrame) -> float:
        """Predice probabilidad de WIN para el estado actual del mercado."""
        if not self.is_trained:
            return 0.5 # Neutral
            
        # Asegurarse de tener solo las columnas usadas en entrenamiento
        # (Esto requeriría guardar feature_names, para V1 asumimos consistencia en FeatureExtractor)
        try:
            # Filtrar columnas no numéricas o extrañas
            X = candle_features.select_dtypes(include=[np.number])
            # Si hay columnas extra o faltantes vs entrenamiento, RF avisará. 
            # En V2 robusteceremos feature alignment.
            
            # Solo tomamos la última fila
            last_row = X.iloc[[-1]] 
            prob = self.model.predict_proba(last_row)[0][1] # Probabilidad de clase 1 (WIN)
            return prob
        except Exception as e:
            print(f"Error predicción: {e}")
            return 0.5
