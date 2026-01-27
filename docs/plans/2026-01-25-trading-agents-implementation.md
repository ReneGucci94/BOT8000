# Trading Agents (MSC Layer 2) Implementation Plan

> **Para Claude:** SUB-SKILL REQUERIDA: Usar superpowers:executing-plans para implementar este plan tarea por tarea.

**Meta:** Crear la capa de agentes especializados que utilizan el Alpha Engine para operar en condiciones específicas de mercado (MSC Layer 2).

**Arquitectura:**
- **Clase Base:** `TradingAgent` (Abstracta).
- **Personalidades:** 5 Agentes con pesos Alpha específicos y regímenes de activación.
- **Contract:** Todos los agentes reciben `MarketRegime` y `MarketState` y retornan `TradeSignal`.

---

## Tarea 1: Clase Base y Enum de Regímenes

**Archivos:**
- Crear: `src/agents/trading_agent.py`
- Crear: `src/core/regime.py`
- Test: `tests/agents/test_trading_agent_base.py`

**Paso 1: Definir `MarketRegime` Enum**
Incluir: `TRENDING_BULLISH`, `TRENDING_BEARISH`, `SIDEWAYS_RANGE`, `HIGH_VOLATILITY`, `BREAKOUT_PENDING`, `NEWS_DRIVEN`.

**Paso 2: Implementar Clase Base `TradingAgent`**
- Constructor que recibe mapping de pesos.
- Atributo list de regímenes permitidos.
- Método `should_activate(regime) -> bool`.
- Método `generate_signal(market_state) -> TradeSignal`.

---

## Tarea 2: Agent - Trend Hunter (Trend Bias)

**Paso 1: Implementar `TrendHunterAgent`**
- Pesos: `Momentum: 3.0`, `OB: 2.0`, `Vol: 1.0`, `ML: 1.0`, `Liq: 0.8`.
- Regímenes: `TRENDING_BULLISH`, `TRENDING_BEARISH`.

---

## Tarea 3: Agent - Mean Reversion (Contrarian Bias)

**Paso 1: Implementar `MeanReversionAgent`**
- Pesos: `OB: 3.0`, `Momentum: -1.5`, `Vol: 0.5`, `ML: 1.0`, `Liq: 0.8`.
- Regímenes: `SIDEWAYS_RANGE`.

---

## Tarea 4: Agent - Volatility Filter (Expansion Bias)

**Paso 1: Implementar `VolatilityFilterAgent`**
- Pesos: `Vol: 4.0`, resto: `0.5`.
- Regímenes: `HIGH_VOLATILITY`.

---

## Tarea 5: Agent - Breakout Hunter (Microstructure Bias)

**Paso 1: Implementar `BreakoutHunterAgent`**
- Pesos: `OB: 2.0`, `Liq: 3.0`, `Vol: 1.5`, `ML: 1.0`, `Momentum: 1.0`.
- Regímenes: `BREAKOUT_PENDING`.

---

## Tarea 6: Agent - Sentiment Scout (News Bias)

**Paso 1: Implementar `SentimentScoutAgent`**
- Pesos: Todos: `1.0` (Placeholder/Baseline).
- Regímenes: `NEWS_DRIVEN`.

---

## Tarea 7: Registry y Orquestación Inicial

**Archivos:**
- Crear: `src/agents/agent_registry.py`

**Paso 1: Implementar Registro de Agentes**
Función `get_all_agents()` que retorna instancias de los 5 agentes.

**Paso 2: Test de Integración**
Validar que podemos ciclar entre todos los agentes y obtener señales consistentes.

---

## Verificación Final

Correr suite completa de agentes:
```bash
python3 -m pytest tests/agents/test_trading_agents.py -v
```

---

> [!IMPORTANT]
> Los pesos Alpha negativos en `MeanReversionAgent` deben ser invertidos cuidadosamente en el `AlphaCombiner` (ya soportado por naturaleza de la suma ponderada).
