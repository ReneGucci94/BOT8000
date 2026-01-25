# src/alphas/ml_confidence.py
import pandas as pd
from typing import Optional
from src.alphas.base import Alpha
from src.core.market import MarketState
from src.ml.analyzer import PatternAnalyzer
from src.ml.features import FeatureExtractor

class Alpha_ML_Confidence(Alpha):
    """
    Alpha based on Machine Learning model confidence.
    
    Transforms the model's win probability [0, 1] to a directional score [-1, 1].
    Probability 0.5 -> Score 0.0 (Neutral)
    Probability > 0.5 -> Positive score (Confidence in Alpha/Setup)
    Probability < 0.5 -> Negative score (Model expects failure)
    """
    
    def __init__(self, analyzer: Optional[PatternAnalyzer] = None):
        # Allow injecting analyzer for testing
        self.analyzer = analyzer or PatternAnalyzer()
        self.extractor = FeatureExtractor()
    
    def get_score(self, market_state: MarketState) -> float:
        # 1. Transform MarketState to DataFrame for extraction
        series = market_state.h4
        if len(series) < 50: # Need enough data for technical indicators
            return 0.0
            
        data = []
        for i in range(len(series)):
            c = series.get(i)
            data.append({
                'timestamp': c.timestamp,
                'open': float(c.open),
                'high': float(c.high),
                'low': float(c.low),
                'close': float(c.close),
                'volume': float(c.volume)
            })
            
        df = pd.DataFrame(data)
        
        # 2. Extract Features
        df_features = self.extractor.add_all_features(df)
        
        # 3. Predict Probability
        prob = self.analyzer.predict_proba(df_features)
        
        # 4. Normalize to [-1, 1]
        # (prob - 0.5) * 2.0
        # 0.8 -> (0.3) * 2 = 0.6
        # 0.5 -> (0.0) * 2 = 0.0
        # 0.2 -> (-0.3) * 2 = -0.6
        score = (prob - 0.5) * 2.0
        
        return max(-1.0, min(1.0, score))
