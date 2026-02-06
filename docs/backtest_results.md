# Resultados de Backtesting 2024 - Comparativa de Sistemas

Este documento detalla el rendimiento simulado del sistema BOT8000 a través de sus tres evoluciones principales durante el periodo fiscal 2024. Los datos reflejan pruebas realizadas sobre el par **BTC/USDT** en el marco temporal de **4 horas (4h)**.

## 1. Resumen Ejecutivo (Scorecard)

La siguiente tabla resume las métricas clave de rendimiento para cada configuración del sistema.

| Métrica | Legacy (v1) | Alpha Engine (v2) | MSC Orchestrator (v3) |
| :--- | :---: | :---: | :---: |
| **Profit Factor** | 0.94 | 1.30 | **1.56** |
| **Win Rate** | 42.1% | 48.5% | **53.2%** |
| **Total Trades** | 85 | 112 | 94 |
| **Max Drawdown** | -18.4% | -12.1% | **-8.5%** |
| **Net Profit** | -6.0% | +22.0% | **+45.0%** |
| **Return/DD Ratio** | -0.32 | 1.81 | **5.29** |

> **Nota:** *Los resultados simulan un capital inicial de $10,000 USD con un riesgo fijo del 1% por operación. No incluye comisiones de exchange ni slippage (deslizamiento).*

---

## 2. Análisis Comparativo

### 2.1. Legacy System (v1) - The Baseline

* **Enfoque:** Sistema monolítico basado en cruces simples de medias móviles y reglas estáticas de RSI.
* **Desempeño:** Sub-óptimo (Profit Factor < 1.0).
* **Fallo Principal:** Incapacidad para detectar condiciones de mercado lateral ("chop"). Durante los meses de consolidación de mediados de 2024, el sistema Legacy generó múltiples señales falsas consecutivas, erosionando las ganancias obtenidas en periodos de tendencia.
* **Conclusión:** Las estrategias estáticas fallan cuando cambia el régimen de volatilidad.

### 2.2. Alpha Engine (v2) - The Specialist

* **Enfoque:** Introducción de señales más sofisticadas (Bollinger Breakouts, MACD Momentum) y mejor gestión de entradas.
* **Mejora:** Logró rentabilidad (PF 1.30).
* **Observación:** Aunque rentable, sufrió drawdowns significativos (-12.1%) cuando múltiples señales alcistas fallaron simultáneamente durante "bull traps" (trampas alcistas). La falta de un filtro de régimen global significó que el sistema seguía siendo agresivo en momentos peligrosos.

### 2.3. MSC Orchestrator (v3) - The Adaptive Solution

* **Enfoque:** Implementación de la arquitectura *Multi-Agent / Strategy / Classifier*. El Orchestrator actúa como un filtro inteligente.
* **Factor Diferenciador:**
  * **Adaptabilidad:** En periodos donde el `Classifier` detectó `SIDEWAYS_VOLATILE`, el Orchestrator redujo la ponderación de las estrategias de seguimiento de tendencia y priorizó agentes neutrales o simplemente se abstuvo de operar.
  * **Calidad sobre Cantidad:** Realizó menos operaciones (94) que el Alpha Engine (112), pero con una tasa de acierto ("Win Rate") significativamente mayor (+4.7%). Filtra el ruido.
* **Equity Curve:** La curva de capital muestra un crecimiento mucho más suave ("smooth"). Mientras que v1 y v2 muestran dientes de sierra pronunciados, v3 mantiene una pendiente ascendente más constante, recuperándose rápidamente de las pérdidas pequeñas.

---

## 3. Análisis de Equity Curve (Descripción)

1. **Q1 2024 (Ene-Mar):** Todos los sistemas capturaron la tendencia alcista inicial. MSC y Alpha tuvieron resultados similares, superando ligeramente a Legacy.
2. **Q2 2024 (Abr-Jun):** Periodo de corrección y volatilidad.
    * *Legacy:* Sufrió su mayor caída, perdiendo casi todas las ganancias de Q1.
    * *Alpha:* Se mantuvo plano (break-even), luchando contra señales falsas.
    * *MSC:* Brilló en este periodo. Detectó el cambio de régimen y preservó capital, operando selectivamente en rebotes de corto plazo. Aquí es donde se generó la brecha de rendimiento (Alpha generation).
3. **Q3 2024 (Jul-Sep):** Recuperación del mercado. MSC capitalizó agresivamente las nuevas tendencias confirmadas, acelerando su curva de beneficios.
4. **Q4 2024 (Oct-Dic):** Cierre fuerte. La gestión de riesgos dinámica (Trailing Stops más ajustados en volatilidad alta) permitió maximizar las ganancias finales.

---

## 4. Métricas Clave Explicadas

* **Profit Factor (PF):** La relación entre ganancia bruta y pérdida bruta. Un PF de 1.56 significa que por cada $1 perdido, el sistema gana $1.56. En trading algorítmico, cualquier valor > 1.5 se considera robusto.
* **Max Drawdown:** La mayor caída porcentual desde un pico histórico de capital. Reducir esto del 18% (Legacy) al 8.5% (MSC) es crítico para la viabilidad a largo plazo y la psicología del inversor.
* **Return/DD Ratio:** Medida de eficiencia ajustada al riesgo. Un ratio de 5.29 indica una recompensa excepcional por el riesgo asumido.

## 5. Conclusiones y Siguientes Pasos

El sistema MSC (v3) ha demostrado empíricamente su superioridad sobre las iteraciones anteriores. La capacidad de filtrar operaciones de baja probabilidad basadas en el régimen de mercado es la ventaja competitiva clave.

**Próximo Paso:** La validación *Walk-Forward* (actualmente en curso) determinará si estos resultados son producto de un ajuste a la curva (overfitting) o si el sistema posee una capacidad predictiva genuina fuera de muestra.

---

## 6. Validación Walk-Forward (Out-of-Sample)

> **Actualización (04-Feb-2026):** El proceso de Walk-Forward ha concluido.

Para confirmar la robustez, se ejecutó un test de ventanas rodantes (Rolling Windows):

* **Entrenamiento:** 3 meses.
* **Prueba:** 1 mes (Inmediatamente siguiente).
* **Total Ventanas:** 9

### Resultados por Ventana

| Ventana | Periodo Test | Win Rate | Profit Factor | Resultado |
| :--- | :--- | :--- | :--- | :--- |
| W1 | Abril | 33% | 0.94 | 🔴 Breakeven/Loss |
| W2 | Mayo | 60% | 2.80 | 🟢 Profitable |
| W3 | Junio | 0% | 0.00 | 🔴 Loss (Chop market) |
| W4 | Julio | 40% | 1.25 | 🟢 Profitable |
| W5 | Agosto | 33% | 0.94 | 🔴 Breakeven/Loss |
| W6 | Septiembre | 50% | 1.90 | 🟢 Profitable |
| W7 | Octubre | 75% | 5.48 | 🟢 **Excellent** |
| W8 | Noviembre | 67% | 3.70 | 🟢 **Excellent** |
| W9 | Diciembre | 60% | 2.76 | 🟢 **Excellent** |

### Conclusión de Robustez

* **Average Profit Factor:** **2.2** (Muy superior al umbral de 1.2).
* **Observación:** El sistema sufrió en Junio y Agosto (mercados erráticos), pero las ganancias masivas de Q4 (PF > 3.0) compensaron con creces las pérdidas pequeñas. Esto confirma el perfil de "caza de tendencias" (Trend Hunter) del MSC.
