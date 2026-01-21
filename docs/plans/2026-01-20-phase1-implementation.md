# Phase 1: Foundation Implementation Plan

> **Para Claude:** SUB-SKILL REQUERIDA: Usar superpowers:executing-plans para implementar este plan tarea por tarea.

**Meta:** Establecer el entorno de desarrollo con linting estricto e implementar los modelos de dominio core (inmutables y tipeados) con TDD.

**Arquitectura:** Domain-Driven Design (Core inmutable), Functional patterns.

**Tech Stack:** Python 3.12+, pytest, mypy (strict), ruff.

---

### Tarea 1: Environment Setup & Linting

**Archivos:**
- Crear: `pyproject.toml`
- Crear: `pytest.ini`
- Crear: `mypy.ini` (o config en pyproject.toml)

**Paso 1: Configuración de Proyecto**
Crear `pyproject.toml` con dependencias: `pytest`, `mypy`, `ruff`.

**Paso 2: Configuración Strict Mypy**
Configurar `mypy` para prohibir `Any`, exigir tipos explícitos, etc.

**Paso 3: Verificar Setup**
Correr `mypy` y `pytest` en un archivo dummy para asegurar que el entorno detecta errores.

**Paso 4: Commit**
`git add . && git commit -m "chore: setup project environment and strict linting"`

---

### Tarea 2: Core Primitives & Timeframe

**Archivos:**
- Crear: `src/core/types.py`
- Crear: `src/core/timeframe.py`
- Test: `tests/core/test_timeframe.py`

**Paso 1: Test que falla (Timeframe)**
Testear que `Timeframe` es un Enum y tiene los valores correctos (M5, M15, H1, H4). Testear conversión desde string si aplica.

**Paso 2: Implementación**
Definir constantes en `types.py` (Price = Decimal) y Enum en `timeframe.py`.

**Paso 3: Verificar**
Correr tests.

**Paso 4: Commit**
`git add . && git commit -m "feat: add core types and timeframe enum"`

---

### Tarea 3: Immutable Candle

**Archivos:**
- Crear: `src/core/candle.py`
- Test: `tests/core/test_candle.py`

**Paso 1: Test que falla (Validación)**
Intentar crear una vela inválida (High < Low) y esperar `ValueError`.
Intentar crear una vela válida y verificar atributos.

**Paso 2: Implementación**
`@dataclass(frozen=True)` con `__post_init__` para validaciones.

**Paso 3: Verificar**
Correr tests.

**Paso 4: Commit**
`git add . && git commit -m "feat: implement immutable Candle model"`

---

### Tarea 4: MarketSeries (Functional Collection)

**Archivos:**
- Crear: `src/core/series.py`
- Test: `tests/core/test_series.py`

**Paso 1: Test que falla (Inmutabilidad)**
Crear series, agregar vela, verificar que la nueva serie es un objeto distinto y la vieja sigue igual.

**Paso 2: Implementación**
Clase `MarketSeries` que retorna nuevas instancias en modificaciones.

**Paso 3: Verificar**
Correr tests.

**Paso 4: Commit**
`git add . && git commit -m "feat: implement immutable MarketSeries"`

---

### Tarea 5: MultiTimeframe Verification Script

**Archivos:**
- Crear: `tests/integration/test_architecture.py`

**Paso 1: Script de verificación**
Un test que importe todo lo creado, instancie estructuras y verifique que los tipos funcionan juntos correctamente.

**Paso 2: Ejecutar**
Correr suite completa.

**Paso 3: Commit**
`git commit -m "verify: phase 1 architecture integration"`
