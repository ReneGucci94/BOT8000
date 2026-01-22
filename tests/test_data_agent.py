# tests/test_data_agent.py
import pytest
from pathlib import Path
import tempfile
import shutil
import uuid

from src.agents.data_agent import DataAgent
from src.agents.types import AgentStatus

@pytest.fixture
def temp_data_dir():
    """Directorio temporal para tests"""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    shutil.rmtree(temp_dir)

def test_data_agent_initialization():
    """Test inicialización del agente"""
    agent = DataAgent()
    assert agent.agent_name == "DataAgent"
    assert agent.status == AgentStatus.IDLE
    assert agent.data_dir.exists()

def test_data_agent_run(temp_data_dir, monkeypatch):
    """Test ejecución del agente (con mock)"""
    agent = DataAgent()
    # Cambiar data_dir del agente al temporal
    agent.data_dir = temp_data_dir
    
    # Mock download_binance_data para no descargar realmente
    def mock_download(*args, **kwargs):
        # Crear archivos fake basados en los argumentos
        pairs = kwargs.get('pairs', [])
        timeframes = kwargs.get('timeframes', [])
        years = kwargs.get('years', [])
        months = kwargs.get('months', [])
        
        for pair in pairs:
            for tf in timeframes:
                for year in years:
                    for month in months:
                        filename = f"{pair}-{tf}-{year}-{month:02d}.csv"
                        filepath = temp_data_dir / filename
                        filepath.write_text("timestamp,open,high,low,close,volume\n1,100,101,99,100,1000\n1,100,101,99,100,1000\n")
    
    monkeypatch.setattr('src.agents.data_agent.download_binance_data', mock_download)
    
    config = {
        'pairs': ['BTCUSDT'],
        'timeframes': ['4h'],
        'years': [2024],
        'months': [1, 2]
    }
    
    # Usar execute para disparar el ciclo de vida (start, run, complete)
    result = agent.execute(config)
    
    assert result['total_files'] == 2
    assert result['total_candles'] == 4 # 2 lines per file (timestamp 1 twice)
    assert agent.status == AgentStatus.COMPLETED

def test_data_agent_get_available_data(temp_data_dir):
    """Test listar datos disponibles"""
    agent = DataAgent()
    agent.data_dir = temp_data_dir
    
    # Crear archivos fake
    (temp_data_dir / "BTCUSDT-4h-2024-01.csv").write_text("test")
    (temp_data_dir / "ETHUSDT-1d-2024-02.csv").write_text("test")
    
    available = agent.get_available_data()
    
    assert len(available) == 2
    # El orden puede variar por glob, así que verificamos pertenencia
    pairs = [a['pair'] for a in available]
    assert 'BTCUSDT' in pairs
    assert 'ETHUSDT' in pairs
