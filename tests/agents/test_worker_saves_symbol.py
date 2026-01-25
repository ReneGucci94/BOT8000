# tests/agents/test_worker_saves_symbol.py
import pytest
from unittest.mock import patch, MagicMock
from src.agents.worker import OptimizerWorker
from src.execution.executor import TradeSignal
from src.execution.broker import OrderSide
from decimal import Decimal
from datetime import datetime

def test_worker_includes_symbol_in_trade_record():
    """Worker debe incluir symbol del config en cada trade guardado."""
    worker = OptimizerWorker("test-worker")
    
    # Mock para capturar lo que se guarda
    captured_trades = []
    
    def capture_trade(db, trade_data):
        captured_trades.append(trade_data)
        return MagicMock()
    
    # Mockeamos TradeRepository.create para capturar los datos del trade
    with patch('src.agents.worker.TradeRepository.create', side_effect=capture_trade):
        # Mock de vela mínima
        mock_candle = MagicMock()
        mock_candle.timestamp = 1704067200000.0 # 2024-01-01
        mock_candle.close = Decimal("40000")
        mock_candle.open = Decimal("39000")
        mock_candle.high = Decimal("41000")
        mock_candle.low = Decimal("38000")
        mock_candle.volume = Decimal("100")
        
        # Mock de load_binance_csv y Path.exists
        with patch('src.agents.worker.load_binance_csv', return_value=[mock_candle]):
            with patch('src.agents.worker.Path.exists', return_value=True):
                # Mock de TJRStrategy para retornar una señal real (no mock)
                # para evitar errores de tipo en los cálculos de risk_manager
                with patch('src.agents.worker.TJRStrategy') as mock_strat_cls:
                    mock_strat = mock_strat_cls.return_value
                    
                    real_signal = TradeSignal(
                        symbol="ETHUSDT",
                        side=OrderSide.BUY,
                        entry_price=Decimal("40000"),
                        stop_loss=Decimal("39000"),
                        take_profit=Decimal("42000")
                    )
                    mock_strat.analyze.return_value = real_signal
                    
                    # Mock de InMemoryBroker
                    with patch('src.agents.worker.InMemoryBroker') as mock_broker_cls:
                        mock_broker = mock_broker_cls.return_value
                        mock_broker.get_balance.return_value = Decimal("10000")
                        mock_broker.get_positions.return_value = []
                        
                        # Mock de una posición cerrada
                        pos = MagicMock()
                        pos.side.value = 'BUY'
                        pos.entry_price = Decimal("40000")
                        pos.exit_price = Decimal("41000")
                        pos.stop_loss = Decimal("39000")
                        pos.take_profit = Decimal("42000")
                        pos.pnl = Decimal("100")
                        pos.quantity = Decimal("1")
                        
                        mock_broker.get_closed_positions.return_value = [pos]
                        
                        # Ejecutar con par específico 'ETHUSDT'
                        worker.run({
                            'pair': 'ETHUSDT',
                            'timeframe': '4h',
                            'year': 2024,
                            'months': [1],
                            'backtest_run_id': '00000000-0000-0000-0000-000000000000',
                            'stop_loss': 2000,
                            'take_profit_multiplier': 2.0,
                            'initial_balance': 10000,
                            'fee_rate': 0.001,
                            'risk_per_trade_pct': 1.0,
                            'use_ml_model': False
                        })
    
    # Verificación
    assert len(captured_trades) > 0, "No se capturaron trades"
    # El test FALLARÁ ahora por la llave 'symbol'
    assert 'symbol' in captured_trades[0], "La llave 'symbol' falta en trade_record"
    assert captured_trades[0]['symbol'] == 'ETHUSDT', f"Se esperaba 'ETHUSDT', se obtuvo {captured_trades[0].get('symbol')}"
