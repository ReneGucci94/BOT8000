# Phase 9: Timeframe Optimization (15m)

> **Contexto:** Hemos visto que 5m es muy ruidoso y costoso en fees, mientras que 1H es demasiado estricto. El timeframe de 15m podría ser el "punto dulce".

---

### Tarea 1: Descarga y Preparación de Datos

**Objetivo:** Asegurar que los datos de 15m para 2024 estén listos en `data/raw/`.
- [x] Descargados: Jan, Feb, Mar, Jun, Sep, Nov, Dec 2024.

---

### Tarea 2: Actualización de Scripts de Backtest

**Objetivo:** Adaptar los scripts existentes para soportar el análisis de 15m.

#### [MODIFY] [run_backtest.py](file:///Users/feux/Desktop/BOT8000/scripts/run_backtest.py)
- Cambiar el path por defecto a un archivo de 15m.
- Asegurar que pase `Timeframe.M15` al cargador y a la estrategia.

#### [MODIFY] [run_multi_month_backtest.py](file:///Users/feux/Desktop/BOT8000/scripts/run_multi_month_backtest.py)
- Agregar una función `run_month_backtest_m15`.
- Cambiar el `glob` para buscar archivos `*-15m-*.csv`.
- Actualizar la lógica de reporte para incluir comparativas si es posible.

---

### Tarea 3: Ejecución y Reporte Comparativo

**Objetivo:** Correr el backtest multi-mes y documentar los resultados en `walkthrough.md`.

**Métricas a comparar:**
- **Trades Totales:** (5m: ~850 | 1H: 0 | 15m: ?)
- **Profit Neto:** (Considerando 0.1% fees)
- **Win Rate:**
- **Max Drawdown:**

---

### Verificación

#### Automated Tests
- Ejecutar `python3 scripts/run_multi_month_backtest.py` después de los cambios.
- Verificar que las transacciones se ejecuten (Total Trades > 0).

#### Manual Verification
- Revisar la tabla de resultados en consola.
- Comparar manualmente los fees pagados en 15m vs 5m.
