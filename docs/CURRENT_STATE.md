# BOT8000 V3 - Estado Actual del Sistema
**Fecha:** 23 Enero 2026  
**Fase Actual:** Phase 5 - Pure Alpha MSC Implementation

---

## 📊 Resumen Ejecutivo

### ✅ Lo que está FUNCIONANDO
- **Sistema completo de backtesting** con 1404 trades ejecutados
- **ML Pipeline** entrenado y filtrando trades
- **Dashboard web** operativo en `localhost:8000`
- **Base de datos PostgreSQL** con 4 tablas principales
- **15 estrategias aprobadas** (aunque todas fallaron OOS)
- **Correlation Matrix** implementado (recién agregado)

### ❌ Problema Principal Identificado
**Overfitting Masivo:** Las estrategias aprobadas tienen PF > 1.5 en training (Ene-Mar 2024) pero **colapsan en OOS** (Jun-Jul 2024):
- Mayo: PF 4.0 ✅
- Junio: PF 0.0 ❌
- Julio: PF 0.82 ❌

**Causa Raíz:** El sistema busca "la mejor estrategia" en lugar de un **portafolio de estrategias no correlacionadas** (Pure Alpha).

---

## 🏗️ Arquitectura Actual

### Estructura de Directorios (`src/`)
```
src/
├── agents/          # Multi-Agent System (10 archivos)
│   ├── base.py                  # BaseAgent class
│   ├── orchestrator.py          # Coordinator
│   ├── worker.py                # OptimizerWorker (backtest executor)
│   ├── validator.py             # ValidatorAgent (WFA + Correlation)
│   ├── optimizer_swarm.py       # Genetic Algorithm
│   ├── strategy_mutator.py      # Strategy evolution
│   ├── pattern_detective.py     # Pattern extraction
│   └── data_agent.py            # Data downloader
│
├── api/             # FastAPI Dashboard
│   ├── main.py                  # API endpoints
│   └── static/index.html        # Dashboard UI
│
├── core/            # Domain Models
│   ├── candle.py                # OHLCV data structure
│   ├── market.py                # MarketState
│   ├── timeframe.py             # Timeframe enum
│   ├── types.py                 # TradeSignal, Position
│   └── series.py                # Time series utils
│
├── database/        # Persistence Layer
│   ├── models.py                # SQLAlchemy models (Trade, Strategy, Pattern, BacktestRun)
│   ├── repository.py            # CRUD operations
│   └── connection.py            # DB session management
│
├── execution/       # Trade Execution
│   ├── broker.py                # OrderRequest, BrokerInterface
│   ├── risk.py                  # RiskManager, RiskConfig
│   └── executor.py              # TradeExecutor
│
├── ml/              # Machine Learning
│   ├── features.py              # FeatureExtractor (20+ indicators)
│   └── analyzer.py              # PatternAnalyzer (XGBoost/RF)
│
├── optimization/    # Genetic Algorithm
│   ├── engine.py                # Optimizer engine
│   ├── analyzer.py              # Performance analysis
│   └── types.py                 # Optimization types
│
├── portfolio/       # 🆕 Pure Alpha Components
│   └── correlation.py           # Correlation matrix (NEW)
│
├── simulation/      # Backtesting
│   ├── broker.py                # InMemoryBroker
│   ├── backtest.py              # Backtest engine
│   └── generator.py             # Trade generator
│
├── strategy/        # Trading Logic
│   ├── engine.py                # TJRStrategy (Price Action)
│   ├── ob.py                    # Order Block detection
│   ├── structure.py             # Market structure
│   ├── fractals.py              # Fractal detection
│   └── fvg.py                   # Fair Value Gaps
│
└── utils/
    └── data_loader.py           # Binance CSV loader
```

---

## 📋 Task List (Phase by Phase)

### ✅ Phase 1: Infrastructure Setup (COMPLETO)
- [x] PostgreSQL con Docker
- [x] Database Schema (4 tablas)
- [x] Repository Layer (CRUD)
- [x] Async Database Client

### ✅ Phase 2: Core ML Components (COMPLETO)
- [x] Feature Engineering Pipeline (20+ features)
- [x] Model Trainer (XGBoost/LightGBM)
- [x] Strategy Generator (Genetic Algo)
- [x] Pattern Recognition Agent

### ✅ Phase 3: Multi-Agent System (COMPLETO)
- [x] Agent Base Class & Communication
- [x] Specialized Agents (Risk, Execution, Sentiment)
- [x] Orchestrator Logic

### ✅ Phase 4: Backtesting & Validation (COMPLETO)
- [x] Parallel Backtest Engine
- [x] Walk-Forward Validation System
- [x] OOS Test (May-Jul 2024) for Top 3 Strategies
- [x] Performance Analytics Dashboard
- [x] Debugging (Fixed 0 Approved Strategies, API 500 errors)

### 🔄 Phase 5: Pure Alpha MSC Implementation (EN PROGRESO)
- [x] **Task 5.1:** Correlation Matrix Module ✅
  - Implementado `src/portfolio/correlation.py`
  - Integrado en `ValidatorAgent`
  - Tests pasando (3/3)
  
- [ ] **Task 5.2:** Multi-Asset Data Infrastructure
  - Agregar columna `symbol` a `Trade` y `Strategy` tables
  - Modificar `data_loader.py` para multi-símbolo
  - Actualizar `OptimizerWorker` para iterar sobre múltiples pares
  
- [ ] **Task 5.3:** Volatility-Based Risk Budgeting
  - Crear `VolatilityRiskManager` en `src/execution/vol_risk.py`
  - Calcular volatilidad anualizada de cada activo
  - Ajustar tamaño de posición por volatilidad (risk parity)
  
- [ ] **Task 5.4:** MSC Coordinator & Regime Detection
  - Crear `src/msc/coordinator.py`
  - Implementar detección de régimen (ADX, ATR)
  - Mapear agentes a regímenes (skill levels)
  - Selección dinámica de agente según mercado
  
- [ ] **Task 5.5:** Portfolio Construction & Rebalancing
  - Crear `src/portfolio/constructor.py`
  - Implementar rebalanceo semanal
  - Dashboard para visualizar correlaciones

---

## 🔑 Componentes Clave

### 1. TJRStrategy (`src/strategy/engine.py`)
**Lógica:** Price Action basada en Order Blocks (OB).
```python
class TJRStrategy:
    def analyze(market: MarketState, timeframe: Timeframe) -> TradeSignal:
        # 1. Detecta OB usando detect_ob()
        # 2. Calcula SL = fixed_stop_loss
        # 3. Calcula TP = entry + (SL_distance * take_profit_multiplier)
        # 4. Retorna TradeSignal con entry, SL, TP
```

### 2. OptimizerWorker (`src/agents/worker.py`)
**Función:** Ejecuta backtests individuales.
```python
def run(config):
    # 1. Carga candles (BTCUSDT-4h-2024-XX.csv)
    # 2. Calcula features (RSI, MACD, etc.)
    # 3. Itera tick-by-tick
    # 4. TJRStrategy.analyze() -> señal
    # 5. ML Filter: Si prob < threshold -> skip
    # 6. Ejecuta trade con InMemoryBroker
    # 7. Guarda trades en DB (batch de 50)
```

### 3. ValidatorAgent (`src/agents/validator.py`)
**Función:** Walk-Forward + Correlation Check.
```python
def run(config):
    # 1. Fetch estrategias en status TESTING
    # 2. Para cada estrategia:
    #    - Ejecutar en múltiples periodos OOS
    #    - Si PF > 1.3 y WR > 40% en TODOS -> candidata
    # 3. Correlation Check (NEW):
    #    - Comparar trades con estrategias aprobadas
    #    - Si corr > 0.3 con alguna -> RECHAZAR
    # 4. Si pasa todo -> APROBAR
```

### 4. Correlation Module (`src/portfolio/correlation.py`) 🆕
**Función:** Calcular correlación de Pearson entre equity curves.
```python
def calculate_correlation(trades_a, trades_b) -> float:
    # 1. Convertir trades a equity curves diarias
    # 2. Alinear timestamps (outer join + ffill)
    # 3. Pearson correlation
    # 4. Return [-1, 1]
```

### 5. Database Schema (`src/database/models.py`)
**Tablas:**
- `trades`: 1404 registros (timestamp, pair, side, entry_price, exit_price, SL, TP, result, profit_loss, market_state JSONB)
- `strategies`: 15 aprobadas (name, parameters JSONB, profit_factor, win_rate, status)
- `patterns`: Patrones ML detectados
- `backtest_runs`: Metadata de ejecuciones

---

## 🧪 Testing

### Tests Existentes
```bash
tests/
├── portfolio/
│   └── test_correlation.py  # 3 tests (✅ passing)
└── (otros tests legacy)
```

### Ejecutar Tests
```bash
python3 -m pytest tests/portfolio/test_correlation.py
# Output: 3 passed, 4 warnings
```

---

## 🚀 Cómo Ejecutar el Sistema

### 1. Iniciar Base de Datos
```bash
docker-compose up -d
```

### 2. Ejecutar Dashboard
```bash
./run_system.sh
# O manualmente:
python3 -m uvicorn src.api.main:app --reload
```

### 3. Acceder
- Dashboard: http://localhost:8000
- API Docs: http://localhost:8000/docs

### 4. Ejecutar Pipeline
1. Click en "Run AI Pipeline"
2. El sistema:
   - Descarga datos (si faltan)
   - Entrena modelo ML
   - Ejecuta backtests paralelos
   - Valida estrategias (ahora con correlation check)
   - Aprueba solo las que pasen WFA + Correlation

---

## 📈 Resultados Actuales

### Estrategias Aprobadas (Top 3)
| Estrategia | SL | TP Mult | PF (Train) | PF (Mayo) | PF (Jun) | PF (Jul) | Estado |
|------------|-----|---------|------------|-----------|----------|----------|--------|
| `TJR_Base_mut_58f9db` | 1896 | 2.17 | 1.52 | 4.00 ✅ | 0.00 ❌ | 0.82 ❌ | Rechazada |
| `TJR_Base_mut_600c4a` | 1850 | 2.10 | 1.52 | 1.02 | N/A | N/A | Rechazada |
| `TJR_Base_mut_0a1ab5` | 1920 | 2.05 | 1.50 | 1.00 | N/A | N/A | Rechazada |

**Conclusión:** Ninguna estrategia sobrevivió 3 meses consecutivos OOS.

---

## 🎯 Próximos Pasos (Roadmap)

### Inmediato (Esta Semana)
1. **Task 5.2:** Multi-Asset Infrastructure
   - Agregar soporte para ETHUSDT, SOLUSDT
   - Modificar DB schema (migration)
   
2. **Task 5.3:** Volatility Risk Budgeting
   - Implementar `VolatilityRiskManager`
   - Normalizar riesgo por activo

### Corto Plazo (2 Semanas)
3. **Task 5.4:** MSC Coordinator
   - Detección de régimen de mercado
   - Asignación dinámica de agentes

4. **Task 5.5:** Portfolio Construction
   - Dashboard de correlaciones
   - Rebalanceo automático

### Mediano Plazo (1 Mes)
5. **Paper Trading:** 30 días mínimo antes de live
6. **Live Deployment:** Solo si PF > 1.5 en paper

---

## 🐛 Issues Conocidos

1. **Pandas FutureWarning:** `fillna(method='ffill')` deprecated
   - Fix: Cambiar a `ffill()` en `correlation.py`
   
2. **SQLAlchemy Warning:** `declarative_base()` deprecated
   - Fix: Migrar a `sqlalchemy.orm.declarative_base()`

3. **Overfitting:** Sistema actual no tiene Pure Alpha
   - Fix: Implementar Tasks 5.2-5.5

---

## 📚 Documentación Adicional

- **Plan de Implementación:** `docs/plans/2026-01-23-pure-alpha-msc-implementation.md`
- **Strategy Analysis:** `.gemini/antigravity/brain/.../strategy_analysis_report.md`
- **CLAUDE.md:** Reglas de desarrollo (TDD, Skills)

---

## 🔗 Referencias

- **Bridgewater Pure Alpha:** Filosofía de correlación < 0.3
- **Dalio's Holy Grail:** 15-20 flujos no correlacionados
- **MSC (Módulo de Sustitución Cognitiva):** Tu framework de agentes especializados
