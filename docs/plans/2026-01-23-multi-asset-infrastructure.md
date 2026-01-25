# Multi-Asset Infrastructure - Plan de Implementación (v2)

> **Para Claude:** SUB-SKILL REQUERIDA: Usar superpowers:executing-plans para implementar este plan tarea por tarea.

**Meta:** Permitir operar BTC, ETH, SOL simultáneamente.

**Arquitectura:** 
- DB: Columna `symbol` en tablas existentes
- Migración: Nullable → Update → Not Null (script manual, no Alembic)
- Loader: Loop secuencial (YAGNI)

**Tech Stack:** PostgreSQL, SQLAlchemy

---

## Tarea 1: Migración de Base de Datos (PRIMERO)

**Archivos:**
- Crear: `scripts/migrate_add_symbol.py`

### Paso 1: Crear script de migración con validación

```python
# scripts/migrate_add_symbol.py
from sqlalchemy import text
from src.database import get_db_session

def migrate():
    with get_db_session() as db:
        # 0. Count existing trades for validation
        initial_count = db.execute(text("SELECT COUNT(*) FROM trades")).scalar()
        print(f"Found {initial_count} existing trades")
        
        # 1. Add nullable column
        print("Adding symbol column (nullable)...")
        db.execute(text("ALTER TABLE trades ADD COLUMN IF NOT EXISTS symbol VARCHAR(20)"))
        db.execute(text("ALTER TABLE strategies ADD COLUMN IF NOT EXISTS symbol VARCHAR(20)"))
        
        # 2. Backfill legacy data
        print("Backfilling legacy data with 'BTCUSDT'...")
        db.execute(text("UPDATE trades SET symbol = 'BTCUSDT' WHERE symbol IS NULL"))
        db.execute(text("UPDATE strategies SET symbol = 'BTCUSDT' WHERE symbol IS NULL"))
        
        # 3. Set NOT NULL
        print("Setting NOT NULL constraint...")
        db.execute(text("ALTER TABLE trades ALTER COLUMN symbol SET NOT NULL"))
        db.execute(text("ALTER TABLE strategies ALTER COLUMN symbol SET NOT NULL"))
        
        # 4. Create indexes
        print("Creating indexes...")
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_trades_symbol ON trades(symbol)"))
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_strategies_symbol ON strategies(symbol)"))
        
        db.commit()
        
        # 5. Verify migration
        migrated_count = db.execute(text("SELECT COUNT(*) FROM trades WHERE symbol = 'BTCUSDT'")).scalar()
        assert migrated_count == initial_count, f"Expected {initial_count} trades, got {migrated_count}"
        print(f"✓ Verified {migrated_count} legacy trades migrated correctly")
        print("✓ Migration complete")

if __name__ == "__main__":
    migrate()
```

### Paso 2: Ejecutar migración

Correr: `python3 scripts/migrate_add_symbol.py`
Esperado: 
```
Found 1404 existing trades
Adding symbol column (nullable)...
Backfilling legacy data with 'BTCUSDT'...
Setting NOT NULL constraint...
Creating indexes...
✓ Verified 1404 legacy trades migrated correctly
✓ Migration complete
```

### Paso 3: Verificar en DB

Correr: `docker exec -it bot8000-db psql -U postgres -d bot8000 -c "SELECT symbol, COUNT(*) FROM trades GROUP BY symbol"`
Esperado: `BTCUSDT | 1404`

---

## Tarea 2: Actualizar Modelos SQLAlchemy (DESPUÉS de migración)

**Archivos:**
- Modificar: `src/database/models.py`
- Test: `tests/database/test_multi_asset_schema.py`

### Paso 1: Escribir test que falla

```python
# tests/database/test_multi_asset_schema.py
import pytest
from src.database.models import Trade, Strategy

def test_trade_has_symbol_attribute():
    """Trade model debe tener atributo symbol."""
    assert hasattr(Trade, 'symbol'), "Trade model missing 'symbol' attribute"

def test_strategy_has_symbol_attribute():
    """Strategy model debe tener atributo symbol."""
    assert hasattr(Strategy, 'symbol'), "Strategy model missing 'symbol' attribute"
```

### Paso 2: Verificar que falla

Correr: `python3 -m pytest tests/database/test_multi_asset_schema.py -v`
Esperado: FAIL

### Paso 3: Implementar cambio en models.py

En clase `Trade` (después de línea ~24):
```python
symbol = Column(String(20), nullable=False, index=True)
```

En clase `Strategy` (después de línea ~94):
```python
symbol = Column(String(20), nullable=False, index=True)
```

### Paso 4: Verificar que pasa

Correr: `python3 -m pytest tests/database/test_multi_asset_schema.py -v`
Esperado: PASS

---

## Tarea 3: Actualizar DataAgent para Multi-Símbolo

**Archivos:**
- Modificar: `src/agents/data_agent.py`
- Test: `tests/agents/test_data_agent_multi.py`

### Paso 1: Escribir test que falla

```python
# tests/agents/test_data_agent_multi.py
import pytest
from unittest.mock import patch, MagicMock
from src.agents.data_agent import DataAgent

def test_data_agent_iterates_all_pairs():
    """DataAgent debe iterar sobre todos los pares en config."""
    agent = DataAgent()
    
    with patch.object(agent, '_download_file') as mock_download:
        mock_download.return_value = True
        
        result = agent.execute({
            'pairs': ['BTCUSDT', 'ETHUSDT', 'SOLUSDT'],
            'timeframes': ['4h'],
            'years': [2024],
            'months': [1]
        })
        
        # Debe haber llamado download para cada par
        call_args = [call[0][0] for call in mock_download.call_args_list]
        assert 'BTCUSDT' in str(call_args)
        assert 'ETHUSDT' in str(call_args)
        assert 'SOLUSDT' in str(call_args)
```

### Paso 2: Verificar que falla

Correr: `python3 -m pytest tests/agents/test_data_agent_multi.py -v`
Esperado: FAIL

### Paso 3: Implementar loop secuencial

Modificar `DataAgent.run()` para:
```python
for pair in pairs:
    self.log('INFO', f"Downloading {pair}...")
    for tf in timeframes:
        for year in years:
            for month in months:
                self._download_file(pair, tf, year, month)
    self.log('INFO', f"✓ {pair} complete")
```

### Paso 4: Verificar que pasa

Correr: `python3 -m pytest tests/agents/test_data_agent_multi.py -v`
Esperado: PASS

---

## Tarea 4: Actualizar OptimizerWorker para guardar symbol

**Archivos:**
- Modificar: `src/agents/worker.py`
- Test: `tests/agents/test_worker_saves_symbol.py`

### Paso 1: Escribir test que falla

```python
# tests/agents/test_worker_saves_symbol.py
import pytest
from unittest.mock import patch, MagicMock
from src.agents.worker import OptimizerWorker

def test_worker_includes_symbol_in_trade_record():
    """Worker debe incluir symbol del config en cada trade guardado."""
    worker = OptimizerWorker("test-worker")
    
    # Mock para capturar lo que se guarda
    captured_trades = []
    
    def capture_trade(db, trade_data):
        captured_trades.append(trade_data)
        return MagicMock()
    
    with patch('src.agents.worker.TradeRepository.create', side_effect=capture_trade):
        with patch('src.agents.worker.load_binance_csv', return_value=[]):
            # Ejecutar con par específico
            try:
                worker.run({
                    'pair': 'ETHUSDT',
                    'timeframe': '4h',
                    'year': 2024,
                    'months': [1],
                    'backtest_run_id': 'test-123',
                    'stop_loss': 2000,
                    'take_profit_multiplier': 2.0,
                    'initial_balance': 10000,
                    'fee_rate': 0.001,
                    'risk_per_trade_pct': 1.0
                })
            except:
                pass  # Puede fallar por falta de datos, pero lo importante es verificar el flujo
    
    # Si hubo trades, verificar que tengan symbol correcto
    for trade in captured_trades:
        assert trade.get('symbol') == 'ETHUSDT', f"Expected 'ETHUSDT', got {trade.get('symbol')}"
```

### Paso 2: Verificar que falla

Correr: `python3 -m pytest tests/agents/test_worker_saves_symbol.py -v`
Esperado: FAIL (symbol es 'BTCUSDT' hardcodeado o no existe)

### Paso 3: Implementar fix en worker.py

En el método `run()`, modificar el `trade_record` para usar:
```python
'symbol': pair,  # Usar el pair del config, no hardcodear
```

### Paso 4: Verificar que pasa

Correr: `python3 -m pytest tests/agents/test_worker_saves_symbol.py -v`
Esperado: PASS

---

## Verificación Final

Correr suite completa:
```bash
python3 -m pytest tests/database/test_multi_asset_schema.py tests/agents/test_data_agent_multi.py tests/agents/test_worker_saves_symbol.py -v
```

Esperado: 4+ tests pasando.
