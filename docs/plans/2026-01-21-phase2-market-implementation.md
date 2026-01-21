# Phase 2: MultiTimeframeMarket Implementation Plan

> **Para Claude:** SUB-SKILL REQUERIDA: Usar superpowers:executing-plans para implementar este plan tarea por tarea.

**Meta:** Implementar `MarketState` y `MultiTimeframeMarket`, permitiendo la sincronización correcta de velas de diferentes timeframes (4H, 1H, 15m, 5m) manteniendo inmutabilidad.

**Arquitectura:** Inmutable God Object (`MarketState`) que contiene `MarketSeries` para cada TJR Timeframe.

**Tech Stack:** Python 3.12+, dataclasses (frozen), mypy (strict).

---

### Tarea 1: Estructura MarketState

**Archivos:**
- Crear: `src/core/market.py`
- Crear: `tests/core/test_market.py`

**Paso 1: Test que falla (Inicialización)**
Testear que `MarketState` requiere `symbol` y series para M5, M15, H1, H4.
Verificar que se puede instanciar con series vacías.

**Paso 2: Implementación**
`@dataclass(frozen=True)` con campos para cada timeframe y symbol string.
Factory method `empty(symbol)` para facilitar creación.

**Paso 3: Verificar**
Correr tests.

**Paso 4: Commit**
`git add . && git commit -m "feat: define immutable MarketState structure"`

---

### Tarea 2: Sincronización de Timeframes (Lógica)

**Archivos:**
- Modificar: `src/core/market.py`
- Modificar: `tests/core/test_market.py`

**Paso 1: Test que falla (Update Logic)**
Test complejo:
1. Estado inicial vacío.
2. Agregar vela M5.
3. Verificar que M5.current es esa vela.
4. Agregar vela M15.
5. Verificar que M5 no cambió (si es que no llegó update) y M15 tiene su vela.
*Nota:* El `MarketState` recibe updates. La lógica de *construir* velas mayores desde menores es tarea del `DataFeed` (o una capa de servicio). El `MarketState` simplemente almacena la verdad. Asumiremos por diseño que `update(candle)` reemplaza la serie del timeframe correspondiente.

**Paso 2: Implementación**
Método `update(self, candle: Candle) -> 'MarketState'`.
Debe detectar el timeframe de la vela entrante y devolver una NUEVA instancia de `MarketState` con esa serie actualizada.

**Paso 3: Verificar**
Correr tests de inmutabilidad y actualización.

**Paso 4: Commit**
`git add . && git commit -m "feat: implement MarketState update logic"`

---

### Tarea 3: Utility Methods (Shortcuts)

**Archivos:**
- Modificar: `src/core/market.py`
- Modificar: `tests/core/test_market.py`

**Paso 1: Test que falla**
Testear helpers como `market.btc_price` (usa cierre de M5), `market.is_aligned(bullish=True)`.
*Wait:* `is_aligned` es lógica de estrategia. `btc_price` es genérico?
*Mejor:* Solo helpers de acceso de datos: `get_series(timeframe)`.

**Paso 2: Implementación**
`get_series(Timeframe) -> MarketSeries` para acceso polimórfico.

**Paso 3: Verificar**
Correr tests.

**Paso 4: Commit**
`git add . && git commit -m "feat: add access helpers to MarketState"`

---

### Tarea 4: Integration Verification (Phase 2)

**Archivos:**
- Crear: `tests/integration/test_market_flow.py`

**Paso 1: Script de simulacro de flujo**
Simular un stream de velas entrando (M5, M5, M5, M15...) y verificar que el `MarketState` evoluciona correctamente retornando nuevas instancias cada vez.

**Paso 2: Ejecutar**
Correr suite completa.

**Paso 3: Commit**
`git commit -m "verify: phase 2 market state integration"`
