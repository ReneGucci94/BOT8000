# BOT8000 V3: ML-Enhanced Trading System

Sistema de trading avanzado que utiliza Machine Learning para optimizar, filtrar y validar estrategias de trading automáticamente.

## Arquitectura

El sistema se compone de una orquestación de Agentes Autónomos:

1. **DataAgent**: Descarga datos históricos de Binance.
2. **OptimizerSwarm (Training)**: Ejecuta backtests masivos paralelos para generar datos de comportamiento.
3. **PatternAnalyzer (ML)**: Entrena modelos Random Forest para predecir probabilidades de éxito de trades.
4. **PatternDetective**: Extrae reglas explícitas de condiciones de mercado adversas.
5. **StrategyMutator**: Evoluciona estrategias base aplicando filtros (ML y Reglas).
6. **ValidatorAgent**: Valida estrategias mutadas en periodos de tiempo no vistos (Out-of-Sample) usando filtrado ML predictivo.

## Stack Tecnológico

- **Backend**: Python 3.9+, FastAPI, SQLAlchemy, PostgreSQL.
- **ML**: Scikit-learn, Pandas, Numpy.
- **Frontend**: HTML5, TailwindCSS, Chart.js.
- **Data**: CSV (Flat files) + PostgreSQL (Metadata & Trades).

## Instalación

1. **Requisitos Previos**:
   - Python 3.9 o superior
   - PostgreSQL corriendo (ver `docker-compose.yml`)

2. **Configurar Entorno**:
   ```bash
   # Iniciar base de datos
   docker-compose up -d

   # Instalar dependencias
   pip install -r requirements.txt
   # O manualmente:
   pip install fastapi uvicorn sqlalchemy psycopg2-binary pandas numpy scikit-learn
   ```

3. **Ejecutar**:
   ```bash
   ./run_system.sh
   # O manualmente:
   uvicorn src.api.main:app --reload
   ```

4. **Acceso**:
   - Dashboard: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Uso del Dashboard

1. Ir al Dashboard.
2. Hacer click en "Run AI Pipeline".
3. El sistema comenzará a:
   - Descargar datos (si faltan).
   - Entrenar modelo ML con datos de 2024 (Ene-Sep).
   - Buscar patrones de fallo.
   - Crear estrategias derivadas.
   - Validarlas en 2024 (Oct-Dic).
4. Ver resultados en la tabla de "Approved Strategies".

## Tests

```bash
python3 -m pytest tests/
```
