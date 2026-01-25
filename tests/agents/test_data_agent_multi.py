# tests/agents/test_data_agent_multi.py
import pytest
from unittest.mock import patch, MagicMock
from src.agents.data_agent import DataAgent

def test_data_agent_iterates_all_pairs():
    """DataAgent debe iterar sobre todos los pares en config."""
    agent = DataAgent()
    
    # Mock download_binance_data (which is called inside DataAgent.run)
    # Note: We need to mock it where it is IMPORTED in src.agents.data_agent
    with patch('src.agents.data_agent.download_binance_data') as mock_download:
        # Mocking open and filepath.exists to avoid real file operations
        with patch('pathlib.Path.exists', return_value=False): # Avoid counting candles
            result = agent.execute({
                'pairs': ['BTCUSDT', 'ETHUSDT', 'SOLUSDT'],
                'timeframes': ['4h'],
                'years': [2024],
                'months': [1]
            })
            
            # Debe haber llamado download_binance_data para cada par
            # calls is a list of call objects
            all_downloaded_pairs = []
            for call in mock_download.call_args_list:
                # kwargs is the second element of the call tuple
                # download_binance_data(pairs=[pair], ...)
                all_downloaded_pairs.extend(call[1].get('pairs', []))
            
            assert 'BTCUSDT' in all_downloaded_pairs
            assert 'ETHUSDT' in all_downloaded_pairs
            assert 'SOLUSDT' in all_downloaded_pairs
            assert len(mock_download.call_args_list) == 3 # 3 pairs * 1 timeframe * 1 year
