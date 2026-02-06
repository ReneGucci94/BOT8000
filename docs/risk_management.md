# Protocolos de Gestión de Riesgo y Capital (Risk Management)

La preservación del capital es la prioridad número uno del sistema BOT8000. Este documento define las reglas matemáticas y lógicas que gobiernan la exposición al riesgo del sistema MSC v3.

## 1. Filosofía de Riesgo

> *"No importa la frecuencia con la que ganas, sino cuánto ganas cuando aciertas y cuánto pierdes cuando fallas."* - George Soros

El sistema opera bajo principios estrictos de anti-fragilidad:

1. **Supervivencia:** Nunca arriesgar una porción del capital que ponga en peligro la continuidad operativa (Risk of Ruin ~ 0%).
2. **Consistencia:** Estandarizar el riesgo por operación para que los resultados sean estadísticamente significativos.
3. **Adaptabilidad:** Ajustar la agresividad basándose en la volatilidad del mercado.

---

## 2. Dimensionamiento de Posición (Position Sizing)

El sistema utiliza el modelo de **Riesgo Fraccional Fijo (Fixed Fractional Risk)**.

### Regla del 1%

Nunca se arriesga más del **1.0%** del capital total (Equity) en una sola operación.

### Fórmula de Cálculo

$$
\text{Position Size} = \frac{\text{Account Equity} \times \text{Risk \%}}{\text{Distance to Stop Loss}}
$$

Donde:

* **Account Equity:** Balance actual + PnL flotante.
* **Risk %:** 0.01 (1%).
* **Distance to Stop Loss:** Diferencia absoluta entre precio de entrada y precio de Stop Loss.

### Ejemplo Numérico

* **Capital:** $10,000 USD
* **Riesgo Máximo Permitido:** $100 USD (1% de $10k)
* **Precio de Entrada (BTC):** $60,000
* **Stop Loss Calculado:** $59,000
* **Distancia:** $1,000

$$
\text{Position Size} = \frac{100}{1,000} = 0.1 \text{ BTC}
$$
*Valor nocional de la posición: $6,000 USD (0.1 x $60k). Apalancamiento efectivo: 0.6x.*

---

## 3. Stop Loss Dinámico (ATR-Based)

En lugar de usar niveles fijos de stop (e.g., "$500 abajo"), el sistema se adapta a la "respiración" del mercado utilizando el **Average True Range (ATR)**.

### Configuración Estándar

* **Stop Loss:** 2.0 x ATR(14) desde el precio de entrada.
  * *Long:* Entrada - 2*ATR
  * *Short:* Entrada + 2*ATR

### Justificación

El ATR mide la volatilidad promedio reciente. Un Stop de 2 ATR coloca la salida de emergencia fuera del "ruido" normal del mercado. Si el precio toca este nivel, significa que la estructura del mercado ha cambiado y la premisa de la operación es inválida.

### Ajuste por Régimen de Mercado

El `Orchestrator` puede modificar dinámicamente el multiplicador de ATR:

* **Régimen Trend:** 2.0 ATR (Standard). Deja correr las ganancias.
* **Régimen Volatile:** 2.5 - 3.0 ATR. Stops más amplios para evitar "violines" (stop hunts), compensado con un menor tamaño de posición (para mantener el riesgo en $100).
* **Régimen Scalping:** 1.5 ATR. Stops ajustados para entradas de alta precisión.

---

## 4. Controles de Max Drawdown (Circuit Breakers)

Para proteger la cuenta de eventos de "CIsne Negro" o fallos sistémicos, se implementan interruptores automáticos.

### Limites Diarios y Semanales

1. **Daily Loss Limit:** Si el sistema pierde **3%** del capital en un día (3 operaciones completas de pérdida consecutiva), se detiene el trading por 24 horas.
    * *Acción:* `HALT_TRADING`. Requiere revisión manual.
2. **Global Drawdown Hard Stop:** -15% del "High Water Mark" (máximo capital alcanzado).
    * *Acción:* `SHUTDOWN`. liquidación total y desactivación de agentes. Esto indica que el mercado ha cambiado fundamentalmente o la estrategia está rota.

### Cooldown Period

Después de **2 pérdidas consecutivas**, el sistema reduce el riesgo por operación al **0.5%** hasta que se registre una operación ganadora. Esto suaviza la curva de caídas (Drawdown Recovery Mode).

---

## 5. Gestión de Profits (Take Profit)

No se utilizan Take Profits fijos duros. El sistema busca capturar tendencias ("Let winners run").

### Trailing Stop

Una vez que la operación está en ganancias (ej. +1R o +1% de beneficio), el Stop Loss se convierte en un **Trailing Stop**.

* Se mueve a favor de la operación siguiendo el precio a una distancia de 1.5 a 2.0 ATR.
* Esto asegura ("locks in") ganancias mientras permite potencial ilimitado al alza.

### Ratio Riesgo/Beneficio (R:R) Esperado

Aunque no se fuerza un TP, el sistema filtra entradas donde el potencial técnico (distancia a la siguiente resistencia) sea menor a 1.5R.

* **Min R:R:** 1:1.5
* **Avg R:R (Histórico):** 1:2.3 (Por cada $1 arriesgado, se ganan $2.3 en promedio).

---

## 6. Correlación y Diversificación (Futuro)

*Actualmente el sistema opera un solo activo (BTC).*
En despliegues multi-activo, el `RiskManager` monitoreará la correlación entre pares.

* **Regla:** No abrir más de 2 posiciones correlacionadas positivamente (e.g., BTC y ETH) simultáneamente en la misma dirección, ya que esto duplica el riesgo efectivo a 2%.
