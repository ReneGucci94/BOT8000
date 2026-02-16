# Plan de Estabilización y Avance BOT8000 (24 Horas)
**Inicia:** Sábado 2026-02-14 07:00 | **Finaliza:** Domingo 2026-02-15 07:00
**Responsable:** Clawd (Asistente Ejecutivo)

## Fase 1: Infraestructura y Supervivencia (0-4 horas)
1. **Detección y Arreglo de DB:** Identificar por qué PostgreSQL rechaza conexiones (Docker status, puertos, volumen lleno). Reiniciar servicios.
2. **Saneamiento del Entorno:** Instalar `pytest` y dependencias faltantes en el `.venv`. Verificar consistencia de la versión de Python.
3. **Snapshot de Emergencia:** Hacer commit de los 16 archivos modificados para evitar pérdida de código si hay un fallo eléctrico o de sistema.

## Fase 2: Validación de Integridad (4-8 horas)
1. **Suite de Tests:** Ejecutar `pytest` en todo el repositorio. Prioridad: `test_orchestrator.py` y `src/execution/risk.py`.
2. **Corrección Quirúrgica:** Si los tests fallan, usaré a Codex para corregir bugs de sintaxis o lógica básica detectados en la auditoría anterior (e.g., `UnboundLocalError`, parámetros fantasma).
3. **Test de Conexión Real:** Validar que el bot ya puede escribir en la DB.

## Fase 3: Optimización Estocástica (8-16 horas)
1. **WFO de Alta Intensidad:** Correr un Walk Forward Optimization completo (no rápido) con una población de 50 y 10 generaciones. 
2. **Validación de Riesgo:** Monitorear que `max_portfolio_risk` realmente bloquee órdenes durante la simulación.
3. **Análisis de Varianza:** Filtrar resultados para reducir la varianza agresiva (buscar PF > 1.2 consistente en todas las ventanas).

## Fase 4: Reporte y Cierre (16-24 horas)
1. **Generación de Reporte Ejecutivo:** Resumen de ganancias estimadas, drawdown real y estabilidad del sistema.
2. **Preparación para ML:** Si todo lo anterior es estable, documentar el pipeline necesario para el entrenamiento del modelo `rf_model_v1.pkl` (Fase ML).
3. **Commit Final y Limpieza:** Dejar el workspace ordenado para tu regreso.

---
**Nota:** Si ocurre un error catastrófico que no puedo resolver, dejaré un mensaje de alerta prioritario en el sistema de mensajes.
