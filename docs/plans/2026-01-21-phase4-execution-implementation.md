# Phase 4: Execution Engine Implementation Plan

> **Para Claude:** SUB-SKILL REQUERIDA: superheroes:executing-plans y Hexagonal Architecture.

**Meta:** Implementar la capa de ejecución que traduce señales de estrategia en órdenes gestionadas con riesgo calculado, desacoplando la lógica de trading del broker específico.

**Ubicación:** `src/execution/`
**Referencias:** `CLAUDE.md` (Risk Management & Interfaces).

---

### Tarea 1: Protocolo de Broker (Interface)

**Objetivo:** Definir la interfaz abstracta (`Protocol`) que cualquier broker (Paper, Binace, Bybit) debe implementar. Esto permite testear sin red.

**Archivos:**
- `src/execution/broker.py`
- `tests/execution/test_broker_interface.py` (Mock implementation test)

**Contrato (Methods):**
- `get_balance() -> Decimal`
- `place_order(order: OrderRequest) -> OrderResult`
- `get_positions() -> List[Position]`
- `cancel_order(order_id: str) -> bool`

**Pasos TDD:**
1.  **Test:** Definir una clase `MockBroker` que implemente el protocolo. Verificar que types.py se usa correctamente.
2.  **Implementación:** Definir `Broker(Protocol)` y las dataclasses `OrderRequest`, `OrderResult`, `Position`.

---

### Tarea 2: Gestión de Riesgo (RiskCalcs)

**Objetivo:** Calcular el tamaño de posición basado en riesgo porcentual y distancia de Stop Loss.
- **Fórmula:** `Position Size = (Account Balance * Risk %) / (Entry - SL)`

**Archivos:**
- `src/execution/risk.py`
- `tests/execution/test_risk.py`

**Pasos TDD:**
1.  **Test (Calculation):**
    - Balance: 10,000
    - Risk: 1% ($100)
    - Entry: 50,000, SL: 49,000 (Diff 1,000)
    - Result Expected: 0.1 BTC ($5,000 value).
2.  **Test (Min Size):** Verificar que respeta lot size mínimo.
3.  **Implementación:** Clase `RiskManager` que recibe config de riesgo.

---

### Tarea 3: Motor de Ejecución (Executor)

**Objetivo:** Coordinar `Strategy` -> `Risk` -> `Broker`.
- Recibe señal de entrada.
- Consulta balance.
- Calcula tamaño.
- Envía orden al broker.

**Archivos:**
- `src/execution/executor.py`
- `tests/execution/test_executor.py`

**Pasos TDD:**
1.  **Test (Flow):**
    - Setup: MockBroker con 10k balance.
    - Action: `executor.execute_trade(signal)`
    - Assert: MockBroker recibió `place_order` con el tamaño correcto calculado por RiskManager.
2.  **Implementación:** `TradeExecutor` class.

---

### Tarea 4: Verificación Fase 4

**Objetivo:** Verificar flujo completo desde señal simulada hasta "orden colocada" en mock.

**Archivos:**
- `tests/integration/test_execution_flow.py`

**Pasos:**
1.  Instanciar `TradingBot` (o componentes) con `MockBroker`.
2.  Inyectar señal de Compra.
3.  Verificar que `MockBroker.orders` contiene la orden correcta con los parámetros de riesgo aplicados.
