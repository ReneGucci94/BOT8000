# Phase 6: Historical Backtesting Plan

> **Para Claude:** SUB-SKILL REQUERIDA: superheroes:executing-plans y Data Analysis.

**Meta:** Validar el sistema completo usando datos reales de Binance (`BTCUSDT-5m-2024-12.csv`) para medir el rendimiento real de la estrategia TJR.

---

### Tarea 1: Data Loader (CSV Parser)

**Objetivo:** Crear un componente que lea el CSV de Binance y lo convierta en objetos `Candle`.

**Archivos:**
- `src/utils/data_loader.py`
- `tests/utils/test_data_loader.py`

**Pasos TDD:**
1.  **Test:** Leer una línea de string simulada del CSV y verificar que el `Candle` resultante tiene los precios correctos (usando `Decimal`).
2.  **Implementación:** Función `load_binance_csv(file_path) -> List[Candle]`.

---

### Tarea 2: Backtest Engine

**Objetivo:** Adaptar el loop de simulación de la Fase 5 para que use los datos del CSV y reporte métricas detalladas.

**Archivos:**
- `src/simulation/backtest.py`
- `tests/simulation/test_real_backtest.py`

**Métricas a incluir:**
- Total Trades
- Win Rate (%)
- Gross Profit / Loss
- Net Profit / Real PnL
- Max Drawdown
- Profit Factor

---

### Tarea 3: Ejecución y Reporte

**Objetivo:** Correr el backtest completo sobre el mes de Diciembre 2024 (8000+ velas) y generar un reporte final.

**Pasos:**
1.  Ejecutar el script de backtest.
2.  Analizar resultados.
3.  Optimizar parámetros (opcional) si el drawdown es excesivo.
