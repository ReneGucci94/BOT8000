# src/ml/features.py
import pandas as pd
import numpy as np
from typing import List, Dict, Any

class FeatureExtractor:
    """
    Motor de ingeniería de características para ML en trading.
    Calcula indicadores técnicos y métricas de price action vectorizadas.
    """
    
    def __init__(self, include_patterns: bool = True):
        self.include_patterns = include_patterns

    def add_all_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Aplica todos los indicadores técnicos y características al DataFrame.
        Espera columnas: open, high, low, close, volume.
        """
        df = df.copy()
        
        # Validación básica de columnas
        required = ['open', 'high', 'low', 'close', 'volume']
        if not all(col in df.columns for col in required):
            # Intentar normalizar nombres si vienen en mayúsculas
            df.columns = [c.lower() for c in df.columns]
            if not all(col in df.columns for col in required):
                raise ValueError(f"DataFrame must contain columns: {required}")
        
        # Conversión a tipos numéricos por si acaso
        for col in required:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
        # 1. Indicadores de Tendencia
        df = self.add_trend_features(df)
        
        # 2. Indicadores de Momento
        df = self.add_momentum_features(df)
        
        # 3. Indicadores de Volatilidad
        df = self.add_volatility_features(df)
        
        # 4. Indicadores de Volumen
        df = self.add_volume_features(df)
        
        # 5. Price Action Features
        df = self.add_price_action_features(df)
        
        # Limpieza de NaN generados por ventanas rodantes
        df = df.dropna()
        
        return df

    def add_trend_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """EMAs, SMAs, Distancia a medias."""
        # EMAs
        df['ema_9'] = df['close'].ewm(span=9, adjust=False).mean()
        df['ema_20'] = df['close'].ewm(span=20, adjust=False).mean()
        df['ema_50'] = df['close'].ewm(span=50, adjust=False).mean()
        df['ema_200'] = df['close'].ewm(span=200, adjust=False).mean()
        
        # Tendencia basada en cruces relativos
        df['trend_short'] = np.where(df['ema_9'] > df['ema_20'], 1, -1)
        df['trend_medium'] = np.where(df['ema_20'] > df['ema_50'], 1, -1)
        df['trend_long'] = np.where(df['ema_50'] > df['ema_200'], 1, -1)
        
        # Distancia porcentual a la EMA 200 (Mean Reversion proxy)
        df['dist_ema_200'] = (df['close'] - df['ema_200']) / df['ema_200'] * 100
        
        return df

    def add_momentum_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """RSI, MACD."""
        # RSI 14
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi_14'] = 100 - (100 / (1 + rs))
        df['rsi_14'] = df['rsi_14'].fillna(50) # Fill inicial
        
        # MACD (12, 26, 9)
        ema_12 = df['close'].ewm(span=12, adjust=False).mean()
        ema_26 = df['close'].ewm(span=26, adjust=False).mean()
        df['macd'] = ema_12 - ema_26
        df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        df['macd_hist'] = df['macd'] - df['macd_signal']
        
        return df

    def add_volatility_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """ATR, Bollinger Bands."""
        # ATR 14
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        df['atr_14'] = true_range.rolling(window=14).mean()
        
        # Bollinger Bands 20, 2
        sma_20 = df['close'].rolling(window=20).mean()
        std_20 = df['close'].rolling(window=20).std()
        df['bb_upper'] = sma_20 + (std_20 * 2)
        df['bb_lower'] = sma_20 - (std_20 * 2)
        df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / sma_20
        
        # Posición relativa en BB (0 a 1)
        df['bb_pos'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
        
        return df

    def add_volume_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Volume Ratio, OBV."""
        # Volume SMA
        df['vol_sma_20'] = df['volume'].rolling(window=20).mean()
        df['vol_ratio'] = df['volume'] / df['vol_sma_20'] # >1 significa volumen alto
        
        # OBV (On-Balance Volume)
        df['obv'] = (np.sign(df['close'].diff()) * df['volume']).fillna(0).cumsum()
        
        return df

    def add_price_action_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Cuerpo de vela, mechas, gaps."""
        # Tamaño del cuerpo y mechas
        df['body_size'] = np.abs(df['close'] - df['open'])
        df['upper_wick'] = df['high'] - np.maximum(df['close'], df['open'])
        df['lower_wick'] = np.minimum(df['close'], df['open']) - df['low']
        
        # Ratio Cuerpo/Total (Fuerza de la vela)
        df['total_range'] = df['high'] - df['low']
        df['body_ratio'] = np.where(df['total_range'] > 0, df['body_size'] / df['total_range'], 0)
        
        # Retornos logarítmicos
        df['log_ret'] = np.log(df['close'] / df['close'].shift(1))
        
        return df
