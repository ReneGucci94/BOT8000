# tests/alphas/test_base_alpha.py
import pytest
from abc import ABC
from src.alphas.base import Alpha
from src.core.market import MarketState

def test_alpha_is_abstract():
    """No se debe poder instanciar la clase Alpha directamente."""
    with pytest.raises(TypeError):
        Alpha()

def test_subclass_must_implement_get_score():
    """Una subclase de Alpha debe implementar get_score."""
    class IncompleteAlpha(Alpha):
        pass
    
    with pytest.raises(TypeError):
        IncompleteAlpha()

def test_valid_subclass_instantiation():
    """Una subclase válida de Alpha debe poder instanciarse."""
    class ValidAlpha(Alpha):
        def get_score(self, market_state: MarketState) -> float:
            return 0.5
            
    alpha = ValidAlpha()
    assert alpha.get_score(None) == 0.5
