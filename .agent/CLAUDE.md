# Trading Bot v2 - Sistema de Trading Automatizado

## Objetivo
Construir un bot de trading robusto usando la estrategia TJR Price Action con arquitectura testeable y verificable.

## Reglas del Proyecto

### 1. Skills Obligatorias
ANTES de cualquier implementación, debo usar las skills en `.agent/skills/`:
- `brainstorming` → Antes de crear features
- `writing-plans` → Antes de implementar tareas multi-paso
- `executing-plans` → Para ejecutar planes paso a paso
- `test-driven-development` → SIEMPRE escribir test antes de código
- `verification-before-completion` → Correr tests antes de decir "listo"

### 2. Arquitectura en Lenguaje Formal
TODO el código debe usar:
- Type hints estrictos (Python typing)
- Contratos formales (docstrings con INPUT/OUTPUT/ALGORITHM)
- Tests automáticos (pytest)
- Clases inmutables donde sea posible (dataclasses con frozen=True)

### 3. Estrategia TJR Price Action
El bot implementa:
- Market Structure (HH/HL vs LH/LL)
- Break of Structure (BOS)
- Order Blocks (OB)
- Fair Value Gaps (FVG)
- Timeframes: 4H (bias), 1H (alignment), 5m/15m (entry)

### 4. Workflow Obligatorio
```
1. BRAINSTORM → diseño
2. WRITE PLAN → tareas de 2-5 min
3. EXECUTE con TDD → test first, code second
4. VERIFY → correr tests
5. DONE (solo si tests pasan)
```

## Estructura del Proyecto
- `src/` → Código de producción
- `tests/` → Tests automáticos
- `.agent/skills/` → Skills de desarrollo
# Superpowers: La Biblioteca Completa de Skills

Esta es la documentación completa del sistema Superpowers - el framework usado por desarrolladores profesionales para construir software sin errores.

**Por qué esto vale oro:** Estas skills fueron creadas por Jesse Vincent (obra) después de años de prueba y error con agentes de IA. Cada regla existe porque alguien la cagó sin ella.

---

# Índice

1. La Regla de Oro: using-superpowers
2. Skills de Proceso (cómo pensar)
3. Skills de Ejecución (cómo hacer)
4. Skills de Calidad (cómo verificar)
5. Skills de Git (cómo organizar)
6. Aplicación a Tu Bot de Trading v2

---

# 1. LA REGLA DE ORO

## using-superpowers

> **SI HAY 1% DE PROBABILIDAD DE QUE UNA SKILL APLIQUE, DEBES USARLA. NO ES OPCIONAL. NO ES NEGOCIABLE.**
> 

### El Flujo Obligatorio

```
Mensaje recibido
    ↓
¿Alguna skill podría aplicar? (aunque sea 1%)
    ↓ SÍ
Invocar la skill
    ↓
Anunciar: "Estoy usando [skill] para [propósito]"
    ↓
¿Tiene checklist?
    ↓ SÍ
Crear TodoWrite con cada item
    ↓
Seguir la skill EXACTAMENTE
    ↓
Responder
```

### Pensamientos que Significan PARA - Estás Racionalizando

| Pensamiento | Realidad |
| --- | --- |
| "Es una pregunta simple" | Las preguntas son tareas. Busca skills. |
| "Necesito más contexto primero" | Buscar skills viene ANTES de preguntas. |
| "Déjame explorar el código primero" | Las skills te dicen CÓMO explorar. |
| "Puedo revisar git/archivos rápido" | Los archivos no tienen contexto. Busca skills. |
| "Esto no necesita una skill formal" | Si existe una skill, úsala. |
| "Me acuerdo de esta skill" | Las skills evolucionan. Lee la versión actual. |
| "Es overkill" | Lo simple se vuelve complejo. Úsala. |
| "Voy a hacer esto primero" | Busca skills ANTES de hacer nada. |
| "Se siente productivo" | Acción sin disciplina = tiempo perdido. |

### Prioridad de Skills

1. **Skills de proceso primero** (brainstorming, debugging) - determinan CÓMO abordar la tarea
2. **Skills de implementación después** (frontend-design, etc.) - guían la ejecución

---

# 2. SKILLS DE PROCESO

## brainstorming

> **OBLIGATORIO antes de cualquier trabajo creativo** - crear features, construir componentes, agregar funcionalidad.
> 

### El Proceso

**Entender la idea:**

- Revisar el estado actual del proyecto (archivos, docs, commits recientes)
- Hacer preguntas UNA A LA VEZ
- Preferir preguntas de opción múltiple cuando sea posible
- Solo una pregunta por mensaje
- Enfocarse en: propósito, restricciones, criterios de éxito

**Explorar enfoques:**

- Proponer 2-3 enfoques diferentes con trade-offs
- Presentar opciones conversacionalmente con tu recomendación y razonamiento
- Liderar con la opción recomendada y explicar por qué

**Presentar el diseño:**

- Una vez que crees entender qué se va a construir, presenta el diseño
- Dividir en secciones de 200-300 palabras
- Preguntar después de cada sección si se ve bien
- Cubrir: arquitectura, componentes, flujo de datos, manejo de errores, testing

**Después del diseño:**

- Escribir el diseño validado a `docs/plans/YYYY-MM-DD-<tema>-[design.md](http://design.md)`
- Commit del documento de diseño a git

### Principios Clave

- **Una pregunta a la vez** - No abrumar con múltiples preguntas
- **Opción múltiple preferido** - Más fácil de responder
- **YAGNI sin piedad** - Remover features innecesarias de todos los diseños
- **Explorar alternativas** - Siempre proponer 2-3 enfoques antes de decidir
- **Validación incremental** - Presentar diseño en secciones, validar cada una

---

## writing-plans

> **Usar cuando tienes spec o requirements para una tarea multi-paso, ANTES de tocar código.**
> 

### Granularidad de Tareas

**Cada paso es UNA acción (2-5 minutos):**

- "Escribir el test que falla" - paso
- "Correrlo para asegurar que falla" - paso
- "Implementar el código mínimo para que pase" - paso
- "Correr los tests y asegurar que pasan" - paso
- "Commit" - paso

### Header del Documento de Plan

**Cada plan DEBE empezar con este header:**

```markdown
# [Nombre de Feature] Plan de Implementación

> **Para Claude:** SUB-SKILL REQUERIDA: Usar superpowers:executing-plans para implementar este plan tarea por tarea.

**Meta:** [Una oración describiendo qué construye esto]

**Arquitectura:** [2-3 oraciones sobre el enfoque]

**Tech Stack:** [Tecnologías/librerías clave]

---
```

### Estructura de Tarea

```markdown
### Tarea N: [Nombre del Componente]

**Archivos:**
- Crear: `ruta/exacta/al/[archivo.py](http://archivo.py)`
- Modificar: `ruta/exacta/al/[existente.py:123](http://existente.py:123)-145`
- Test: `tests/ruta/exacta/al/[test.py](http://test.py)`

**Paso 1: Escribir el test que falla**

[código del test]

**Paso 2: Correr test para verificar que falla**

Correr: `pytest tests/ruta/[test.py](http://test.py)::nombre_test -v`
Esperado: FAIL con "función no definida"

**Paso 3: Escribir implementación mínima**

[código mínimo]

**Paso 4: Correr test para verificar que pasa**

Correr: `pytest tests/ruta/[test.py](http://test.py)::nombre_test -v`
Esperado: PASS

**Paso 5: Commit**

```

git add tests/ruta/[test.py](http://test.py) src/ruta/[archivo.py](http://archivo.py)

git commit -m "feat: agregar feature específica"

```

```

### Recuerda

- Rutas de archivo exactas siempre
- Código completo en el plan (no "agregar validación")
- Comandos exactos con output esperado
- DRY, YAGNI, TDD, commits frecuentes

---

# 3. SKILLS DE EJECUCIÓN

## executing-plans

> **Usar cuando tienes un plan de implementación escrito para ejecutar en una sesión separada con checkpoints de revisión.**
> 

### El Proceso

**Paso 1: Cargar y Revisar Plan**

1. Leer archivo del plan
2. Revisar críticamente - identificar preguntas o concerns
3. Si hay concerns: Plantearlos antes de empezar
4. Si no hay concerns: Crear TodoWrite y proceder

**Paso 2: Ejecutar Batch**

**Default: Primeras 3 tareas**

Para cada tarea:

1. Marcar como in_progress
2. Seguir cada paso exactamente
3. Correr verificaciones como se especifica
4. Marcar como completed

**Paso 3: Reportar**

Cuando el batch esté completo:

- Mostrar qué se implementó
- Mostrar output de verificación
- Decir: "Listo para feedback."

**Paso 4: Continuar**

Basado en feedback:

- Aplicar cambios si es necesario
- Ejecutar siguiente batch
- Repetir hasta completar

### Cuándo Parar y Pedir Ayuda

**PARA de ejecutar inmediatamente cuando:**

- Encuentres un blocker a medio batch
- El plan tiene gaps críticos
- No entiendes una instrucción
- La verificación falla repetidamente

**Pide clarificación en vez de adivinar.**

---

## dispatching-parallel-agents

> **Usar cuando enfrentas 2+ tareas independientes que pueden trabajarse sin estado compartido o dependencias secuenciales.**
> 

### Cuándo Usar

**Usar cuando:**

- 3+ archivos de test fallando con diferentes causas raíz
- Múltiples subsistemas rotos independientemente
- Cada problema puede entenderse sin contexto de los otros
- No hay estado compartido entre investigaciones

**NO usar cuando:**

- Las fallas están relacionadas (arreglar una podría arreglar otras)
- Necesitas entender el estado completo del sistema
- Los agentes interferirían entre sí

### El Patrón

**1. Identificar Dominios Independientes**

Agrupar fallas por qué está roto:

- Archivo A tests: Flujo de aprobación
- Archivo B tests: Comportamiento de batch
- Archivo C tests: Funcionalidad de abort

**2. Crear Tareas de Agente Enfocadas**

Cada agente obtiene:

- **Scope específico:** Un archivo de test o subsistema
- **Meta clara:** Hacer que estos tests pasen
- **Restricciones:** No cambiar otro código
- **Output esperado:** Resumen de qué encontraste y arreglaste

**3. Dispatch en Paralelo**

```
Task("Arreglar agent-tool-abort.test.ts")
Task("Arreglar batch-completion-behavior.test.ts")
Task("Arreglar tool-approval-race-conditions.test.ts")
// Los tres corren concurrentemente
```

**4. Revisar e Integrar**

Cuando los agentes regresen:

- Leer cada resumen
- Verificar que los fixes no conflictúan
- Correr suite completa de tests
- Integrar todos los cambios

---

# 4. SKILLS DE CALIDAD

## test-driven-development (TDD)

> **Usar cuando implementas cualquier feature o bugfix, ANTES de escribir código de implementación.**
> 

### LA LEY DE HIERRO

```
NINGÚN CÓDIGO DE PRODUCCIÓN SIN UN TEST QUE FALLE PRIMERO
```

**¿Escribiste código antes del test? Bórralo. Empieza de nuevo.**

**Sin excepciones:**

- No lo guardes como "referencia"
- No lo "adaptes" mientras escribes tests
- No lo mires
- Borrar significa borrar

Implementa fresco desde los tests. Punto.

### Red-Green-Refactor

```
RED: Escribir test que falla
    ↓
Verificar que falla correctamente
    ↓
GREEN: Código mínimo para pasar
    ↓
Verificar que pasa (todo verde)
    ↓
REFACTOR: Limpiar
    ↓
Verificar que sigue verde
    ↓
Siguiente test
```

### RED - Escribir Test que Falla

Escribir UN test mínimo mostrando qué debería pasar.

**Bueno:**

```python
def test_retry_3_veces_operaciones_fallidas():
    intentos = 0
    def operacion():
        nonlocal intentos
        intentos += 1
        if intentos < 3:
            raise Exception('fallo')
        return 'éxito'
    
    resultado = retry_operation(operacion)
    
    assert resultado == 'éxito'
    assert intentos == 3
```

Nombre claro, testea comportamiento real, una cosa

**Malo:**

```python
def test_retry_funciona():
    mock = Mock(side_effect=[Exception(), Exception(), 'éxito'])
    retry_operation(mock)
    assert [mock.call](http://mock.call)_count == 3
```

Nombre vago, testea el mock no el código

### Verificar RED - Ver que Falle

**OBLIGATORIO. Nunca saltear.**

```bash
pytest tests/ruta/[test.py](http://test.py) -v
```

Confirmar:

- Test falla (no errores)
- Mensaje de falla es el esperado
- Falla porque la feature no existe (no typos)

**¿El test pasa?** Estás testeando comportamiento existente. Arregla el test.

### GREEN - Código Mínimo

Escribir el código más simple para pasar el test.

**Bueno:** Solo lo suficiente para pasar

**Malo:** Over-engineered con features extras

No agregar features, refactorear otro código, o "mejorar" más allá del test.

### Verificar GREEN - Ver que Pase

**OBLIGATORIO.**

Confirmar:

- Test pasa
- Otros tests siguen pasando
- Output limpio (sin errores, warnings)

### REFACTOR - Limpiar

Solo después de verde:

- Remover duplicación
- Mejorar nombres
- Extraer helpers

Mantener tests verdes. No agregar comportamiento.

### Racionalizaciones Comunes

| Excusa | Realidad |
| --- | --- |
| "Muy simple para testear" | El código simple se rompe. El test toma 30 segundos. |
| "Voy a testear después" | Tests que pasan inmediatamente no prueban nada. |
| "Ya lo testeé manualmente" | Ad-hoc ≠ sistemático. Sin registro, no se puede re-correr. |
| "Borrar X horas es desperdicio" | Falacia de costo hundido. Mantener código sin verificar es deuda técnica. |
| "Necesito explorar primero" | OK. Bota la exploración, empieza con TDD. |
| "TDD me va a hacer más lento" | TDD es más rápido que debuggear. |

---

## verification-before-completion

> **Usar cuando estás a punto de decir que el trabajo está completo, arreglado, o pasando, ANTES de commitear o crear PRs.**
> 

### LA LEY DE HIERRO

```
NINGÚN CLAIM DE COMPLETADO SIN EVIDENCIA FRESCA DE VERIFICACIÓN
```

Si no corriste el comando de verificación en este mensaje, no puedes clamar que pasa.

### La Función de Gate

```
ANTES de clamar cualquier status o expresar satisfacción:

1. IDENTIFICAR: ¿Qué comando prueba este claim?
2. CORRER: Ejecutar el comando COMPLETO (fresco, completo)
3. LEER: Output completo, verificar exit code, contar fallas
4. VERIFICAR: ¿El output confirma el claim?
   - Si NO: Declarar status actual con evidencia
   - Si SÍ: Declarar claim CON evidencia
5. SOLO ENTONCES: Hacer el claim

Saltear cualquier paso = mentir, no verificar
```

### Fallas Comunes

| Claim | Requiere | NO Suficiente |
| --- | --- | --- |
| Tests pasan | Output del comando: 0 fallas | Corrida anterior, "debería pasar" |
| Linter limpio | Output del linter: 0 errores | Chequeo parcial |
| Build exitoso | Comando de build: exit 0 | Linter pasando |
| Bug arreglado | Testear síntoma original: pasa | Código cambiado, asumir arreglado |
| Agente completó | VCS diff muestra cambios | Agente reporta "éxito" |

### Red Flags - PARA

- Usar "debería", "probablemente", "parece que"
- Expresar satisfacción antes de verificación ("¡Genial!", "¡Perfecto!", "¡Listo!")
- A punto de commitear/push/PR sin verificación
- Confiar en reportes de éxito de agentes
- Depender de verificación parcial
- Pensar "solo esta vez"
- Cansado y querer que el trabajo termine

### Prevención de Racionalización

| Excusa | Realidad |
| --- | --- |
| "Debería funcionar ahora" | CORRE la verificación |
| "Estoy confiado" | Confianza ≠ evidencia |
| "Solo esta vez" | Sin excepciones |
| "El linter pasó" | Linter ≠ compilador |
| "El agente dijo éxito" | Verifica independientemente |
| "Estoy cansado" | Cansancio ≠ excusa |

---

## code-reviewer

> **Usar cuando un paso mayor del proyecto se completó y necesita revisión contra el plan original y estándares de código.**
> 

### Qué Hace el Code Reviewer

1. **Análisis de Alineación con Plan:**
    - Comparar implementación contra documento de planning original
    - Identificar desviaciones del enfoque planeado
    - Evaluar si las desviaciones son mejoras justificadas o departures problemáticos
    - Verificar que toda la funcionalidad planeada fue implementada
2. **Evaluación de Calidad de Código:**
    - Revisar adherencia a patrones y convenciones establecidas
    - Chequear manejo de errores apropiado, type safety, programación defensiva
    - Evaluar organización del código, convenciones de nombres, mantenibilidad
    - Evaluar cobertura de tests y calidad de implementación de tests
    - Buscar vulnerabilidades de seguridad o issues de performance
3. **Identificación de Issues:**
    - Categorizar issues como: Crítico (debe arreglar), Importante (debería arreglar), o Sugerencias
    - Para cada issue, proveer ejemplos específicos y recomendaciones accionables

---

## receiving-code-review

> **Usar cuando recibes feedback de code review, ANTES de implementar sugerencias.**
> 

### El Patrón de Respuesta

```
CUANDO recibes feedback de code review:

1. LEER: Feedback completo sin reaccionar
2. ENTENDER: Reformular el requirement en tus palabras (o preguntar)
3. VERIFICAR: Chequear contra realidad del codebase
4. EVALUAR: ¿Técnicamente correcto para ESTE codebase?
5. RESPONDER: Acknowledgment técnico o pushback razonado
6. IMPLEMENTAR: Un item a la vez, testear cada uno
```

### Respuestas Prohibidas

**NUNCA:**

- "¡Tienes toda la razón!"
- "¡Buen punto!"
- "¡Excelente feedback!"
- "Déjame implementar eso ahora" (antes de verificación)

**EN CAMBIO:**

- Reformular el requirement técnico
- Hacer preguntas clarificadoras
- Push back con razonamiento técnico si está mal
- Solo empezar a trabajar (acciones > palabras)

### Cuándo Hacer Push Back

Hacer push back cuando:

- La sugerencia rompe funcionalidad existente
- El reviewer no tiene contexto completo
- Viola YAGNI (feature no usada)
- Técnicamente incorrecto para este stack
- Hay razones de legacy/compatibilidad

**Cómo hacer push back:**

- Usar razonamiento técnico, no defensividad
- Hacer preguntas específicas
- Referenciar tests/código funcionando

---

# 5. SKILLS DE GIT

## using-git-worktrees

> **Usar cuando empiezas trabajo de feature que necesita aislamiento del workspace actual.**
> 

### Proceso de Selección de Directorio

**Orden de prioridad:**

1. Chequear directorios existentes:

```bash
ls -d .worktrees 2>/dev/null     # Preferido (oculto)
ls -d worktrees 2>/dev/null      # Alternativa
```

1. Chequear [CLAUDE.md](http://CLAUDE.md)
2. Preguntar al usuario

### Pasos de Creación

```bash
# Detectar nombre de proyecto
project=$(basename "$(git rev-parse --show-toplevel)")

# Crear worktree con nueva rama
git worktree add "$path" -b "$BRANCH_NAME"
cd "$path"

# Correr setup del proyecto
if [ -f package.json ]; then npm install; fi
if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

# Verificar baseline limpio
npm test  # o pytest, etc.
```

---

## finishing-a-development-branch

> **Usar cuando la implementación está completa, todos los tests pasan, y necesitas decidir cómo integrar el trabajo.**
> 

### El Proceso

**Paso 1: Verificar Tests**

```bash
npm test / pytest / go test ./...
```

**Si los tests fallan:** Para. No proceder al Paso 2.

**Paso 2: Presentar Opciones**

```
Implementación completa. ¿Qué te gustaría hacer?

1. Merge back a <base-branch> localmente
2. Push y crear Pull Request
3. Mantener la rama como está (yo lo manejo después)
4. Descartar este trabajo

¿Cuál opción?
```

**Paso 3: Ejecutar Opción Elegida**

| Opción | Merge | Push | Mantener Worktree | Cleanup Branch |
| --- | --- | --- | --- | --- |
| 1. Merge local | ✓ | - | - | ✓ |
| 2. Crear PR | - | ✓ | ✓ | - |
| 3. Mantener | - | - | ✓ | - |
| 4. Descartar | - | - | - | ✓ (force) |

---

# 6. APLICACIÓN A TU BOT DE TRADING v2

## Tu Problema con v1

1. Construiste el bot
2. Ganaste 7k
3. Asumiste que funcionaba sin verificar
4. Lo quemaste y perdiste todo
5. Señales diferentes en dispositivos

**Skills que habrían prevenido esto:**

- `test-driven-development` → Tests antes de código
- `verification-before-completion` → No decir "funciona" sin pruebas
- `brainstorming` → Pensar en edge cases antes

## El Flujo Correcto para v2

### Fase 1: Diseño (usa brainstorming)

1. Definir exactamente qué hace el bot
2. Proponer 2-3 arquitecturas
3. Validar cada sección del diseño
4. Documentar en `docs/plans/[YYYY-MM-DD-trading-bot-design.md](http://YYYY-MM-DD-trading-bot-design.md)`

### Fase 2: Plan (usa writing-plans)

1. Dividir en tareas de 2-5 minutos cada una
2. Cada tarea: test → verificar falla → implementar → verificar pasa → commit
3. Guardar en `docs/plans/[YYYY-MM-DD-trading-bot-implementation.md](http://YYYY-MM-DD-trading-bot-implementation.md)`

### Fase 3: Implementación (usa executing-plans + TDD)

1. Ejecutar batches de 3 tareas
2. Reportar después de cada batch
3. NUNCA decir "funciona" sin correr tests
4. NUNCA commitear sin verificación

### Fase 4: Verificación (usa verification-before-completion)

Antes de decir "el bot está listo":

```bash
# Correr tests
pytest tests/ -v

# Ver output completo
# Contar fallas: 0
# SOLO ENTONCES: "El bot pasa todos los tests"
```

### Fase 5: Paper Trading (30 días MÍNIMO)

No ir a real hasta:

- 30 días de paper trading
- Win rate > 50%
- Drawdown definido
- Todas las verificaciones pasan

---

# Checklist Final

## Antes de CUALQUIER código:

- [ ]  ¿Usé brainstorming para diseñar?
- [ ]  ¿Tengo un plan escrito con pasos de 2-5 min?
- [ ]  ¿Cada paso tiene su test?

## Durante implementación:

- [ ]  ¿Escribí el test ANTES del código?
- [ ]  ¿Vi el test fallar?
- [ ]  ¿Escribí el código MÍNIMO para pasar?
- [ ]  ¿Vi el test pasar?
- [ ]  ¿Commiteé?

## Antes de decir "funciona":

- [ ]  ¿Corrí el comando de verificación?
- [ ]  ¿Vi el output completo?
- [ ]  ¿Hay 0 fallas?
- [ ]  ¿TENGO EVIDENCIA?

## Antes de ir a real:

- [ ]  ¿30 días de paper trading?
- [ ]  ¿Win rate documentado?
- [ ]  ¿Límite de pérdida diaria configurado?
- [ ]  ¿Una sola fuente de datos?
- [ ]  ¿Una sola timezone?

---

*Esta documentación está basada en el repositorio Superpowers de Jesse Vincent ([github.com/obra/superpowers](http://github.com/obra/superpowers)) - el framework usado por desarrolladores profesionales para construir software con agentes de IA sin cagar el palo.*

[🚫 Testing Anti-Patterns - Qué NO Hacer](https://www.notion.so/Testing-Anti-Patterns-Qu-NO-Hacer-2ecf95ac6b6981d69564e24f14565b35?pvs=21)

[🧠 Principios de Persuasión para Diseño de Skills](https://www.notion.so/Principios-de-Persuasi-n-para-Dise-o-de-Skills-2ecf95ac6b6981d58d75fd6335db372a?pvs=21)

[📈 Skill: TJR Price Action - Estrategia Completa](https://www.notion.so/Skill-TJR-Price-Action-Estrategia-Completa-2ecf95ac6b6981d78c52cd6c2374f0db?pvs=21)

[🚀 Trading Bot v2 - Roadmap Completo](https://www.notion.so/Trading-Bot-v2-Roadmap-Completo-2ecf95ac6b698191adc8c3ca97c65ebd?pvs=21)

[🛠️ Cómo Crear Tus Propias Skills](https://www.notion.so/C-mo-Crear-Tus-Propias-Skills-2ecf95ac6b6981f78b55e545602fa9f6?pvs=21)

[🎯 Quick Reference - Cheat Sheet](https://www.notion.so/Quick-Reference-Cheat-Sheet-2ecf95ac6b69817e9d40ff0105d0438a?pvs=21)

[📘 Anthropic Best Practices - Guía Oficial](https://www.notion.so/Anthropic-Best-Practices-Gu-a-Oficial-2ecf95ac6b698178858bcf15a331925f?pvs=21)
