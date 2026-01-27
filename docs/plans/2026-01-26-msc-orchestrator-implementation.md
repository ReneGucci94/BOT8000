# MSC Orchestrator (Layer 1) Implementation Plan

> **Para Claude:** SUB-SKILL REQUERIDA: Usar superpowers:executing-plans para implementar este plan tarea por tarea.

**Meta:** Implementar el "Cerebro" del sistema (Layer 1) que clasifica el mercado y delega la toma de decisiones al agente especializado (Single Winner).

**Estrategia:** 
- **Simplicidad (KISS):** Menos es más. Un solo agente activo por cada vela.
- **Transparencia:** Tags de `agent_name` y `regime` en cada trade para auditoría.
- **Mecánica:** Uso de indicadores técnicos tradicionales para la clasificación de regímenes.

---

## Tarea 1: MarketState Indicators

**Archivos:**
- Modificar: `src/core/market.py`
- Test: `tests/core/test_market_indicators.py`

**Paso 1: Implementar indicadores técnicos en `MarketState`**
Usar el sistema `_cache` (Lazy) para:
- `adx`: Average Directional Index (Trend strength).
- `atr_avg_14`: Media simple del ATR de 14 periodos.
- `ema_alignment`: Determinar si EMAs (ej: 20, 50, 200) están en orden `bullish`, `bearish` o `neutral`.

---

## Tarea 2: Market Regime Classifier

**Archivos:**
- Crear: `src/core/classifier.py`
- Test: `tests/core/test_classifier.py`

**Paso 1: Implementar `classify_regime(market_state)`**
Seguir lógica de prioridad:
1. `High Volatility` (ATR > 1.5 * Avg)
2. `Trending` (ADX > 25 + EMA Alignment)
3. `Breakout Pending` (ATR < 0.7 * Avg + ADX < 25)
4. `Sideways` (Default / ADX < 20)

---

## Tarea 3: MSCOrchestrator (Single Winner)

**Archivos:**
- Crear: `src/agents/orchestrator.py`
- Test: `tests/agents/test_orchestrator.py`

**Paso 1: Implementar `MSCOrchestrator`**
- Constructor: Instancia y mapea los 5 agentes a sus regímenes respectivos.
- Método `get_signal(market_state)`:
    - Clasifica régimen.
    - Delega al agente especializado.
    - Inyecta metadata (`agent_name`, `regime`) en el `TradeSignal`.

---

## Tarea 4: Refactor OptimizerWorker (MSC Integration)

**Archivos:**
- Modificar: `src/agents/worker.py`

**Paso 1: Integrar MSC**
Permitir que el worker use `MSCOrchestrator` cuando el flag `use_msc` esté activo.

---

## Tarea 5: Validación Multi-Agente

**Archivos:**
- Crear: `scripts/validate_msc.py`

**Paso 1: Test Comparativo**
Correr backtest con `TrendHunter` puro vs `MSCOrchestrator`. El MSC debería ser capaz de evitar operar en regímenes que no le favorecen.

---

## Verificación Final

Correr suite completa del cerebro:
```bash
python3 -m pytest tests/agents/test_orchestrator.py -v
```
