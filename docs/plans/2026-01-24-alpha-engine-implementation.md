# Alpha Engine Implementation Plan

> **Para Claude:** SUB-SKILL REQUERIDA: Usar superpowers:executing-plans para implementar este plan tarea por tarea.

**Meta:** Crear la arquitectura de Alpha Engine (Layer 3) para descomponer decisiones monolíticas en señales independientes combinables.

**Arquitectura:** 
- Alphas: Clases independientes con interface `get_score(market_state) -> float [-1, 1]`.
- Combiner: Motor de suma ponderada de señales.
- Optimización: `MarketState` con cache lazy para indicadores técnicos.
- Risk Management: Separación de Concerns (Alphas dan dirección, RiskManager da SL/TP).

**Tech Stack:** Python, SQLAlchemy, Pytest.

---

## Tarea 1: Interface Base de Alphas

**Archivos:**
- Crear: `src/alphas/base.py`
- Test: `tests/alphas/test_base_alpha.py`

**Paso 1: Escribir test de interface**
Verificar que no se puede instanciar la clase base y que las subclases deben implementar `get_score`.

**Paso 2: Implementar Abstract Base Class**
Uso de `abc.ABC` y `@abstractmethod`.

---

## Tarea 2: Optimización MarketState (Lazy Cache)

**Archivos:**
- Modificar: `src/core/market.py`
- Test: `tests/core/test_market_cache.py`

**Paso 1: Test de redundancia**
Verificar que el cálculo de un indicador (ej: RSI) solo se ejecuta una vez aunque se pida 5 veces.

**Paso 2: Implementar `_cache` en `MarketState`**
Modificar dataclass para soportar cache interno sin romper la inmutabilidad lógica.

---

## Tarea 3: Alpha - OB Quality (TJR Signal)

**Archivos:**
- Crear: `src/alphas/ob_quality.py`
- Test: `tests/alphas/test_ob_quality.py`

**Paso 1: Test de señal OB**
Verificar score > 0 en setups alcistas y < 0 en bajistas.

**Paso 2: Portar lógica de `src/strategy/engine.py`**
Mover la detección de Order Blocks al score de este Alpha.

---

## Tarea 4: Alpha - Momentum (Trend Strength)

**Archivos:**
- Crear: `src/alphas/momentum.py`
- Test: `tests/alphas/test_momentum.py`

**Paso 1: Implementar Alpha de Momentum**
Uso de RSI/MACD coordinado con `MarketState.cache`.

---

## Tarea 5: Alpha - Volatility (Regime Detection)

**Archivos:**
- Crear: `src/alphas/volatility.py`
- Test: `tests/alphas/test_volatility.py`

**Paso 1: Implementar Alpha de Volatilidad**
Filtrar o penalizar scores en baja volatilidad (rango) vs expansión.

---

## Tarea 6: Alpha - ML Confidence (Integración Modelos)

**Archivos:**
- Crear: `src/alphas/ml_confidence.py`
- Test: `tests/alphas/test_ml_confidence.py`

**Paso 1: Integrar `PatternAnalyzer`**
Convertir la probabilidad del modelo ML [0, 1] a score alpha [-1, 1].

---

## Tarea 7: Alpha - Liquidity (Microstructure)

**Archivos:**
- Crear: `src/alphas/liquidity.py`
- Test: `tests/alphas/test_liquidity.py`

**Paso 1: Implementar Score de Liquidez**
Uso de volumen relativo y spreads para validar la calidad de la señal.

---

## Tarea 8: AlphaCombiner (Engine de Decisión)

**Archivos:**
- Crear: `src/alphas/combiner.py`
- Test: `tests/alphas/test_combiner.py`

**Paso 1: Test de combinación ponderada**
Verificar que el Combiner suma correctamente 5 alphas con diferentes pesos.

**Paso 2: Implementar lógica de aggregate_score**
Normalización y threshold de entrada.

---

## Tarea 9: Integración Global y Refactor Orchestrator

**Archivos:**
- Modificar: `src/agents/orchestrator.py`
- Modificar: `src/optimization/engine.py`

**Paso 1: Reemplazar Estrategia Monolítica**
Cambiar llamadas a `TJRStrategy.analyze` por `AlphaCombiner.get_signal`.

**Paso 2: Verificación de Sistema**
Correr un backtest completo de un par (BTC) usando la nueva arquitectura Alpha Engine.

---

## Verificación Final

Correr suite completa:
```bash
python3 -m pytest tests/alphas/ -v
```

Esperado: Todos los Alphas y el Combiner funcionando bajo la nueva interface.
