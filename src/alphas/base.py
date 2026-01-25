# src/alphas/base.py
from abc import ABC, abstractmethod
from src.core.market import MarketState

class Alpha(ABC):
    """
    Abstract Base Class for all Alphas in the Pure Alpha Engine.
    
    An Alpha is an independent agent that provides a directional score 
    reflecting its opinion on the market state.
    """
    
    @abstractmethod
    def get_score(self, market_state: MarketState) -> float:
        """
        Calculate the alpha score for the given market state.
        
        Args:
            market_state: The current state of the market.
            
        Returns:
            float: A score between -1.0 (Strong Short) and 1.0 (Strong Long).
                   0.0 implies Neutral.
        """
        pass
