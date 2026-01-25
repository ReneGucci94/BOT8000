# tests/database/test_multi_asset_schema.py
import pytest
from src.database.models import Trade, Strategy

def test_trade_has_symbol_attribute():
    """Trade model debe tener atributo symbol."""
    assert hasattr(Trade, 'symbol'), "Trade model missing 'symbol' attribute"

def test_strategy_has_symbol_attribute():
    """Strategy model debe tener atributo symbol."""
    assert hasattr(Strategy, 'symbol'), "Strategy model missing 'symbol' attribute"
