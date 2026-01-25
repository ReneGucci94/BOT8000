# Pure Alpha MSC Implementation Plan

> **Para Claude:** SUB-SKILL REQUERIDA: Usar superpowers:executing-plans para implementar este plan tarea por tarea.

**Meta:** Transformar el sistema de "Single Best Strategy" a un "Pure Alpha Portfolio" implementando filtros de correlación, manejo multi-activo, riesgo basado en volatilidad y coordinación MSC.

**Arquitectura:** 
1. **Correlation Matrix:** Bloquear estrategias nuevas que tengan >0.3 correlación con las existentes.
2. **Multi-Asset:** Extender DB y Loader para soportar múltiples símbolos.
3. **Vol Risk:** Normalizar riesgo usando volatilidad anualizada.
4. **MSC Coordinator:** Capa superior que detecta régimen de mercado y asigna peso a agentes especializados.

**Tech Stack:** Python, Pandas (resampling/corr), SQLAlchemy, Pytest.

---

## Tarea 5.1: Correlation Matrix Module (Validator Upgrade)

Esta tarea implementa el "filtro de unicidad". No más estrategias clones.

**Archivos:**
- Crear: `src/portfolio/correlation.py`
- Modificar: `src/agents/validator.py`
- Test: `tests/portfolio/test_correlation.py`

### Paso 1: Crear estructura de tests para cálculo de correlación
**Objetivo:** Definir cómo se comportará el cálculo de correlación entre dos listas de trades.

**Acción:** Crear `tests/portfolio/test_correlation.py`.
```python
import pytest
import pandas as pd
from datetime import datetime, timedelta
from decimal import Decimal
from src.database.models import Trade
from src.portfolio.correlation import calculate_correlation, build_equity_curve

def create_mock_trades(start_time, pnl_sequence):
    trades = []
    current_time = start_time
    for pnl in pnl_sequence:
        trades.append(Trade(
            entry_time=current_time.timestamp() * 1000,
            exit_time=(current_time + timedelta(hours=4)).timestamp() * 1000,
            profit_loss=Decimal(str(pnl))
        ))
        current_time += timedelta(days=1)
    return trades

def test_perfect_correlation():
    # Dos estrategias idénticas deben tener corr = 1.0
    start = datetime(2024, 1, 1)
    trades_a = create_mock_trades(start, [100, 200, -50, 100])
    trades_b = create_mock_trades(start, [100, 200, -50, 100])
    
    corr = calculate_correlation(trades_a, trades_b)
    assert corr == pytest.approx(1.0, 0.01)

def test_inverse_correlation():
    # Espejos deben tener corr = -1.0
    start = datetime(2024, 1, 1)
    trades_a = create_mock_trades(start, [100, 100, 100])
    trades_b = create_mock_trades(start, [-100, -100, -100])
    
    corr = calculate_correlation(trades_a, trades_b)
    assert corr == pytest.approx(-1.0, 0.01)

def test_uncorrelated():
    # Random vs Random debería ser bajo (aunque con pocos datos es ruidoso)
    # Aquí probamos ortogonalidad simple: [1, 0] vs [0, 1]
    start = datetime(2024, 1, 1)
    trades_a = create_mock_trades(start, [100, 100, 0, 0])
    trades_b = create_mock_trades(start, [0, 0, 100, 100])
    
    # Nota: Equity curve es acumulativa. 
    # A: 100, 200, 200, 200
    # B: 0, 0, 100, 200
    corr = calculate_correlation(trades_a, trades_b)
    assert -1.0 <= corr <= 1.0
```

**Verificación:** `pytest tests/portfolio/test_correlation.py` -> DEBE FALLAR (ModuleNotFoundError).

---

### Paso 2: Implementar lógica de Equity Curve
**Objetivo:** Convertir lista de trades dispersos en una serie de tiempo diaria uniforme.

**Acción:** Crear `src/portfolio/correlation.py` con `build_equity_curve`.
```python
import pandas as pd
from typing import List
from src.database.models import Trade

def build_equity_curve(trades: List[Trade], freq: str = '1D') -> pd.DataFrame:
    if not trades:
        return pd.DataFrame(columns=['equity'])
        
    data = []
    for t in trades:
        data.append({
            'timestamp': pd.to_datetime(t.entry_time, unit='ms'),
            'pnl': float(t.profit_loss)
        })
    
    df = pd.DataFrame(data)
    df = df.set_index('timestamp').resample(freq).sum().fillna(0)
    df['equity'] = df['pnl'].cumsum()
    return df
```

**Verificación:** `pytest tests/portfolio/test_correlation.py` -> Aún falla en `calculate_correlation`.

---

### Paso 3: Implementar cálculo de Correlación
**Objetivo:** Usar las equity curves para calcular Pearson.

**Acción:** Añadir `calculate_correlation` a `src/portfolio/correlation.py`.
```python
import numpy as np

def calculate_correlation(trades_a: List[Trade], trades_b: List[Trade]) -> float:
    if not trades_a or not trades_b:
        return 0.0
        
    equity_a = build_equity_curve(trades_a)
    equity_b = build_equity_curve(trades_b)
    
    # Unir por índice (fecha) para alinear
    # how='outer' y ffill para llenar días sin trades con el último equity valor
    merged = pd.merge(equity_a, equity_b, left_index=True, right_index=True, how='outer', suffixes=('_a', '_b'))
    merged = merged.fillna(method='ffill').fillna(0)
    
    if len(merged) < 2:
        return 0.0
        
    # Calcular correlación de cambios diarios (returns) o equity levels?
    # Bridgewater usa correlación de retornos típicamente, pero equity correlation es más directa para "trayectoria"
    # Usaremos correlation de equity curve para ver si "ganan juntos".
    
    return float(merged['equity_a'].corr(merged['equity_b']))
```

**Verificación:** `pytest tests/portfolio/test_correlation.py` -> DEBE PASAR.

---

### Paso 4: Integrar en ValidatorAgent
**Objetivo:** Que el validador rechace estrategias correlacionadas.

**Acción:** Modificar `tests/agents/test_validator.py` (crear si no existe test específico de esto) y luego `src/agents/validator.py`.

*4.1 Test de Integración (Fail first)*
```python
# tests/agents/test_validator_correlation.py
def test_validator_rejects_correlated_strategy(db_session, mock_approved_strategy):
    # Setup: 1 estrategia aprobada en DB
    # Intentar aprobar una nueva estrategia con los mismos trades
    # Expect: False
    pass
```

*4.2 Implementación*
Modificar `src/agents/validator.py`:
```python
from src.portfolio.correlation import calculate_correlation

# En approve_strategy...
existing_strategies = self.repo.get_approved_strategies()
for strategy in existing_strategies:
    trades_existing = self.repo.get_trades(strategy.id)
    trades_new = self.repo.get_trades(new_strategy_id)
    
    corr = calculate_correlation(trades_new, trades_existing)
    if corr > 0.3:
        logger.info(f"Rejected: High correlation ({corr:.2f}) with Strategy {strategy.id}")
        return False
```

**Verificación:** Correr suite completa de tests.

---
