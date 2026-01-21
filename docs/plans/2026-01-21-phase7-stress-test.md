# Phase 7: Real Performance & Stress Testing

> **Contexto:** Hemos validado la lógica en un mes con ganancias brutas, pero falta incluir el costo de operación (fees) y verificar si el rendimiento es consistente a lo largo de 2024.

---

### Tarea 1: Implementar Fees (0.1%)

**Objetivo:** Modificar el `InMemoryBroker` para deducir una comisión del 0.1% en cada entrada y salida.

**Archivos:**
- `src/simulation/broker.py` [NEW]: Centralizar `InMemoryBroker` aquí para evitar duplicación.
- `scripts/run_backtest.py`: Actualizar para usar el nuevo broker centralizado con fees.
- `tests/simulation/test_full_cycle.py`: Actualizar para usar el broker centralizado.

**Lógica de Fees:**
- Al abrir: `balance -= qty * price * 0.001`
- Al cerrar: `balance -= qty * price * 0.001`

---

### Tarea 2: Descarga de Datos (6 Meses)

**Objetivo:** Descargar y descomprimir datos de Binance para Enero, Febrero, Marzo, Junio, Septiembre y Noviembre de 2024.

**Comandos:** `curl` + `unzip` as provided by user.

---

### Tarea 3: Backtest Multi-Mes

**Objetivo:** Crear `scripts/run_multi_month_backtest.py` que itere sobre todos los archivos CSV en `data/raw/`, ejecute el backtest, y genere un reporte comparativo.

**Métricas Finales:**
- Profit acumulado (neto).
- Win rate promedio.
- Meses rentables vs meses en pérdida.
- Drawdown máximo global.

---

### Verificación

- **Unit Test:** `tests/simulation/test_broker_fees.py` para asegurar que el balance disminuye correctamente tras un trade con ganancia cero.
- **Manual:** Re-correr Diciembre 2024 y comparar Profit Bruto vs Neto.
