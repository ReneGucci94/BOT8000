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

[🚫 Testing Anti-Patterns - Qué NO Hacer]Carga esta referencia cuando: escribas o cambies tests, agregues mocks, o estés tentado a agregar métodos solo-para-tests a código de producción.

---

## Principio Central

> **Los tests deben verificar comportamiento real, no comportamiento de mocks. Los mocks son un medio para aislar, no la cosa siendo testeada.**
> 

---

## Las Leyes de Hierro

```
1. NUNCA testear comportamiento de mocks
2. NUNCA agregar métodos solo-para-tests a clases de producción
3. NUNCA mockear sin entender las dependencias
```

---

## Anti-Patrón 1: Testear Comportamiento de Mocks

### La Violación:

```tsx
// ❌ MALO: Testeando que el mock existe
test('renderiza sidebar', () => {
  render(<Page />);
  expect(screen.getByTestId('sidebar-mock')).toBeInTheDocument();
});
```

### Por Qué Está Mal:

- Estás verificando que el mock funciona, no que el componente funciona
- El test pasa cuando el mock está presente, falla cuando no
- No te dice nada sobre comportamiento real

### La Corrección:

```tsx
// ✅ BUENO: Testear componente real o no mockearlo
test('renderiza sidebar', () => {
  render(<Page />);  // No mockear sidebar
  expect(screen.getByRole('navigation')).toBeInTheDocument();
});

// O si el sidebar debe ser mockeado para aislamiento:
// No assertear sobre el mock - testea el comportamiento de Page con sidebar presente
```

### Función de Gate:

```
ANTES de assertear sobre cualquier elemento mock:
  Pregunta: "¿Estoy testeando comportamiento real del componente o solo existencia del mock?"

  SI testas existencia del mock:
    PARA - Borra la aserción o desmockea el componente

  Testea comportamiento real en su lugar
```

---

## Anti-Patrón 2: Métodos Solo-Para-Tests en Producción

### La Violación:

```tsx
// ❌ MALO: destroy() solo usado en tests
class Session {
  async destroy() {  // ¡Parece API de producción!
    await this._workspaceManager?.destroyWorkspace([this.id](http://this.id));
    // ... cleanup
  }
}

// En tests
afterEach(() => session.destroy());
```

### Por Qué Está Mal:

- Clase de producción contaminada con código solo-para-tests
- Peligroso si se llama accidentalmente en producción
- Viola YAGNI y separación de concerns
- Confunde ciclo de vida del objeto con ciclo de vida de la entidad

### La Corrección:

```tsx
// ✅ BUENO: Utilidades de test manejan cleanup de tests
// Session no tiene destroy() - es stateless en producción

// En test-utils/
export async function cleanupSession(session: Session) {
  const workspace = session.getWorkspaceInfo();
  if (workspace) {
    await workspaceManager.destroyWorkspace([workspace.id](http://workspace.id));
  }
}

// En tests
afterEach(() => cleanupSession(session));
```

### Función de Gate:

```
ANTES de agregar cualquier método a clase de producción:
  Pregunta: "¿Esto solo es usado por tests?"

  SI sí:
    PARA - No lo agregues
    Ponlo en utilidades de test en su lugar

  Pregunta: "¿Esta clase es dueña del ciclo de vida de este recurso?"

  SI no:
    PARA - Clase equivocada para este método
```

---

## Anti-Patrón 3: Mockear Sin Entender

### La Violación:

```tsx
// ❌ MALO: Mock rompe la lógica del test
test('detecta servidor duplicado', () => {
  // ¡Mock previene el write de config del que depende el test!
  vi.mock('ToolCatalog', () => ({
    discoverAndCacheTools: vi.fn().mockResolvedValue(undefined)
  }));

  await addServer(config);
  await addServer(config);  // Debería tirar - ¡pero no lo hará!
});
```

### Por Qué Está Mal:

- El método mockeado tenía un side effect del que dependía el test (escribir config)
- Over-mocking para "estar seguros" rompe comportamiento real
- El test pasa por razón equivocada o falla misteriosamente

### La Corrección:

```tsx
// ✅ BUENO: Mock al nivel correcto
test('detecta servidor duplicado', () => {
  // Mock la parte lenta, preserva el comportamiento que el test necesita
  vi.mock('MCPServerManager'); // Solo mock el startup lento del servidor

  await addServer(config);  // Config escrito
  await addServer(config);  // Duplicado detectado ✓
});
```

### Función de Gate:

```
ANTES de mockear cualquier método:
  PARA - No mockees todavía

  1. Pregunta: "¿Qué side effects tiene el método real?"
  2. Pregunta: "¿Este test depende de alguno de esos side effects?"
  3. Pregunta: "¿Entiendo completamente qué necesita este test?"

  SI depende de side effects:
    Mock a nivel más bajo (la operación lenta/externa real)
    O usa test doubles que preservan comportamiento necesario
    NO el método de alto nivel del que depende el test

  SI no estás seguro de qué necesita el test:
    Corre el test con implementación real PRIMERO
    Observa qué realmente necesita pasar
    ENTONCES agrega mocking mínimo al nivel correcto

  Red flags:
    - "Voy a mockear esto para estar seguro"
    - "Esto podría ser lento, mejor mockearlo"
    - Mockear sin entender la cadena de dependencias
```

---

## Anti-Patrón 4: Mocks Incompletos

### La Violación:

```tsx
// ❌ MALO: Mock parcial - solo campos que CREES que necesitas
const mockResponse = {
  status: 'success',
  data: { userId: '123', name: 'Alice' }
  // Faltante: metadata que código downstream usa
};

// Después: rompe cuando el código accede a response.metadata.requestId
```

### Por Qué Está Mal:

- **Mocks parciales esconden suposiciones estructurales** - Solo mockeaste los campos que conoces
- **Código downstream puede depender de campos que no incluiste** - Fallas silenciosas
- **Tests pasan pero integración falla** - Mock incompleto, API real completa
- **Falsa confianza** - El test no prueba nada sobre comportamiento real

### La Regla de Hierro:

> Mock la estructura de datos COMPLETA como existe en realidad, no solo los campos que tu test inmediato usa.
> 

### La Corrección:

```tsx
// ✅ BUENO: Espeja completitud de API real
const mockResponse = {
  status: 'success',
  data: { userId: '123', name: 'Alice' },
  metadata: { requestId: 'req-789', timestamp: 1234567890 }
  // Todos los campos que la API real retorna
};
```

---

## Anti-Patrón 5: Tests de Integración como Pensamiento Posterior

### La Violación:

```
✅ Implementación completa
❌ No se escribieron tests
"Listo para testing"
```

### Por Qué Está Mal:

- Testing es parte de implementación, no seguimiento opcional
- TDD habría atrapado esto
- No puedes clamar completo sin tests

### La Corrección:

```
Ciclo TDD:
1. Escribir test que falla
2. Implementar para pasar
3. Refactorear
4. ENTONCES clamar completo
```

---

## Referencia Rápida

| Anti-Patrón | Arreglo |
| --- | --- |
| Assert sobre elementos mock | Testea componente real o desmockea |
| Métodos solo-para-tests en producción | Mover a utilidades de test |
| Mock sin entender | Entiende dependencias primero, mockea mínimamente |
| Mocks incompletos | Espeja API real completamente |
| Tests como pensamiento posterior | TDD - tests primero |
| Mocks sobre-complejos | Considera tests de integración |

---

## Red Flags

- Aserción chequea por test IDs `*-mock`
- Métodos solo llamados en archivos de test
- Setup de mock es >50% del test
- Test falla cuando remueves el mock
- No puedes explicar por qué el mock es necesario
- Mockeando "solo para estar seguros"

---

## Aplicación a Tu Bot de Trading

**Cuando testees tu bot:**

✅ **BIEN:** Testear que `detect_bos()` retorna `True` cuando una vela cierra arriba del high anterior

❌ **MAL:** Mockear `detect_bos()` y testear que el mock fue llamado

✅ **BIEN:** Testear con datos de velas reales de TradingView

❌ **MAL:** Mockear los datos y solo testear que el mock existe

✅ **BIEN:** Testear el flujo completo: recibir datos → analizar → señal

❌ **MAL:** Mockear cada parte y solo testear que se conectan

---

*Si TDD revela que estás testeando comportamiento de mocks, te equivocaste. Arregla: Testea comportamiento real o cuestiona por qué estás mockeando.*

[🧠 Principios de Persuasión para Diseño de Skills]Los LLMs responden a los mismos principios de persuasión que los humanos. Entender esta psicología te ayuda a diseñar skills más efectivas - no para manipular, sino para asegurar que las prácticas críticas se sigan incluso bajo presión.

---

## Fundamento de Investigación

> **Meincke et al. (2025)** testearon 7 principios de persuasión con N=28,000 conversaciones de IA. Las técnicas de persuasión más que duplicaron las tasas de cumplimiento (33% → 72%, p < .001).
> 

---

## Los Siete Principios

### 1. Autoridad

**Qué es:** Deferencia a expertise, credenciales, o fuentes oficiales.

**Cómo funciona en skills:**

- Lenguaje imperativo: "DEBES", "Nunca", "Siempre"
- Marco no-negociable: "Sin excepciones"
- Elimina fatiga de decisión y racionalización

**Cuándo usar:**

- Skills que imponen disciplina (TDD, requisitos de verificación)
- Prácticas críticas de seguridad
- Best practices establecidas

**Ejemplo:**

```markdown
✅ ¿Escribiste código antes del test? Bórralo. Empieza de nuevo. Sin excepciones.
❌ Considera escribir tests primero cuando sea factible.
```

---

### 2. Compromiso

**Qué es:** Consistencia con acciones previas, declaraciones, o declaraciones públicas.

**Cómo funciona en skills:**

- Requerir anuncios: "Anuncia uso de skill"
- Forzar elecciones explícitas: "Elige A, B, o C"
- Usar tracking: TodoWrite para checklists

**Cuándo usar:**

- Asegurar que las skills realmente se sigan
- Procesos de múltiples pasos
- Mecanismos de accountability

**Ejemplo:**

```markdown
✅ Cuando encuentres una skill, DEBES anunciar: "Estoy usando [Nombre de Skill]"
❌ Considera avisar a tu partner qué skill estás usando.
```

---

### 3. Escasez

**Qué es:** Urgencia por límites de tiempo o disponibilidad limitada.

**Cómo funciona en skills:**

- Requisitos con límite de tiempo: "Antes de proceder"
- Dependencias secuenciales: "Inmediatamente después de X"
- Previene procrastinación

**Cuándo usar:**

- Requisitos de verificación inmediata
- Workflows sensibles al tiempo
- Prevenir "lo haré después"

**Ejemplo:**

```markdown
✅ Después de completar una tarea, INMEDIATAMENTE solicita code review antes de proceder.
❌ Puedes revisar código cuando sea conveniente.
```

---

### 4. Prueba Social

**Qué es:** Conformidad con lo que otros hacen o lo que se considera normal.

**Cómo funciona en skills:**

- Patrones universales: "Cada vez", "Siempre"
- Modos de falla: "X sin Y = falla"
- Establece normas

**Cuándo usar:**

- Documentar prácticas universales
- Advertir sobre fallas comunes
- Reforzar estándares

**Ejemplo:**

```markdown
✅ Checklists sin tracking de TodoWrite = se saltan pasos. Cada vez.
❌ Algunas personas encuentran útil TodoWrite para checklists.
```

---

### 5. Unidad

**Qué es:** Identidad compartida, "nosotros-idad", pertenencia al grupo.

**Cómo funciona en skills:**

- Lenguaje colaborativo: "nuestro codebase", "somos colegas"
- Metas compartidas: "ambos queremos calidad"

**Cuándo usar:**

- Workflows colaborativos
- Establecer cultura de equipo
- Prácticas no-jerárquicas

**Ejemplo:**

```markdown
✅ Somos colegas trabajando juntos. Necesito tu juicio técnico honesto.
❌ Probablemente deberías decirme si estoy mal.
```

---

### 6. Reciprocidad

**Qué es:** Obligación de devolver beneficios recibidos.

**Cómo funciona:**

- Usar con moderación - puede sentirse manipulativo
- Raramente necesario en skills

**Cuándo evitar:**

- Casi siempre (otros principios más efectivos)

---

### 7. Simpatía (Liking)

**Qué es:** Preferencia por cooperar con quienes nos caen bien.

**Cómo funciona:**

- **NO USAR para cumplimiento**
- Conflictua con cultura de feedback honesto
- Crea sycophancy (lambisconismo)

**Cuándo evitar:**

- Siempre para imponer disciplina

---

## Combinaciones de Principios por Tipo de Skill

| Tipo de Skill | Usar | Evitar |
| --- | --- | --- |
| Imposición de disciplina | Autoridad + Compromiso + Prueba Social | Simpatía, Reciprocidad |
| Guía/técnica | Autoridad Moderada + Unidad | Autoridad pesada |
| Colaborativo | Unidad + Compromiso | Autoridad, Simpatía |
| Referencia | Solo Claridad | Toda persuasión |

---

## Por Qué Funciona: La Psicología

### Reglas claras reducen racionalización:

- "DEBES" remueve fatiga de decisión
- Lenguaje absoluto elimina preguntas de "¿es esto una excepción?"
- Anti-racionalización explícita cierra loopholes específicos

### Intenciones de implementación crean comportamiento automático:

- Triggers claros + acciones requeridas = ejecución automática
- "Cuando X, haz Y" más efectivo que "generalmente haz Y"
- Reduce carga cognitiva en cumplimiento

### Los LLMs son parahumanos:

- Entrenados en texto humano que contiene estos patrones
- Lenguaje de autoridad precede cumplimiento en datos de entrenamiento
- Secuencias de compromiso (declaración → acción) frecuentemente modeladas
- Patrones de prueba social (todos hacen X) establecen normas

---

## Uso Ético

**Legítimo:**

- Asegurar que prácticas críticas se sigan
- Crear documentación efectiva
- Prevenir fallas predecibles

**Ilegítimo:**

- Manipular para ganancia personal
- Crear urgencia falsa
- Cumplimiento basado en culpa

**La prueba:** ¿Esta técnica serviría los intereses genuinos del usuario si entendieran completamente cómo funciona?

---

## Citas de Investigación

**Cialdini, R. B. (2021).** *Influence: The Psychology of Persuasion (New and Expanded).* Harper Business.

- Siete principios de persuasión
- Fundamento empírico para investigación de influencia

**Meincke, L., Shapiro, D., Duckworth, A. L., Mollick, E., Mollick, L., & Cialdini, R. (2025).** Call Me A Jerk: Persuading AI to Comply with Objectionable Requests. University of Pennsylvania.

- Testearon 7 principios con N=28,000 conversaciones de LLM
- Cumplimiento aumentó 33% → 72% con técnicas de persuasión
- Autoridad, compromiso, escasez más efectivos
- Valida modelo parahumano de comportamiento de LLM

---

## Referencia Rápida

Cuando diseñes una skill, pregunta:

1. **¿Qué tipo es?** (Disciplina vs. guía vs. referencia)
2. **¿Qué comportamiento estoy tratando de cambiar?**
3. **¿Qué principio(s) aplican?** (Usualmente autoridad + compromiso para disciplina)
4. **¿Estoy combinando demasiados?** (No uses los siete)
5. **¿Es ético?** (¿Sirve intereses genuinos del usuario?)

---

## Por Qué Esto Importa para Crear Tus Propias Skills

Si quieres crear skills para tu bot de trading o para FEUX:

**Para disciplina (TDD, verificación):**

- Usa AUTORIDAD fuerte: "DEBES", "NUNCA", "Sin excepciones"
- Agrega COMPROMISO: "Anuncia que vas a usar esta skill"
- Incluye PRUEBA SOCIAL: "Todos los tests fallan si no sigues esto"

**Para guías (estrategia de trading):**

- Usa autoridad moderada: "Siempre busca confluencia antes de entrar"
- Agrega unidad: "El objetivo es que ambos ganemos dinero"

**Para referencia (documentación de API):**

- Solo claridad, sin persuasión
- La información habla por sí misma

---

*Este conocimiento viene de investigación académica real. Las skills de Superpowers usan estos principios intencionalmente - por eso funcionan incluso cuando el agente quiere tomar atajos.*

[📈 Skill: TJR Price Action - Estrategia Completa]# Skill: TJR Price Action - Estrategia Completa

Esta skill contiene la estrategia completa de TJR Price Action extraída del curso de 9 horas. Formato listo para usar como skill en Claude Code/AntiGravity.

---

## Frontmatter de la Skill

```yaml
---
name: tjr-price-action
description: "Usar cuando analices charts, identifiques setups, o tomes decisiones de trading. Contiene la metodología completa de TJR para estructura de mercado, liquidez, order blocks, y entradas."
---
```

---

# La Estrategia Completa

## 1. ESTRUCTURA DE MERCADO

### Definiciones Fundamentales

**HIGH VÁLIDO:**

- Vela verde seguida de vela roja
- El high de la vela verde es el "high"

**LOW VÁLIDO:**

- Vela roja seguida de vela verde
- El low de la vela roja es el "low"

### Tendencias

**ALCISTA (Bullish):**

```
    HH
   /
  HL
 /
HH
```

- Higher Highs (HH) + Higher Lows (HL)
- Buscar COMPRAS

**BAJISTA (Bearish):**

```
LH
 \
  LL
   \
    LH
```

- Lower Highs (LH) + Lower Lows (LL)
- Buscar VENTAS

### Break of Structure (BOS)

**BOS ALCISTA:**

- Vela CIERRA (cuerpo, no mecha) ARRIBA del high anterior
- Confirma continuación alcista

**BOS BAJISTA:**

- Vela CIERRA (cuerpo, no mecha) ABAJO del low anterior
- Confirma continuación bajista

**IMPORTANTE:** El cierre del cuerpo es lo que cuenta, no la mecha.

---

## 2. LIQUIDEZ

### Concepto Central

> **El mercado es un imán de liquidez. Siempre busca los stop losses.**
> 

### Dónde Está la Liquidez

**Arriba de highs:**

- Stop losses de ventas
- El mercado los "barre" antes de bajar

**Abajo de lows:**

- Stop losses de compras
- El mercado los "barre" antes de subir

### Sweep de Liquidez

```
     [Sweep]
        |
    ───────  <-- High anterior
       /
      /
     /
[Entrada después del sweep]
```

**Pattern:**

1. Precio rompe un high/low (barre stop losses)
2. Inmediatamente revierte
3. ESTA es la entrada de alta probabilidad

---

## 3. ORDER BLOCKS

### Definición

> **El último movimiento contrario antes de un sweep + BOS**
> 

### Identificación

**Order Block Alcista:**

```
1. Mercado hace sweep de low
2. BOS alcista ocurre
3. Última vela ROJA antes del movimiento = Order Block
4. Esperar que precio regrese a esa zona para comprar
```

**Order Block Bajista:**

```
1. Mercado hace sweep de high
2. BOS bajista ocurre
3. Última vela VERDE antes del movimiento = Order Block
4. Esperar que precio regrese a esa zona para vender
```

### Validación de Order Block

- DEBE haber sweep de liquidez antes
- DEBE haber BOS después
- Sin sweep + BOS = NO es Order Block válido

---

## 4. FAIR VALUE GAP (FVG)

### Definición

> **Espacio donde las mechas de vela 1 y vela 3 NO se tocan**
> 

### Identificación

```
Vela 1    Vela 2    Vela 3
  |         |         |
  |        |||        |
  |       |||||       |
 |||     |||||||     |||
||||    |||||||||   ||||
        ^^^^^^^^^
        FVG (gap)
```

**El FVG es:**

- Desde el high de vela 1 hasta el low de vela 3 (FVG alcista)
- Desde el low de vela 1 hasta el high de vela 3 (FVG bajista)

### Uso

- El mercado tiende a "llenar" el FVG
- Zona de entrada cuando el precio regresa
- Combinado con Order Block = setup de alta probabilidad

---

## 5. EQUILIBRIUM (50%)

### Concepto

> **El 50% de cualquier rango es el equilibrio**
> 

### Aplicación

**Comprar en DESCUENTO (<50%):**

- Precio debajo del equilibrio
- Zona favorable para compras

**Vender en PREMIUM (>50%):**

- Precio arriba del equilibrio
- Zona favorable para ventas

### Cálculo

```python
equilibrium = (range_high + range_low) / 2

# Si precio < equilibrium = descuento (comprar)
# Si precio > equilibrium = premium (vender)
```

---

## 6. BREAKER BLOCK

### Definición

> **Order Block que FALLÓ. Ahora actúa como soporte/resistencia inversa.**
> 

### Pattern

```
1. Order Block identificado
2. Precio rompe el Order Block (falla)
3. El Order Block ahora es Breaker Block
4. Actua como zona de reacción inversa
```

---

## 7. ESTRATEGIA DE ENTRADA (SISTEMÁTICA)

### Paso 1: Determinar BIAS (4H)

- Ver estructura en 4H
- HH/HL = Bias alcista (solo compras)
- LH/LL = Bias bajista (solo ventas)

### Paso 2: Verificar Alineación (1H)

| 4H | 1H | Timeframe de Entrada |
| --- | --- | --- |
| Alcista | Alcista | 5m |
| Alcista | Bajista | 15m |
| Bajista | Bajista | 5m |
| Bajista | Alcista | 15m |

### Paso 3: ESPERAR Confluencia

**"Manos en el culo" hasta que ocurra UNO de estos:**

1. Sweep de high/low de 1H/4H
2. Toque de Order Block de 1H/4H
3. Toque de FVG de 1H/4H

**SI NO HAY CONFLUENCIA = NO HAY TRADE**

### Paso 4: Confirmación (LTF)

- En el timeframe de entrada (5m o 15m)
- Esperar BOS en dirección del bias
- SOLO ENTONCES considerar entrada

### Paso 5: Entrada

**Zonas de entrada (dentro del nuevo rango):**

- FVG del movimiento
- Order Block del movimiento
- Breaker Block
- Equilibrio (50%)

---

## 8. KILLZONES

### ÚNICAS Horas para Tradear

| Sesión | Hora (New York) | Hora (México) |
| --- | --- | --- |
| AM Killzone | 9:50 - 10:10 AM | 7:50 - 8:10 AM |
| PM Killzone | 1:50 - 2:10 PM | 11:50 AM - 12:10 PM |

**FUERA de killzones = NO TRADEAR**

---

## 9. MANEJO DE RIESGO

### Stop Loss

| Tipo | Dónde |
| --- | --- |
| Conservador | Detrás del sweep |
| Moderado | Detrás del OB/FVG |
| Agresivo | Detrás de estructura interna |

### Take Profit

- Siguiente zona de liquidez opuesta
- Order Block/FVG opuesto
- **NUNCA usar R:R fijos** (1:2, 1:3, etc.)

### Reglas Inquebrantables

1. **NUNCA** mover SL para ampliar pérdida
2. **NUNCA** mover TP por codicia
3. **SIEMPRE** tener límite de pérdida diaria
4. **SIEMPRE** respetar killzones

---

## 10. MERCADOS

**Recomendados:**

- Futuros/Índices: ES, NQ
- Forex: GBP/JPY, Gold
- Crypto: Bitcoin

---

## 11. REGLAS PSICOLÓGICAS

> "Trading es predecir movimiento de precio con alta probabilidad. El dinero es efecto secundario."
> 

**Las Reglas:**

1. Un solo mentor (no mezclar TJR con otros YouTubers)
2. Una sola estrategia
3. Pensar en décadas, no días
4. 98% fallan porque abandonan, no porque sea difícil

---

## 12. CHECKLIST DE ENTRADA

Antes de CUALQUIER trade:

- [ ]  ¿Tengo bias claro en 4H?
- [ ]  ¿El bias de 1H está definido?
- [ ]  ¿Estoy en el timeframe de entrada correcto?
- [ ]  ¿Hubo sweep de liquidez O toque de OB/FVG?
- [ ]  ¿Hay BOS en mi dirección en LTF?
- [ ]  ¿Mi entrada está en zona válida (FVG/OB/Breaker/50%)?
- [ ]  ¿Estoy dentro de killzone?
- [ ]  ¿Tengo SL definido?
- [ ]  ¿Tengo TP en zona de liquidez opuesta?
- [ ]  ¿Este trade respeta mi límite de pérdida diaria?

**Si alguna respuesta es NO = NO TRADE**

---

*Esta skill contiene la metodología completa de TJR Price Action. Úsala como referencia constante cuando analices charts o tomes decisiones de trading.*

[🚀 Trading Bot v2 - Roadmap Completo]# Trading Bot v2 - Roadmap de Implementación

Este es el plan completo para construir tu bot de trading usando las skills de Superpowers + la estrategia TJR Price Action.

---

## Por Qué v1 Falló

| Qué pasó | Skill que lo habría prevenido |
| --- | --- |
| Asumiste que funcionaba sin verificar | verification-before-completion |
| No tenías tests | test-driven-development |
| Señales diferentes en dispositivos | Tests automatizados |
| "El bot es infalible" | brainstorming (pensar edge cases) |
| Fuiste a real sin paper trading | Disciplina de proceso |

---

## El Plan

### FASE 0: Setup del Ambiente (1-2 días)

**Objetivo:** Tener todo listo para empezar a construir

**Tareas:**

- [ ]  Instalar Claude Code o configurar AntiGravity
- [ ]  Crear repositorio `trading-bot-v2`
- [ ]  Crear archivo [`CLAUDE.md`](http://CLAUDE.md) con reglas del proyecto
- [ ]  Crear estructura de carpetas
- [ ]  Subir código limpio de bot v1 como referencia

**Estructura de carpetas:**

```
trading-bot-v2/
├── .agent/
│   └── skills/
│       ├── tjr-price-action/
│       │   └── [SKILL.md](http://SKILL.md)
│       ├── python-trading/
│       │   └── [SKILL.md](http://SKILL.md)
│       └── trading-debug/
│           └── [SKILL.md](http://SKILL.md)
├── core/
│   ├── market_[structure.py](http://structure.py)
│   ├── [liquidity.py](http://liquidity.py)
│   ├── order_[blocks.py](http://blocks.py)
│   ├── [fvg.py](http://fvg.py)
│   └── [equilibrium.py](http://equilibrium.py)
├── strategy/
│   ├── [bias.py](http://bias.py)
│   ├── [entry.py](http://entry.py)
│   └── [exit.py](http://exit.py)
├── execution/
│   ├── [broker.py](http://broker.py)
│   └── [orders.py](http://orders.py)
├── utils/
│   ├── [logging.py](http://logging.py)
│   └── [timezone.py](http://timezone.py)
├── tests/
│   ├── test_market_[structure.py](http://structure.py)
│   ├── test_[liquidity.py](http://liquidity.py)
│   └── ...
├── docs/
│   └── plans/
└── [CLAUDE.md](http://CLAUDE.md)
```

**Contenido de [CLAUDE.md](http://CLAUDE.md):**

```markdown
# Trading Bot v2

## Reglas Inquebrantables

1. NUNCA escribir código sin test que falle primero
2. NUNCA decir "funciona" sin correr tests
3. NUNCA commitear sin verificación
4. Una sola fuente de datos (TradingView/broker)
5. Una sola timezone (New York)
6. Límite de pérdida diaria siempre activo

## Skills Disponibles

- tjr-price-action: Estrategia de trading
- python-trading: Patrones de código reutilizables
- trading-debug: Troubleshooting común

## Flujo de Trabajo

1. brainstorming antes de features nuevas
2. writing-plans para crear el plan
3. TDD para cada paso
4. verification-before-completion antes de merge
```

---

### FASE 1: Crear Skills (2-3 días)

**Objetivo:** Tener las skills listas para que el agente las use

**Tareas:**

**1.1 Skill: tjr-price-action**

- [ ]  Crear `.agent/skills/tjr-price-action/[SKILL.md](http://SKILL.md)`
- [ ]  Copiar contenido de la página "TJR Price Action - Estrategia Completa"
- [ ]  Verificar que el frontmatter está correcto

**1.2 Skill: python-trading**

- [ ]  Crear `.agent/skills/python-trading/[SKILL.md](http://SKILL.md)`
- [ ]  Incluir patrones comunes:
    - Estructura de velas (OHLC)
    - Cálculo de highs/lows
    - Detección de BOS
    - Manejo de timezone

**1.3 Skill: trading-debug**

- [ ]  Crear `.agent/skills/trading-debug/[SKILL.md](http://SKILL.md)`
- [ ]  Incluir problemas comunes:
    - Errores de broker/API
    - Problemas de datos
    - Timezone mismatches
    - Señales diferentes entre dispositivos

---

### FASE 2: Arquitectura (3-5 días)

**Objetivo:** Diseñar la arquitectura antes de codear

**Usar skill:** `brainstorming`

**Preguntas a responder:**

1. ¿De dónde vienen los datos? (TradingView, broker API, websocket?)
2. ¿Cómo se almacenan las velas? (pandas DataFrame, SQLite, en memoria?)
3. ¿Cómo se detecta la estructura? (por vela, por batch, por timeframe?)
4. ¿Cómo se sincronizan timeframes? (4H → 1H → 5m)
5. ¿Cómo se ejecutan órdenes? (API de broker, manual alert?)
6. ¿Cómo se manejan errores? (retry, alert, stop?)

**Output:** `docs/plans/[YYYY-MM-DD-trading-bot-architecture.md](http://YYYY-MM-DD-trading-bot-architecture.md)`

---

### FASE 3: Plan de Implementación (2-3 días)

**Objetivo:** Crear plan detallado paso a paso

**Usar skill:** `writing-plans`

**Módulos a planear:**

| Módulo | Funcionalidad | Prioridad |
| --- | --- | --- |
| market_[structure.py](http://structure.py) | Detectar HH/HL/LH/LL y BOS | 1 |
| [liquidity.py](http://liquidity.py) | Identificar zonas de liquidez | 2 |
| order_[blocks.py](http://blocks.py) | Detectar Order Blocks válidos | 3 |
| [fvg.py](http://fvg.py) | Identificar Fair Value Gaps | 4 |
| [equilibrium.py](http://equilibrium.py) | Calcular 50% de rangos | 5 |
| [bias.py](http://bias.py) | Determinar bias por timeframe | 6 |
| [entry.py](http://entry.py) | Lógica de entrada | 7 |
| [exit.py](http://exit.py) | Lógica de salida (SL/TP) | 8 |

**Output:** `docs/plans/[YYYY-MM-DD-trading-bot-implementation.md](http://YYYY-MM-DD-trading-bot-implementation.md)`

---

### FASE 4: Implementación con TDD (5-7 días)

**Objetivo:** Construir el bot siguiendo TDD estricto

**Usar skills:** `executing-plans` + `test-driven-development`

**Para CADA función:**

```
1. Escribir test que falla
2. Correr test, verificar que falla
3. Escribir código MÍNIMO para pasar
4. Correr test, verificar que pasa
5. Commit
6. Siguiente función
```

**Ejemplo para detect_high():**

```python
# Paso 1: Test que falla
def test_detect_valid_high():
    candles = [
        {"open": 100, "high": 110, "low": 95, "close": 108},  # verde
        {"open": 108, "high": 109, "low": 100, "close": 102},  # roja
    ]
    assert detect_high(candles, index=0) == True

# Paso 2: Correr - DEBE fallar con "detect_high not defined"

# Paso 3: Implementación mínima
def detect_high(candles, index):
    if index + 1 >= len(candles):
        return False
    current = candles[index]
    next_c = candles[index + 1]
    is_green = current["close"] > current["open"]
    next_is_red = next_c["close"] < next_c["open"]
    return is_green and next_is_red

# Paso 4: Correr - DEBE pasar

# Paso 5: Commit
```

---

### FASE 5: Backtesting (3-5 días)

**Objetivo:** Probar el bot con datos históricos

**Tareas:**

- [ ]  Obtener datos históricos de killzones
- [ ]  Correr bot en modo simulación
- [ ]  Registrar: entradas, salidas, P&L, win rate
- [ ]  Analizar resultados

**Métricas a trackear:**

- Win rate
- Average R:R
- Max drawdown
- Trades por día/semana
- Accuracy de detección de estructura

---

### FASE 6: Paper Trading (30+ días MÍNIMO)

**Objetivo:** Validar en tiempo real sin arriesgar dinero

**Usar skill:** `verification-before-completion`

**Setup:**

- [ ]  Conectar a cuenta demo del broker
- [ ]  Bot ejecuta con dinero falso
- [ ]  Journaling obligatorio por trade

**Journal por trade:**

```
Fecha: YYYY-MM-DD
Hora: HH:MM (NY time)
Par: ES/NQ/BTC
Dirección: Long/Short
Bias 4H: Alcista/Bajista
Bias 1H: Alcista/Bajista
Confluencia: Sweep/OB/FVG
Entrada: $XXX
SL: $XXX
TP: $XXX
Resultado: Win/Loss
P&L: +$XX / -$XX
Screenshot: [link]
Notas: Qué salió bien/mal
```

**Review semanal:**

- Win rate de la semana
- ¿Mala ejecución o mala estrategia?
- ¿El bot detectó correctamente?
- ¿Qué ajustar?

**Criterios para pasar a real:**

- [ ]  30 días MÍNIMO de paper trading
- [ ]  Win rate > 50%
- [ ]  R:R promedio > 1:1.5
- [ ]  Max drawdown definido y respetado
- [ ]  0 bugs críticos en las últimas 2 semanas

---

### FASE 7: Real (Solo si FASE 6 exitosa)

**Reglas para ir a real:**

1. **Capital mínimo** - No todo tu dinero
2. **Límite de pérdida diaria** - Configurado y respetado
3. **Primeras 2 semanas** - Tamaño de posición reducido (25%)
4. **Monitoreo constante** - No dejar el bot solo las primeras semanas
5. **Kill switch** - Botón para apagar todo inmediatamente

---

## Timeline Estimado

| Fase | Duración | Total |
| --- | --- | --- |
| 0. Setup | 1-2 días | 2 días |
| 1. Skills | 2-3 días | 5 días |
| 2. Arquitectura | 3-5 días | 10 días |
| 3. Plan | 2-3 días | 13 días |
| 4. Implementación | 5-7 días | 20 días |
| 5. Backtesting | 3-5 días | 25 días |
| 6. Paper Trading | 30+ días | 55+ días |
| 7. Real | - | - |

**Total antes de dinero real: ~2 meses MÍNIMO**

---

## Reglas Inquebrantables

1. **TDD no es opcional** - Test antes de código, siempre
2. **Paper trading no es opcional** - 30 días mínimo
3. **Una sola fuente de datos** - No más señales diferentes
4. **Una sola timezone** - New York, siempre
5. **Límite de pérdida diaria** - Configurado desde día 1
6. **El bot NO es infalible** - Nunca, jamás, ever

---

*Este roadmap está diseñado para que NO repitas los errores de v1. Sigue cada fase. No te saltes nada. La disciplina es lo que separa a los traders rentables de los que pierden todo.*

# Skill: TJR Price Action - Estrategia Completa

Esta skill contiene la estrategia completa de TJR Price Action extraída del curso de 9 horas. Formato listo para usar como skill en Claude Code/AntiGravity.

---

## Frontmatter de la Skill

```yaml
---
name: tjr-price-action
description: "Usar cuando analices charts, identifiques setups, o tomes decisiones de trading. Contiene la metodología completa de TJR para estructura de mercado, liquidez, order blocks, y entradas."
---
```

---

# La Estrategia Completa

## 1. ESTRUCTURA DE MERCADO

### Definiciones Fundamentales

**HIGH VÁLIDO:**

- Vela verde seguida de vela roja
- El high de la vela verde es el "high"

**LOW VÁLIDO:**

- Vela roja seguida de vela verde
- El low de la vela roja es el "low"

### Tendencias

**ALCISTA (Bullish):**

```
    HH
   /
  HL
 /
HH
```

- Higher Highs (HH) + Higher Lows (HL)
- Buscar COMPRAS

**BAJISTA (Bearish):**

```
LH
 \
  LL
   \
    LH
```

- Lower Highs (LH) + Lower Lows (LL)
- Buscar VENTAS

### Break of Structure (BOS)

**BOS ALCISTA:**

- Vela CIERRA (cuerpo, no mecha) ARRIBA del high anterior
- Confirma continuación alcista

**BOS BAJISTA:**

- Vela CIERRA (cuerpo, no mecha) ABAJO del low anterior
- Confirma continuación bajista

**IMPORTANTE:** El cierre del cuerpo es lo que cuenta, no la mecha.

---

## 2. LIQUIDEZ

### Concepto Central

> **El mercado es un imán de liquidez. Siempre busca los stop losses.**
> 

### Dónde Está la Liquidez

**Arriba de highs:**

- Stop losses de ventas
- El mercado los "barre" antes de bajar

**Abajo de lows:**

- Stop losses de compras
- El mercado los "barre" antes de subir

### Sweep de Liquidez

```
     [Sweep]
        |
    ───────  <-- High anterior
       /
      /
     /
[Entrada después del sweep]
```

**Pattern:**

1. Precio rompe un high/low (barre stop losses)
2. Inmediatamente revierte
3. ESTA es la entrada de alta probabilidad

---

## 3. ORDER BLOCKS

### Definición

> **El último movimiento contrario antes de un sweep + BOS**
> 

### Identificación

**Order Block Alcista:**

```
1. Mercado hace sweep de low
2. BOS alcista ocurre
3. Última vela ROJA antes del movimiento = Order Block
4. Esperar que precio regrese a esa zona para comprar
```

**Order Block Bajista:**

```
1. Mercado hace sweep de high
2. BOS bajista ocurre
3. Última vela VERDE antes del movimiento = Order Block
4. Esperar que precio regrese a esa zona para vender
```

### Validación de Order Block

- DEBE haber sweep de liquidez antes
- DEBE haber BOS después
- Sin sweep + BOS = NO es Order Block válido

---

## 4. FAIR VALUE GAP (FVG)

### Definición

> **Espacio donde las mechas de vela 1 y vela 3 NO se tocan**
> 

### Identificación

```
Vela 1    Vela 2    Vela 3
  |         |         |
  |        |||        |
  |       |||||       |
 |||     |||||||     |||
||||    |||||||||   ||||
        ^^^^^^^^^
        FVG (gap)
```

**El FVG es:**

- Desde el high de vela 1 hasta el low de vela 3 (FVG alcista)
- Desde el low de vela 1 hasta el high de vela 3 (FVG bajista)

### Uso

- El mercado tiende a "llenar" el FVG
- Zona de entrada cuando el precio regresa
- Combinado con Order Block = setup de alta probabilidad

---

## 5. EQUILIBRIUM (50%)

### Concepto

> **El 50% de cualquier rango es el equilibrio**
> 

### Aplicación

**Comprar en DESCUENTO (<50%):**

- Precio debajo del equilibrio
- Zona favorable para compras

**Vender en PREMIUM (>50%):**

- Precio arriba del equilibrio
- Zona favorable para ventas

### Cálculo

```python
equilibrium = (range_high + range_low) / 2

# Si precio < equilibrium = descuento (comprar)
# Si precio > equilibrium = premium (vender)
```

---

## 6. BREAKER BLOCK

### Definición

> **Order Block que FALLÓ. Ahora actúa como soporte/resistencia inversa.**
> 

### Pattern

```
1. Order Block identificado
2. Precio rompe el Order Block (falla)
3. El Order Block ahora es Breaker Block
4. Actua como zona de reacción inversa
```

---

## 7. ESTRATEGIA DE ENTRADA (SISTEMÁTICA)

### Paso 1: Determinar BIAS (4H)

- Ver estructura en 4H
- HH/HL = Bias alcista (solo compras)
- LH/LL = Bias bajista (solo ventas)

### Paso 2: Verificar Alineación (1H)

| 4H | 1H | Timeframe de Entrada |
| --- | --- | --- |
| Alcista | Alcista | 5m |
| Alcista | Bajista | 15m |
| Bajista | Bajista | 5m |
| Bajista | Alcista | 15m |

### Paso 3: ESPERAR Confluencia

**"Manos en el culo" hasta que ocurra UNO de estos:**

1. Sweep de high/low de 1H/4H
2. Toque de Order Block de 1H/4H
3. Toque de FVG de 1H/4H

**SI NO HAY CONFLUENCIA = NO HAY TRADE**

### Paso 4: Confirmación (LTF)

- En el timeframe de entrada (5m o 15m)
- Esperar BOS en dirección del bias
- SOLO ENTONCES considerar entrada

### Paso 5: Entrada

**Zonas de entrada (dentro del nuevo rango):**

- FVG del movimiento
- Order Block del movimiento
- Breaker Block
- Equilibrio (50%)

---

## 8. KILLZONES

### ÚNICAS Horas para Tradear

| Sesión | Hora (New York) | Hora (México) |
| --- | --- | --- |
| AM Killzone | 9:50 - 10:10 AM | 7:50 - 8:10 AM |
| PM Killzone | 1:50 - 2:10 PM | 11:50 AM - 12:10 PM |

**FUERA de killzones = NO TRADEAR**

---

## 9. MANEJO DE RIESGO

### Stop Loss

| Tipo | Dónde |
| --- | --- |
| Conservador | Detrás del sweep |
| Moderado | Detrás del OB/FVG |
| Agresivo | Detrás de estructura interna |

### Take Profit

- Siguiente zona de liquidez opuesta
- Order Block/FVG opuesto
- **NUNCA usar R:R fijos** (1:2, 1:3, etc.)

### Reglas Inquebrantables

1. **NUNCA** mover SL para ampliar pérdida
2. **NUNCA** mover TP por codicia
3. **SIEMPRE** tener límite de pérdida diaria
4. **SIEMPRE** respetar killzones

---

## 10. MERCADOS

**Recomendados:**

- Futuros/Índices: ES, NQ
- Forex: GBP/JPY, Gold
- Crypto: Bitcoin

---

## 11. REGLAS PSICOLÓGICAS

> "Trading es predecir movimiento de precio con alta probabilidad. El dinero es efecto secundario."
> 

**Las Reglas:**

1. Un solo mentor (no mezclar TJR con otros YouTubers)
2. Una sola estrategia
3. Pensar en décadas, no días
4. 98% fallan porque abandonan, no porque sea difícil

---

## 12. CHECKLIST DE ENTRADA

Antes de CUALQUIER trade:

- [ ]  ¿Tengo bias claro en 4H?
- [ ]  ¿El bias de 1H está definido?
- [ ]  ¿Estoy en el timeframe de entrada correcto?
- [ ]  ¿Hubo sweep de liquidez O toque de OB/FVG?
- [ ]  ¿Hay BOS en mi dirección en LTF?
- [ ]  ¿Mi entrada está en zona válida (FVG/OB/Breaker/50%)?
- [ ]  ¿Estoy dentro de killzone?
- [ ]  ¿Tengo SL definido?
- [ ]  ¿Tengo TP en zona de liquidez opuesta?
- [ ]  ¿Este trade respeta mi límite de pérdida diaria?

**Si alguna respuesta es NO = NO TRADE**

---

*Esta skill contiene la metodología completa de TJR Price Action. Úsala como referencia constante cuando analices charts o tomes decisiones de trading.*

[🛠️ Cómo Crear Tus Propias Skills]# Cómo Crear Tus Propias Skills

Esta guía te enseña a crear skills efectivas para cualquier proyecto - ya sea tu bot de trading, FEUX, o cualquier otra cosa.

---

## Anatomía de una Skill

### Estructura de Archivos

```
.agent/skills/nombre-de-skill/
├── [SKILL.md](http://SKILL.md)          # REQUERIDO - El contenido principal
├── scripts/          # Opcional - Scripts ejecutables
├── examples/         # Opcional - Implementaciones de referencia
└── resources/        # Opcional - Templates, assets
```

### Frontmatter Obligatorio

```yaml
---
name: nombre-en-minusculas-con-guiones
description: "Usar cuando [condición] - [qué hace]; [contexto adicional]"
---
```

**Reglas del name:**

- Forma de gerundio preferida ("using-", "writing-", "debugging-")
- Minúsculas
- Solo guiones (no underscores)
- Máximo 64 caracteres

**Reglas de la description:**

- Tercera persona
- Empieza con "Usar cuando..."
- Incluye triggers que activan la skill
- Máximo 1024 caracteres

---

## Tipos de Skills

### 1. Skills de Disciplina

**Propósito:** Imponer comportamiento específico

**Características:**

- Lenguaje fuerte: "DEBES", "NUNCA", "Sin excepciones"
- Reglas claras sin ambigüedad
- Anti-racionalización explícita
- Checklists obligatorios

**Ejemplos:** TDD, verification-before-completion

**Template:**

```markdown
---
name: nombre-de-skill
description: "Usar cuando [trigger] - requiere [acción]; [contexto]"
---

# Nombre de Skill

## LA LEY DE HIERRO

```

[REGLA ABSOLUTA EN MAYÚSCULAS]

```

## El Proceso

[Pasos numerados, claros, sin ambigüedad]

## Red Flags - PARA

[Lista de pensamientos que indican racionalización]

## Racionalizaciones Comunes

| Excusa | Realidad |
|--------|----------|
| "[excusa]" | [por qué no aplica] |

## Checklist

- [ ] [Item verificable]
- [ ] [Item verificable]
```

---

### 2. Skills de Guía/Técnica

**Propósito:** Enseñar cómo hacer algo

**Características:**

- Más flexible que disciplina
- Principios > reglas absolutas
- Ejemplos concretos
- Adaptable al contexto

**Ejemplos:** brainstorming, TJR Price Action

**Template:**

```markdown
---
name: nombre-de-skill
description: "Usar cuando [trigger] - [qué hace]"
---

# Nombre de Skill

## Resumen

[1-2 párrafos explicando el propósito]

## El Proceso

### Paso 1: [Nombre]
[Explicación]

### Paso 2: [Nombre]
[Explicación]

## Principios Clave

| Principio | Descripción |
|-----------|-------------|
| [Nombre] | [Descripción] |

## Ejemplos

[Ejemplos concretos de aplicación]
```

---

### 3. Skills de Referencia

**Propósito:** Documentar información para consulta

**Características:**

- Sin persuasión
- Solo información clara
- Fácil de escanear
- Tablas y listas

**Ejemplos:** testing-anti-patterns, API docs

**Template:**

```markdown
---
name: nombre-de-skill
description: "Cargar cuando [situación] - referencia para [tema]"
---

# Nombre de Skill

## Referencia Rápida

| Situación | Solución |
|-----------|----------|
| [caso] | [qué hacer] |

## [Sección 1]

[Información detallada]

## [Sección 2]

[Información detallada]
```

---

## Principios de Escritura

### 1. Concisión

- Máximo 500 líneas por skill
- Si es más largo, dividir en múltiples skills
- Cada oración debe agregar valor

### 2. Divulgación Progresiva

- Lo más importante primero
- Detalles después
- El agente puede dejar de leer en cualquier momento y aún entender lo esencial

### 3. Grados de Libertad

| Elemento | Libertad | Ejemplo |
| --- | --- | --- |
| Bullets | Alta | Orden puede variar |
| Bloques de código | Media | Adaptar al contexto |
| Comandos bash | Baja | Ejecutar exactamente |

### 4. Solo Forward Slashes

```
✅ path/to/[file.py](http://file.py)
❌ path\to\[file.py](http://file.py)
```

---

## Usando Persuasión Efectivamente

### Para Skills de Disciplina

**Usa:**

- **Autoridad:** "DEBES", "NUNCA", "Sin excepciones"
- **Compromiso:** "Anuncia que vas a usar esta skill"
- **Prueba Social:** "Esto siempre falla si no lo sigues"

**Evita:**

- Lenguaje suave: "considera", "podrías", "tal vez"
- Opcionalidad: "si quieres", "cuando sea conveniente"

### Para Skills de Guía

**Usa:**

- **Unidad:** "Nuestro objetivo es..."
- **Autoridad moderada:** "Siempre busca...", "Prefiere..."

**Evita:**

- Exceso de autoridad (no es disciplina)
- Falta de estructura

---

## Ejemplos de Skills para FEUX

### Skill: Cliente Onboarding

```markdown
---
name: cliente-onboarding
description: "Usar cuando se cierra un nuevo cliente de FEUX - proceso completo de onboarding desde firma hasta activación"
---

# Cliente Onboarding

## El Proceso

### Día 0: Cierre
- [ ] Contrato firmado
- [ ] Pago inicial recibido
- [ ] Datos del negocio recolectados

### Día 1-3: Setup
- [ ] WhatsApp Business configurado
- [ ] n8n workflows creados
- [ ] Integraciones conectadas

### Día 4-5: Testing
- [ ] Pruebas internas completadas
- [ ] Cliente hace prueba
- [ ] Ajustes necesarios

### Día 6-7: Lanzamiento
- [ ] Capacitación al cliente
- [ ] Go-live
- [ ] Monitoreo 24h

## Checklist de Activación

- [ ] WhatsApp responde mensajes
- [ ] Pedidos se registran correctamente
- [ ] Cliente sabe usar el dashboard
- [ ] Soporte configurado
```

### Skill: n8n Troubleshooting

```markdown
---
name: n8n-troubleshooting
description: "Cargar cuando un workflow de n8n falla - referencia de errores comunes y soluciones"
---

# n8n Troubleshooting

## Errores Comunes

| Error | Causa | Solución |
|-------|-------|----------|
| "Connection refused" | Servicio caído | Verificar que n8n esté corriendo |
| "Invalid credentials" | Token expirado | Reconectar la integración |
| "Timeout" | Request muy largo | Aumentar timeout o dividir batch |
| "Rate limited" | Demasiadas requests | Agregar delays entre requests |

## Debugging de Webhooks

1. Verificar URL del webhook
2. Probar con curl/Postman
3. Revisar logs de n8n
4. Verificar firewall/proxy

## Debugging de WhatsApp

1. Verificar que Evolution API esté conectada
2. Revisar estado de la sesión
3. Verificar número de destino
4. Revisar rate limits
```

---

## Checklist para Nueva Skill

Antes de usar tu skill:

- [ ]  Frontmatter correcto (name, description)
- [ ]  Name en minúsculas con guiones
- [ ]  Description empieza con "Usar cuando..."
- [ ]  Menos de 500 líneas
- [ ]  Lo más importante está al inicio
- [ ]  Ejemplos concretos incluidos
- [ ]  Si es disciplina: lenguaje fuerte + anti-racionalización
- [ ]  Si es guía: principios claros + proceso
- [ ]  Si es referencia: tablas fáciles de escanear

---

*Las skills bien escritas son la diferencia entre un agente que hace lo que quieres y uno que racionaliza para tomar atajos. Invierte tiempo en escribirlas bien.*

[🎯 Quick Reference - Cheat Sheet]# 🎯 Quick Reference - Cheat Sheet

Imprimir esto y tenerlo a la mano mientras desarrollas.

---

## Antes de CUALQUIER Tarea

```
¿Podría aplicar alguna skill? (aunque sea 1%)
    ↓ SÍ
Invocar la skill
    ↓
Anunciar: "Estoy usando [skill] para [propósito]"
    ↓
Seguir la skill EXACTAMENTE
```

---

## TDD en 30 Segundos

```
🔴 RED: Escribir test que falla
    ↓
Correr test - VER QUE FALLA
    ↓
🟢 GREEN: Código MÍNIMO para pasar
    ↓
Correr test - VER QUE PASA
    ↓
🔵 REFACTOR: Limpiar (mantener verde)
    ↓
Commit
    ↓
Repetir
```

**¿Escribiste código antes del test? BÓRRALO.**

---

## Antes de Decir "Funciona"

```
1. ¿Qué comando prueba que funciona?
2. CORRER el comando
3. LEER el output completo
4. ¿Hay 0 fallas?
5. SOLO ENTONCES: "Funciona"
```

**Si no corriste el comando, NO puedes decir que funciona.**

---

## Flujo de Desarrollo

```
1. BRAINSTORMING
   → docs/plans/[YYYY-MM-DD-design.md](http://YYYY-MM-DD-design.md)

2. WRITING-PLANS
   → docs/plans/[YYYY-MM-DD-implementation.md](http://YYYY-MM-DD-implementation.md)

3. EXECUTING-PLANS + TDD
   → Código con tests

4. VERIFICATION
   → Todos los tests pasan

5. CODE-REVIEW
   → Aprobado

6. FINISHING-BRANCH
   → Merge/PR
```

---

## TJR Entry Checklist

- [ ]  Bias 4H definido
- [ ]  Bias 1H definido
- [ ]  Timeframe de entrada correcto (5m o 15m)
- [ ]  Confluencia presente (sweep/OB/FVG)
- [ ]  BOS en LTF en dirección del bias
- [ ]  Entrada en zona válida
- [ ]  Dentro de killzone
- [ ]  SL definido
- [ ]  TP en liquidez opuesta
- [ ]  Respeta límite de pérdida diaria

**Si alguno es NO = NO TRADE**

---

## Killzones (New York Time)

| Sesión | NY Time | México Time |
| --- | --- | --- |
| AM | 9:50-10:10 | 7:50-8:10 |
| PM | 1:50-2:10 | 11:50-12:10 |

---

## Racionalizaciones = PARA

| Si piensas esto... | Haz esto... |
| --- | --- |
| "Es simple, no necesito skill" | BUSCA LA SKILL |
| "Ya sé cómo hacerlo" | BUSCA LA SKILL |
| "Solo esta vez" | SIGUE EL PROCESO |
| "Debería funcionar" | CORRE EL TEST |
| "Ya lo testeé manualmente" | ESCRIBE EL TEST |
| "Borrar X horas es desperdicio" | BÓRRALO |

---

## Comandos Útiles

```bash
# Correr tests
pytest tests/ -v

# Correr un test específico
pytest tests/test_[file.py](http://file.py)::test_name -v

# Ver cobertura
pytest --cov=src tests/

# Git worktree
git worktree add .worktrees/feature -b feature/name
```

---

## Estructura de Market Structure

```
ALCISTA (Bullish):
    HH
   /
  HL
 /
HH

BAJISTA (Bearish):
LH
 \
  LL
   \
    LH
```

**BOS = Cierre de CUERPO arriba/abajo del high/low anterior**

---

## High/Low Válido

```
HIGH VÁLIDO:
Vela verde → Vela roja
(el high de la verde es el "high")

LOW VÁLIDO:
Vela roja → Vela verde
(el low de la roja es el "low")
```

---

## Alineación de Timeframes

| 4H | 1H | Entrada |
| --- | --- | --- |
| ↑ Alcista | ↑ Alcista | 5m |
| ↑ Alcista | ↓ Bajista | 15m |
| ↓ Bajista | ↓ Bajista | 5m |
| ↓ Bajista | ↑ Alcista | 15m |

---

## Stop Loss

| Tipo | Dónde |
| --- | --- |
| Conservador | Detrás del sweep |
| Moderado | Detrás del OB/FVG |
| Agresivo | Detrás de estructura interna |

---

## Reglas Inquebrantables

1. ❌ NUNCA código sin test primero
2. ❌ NUNCA "funciona" sin verificar
3. ❌ NUNCA trade sin confluencia
4. ❌ NUNCA fuera de killzones
5. ❌ NUNCA mover SL para ampliar pérdida
6. ❌ NUNCA saltar paper trading
7. ✅ SIEMPRE usar skills
8. ✅ SIEMPRE verificar antes de clamar
9. ✅ SIEMPRE una sola fuente de datos
10. ✅ SIEMPRE una sola timezone (NY)

---

*Esta página es tu brújula. Consúltala constantemente.*
[📘 Anthropic Best Practices - Guía Oficial]# Anthropic Best Practices - Guía Oficial para Escribir Skills

Esta es la documentación **OFICIAL de Anthropic** sobre cómo escribir skills efectivas. Si vas a crear skills para tu bot, FEUX, o cualquier proyecto, esta es la referencia autoritativa.

**Fuente:** https://docs.anthropic.com/en/docs/agents-and-tools/agent-skills/best-practices

---

# Principios Fundamentales

## 1. La Concisión es Clave

> **El context window es un bien público.** Tu skill comparte espacio con todo lo demás que Claude necesita saber.
> 

**Suposición por defecto:** Claude ya es muy inteligente.

Solo agrega contexto que Claude NO tiene. Para cada pieza de información, pregunta:

- "¿Claude realmente necesita esta explicación?"
- "¿Puedo asumir que Claude sabe esto?"
- "¿Este párrafo justifica su costo en tokens?"

### Ejemplo

**✅ BIEN - Conciso (~50 tokens):**

```markdown
## Extraer texto de PDF

Usa pdfplumber para extracción de texto:

```

import pdfplumber

with [pdfplumber.open](http://pdfplumber.open)("file.pdf") as pdf:

text = pdf.pages[0].extract_text()

```

```

**❌ MAL - Muy verboso (~150 tokens):**

```markdown
## Extraer texto de PDF

PDF (Portable Document Format) son archivos comunes que contienen
texto, imágenes, y otro contenido. Para extraer texto de un PDF,
necesitarás usar una librería. Hay muchas librerías disponibles
para procesamiento de PDF, pero recomendamos pdfplumber porque
es fácil de usar y maneja la mayoría de casos bien...
```

La versión concisa asume que Claude sabe qué son los PDFs y cómo funcionan las librerías.

---

## 2. Grados de Libertad Apropiados

Ajusta el nivel de especificidad según la fragilidad y variabilidad de la tarea.

### Alta Libertad (instrucciones basadas en texto)

**Usar cuando:**

- Múltiples enfoques son válidos
- Las decisiones dependen del contexto
- Heurísticas guían el enfoque

```markdown
## Proceso de code review

1. Analizar estructura y organización del código
2. Buscar bugs potenciales o edge cases
3. Sugerir mejoras para legibilidad y mantenibilidad
4. Verificar adherencia a convenciones del proyecto
```

### Media Libertad (pseudocódigo o scripts con parámetros)

**Usar cuando:**

- Existe un patrón preferido
- Algo de variación es aceptable
- La configuración afecta el comportamiento

```markdown
## Generar reporte

Usa este template y customiza según necesites:

```

def generate_report(data, format="markdown", include_charts=True):

# Procesar datos

# Generar output en formato especificado

# Opcionalmente incluir visualizaciones

```

```

### Baja Libertad (scripts específicos, pocos o ningún parámetro)

**Usar cuando:**

- Las operaciones son frágiles y propensas a errores
- La consistencia es crítica
- Una secuencia específica debe seguirse

```markdown
## Migración de base de datos

Corre exactamente este script:

```

python scripts/[migrate.py](http://migrate.py) --verify --backup

```

No modifiques el comando ni agregues flags adicionales.
```

### Analogía

Piensa en Claude como un robot explorando un camino:

- **Puente angosto con acantilados:** Solo hay un camino seguro. Provee guardrails específicos e instrucciones exactas (baja libertad). Ejemplo: migraciones de DB que deben correr en secuencia exacta.
- **Campo abierto sin peligros:** Muchos caminos llevan al éxito. Da dirección general y confía en que Claude encuentre la mejor ruta (alta libertad). Ejemplo: code reviews donde el contexto determina el mejor enfoque.

---

## 3. Testear con Todos los Modelos

Las skills actúan como adiciones a los modelos, así que la efectividad depende del modelo subyacente.

| Modelo | Consideración |
| --- | --- |
| **Claude Haiku** (rápido, económico) | ¿La skill provee suficiente guía? |
| **Claude Sonnet** (balanceado) | ¿La skill es clara y eficiente? |
| **Claude Opus** (razonamiento poderoso) | ¿La skill evita sobre-explicar? |

Lo que funciona perfecto para Opus podría necesitar más detalle para Haiku.

---

# Estructura de Skills

## YAML Frontmatter

```yaml
---
name: nombre-de-skill
description: Descripción de qué hace y cuándo usarla
---
```

| Campo | Límite | Notas |
| --- | --- | --- |
| `name` | 64 caracteres máx | Forma gerundio preferida ("processing-", "analyzing-") |
| `description` | 1024 caracteres máx | Tercera persona, incluir triggers |

## Convenciones de Nombres

**✅ Buenos ejemplos (forma gerundio):**

- "Processing PDFs"
- "Analyzing spreadsheets"
- "Managing databases"
- "Testing code"
- "Writing documentation"

**❌ Evitar:**

- Nombres vagos: "Helper", "Utils", "Tools"
- Muy genéricos: "Documents", "Data", "Files"
- Patrones inconsistentes en tu colección de skills

## Escribir Descripciones Efectivas

> **SIEMPRE escribir en tercera persona.** La descripción se inyecta en el system prompt, y punto de vista inconsistente puede causar problemas de descubrimiento.
> 

**✅ Bien:** "Processes Excel files and generates reports"

**❌ Evitar:** "I can help you process Excel files"

**❌ Evitar:** "You can use this to process Excel files"

### Ejemplo de Descripción Efectiva

```yaml
description: Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction.
```

Incluye:

1. QUÉ hace la skill
2. CUÁNDO usarla (triggers)

---

# Patrones Avanzados

## Progressive Disclosure (Divulgación Progresiva)

No todo va en [SKILL.md](http://SKILL.md). Estructura archivos para que Claude cargue solo lo necesario:

```
bigquery-skill/
├── [SKILL.md](http://SKILL.md) (overview, apunta a archivos de referencia)
└── reference/
    ├── [finance.md](http://finance.md) (métricas de revenue)
    ├── [sales.md](http://sales.md) (datos de pipeline)
    └── [product.md](http://product.md) (analytics de uso)
```

Cuando el usuario pregunta sobre revenue, Claude lee [SKILL.md](http://SKILL.md), ve la referencia a `reference/[finance.md](http://finance.md)`, y lee solo ese archivo. Los otros archivos permanecen en el filesystem, consumiendo cero tokens de contexto hasta que se necesiten.

## Patrón Plan-Validate-Execute

Para tareas complejas y abiertas, Claude puede cometer errores. El patrón "plan-validate-execute" atrapa errores temprano:

```
analizar → crear archivo de plan → validar plan → ejecutar → verificar
```

**Por qué funciona:**

- **Atrapa errores temprano:** La validación encuentra problemas antes de aplicar cambios
- **Verificable por máquina:** Scripts proveen verificación objetiva
- **Planning reversible:** Claude puede iterar en el plan sin tocar originales
- **Debugging claro:** Mensajes de error apuntan a problemas específicos

**Cuándo usar:** Operaciones batch, cambios destructivos, reglas de validación complejas, operaciones de alto riesgo.

## Referencias a MCP Tools

Si tu skill usa herramientas MCP, siempre usa nombres completamente calificados:

**Formato:** `ServerName:tool_name`

```markdown
Usa la herramienta BigQuery:bigquery_schema para obtener schemas de tablas.
Usa la herramienta GitHub:create_issue para crear issues.
```

Sin el prefijo del servidor, Claude puede fallar en localizar la herramienta.

---

# Límites Técnicos

| Elemento | Límite |
| --- | --- |
| `name` | 64 caracteres máximo |
| `description` | 1024 caracteres máximo |
| [SKILL.md](http://SKILL.md) body | 500 líneas máximo recomendado |
| File paths | Solo forward slashes (`/`) |

Si tu contenido excede 500 líneas, divídelo en archivos separados usando progressive disclosure.

---

# Checklist Oficial de Calidad

Antes de compartir una skill, verifica:

## Calidad Core

- [ ]  Descripción es específica e incluye términos clave
- [ ]  Descripción incluye qué hace Y cuándo usarla
- [ ]  [SKILL.md](http://SKILL.md) body es menor a 500 líneas
- [ ]  Detalles adicionales están en archivos separados (si es necesario)
- [ ]  Sin información sensible al tiempo (o en sección "old patterns")
- [ ]  Terminología consistente en todo el documento
- [ ]  Ejemplos son concretos, no abstractos
- [ ]  Referencias a archivos son un nivel de profundidad
- [ ]  Progressive disclosure usado apropiadamente
- [ ]  Workflows tienen pasos claros

## Código y Scripts

- [ ]  Scripts resuelven problemas en vez de delegar a Claude
- [ ]  Manejo de errores es explícito y útil
- [ ]  Sin "constantes vudú" (todos los valores justificados)
- [ ]  Paquetes requeridos listados en instrucciones y verificados como disponibles
- [ ]  Scripts tienen documentación clara
- [ ]  Sin paths estilo Windows (todos forward slashes)
- [ ]  Pasos de validación/verificación para operaciones críticas
- [ ]  Feedback loops incluidos para tareas críticas de calidad

## Testing

- [ ]  Al menos tres evaluaciones creadas
- [ ]  Testeado con Haiku, Sonnet, y Opus
- [ ]  Testeado con escenarios de uso real
- [ ]  Feedback del equipo incorporado (si aplica)

---

# Errores Comunes a Evitar

## 1. Asumir que Herramientas Están Instaladas

**❌ Malo:**

```markdown
Usa la librería pdf para procesar el archivo.
```

**✅ Bueno:**

```markdown
Instala el paquete requerido: `pip install pypdf`

Luego úsalo:
```

from pypdf import PdfReader

reader = PdfReader("file.pdf")

```

```

## 2. Paths Estilo Windows

**❌ Malo:** `reference\[guide.md](http://guide.md)`

**✅ Bueno:** `reference/[guide.md](http://guide.md)`

## 3. Nombres de Archivos No Descriptivos

**❌ Malo:** `docs/[file1.md](http://file1.md)`, `docs/[file2.md](http://file2.md)`

**✅ Bueno:** `reference/[finance.md](http://finance.md)`, `reference/[sales.md](http://sales.md)`

## 4. Sobre-explicar

Claude ya sabe muchas cosas. No expliques conceptos básicos de programación, formatos de archivo comunes, o sintaxis de lenguajes.

---

# Entorno de Ejecución

## Cómo Claude Accede a Skills

1. **Metadata pre-cargada:** Al inicio, el name y description de todas las skills se cargan en el system prompt
2. **Archivos leídos on-demand:** Claude usa herramientas bash Read para acceder a [SKILL.md](http://SKILL.md) y otros archivos cuando se necesitan
3. **Scripts ejecutados eficientemente:** Scripts de utilidad pueden ejecutarse via bash sin cargar su contenido completo en contexto
4. **Sin penalización de contexto para archivos grandes:** Archivos de referencia, datos, o documentación no consumen tokens de contexto hasta que se lean

## Implicaciones para tu Authoring

- **File paths importan:** Claude navega tu directorio de skill como un filesystem
- **Nombra archivos descriptivamente:** Usa nombres que indiquen contenido
- **Organiza para descubrimiento:** Estructura directorios por dominio o feature
- **Bundlea recursos comprehensivos:** Incluye docs de API completos, ejemplos extensivos; sin penalización de contexto hasta que se acceda
- **Prefiere scripts para operaciones determinísticas:** Escribe `validate_[form.py](http://form.py)` en vez de pedir a Claude que genere código de validación

---

*Este documento es la guía oficial de Anthropic. Cuando crees skills, esta es la referencia autoritativa. Las skills de Superpowers siguen estos principios y los extienden con disciplina adicional.*

## Regla Extra: Memoria de Errores

Cuando algo falle:

1. Arregla el código
2. Actualiza el plan/doc diciendo: "Aprendí que X causa error Y"
3. Nunca cometas el mismo error dos veces

Ejemplo:
En docs/plans/alpha-engine.md agrega:
- ❌ Error: API X no acepta límite > 100
- ✅ Solución: Usar límite de 50