# Phase 3: Core Strategy Implementation Plan (TJR Price Action)

> **Para Claude:** SUB-SKILL REQUERIDA: superheroes:executing-plans y superheroes:test-driven-development (TDD) estricto.

**Meta:** Implementar la lógica pura de la estrategia TJR (Market Structure, BOS, FVG, OB) como funciones puras o componentes aislados.

**Ubicación:** `src/strategy/` (Separación de Data y Logic).
**Referencias:** `CLAUDE.md` (Sección TJR Price Action).

---

### Tarea 1: Detección de Swing Points (Fractales)

**Objetivo:** Identificar Highs y Lows válidos según definición TJR.
- **High Válido:** Vela Verde (i) -> Vela Roja (i+1). High es `candles[i].high`.
- **Low Válido:** Vela Roja (i) -> Vela Verde (i+1). Low es `candles[i].low`.

**Archivos:**
- `src/strategy/fractals.py`
- `tests/strategy/test_fractals.py`

**Pasos TDD:**
1.  **Test:** Crear lista de velas simuladas (Verde, Roja, Verde, Roja...). Verificar `is_valid_high(series, index)` y `is_valid_low(series, index)`.
2.  **Implementación:** Funciones puras que reciben `MarketSeries` e índice.
3.  **Verificación:** Casos borde (inicio/fin de serie).

---

### Tarea 2: Market Structure & BOS

**Objetivo:** Determinar la estructura (HH, HL, LH, LL) y detectar Break of Structure (BOS).
- **BOS:** Cierre de CUERPO más allá del último fractal válido.

**Archivos:**
- `src/strategy/structure.py`
- `tests/strategy/test_structure.py`

**Pasos TDD:**
1.  **Test (Bullish BOS):**
    - Setup: High Válido previo en precio 100.
    - Acción: Vela actual cierra en 101.
    - Assert: `detect_bos` retorna True/StructureEvent.
2.  **Test (Wick Failure):**
    - Setup: High Válido en 100.
    - Acción: Vela hace wick a 102 pero cierra en 99.
    - Assert: `detect_bos` retorna False.
3.  **Implementación:** Clase `MarketStructure` o funciones que traingan el estado de los swings.

---

### Tarea 3: Fair Value Gaps (FVG)

**Objetivo:** Detectar ineficiencias (Gaps) de 3 velas.
- **Bullish FVG:** `High(i) < Low(i+2)` (Gap entre vela 1 y 3).
- **Bearish FVG:** `Low(i) > High(i+2)`.

**Archivos:**
- `src/strategy/fvg.py`
- `tests/strategy/test_fvg.py`

**Pasos TDD:**
1.  **Test:** Crear patrón de 3 velas con gap. Assert FVG detectado con coordenadas correctas (Top, Bottom).
2.  **Test:** Patrón sin gap (mechas se tocan/superponen). Assert FVG no detectado.
3.  **Implementación:** Iterar sobre ventanas de 3 velas.

---

### Tarea 4: Order Blocks (Completo TJR)

**Objetivo:** Identificar Order Blocks válidos requiriendo Sweep de Liquidez previo y BOS posterior.
- **Validación TJR:**
  1. **Liquidity Sweep:** El movimiento debe haber barrido un swing point previo (tomado liquidez) ANTES del reversal.
  2. **BOS:** El movimiento debe romper estructura (cuerpo) en la dirección del nuevo bias.
  3. **OB Zone:** El rango completo (High-Low) de la vela responsable.

**Archivos:**
- `src/strategy/ob.py`
- `tests/strategy/test_ob.py`

**Pasos TDD:**
1.  **Test (Valid Bullish OB):**
    - Setup: Swing Low anterior en 95.
    - Acción: Precio baja a 94 (Sweep), revierte fuerte, rompe Swing High reciente (BOS).
    - Assert: `detect_ob` retorna la última vela roja antes del impulso.
2.  **Test (Invalid - No Sweep):**
    - Setup: Precio sube y hace BOS, pero el movimiento inició en un Higher Low sin barrer liquidez previa.
    - Assert: `detect_ob` no reporta OB válido.
3.  **Test (OB Zone):**
    - Assert: El objeto `OrderBlock` incluye `top`, `bottom` correspondientes a la vela completa.
4.  **Implementación:** Algoritmo que rastrea swings previos para confirmar el sweep antes de validar el OB.

---

### Tarea 5: Verificación Integrada

**Objetivo:** Verificar que todas las funciones trabajan sobre `MarketState`.

**Archivos:**
- `tests/integration/test_strategy_logic.py`

**Pasos:**
1.  Simular un mini-market cycle (Acumulación -> Expansión).
2.  Verificar que se detectaron los Swing Highs, luego el BOS, dejando un FVG y un OB.
