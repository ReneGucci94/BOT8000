# Sistema de Trading Modular Multi-Agente (MSC v3) - Arquitectura Técnica

## 1. Visión General del Sistema

El BOT8000 v3 implementa una arquitectura **Multi-Agent / Strategy / Classifier (MSC)** diseñada para adaptarse dinámicamente a las condiciones cambiantes del mercado. A diferencia de los sistemas monolíticos tradicionales que utilizan un conjunto fijo de parámetros, MSC v3 emplea un enfoque jerárquico donde un clasificador de régimen de mercado informa a un orquestador, el cual selecciona y pondera dinámicamente las señales de múltiples agentes especializados.

### Principios de Diseño

* **Modularidad:** Cada componente (indicador, estrategia, agente) es independiente y testeable de forma aislada.
* **Adaptabilidad:** El sistema ajusta su comportamiento basándose en la volatilidad y la tendencia del mercado (Régimen).
* **Robustez:** Validación estricta de tipos de datos (`Decimal` para precios) y manejo de errores en tiempo de ejecución.
* **Trazabilidad:** Registro granular de cada decisión en base de datos PostgreSQL.

---

## 2. Diagrama de Componentes y Flujo de Datos

El siguiente diagrama ilustra el flujo de procesamiento desde la ingestión de datos crudos hasta la generación de la señal final de trading.

```ascii
+-------------------+       +-------------------+       +-------------------+
|   Data Sources    |       |   Feature Eng.    |       |   Market State    |
| (Binance REST API)| ----> | (Pandas/TA-Lib)   | ----> | (Series Manager)  |
+-------------------+       +-------------------+       +-------------------+
          |                           |                           |
          v                           v                           v
+---------------------------------------------------------------------------+
|                           CORE PROCESSING LAYER                           |
+---------------------------------------------------------------------------+
          |
          v
+-------------------+       +-------------------+
| regime_classifier | ----> |   Orchestrator    | <---- (Config & State)
| (Trend/Volatility)|       |   (Brain / v3)    |
+-------------------+       +-------------------+
                                      |
                                      v
                    +-----------------------------------+
                    |         Sub-Agent Selection       |
                    | (Bullish / Bearish / Neutral / Vol) |
                    +-----------------------------------+
                                      |
              +-----------------------+-----------------------+
              |                       |                       |
      +---------------+       +---------------+       +---------------+
      |  Alpha Engine |       |  Risk Engine  |       |  Exec Engine  |
      | (Signal Gen)  |       | (Sizing/SL)   |       | (Order Mgmt)  |
      +---------------+       +---------------+       +---------------+
              |                       |                       |
              v                       v                       v
      +---------------------------------------------------------------+
      |                     FINAL SIGNAL / ORDER                      |
      +---------------------------------------------------------------+
              |
              v
      +-------------------+
      |   Persistence     |
      |   (PostgreSQL)    |
      +-------------------+
```

---

## 3. Descripción Detallada de Componentes

### 3.1. Ingestión y Procesamiento de Datos (Data Layer)

El sistema comienza con la ingestión de datos de mercado (velas OHLCV).

* **Clase `Candle`:** Estructura de datos inmutable que garantiza la integridad de los precios (Open, High, Low, Close) y Volumen. Utiliza `decimal.Decimal` para precisión financiera.
* **Librería `ta` Wrapper:** Se implementó una capa de compatibilidad en `src/core/market.py` para interactuar con la librería `ta`. Esta capa convierte series de `Decimal` a `float` estrictamente para los cálculos matemáticos de indicadores (RSI, ATR, ADX, EMA), retornando los resultados al formato nativo del sistema.

### 3.2. Clasificador de Régimen (Classifier)

El corazón de la adaptabilidad del sistema.

* **Función:** Analiza la estructura del mercado para determinar el estado actual.
* **Entradas:** ADX (fuerza de tendencia), EMA (dirección macro), Volatilidad Reciente.
* **Salidas (Regímenes):**
    1. **BULL_TREND:** Tendencia alcista fuerte (EMA rápida > EMA lenta, ADX > 25).
    2. **BEAR_TREND:** Tendencia bajista fuerte.
    3. **SIDEWAYS_STABLE:** Mercado lateral con baja volatilidad.
    4. **SIDEWAYS_VOLATILE:** Mercado lateral con alta volatilidad (peligro de "whipsaw").

### 3.3. El Orquestador (Orchestrator)

Actúa como el cerebro central.

* **Responsabilidad:** Basado en el régimen detectado por el Classifier, el Orchestrator activa y asigna pesos a los sub-agentes apropiados.
* **Ejemplo de Lógica:**
  * Si Régimen == `BULL_TREND`: Activa `TrendFollowingAgent` con peso 0.8 y `MeanReversionAgent` con peso 0.2 (para comprar dips).
  * Si Régimen == `SIDEWAYS_VOLATILE`: Reduce exposición global o activa `ShortVolatilityAgent`.

### 3.4. Agentes y Generación de Señales (Alpha Layer)

Los agentes son contenedores de lógica de estrategia pura.

* **Alpha Engine:** Un motor unificado que encapsula señales técnicas.
* **Estrategias implementadas:**
  * *RSI Reversal:* Cruces de niveles 30/70.
  * *Bollinger Breakout:* Ruptura de bandas con confirmación de volumen.
  * *MACD Crossover:* Confirmación de momentum.
* **Consenso:** El Orchestrator agrega las señales ponderadas. Si el "Score" final supera un umbral definido (e.g., 0.65), se emite una señal de entrada.

### 3.5. Gestión de Riesgo y Ejecución

Componente crítico desacoplado de la generación de señal.

* **Position Sizing:** Modelo de riesgo fijo fraccional (Fixed Fractional). Por defecto 1% del capital por operación.
* **Stop Loss Dinámico:** Calculado basado en ATR (Average True Range).
  * *Fórmula Standard:* `Entry Price - (2.0 * ATR(14))` para largos.
* **Filtros de Ejecución:** Evita operar durante ventanas de tiempo de "no-trade" (e.g., cierres de mercado, alta volatilidad de noticias si se conecta a un calendario económico).

---

## 4. Stack Tecnológico y Dependencias

El sistema está construido sobre un stack moderno y robusto de Python, priorizando la seguridad de tipos y la velocidad de ejecución.

### Core

* **Python:** 3.9+
* **OS:** Compatible con Linux (Ubuntu/Debian) y macOS.

### Librerías de Análisis y Datos

| Librería | Versión | Propósito |
| :--- | :--- | :--- |
| **pandas** | >= 2.0.0 | Manipulación eficiente de series de tiempo y DataFrames para el motor de backtesting vectorizado. |
| **ta** | >= 0.10.0 | Biblioteca estándar industrial para análisis técnico. Wrapper personalizado para compatibilidad con Decimal. |
| **numpy** | >= 1.24.0 | Operaciones numéricas de bajo nivel optimizadas. |
| **scikit-learn** | (Opcional) | Utilizado en módulos experimentales de ML del clasificador. |

### Infraestructura y Persistencia

| Componente | Tecnología | Descripción |
| :--- | :--- | :--- |
| **Base de Datos** | PostgreSQL 14+ | Almacenamiento relacional robusto para logs de operaciones, historial de órdenes y métricas de rendimiento. |
| **Driver BD** | psycopg2-binary | Conector de alto rendimiento para PostgreSQL. |
| **ORM** | SQLAlchemy | Abstracción de base de datos para consultas seguras y mantenibles. |
| **Containerización** | Docker | (Planeado) Empaquetado de la aplicación para despliegue consistente. |

### Testing y Calidad

* **pytest:** Framework de testing para unidades y pruebas de integración.
* **mypy:** Verificación estática de tipos para prevenir errores de tipo en tiempo de desarrollo.
* **black/flake8:** Formateo y linting de código.

---

## 5. Decisiones de Diseño Clave

### 5.1. Precisión Flotante vs. Decimal

Una de las decisiones arquitectónicas más importantes fue el manejo de la precisión numérica.

* **Problema:** Los números de punto flotante (`float`) introducen errores de redondeo que pueden acumularse en sistemas financieros.
* **Solución:** Se utiliza `decimal.Decimal` para todos los cálculos monetarios (precios, balances, PnL).
* **Adaptación:** Dado que las librerías de data science (`numpy`, `ta`, `pandas`) están optimizadas para `float`, se implementó un sistema de "casting justo a tiempo" (JIT casting) en los bordes del sistema. Los datos se convierten a `float` solo para el cálculo de indicadores técnicos inmutables (RSI, ATR) y se descartan inmediatamente, manteniendo la lógica de negocio puramente en `Decimal`.

### 5.2. Arquitectura Orientada a Eventos (Simulation)

El motor de backtest (`OptimizerWorker`) simula un bucle de eventos vela a vela.

* Esto evita el "mirar hacia adelante" (look-ahead bias) común en backtests puramente vectorizados.
* Permite simular latencia y deslizamiento (slippage) de manera más realista.
* Facilita la transición a "Live Trading", ya que el bucle de eventos es idéntico: solo cambia la fuente del evento (WebSocket en vivo vs. Iterador de lista histórica).

### 5.3. Aislamiento de Estrategias (Orchestrator Pattern)

En lugar de codificar reglas complejas `if/else` en un solo script, se delegó la lógica a clases `Agent`.

* Esto permite desarrollar y optimizar el `TrendFollowingAgent` sin riesgo de romper el `MeanReversionAgent`.
* El Orchestrator actúa como un "meta-algoritmo" que decide a quién escuchar. Esta separación de intereses es fundamental para el mantenimiento a largo plazo.

---

## 6. Flujos de Trabajo (Workflows)

### 6.1. Flujo de Entrenamiento (Optimization)

1. **Selección de Datos:** Se cargan datos históricos (e.g., 2024).
2. **Extracción de Features:** Se calculan indicadores técnicos.
3. **Simulación:** El `OptimizerWorker` itera sobre los datos.
4. **Registro:** Cada operación se guarda en DB.
5. **Evaluación:** Se calcula Profit Factor, Sharpe Ratio, Max Drawdown.

### 6.2. Flujo de Validación Walk-Forward

Para evitar el sobreajuste (overfitting):

1. Se define una ventana de entrenamiento (e.g., 3 meses) y una de prueba (e.g., 1 mes).
2. El sistema "rueda" (rolls) estas ventanas a través del tiempo.
3. Se agregan los resultados de las ventanas de prueba (Out-of-Sample) para obtener una métrica de rendimiento realista.

---

## 7. Escalabilidad y Futuro

La arquitectura actual soporta escalado vertical (más pares en una máquina potente). Para escalado horizontal:

* Se planea desacoplar el `OptimizerWorker` en microservicios independientes que consuman tareas de una cola (e.g., RabbitMQ/Redis).
* El Orchestrator podría evolucionar hacia un modelo de Reinforcement Learning (RL) para ajustar los pesos de los agentes de forma autónoma.
