<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12+-blue?logo=python&logoColor=white" alt="Python 3.12+">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="MIT License">
  <img src="https://img.shields.io/badge/PostgreSQL-15+-336791?logo=postgresql&logoColor=white" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/XGBoost-ML-orange?logo=xgboost" alt="XGBoost ML">
</p>

<h1 align="center">🤖 BOT8000</h1>

<p align="center">
  <strong>Multi-Agent Algorithmic Trading System with Cognitive Substitution</strong>
</p>

<p align="center">
  A production-grade trading framework that combines <em>Price Action</em>, <em>Machine Learning</em>, and <em>Genetic Algorithms</em> — orchestrated by an intelligent <strong>MSC (Módulo de Sustitución Cognitiva)</strong> that adapts to market regimes in real-time.
</p>

---

## 🎯 Core Philosophy

> *"The key is not finding the best strategy, but finding 15-20 uncorrelated return streams."*
> — Ray Dalio, Bridgewater Associates

BOT8000 implements the **Pure Alpha** philosophy: instead of searching for a single "holy grail" strategy, the system cultivates a portfolio of **specialized agents** that excel in different market conditions. The MSC Orchestrator acts as a meta-brain, routing decisions to the right specialist at the right time.

---

## 🧠 Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          MSC ORCHESTRATOR (Layer 1)                         │
│            Market Regime Classifier → Agent Selection → Audit Tags          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │ TrendHunter │  │MeanReversion│  │  Volatility │  │   BreakoutHunter    │ │
│  │   Agent     │  │    Agent    │  │FilterAgent  │  │       Agent         │ │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘ │
│         │                │                │                    │            │
│         └────────────────┴────────────────┴────────────────────┘            │
│                                  │                                          │
│                          ┌───────▼───────┐                                  │
│                          │ ALPHA ENGINE  │                                  │
│                          │  (Layer 3)    │                                  │
│                          └───────────────┘                                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
            ┌───────▼───────┐               ┌───────▼───────┐
            │  Risk Manager │               │ Trade Executor│
            │ (Position Size)│               │  (Simulation) │
            └───────────────┘               └───────────────┘
```

### Layer Breakdown

| Layer | Component | Responsibility |
|-------|-----------|----------------|
| **Layer 1** | MSC Orchestrator | Regime detection (ADX, ATR, EMA Alignment) → Agent selection |
| **Layer 2** | Specialized Agents | Each agent has unique Alpha weights for its market niche |
| **Layer 3** | Alpha Engine | 5 independent signal generators combined via weighted average |

---

## 🔧 Features

### Multi-Agent System
- **5 Specialized Trading Agents** with distinct "personalities"
  - `TrendHunterAgent` → Momentum-heavy for directional markets
  - `MeanReversionAgent` → Contrarian for ranging markets
  - `VolatilityFilterAgent` → Expansion plays during high volatility
  - `BreakoutHunterAgent` → Microstructure focus for breakouts
  - `SentimentScoutAgent` → Balanced baseline for news-driven events

### Alpha Engine (Pure Alpha)
- **5 Independent Alpha Generators:**
  - `MomentumAlpha` — Trend strength scoring
  - `OBQualityAlpha` — Order Block quality assessment
  - `VolatilityAlpha` — ATR-based regime detection
  - `LiquidityAlpha` — Volume imbalance signals
  - `MLConfidenceAlpha` — XGBoost probability filter

### Genetic Optimization
- **Strategy Mutator** evolves parameters (SL, TP ratios) across generations
- **Optimizer Swarm** distributes backtests across Celery workers
- **Validator Agent** applies Walk-Forward validation (PF > 1.3, WR > 40%, DD < 20%)

### Risk Management
- **Volatility-based position sizing** (Risk per trade tied to ATR, not fixed %)
- **Correlation filtering** (new strategies must have ρ < 0.3 with existing portfolio)
- **Realistic simulation** with 0.1% fees per leg

---

## 📁 Project Structure

```
BOT8000/
├── src/
│   ├── agents/             # Trading agents & orchestrator
│   │   ├── orchestrator.py     # MSC Coordinator (Layer 1)
│   │   ├── trend_hunter.py     # Specialized agent
│   │   ├── mean_reversion.py
│   │   ├── volatility_filter.py
│   │   ├── breakout_hunter.py
│   │   ├── sentiment_scout.py
│   │   ├── worker.py           # Optimizer backtest worker
│   │   └── validator.py        # Walk-forward validator
│   │
│   ├── alphas/             # Pure Alpha signal generators
│   │   ├── combiner.py         # Weighted aggregation
│   │   ├── momentum.py
│   │   ├── ob_quality.py
│   │   ├── volatility.py
│   │   ├── liquidity.py
│   │   └── ml_confidence.py
│   │
│   ├── core/               # Domain models
│   │   ├── candle.py           # OHLCV wrapper (Decimal precision)
│   │   ├── market.py           # MarketState with indicators
│   │   ├── regime.py           # MarketRegime enum
│   │   └── classifier.py       # Regime classification logic
│   │
│   ├── strategy/           # TJR Price Action engine
│   │   ├── engine.py           # Main strategy logic
│   │   └── ob.py               # Order Block detection
│   │
│   ├── simulation/         # Paper trading
│   │   └── broker.py           # InMemoryBroker with fees
│   │
│   ├── execution/          # Trade management
│   │   ├── executor.py         # TradeSignal execution
│   │   └── risk.py             # Position sizing
│   │
│   ├── ml/                 # Machine Learning
│   │   ├── features.py         # 20+ technical features
│   │   └── analyzer.py         # XGBoost pattern classifier
│   │
│   ├── database/           # Persistence
│   │   └── repositories/       # SQLAlchemy repositories
│   │
│   └── api/                # Dashboard
│       └── main.py             # FastAPI endpoints
│
├── tests/                  # Comprehensive test suite
├── scripts/                # Utility scripts (OOS validation, analysis)
├── data/                   # Binance historical CSVs
└── docs/                   # Implementation plans
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- PostgreSQL 15+
- Docker (optional, for containerized setup)

### Installation

```bash
# Clone repository
git clone https://github.com/feux/BOT8000.git
cd BOT8000

# Create virtual environment
python3.12 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e ".[dev]"

# Set up database
docker-compose up -d postgres
python scripts/init_db.py
```

### Running Tests

```bash
# Full test suite with coverage
python -m pytest tests/ -v --cov=src

# Specific test modules
python -m pytest tests/agents/test_orchestrator.py -v
python -m pytest tests/alphas/ -v
```

### Launch Dashboard

```bash
# Start API server
uvicorn src.api.main:app --reload

# Access at http://localhost:8000
```

---

## 📊 Backtesting

```bash
# Run optimization pipeline
python -m src.orchestration.main --config optimizer_config.yaml

# Out-of-Sample validation
python scripts/run_oos_validation.py

# Generate top strategies report
python scripts/analyze_top_3.py
```

---

## 🔬 How the MSC Works

The **Módulo de Sustitución Cognitiva** (Cognitive Substitution Module) is the brain of BOT8000. Instead of relying on a single strategy, it:

1. **Classifies the Market Regime** using technical indicators:
   - ADX > 25 + EMA Alignment → `TRENDING`
   - ATR > 1.5× Average → `HIGH_VOLATILITY`
   - ATR < 0.7× Average + ADX < 25 → `BREAKOUT_PENDING`
   - Default → `SIDEWAYS_RANGE`

2. **Selects the Specialist Agent** that excels in that regime

3. **Injects Audit Metadata** into every trade for transparency:
   ```python
   signal.metadata = {
       'agent': 'TrendHunterAgent',
       'regime': 'TRENDING_BULLISH',
       'timestamp': 1706000000
   }
   ```

This approach ensures the system **adapts** to changing conditions rather than overfitting to a single market environment.

---

## 📈 Performance Philosophy

This system prioritizes **robustness over raw returns**:

- Walk-Forward validation ensures strategies generalize
- Multi-month Out-of-Sample testing catches overfitting
- Correlation filtering maintains portfolio diversification
- Every strategy must prove it can perform across **different regimes**

> **Note:** Past performance ≠ future results. This is a research & educational project.

---

## 🛠️ Configuration

```yaml
# optimizer_config.yaml
optimizer:
  population_size: 20
  generations: 10
  mutation_rate: 0.15

validation:
  min_profit_factor: 1.3
  min_win_rate: 0.40
  max_drawdown: 0.20

risk:
  base_risk_pct: 0.01
  max_correlation: 0.3
```

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [MSC Orchestrator Plan](docs/plans/2026-01-26-msc-orchestrator-implementation.md) | Layer 1 implementation details |
| [Trading Agents Plan](docs/plans/2026-01-25-trading-agents-implementation.md) | Layer 2 agent architecture |
| [Alpha Engine Docs](docs/alphas/) | Individual alpha generator specs |

---

## 🧪 Testing Coverage

```
Module                     Coverage
───────────────────────────────────
src/agents/                    92%
src/alphas/                    95%
src/core/                      88%
src/simulation/                91%
src/execution/                 87%
───────────────────────────────────
TOTAL                          90%
```

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Write tests for new functionality
4. Ensure all tests pass (`python -m pytest`)
5. Submit a Pull Request

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Feux**

- GitHub: [@feux](https://github.com/feux)
- Website: [feux.mx](https://feux.mx)
## 🎬 Demo Video

[![BOT8000 Demo](https://youtu.be/w8o_ZQy0rD4)

*30-second overview of the multi-agent architecture*
---

<p align="center">
  <em>Built with 🧠 and a lot of caffeine in Hermosillo, Mexico</em>
</p>
