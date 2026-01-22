# src/agents/data_agent.py
from typing import Dict, Any, List
from pathlib import Path
import os

from src.agents.base import BaseAgent
from src.data.downloader import download_binance_data

class DataAgent(BaseAgent):
    """
    Agente responsable de descargar y gestionar datos históricos
    
    Responsabilidades:
    - Descargar CSVs de Binance Vision
    - Validar integridad de archivos
    - Reportar metadata de datasets
    """
    
    def __init__(self):
        super().__init__("DataAgent")
        self.data_dir = Path("data/raw")
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def run(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ejecutar descarga de datos
        
        Args:
            config: {
                'pairs': ['BTCUSDT', 'ETHUSDT'],
                'timeframes': ['4h', '1d'],
                'years': [2023, 2024],
                'months': [1, 2, ..., 12]  # opcional
            }
        
        Returns:
            {
                'downloaded_files': ['BTCUSDT-4h-2024-01.csv', ...],
                'total_files': 24,
                'total_candles': 52560,
                'data_dir': 'data/raw/'
            }
        """
        pairs = config.get('pairs', [])
        timeframes = config.get('timeframes', [])
        years = config.get('years', [])
        months = config.get('months', list(range(1, 13)))
        
        # Calcular total de archivos proyectados
        total_files_projected = len(pairs) * len(timeframes) * len(years) * len(months)
        
        self.log('INFO', f"Starting download request for {total_files_projected} potential files", {
            'pairs': pairs,
            'timeframes': timeframes,
            'years': years
        })
        
        # El downloader corporativo ya itera sobre todo si le pasamos listas.
        # Pero para tener granularidad en el progreso del agente, podríamos llamarlo por par/tf.
        
        downloaded_files = []
        total_candles = 0
        current_step = 0
        total_steps = len(pairs) * len(timeframes) * len(years)
        
        for pair in pairs:
            for timeframe in timeframes:
                for year in years:
                    self.log('INFO', f"Processing {pair} {timeframe} {year}")
                    
                    try:
                        # Adaptado para usar la firma correcta de src/data/downloader.py
                        download_binance_data(
                            pairs=[pair],
                            timeframes=[timeframe],
                            years=[year],
                            months=months,
                            data_dir=str(self.data_dir)
                        )
                        
                        # Verificar qué se descargó realmente
                        for month in months:
                            filename = f"{pair}-{timeframe}-{year}-{month:02d}.csv"
                            filepath = self.data_dir / filename
                            
                            if filepath.exists():
                                # Solo agregamos si no estaba ya en la lista (evitar duplicados si corre varias veces)
                                if filename not in downloaded_files:
                                    downloaded_files.append(filename)
                                    # Contar líneas (velas)
                                    with open(filepath, 'r') as f:
                                        # Restamos el header si existe
                                        lines = sum(1 for _ in f)
                                        if lines > 0:
                                            total_candles += (lines - 1)
                        
                        current_step += 1
                        self.update_progress(
                            current_step,
                            total_steps,
                            f"Processed {pair} {timeframe} {year}. Total files: {len(downloaded_files)}"
                        )
                    
                    except Exception as e:
                        self.log('ERROR', f"Error processing {pair} {timeframe} {year}: {str(e)}")
                        current_step += 1
                        continue
        
        result = {
            'downloaded_files': downloaded_files,
            'total_files': len(downloaded_files),
            'total_candles': total_candles,
            'data_dir': str(self.data_dir)
        }
        
        self.log('INFO', f"DataAgent run completed: {len(downloaded_files)} files active, {total_candles} candles total")
        
        return result
    
    def get_available_data(self) -> List[Dict[str, Any]]:
        """Listar datos disponibles en disco"""
        files = []
        for filepath in self.data_dir.glob("*.csv"):
            parts = filepath.stem.split('-')
            if len(parts) >= 4:
                files.append({
                    'filename': filepath.name,
                    'pair': parts[0],
                    'timeframe': parts[1],
                    'year': parts[2],
                    'month': parts[3],
                    'size_bytes': filepath.stat().st_size,
                    'path': str(filepath)
                })
        return files
