# Phase 4.5/5: Strategy Orchestration & Full Verification

> **Contexto:** Tenemos la lógica TJR (`detect_ob`, `detect_bos`) y el Executor, pero falta el **Orchestrator** que escanee el mercado en cada vela y emita el `TradeSignal`.

**Meta:** Conectar Market -> Logic -> Execution y simular 1000+ velas.

---

### Tarea 1: Strategy Orchestrator (The "Brain")

**Objetivo:** Implementar clase `TJRStrategy` que:
1.  Reciba `MarketState`.
2.  Mantenga estado interno (Bias, POIs, Pending Setups).
3.  En cada `update`, verifique condiciones:
    - ¿Estamos en un POI (OB)?
    - ¿Hay confirmación LTF (Lower Timeframe)? (Simulado o simplificado a 1 TF por ahora).
    - Emitir `TradeSignal` si hay Trigger.

**Archivos:**
- `src/strategy/engine.py` (Clase `TJRStrategy`)
- `tests/strategy/test_engine.py`

**Lógica Simplificada (MVP):**
- **Trigger:** Detectar formación de OB alcista + FVG subsecuente (Entry agresiva) o re-test del OB.
- Para la simulación, usaremos entrada en re-test de OB:
  1. Detect OB.
  2. Guardar OB en memoria.
  3. Si precio vuelve a tocar OB.top, Emitir BUY.
  4. SL = OB.bottom.
  5. TP = 2R (o basado en next liquidity).

### Tarea 2: Synthetic Data Generator

**Objetivo:** Generar datos OHLC "químicamente válidos" con patrones inyectados.
- No basta con Random Walk. Necesitamos **Cycles**:
  - Consolidation -> Expansion (Up) -> Consolidation -> Reversal (Down).

**Archivos:**
- `src/simulation/generator.py`

### Tarea 3: Full Cycle Simulation (Paper Trading)

**Objetivo:** Script que corra el loop principal.

**Archivos:**
- `tests/simulation/test_full_cycle.py`

**Loop:**
```python
market = MarketState.empty()
strategy = TJRStrategy()
broker = MockBroker(10000)
executor = TradeExecutor(broker, risk)

for candle in generator.generate_cycle(1000):
   market = market.update(candle)
   signal = strategy.analyze(market)
   if signal:
       executor.execute(signal)

# Verify
assert len(broker.orders) > 0
assert broker.balance != 10000
```

---

### Tarea 4: Final Report

**Archivos:**
- `reports/session_report.md` (Generado automáticamente o manual)
