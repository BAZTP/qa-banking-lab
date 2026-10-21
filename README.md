# QA Banking Lab

**Nuevo: [Mini Banca Java](java-bank/README.md)** con Spring Boot, retiros, transferencias, login, saldo, historial, JUnit/REST Assured y modo de entrenamiento aislado con bugs intencionales. Sigue su guía para Windows 11 y Postman. El módulo Python de esta página sigue disponible.

Laboratorio educativo para aprender a **pensar y trabajar como QA tester**: Python 3.12, FastAPI, SQLite y frontend HTML/CSS/JavaScript sin compilación. MVP con login de demostración, cuentas ficticias, saldos, transferencias simuladas e historial persistente.

**Todo es ficticio.** No conecta con bancos, no mueve dinero, no necesita secretos. Las credenciales publicadas son parte del ejercicio. No uses datos personales, contraseñas reales ni información bancaria. Ejecútalo localmente; no es un sistema financiero de producción.

## 1. Primer arranque en Windows 11 (PowerShell)

Instala [Python 3.12](https://www.python.org/downloads/) (marca «Add python.exe to PATH») y [Git para Windows](https://git-scm.com/download/win). Verifica `py -3.12 --version` y `git --version`. Chromium para los tests se instala con Playwright; no necesitas Node, Docker ni un servidor de base de datos.

```powershell
git clone https://github.com/BAZTP/qa-banking-lab.git
cd qa-banking-lab
# Mientras el MVP esté en revisión, usa esta rama:
git switch feat/qa-banking-lab-mvp
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.lock
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Abre `http://127.0.0.1:8000` en tu navegador **local**. Detén con `Ctrl+C`. Todos los comandos se ejecutan desde la raíz del repositorio. Usamos directamente el ejecutable del entorno para evitar problemas de `Activate.ps1`; no cambies la política de ejecución de Windows.

En Linux/macOS:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock
.venv/bin/python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

| Usuario ficticio | Contraseña pública de práctica | Cuentas iniciales / saldo USD-DEMO |
| --- | --- | --- |
| `ana` | `Demo123!` | `LAB-ANA-01`: 1000.00; `LAB-ANA-02`: 250.00 |
| `bruno` | `Demo123!` | `LAB-BRU-01`: 750.00 |

SQLite se crea automáticamente en `data/lab.db`. Reiniciar conserva saldos e historial, pero cierra sesiones. Para empezar de cero: **detén el servidor**, elimina únicamente `data/lab.db` con `Remove-Item .\data\lab.db`, y arranca otra vez. Esto borra la práctica local. Nunca se reinician datos automáticamente al arrancar.

Si el puerto está ocupado usa `--port 8002`. Si aparece `ModuleNotFoundError`, verifica estar en la raíz y usar el Python de `.venv`. Si Playwright pide instalar navegadores, ejecuta el comando de la sección siguiente. Evita una carpeta sincronizada o una unidad de red para SQLite.

## 2. Ejecutar pruebas

### Unitarias, API, integración y BDD (sin servidor)

```powershell
.\.venv\Scripts\python.exe -m pytest -m "not e2e" -v
.\.venv\Scripts\python.exe -m pytest -m "not e2e" --cov=app --cov-report=html --cov-fail-under=90 --junitxml=test-results/api.xml
```

Cada prueba de API crea una base temporal y usa el ciclo de vida real de FastAPI. No modifica `data/lab.db`. La cobertura mide líneas ejecutadas; no demuestra por sí sola la calidad ni la seguridad.

### E2E con navegador real

```powershell
.\.venv\Scripts\python.exe -m playwright install chromium
.\.venv\Scripts\python.exe scripts/run_e2e.py --browser chromium --tracing retain-on-failure --screenshot only-on-failure --junitxml=test-results/e2e.xml
# Opcional: observar el navegador
.\.venv\Scripts\python.exe scripts/run_e2e.py --headed
```

El runner inicia su propio Uvicorn en un puerto libre, espera `/api/health`, usa SQLite temporal, ejecuta las pruebas y detiene su servidor. No debes levantarlo manualmente. Cada ejecución comienza con datos nuevos; dentro de la ejecución una transferencia cambia el estado. No paralelices estos E2E contra la misma base.

Si ya tienes Chromium instalado y la descarga está restringida, puedes indicar su ruta existente con `$env:LAB_CHROMIUM_EXECUTABLE = 'C:\ruta\a\chrome.exe'`. El resultado puede variar con versiones distintas; CI usa el navegador administrado por Playwright. En Linux el equivalente es `LAB_CHROMIUM_EXECUTABLE=/usr/bin/chromium .venv/bin/python scripts/run_e2e.py`.

Sin `RUN_E2E=1`, `python -m pytest` omite explícitamente E2E para evitar fallos por falta de servidor. **Un test omitido no cuenta como aprobado**. El runner activa la variable y configura `LAB_BASE_URL`; no la apuntes a servicios reales.

### Seleccionar escenarios

```powershell
.\.venv\Scripts\python.exe -m pytest -m "smoke and not e2e" -v
.\.venv\Scripts\python.exe -m pytest -m sanity -v
.\.venv\Scripts\python.exe -m pytest -m regression -v
.\.venv\Scripts\python.exe -m pytest -m security -v
.\.venv\Scripts\python.exe -m pytest -m bdd -v
.\.venv\Scripts\python.exe -m pytest tests/integration/test_api.py -k data_driven -v
.\.venv\Scripts\python.exe -m pytest exercises -rx
```

Los ejercicios producen **2 XFAIL conocidos**, no 2 aprobados. Para ver el fallo real: `python -m pytest exercises --runxfail -v` (debe fallar). Corrige las funciones en tu propia rama y retira sus marcas XFAIL; con `strict=True`, un ejercicio corregido que conserva la marca genera XPASS y falla para recordarte actualizarlo. La aplicación **nunca importa `exercises/`** y no tiene un interruptor para habilitar los bugs.

## 3. Qué probar y cómo aprender

La guía de la imagen inspira esta matriz; no necesitas instalar todas las herramientas para aplicar los conceptos.

| Concepto | Aplicación en este laboratorio | Evidencia o actividad |
| --- | --- | --- |
| Smoke | Salud, login, cuentas, logout | Marcador `smoke`, API y navegador |
| Sanity | Comprobar una transferencia tras un cambio focalizado | Marcador `sanity`, saldo de ambas cuentas e historial |
| Regression | Límites, saldos, errores, concurrencia | Marcador `regression` |
| Funcional | Transferencia válida, rechazo y autorización | Suite API, BDD, E2E |
| No funcional | Seguridad básica, usabilidad, rendimiento, compatibilidad | Tests `security` + actividades manuales; no auditoría completa |
| Continuous testing | Ejecutar suites en cada PR y push | GitHub Actions, XML de resultados y trazas |
| Modular | Fixtures, reglas puras, DB, API y UI separados | `app/`, `tests/` |
| Data-driven | Equivalencias y valores límite en JSON | `tests/data/transfers.json` + parametrización |
| BDD | Given / When / Then como lenguaje compartido | `tests/bdd/features/transfer.feature` y steps pytest-bdd |
| Linear scripting | Un recorrido de usuario de principio a fin | `tests/e2e/test_journey.py` |
| Hybrid | Combinar módulos, datos y BDD | Suites existentes; no framework adicional necesario |
| Keyword-driven | Diseñar tabla acción / objetivo / valor | Actividad avanzada; no motor Robot Framework implementado |
| A/B testing | Comparar textos de un botón con una hipótesis | Ejercicio de diseño; sin telemetría ni asignación de variantes en el MVP |
| Alpha / Beta | Revisión interna y luego compañeros voluntarios | Plan en `docs/aprendizaje.md`; no prueba con clientes bancarios |

### Ruta progresiva

1. **Exploración manual:** ejecuta TC-01 a TC-08, registra esperado/observado y una captura. Aprende severidad frente a prioridad.
2. **Pruebas API:** usa `docs/api.http` o PowerShell; relaciona 401, 403, 404, 409 y 422 con la condición de prueba.
3. **Unit testing:** añade límites a `test_money.py`; distingue regla de negocio de detalle técnico.
4. **Data-driven:** agrega una fila al JSON, predice el resultado y ejecuta solo el escenario nuevo.
5. **BDD:** escribe primero un escenario de rechazo por destino inexistente, luego implementa sus steps.
6. **E2E:** añade un test que navegue solo con teclado. Observa qué errores pertenecen al HTML y cuáles a la API.
7. **Bugs aislados:** reproduce BUG-01/02, registra un reporte con `docs/plantilla-bug.md`, corrige en tu rama y ejecuta regresión.
8. **CI y revisión:** crea PR, inspecciona resultados y artefactos. Diseña un experimento A/B y un plan alpha/beta sin afirmar que una preferencia individual demuestra una mejora.

Casos manuales, criterios de aceptación y resultados esperados: [docs/casos-manuales.md](docs/casos-manuales.md). Actividades de seguridad, usabilidad y rendimiento: [docs/aprendizaje.md](docs/aprendizaje.md). Evidencia real de ejecución: [docs/resultados.md](docs/resultados.md).

## 4. Contrato del MVP

| Método / ruta | Comportamiento |
| --- | --- |
| `GET /api/health` | Comprueba acceso a SQLite, estado educativo |
| `POST /api/login` | JSON `username`, `password`; cookie HttpOnly, SameSite Strict |
| `POST /api/logout` | Invalida cookie/sesión; requiere `X-Lab-Request: 1` |
| `GET /api/accounts` | Solo cuentas del usuario autenticado |
| `POST /api/transfers` | JSON `source`, `destination`, `amount` como **texto**, `note` opcional; requiere `X-Lab-Request: 1` |
| `GET /api/transfers` | Enviadas y recibidas de las cuentas del usuario, más recientes primero |
| `GET /openapi.json` | Contrato OpenAPI generado |
| `GET /docs` | Swagger UI; requiere acceso del navegador a jsDelivr para sus recursos |

Reglas: importe positivo hasta 1,000,000, precisión monetaria máxima de dos decimales, sin redondeo silencioso. Cuentas distintas, origen propio, destino ficticio existente y saldo suficiente. Se permite transferir todo el saldo y enviar a otro usuario ficticio. Un rechazo no cambia ninguna cuenta ni crea historial. Dinero almacenado como enteros en centavos; no hay comisiones, cambio de moneda ni conexiones externas.

Ejemplo PowerShell con el servidor local iniciado:

```powershell
$base = 'http://127.0.0.1:8000'
Invoke-RestMethod "$base/api/login" -Method Post -ContentType 'application/json' -Body '{"username":"ana","password":"Demo123!"}' -SessionVariable lab
Invoke-RestMethod "$base/api/accounts" -WebSession $lab
Invoke-RestMethod "$base/api/transfers" -Method Post -WebSession $lab -ContentType 'application/json' -Headers @{'X-Lab-Request'='1'} -Body '{"source":"LAB-ANA-01","destination":"LAB-ANA-02","amount":"10.25","note":"Ejercicio API"}'
Invoke-RestMethod "$base/api/transfers" -WebSession $lab
```

Sesiones en memoria de una hora, proceso único: no uses múltiples workers. El modo `--reload` reinicia sesiones al cambiar código. No hay rate limiting, recuperación de contraseña, MFA, paginación del historial ni claves de idempotencia: reenviar la misma petición crea otra operación. Son futuras actividades, no capacidades ya implementadas. Las consultas usan parámetros; los conceptos de transferencias se dibujan con `textContent`. Esto no sustituye un análisis profesional de seguridad.

## 5. Organización y configuración

```text
app/                  # API, reglas monetarias, SQLite y frontend estático
tests/unit/           # reglas puras
tests/integration/    # API, persistencia, autorización y concurrencia
tests/data/           # dataset ficticio JSON
tests/bdd/            # Gherkin y steps
tests/e2e/            # Playwright
exercises/            # bugs aislados, excluidos de testpaths por defecto
scripts/run_e2e.py    # servidor y base temporal para E2E
docs/                 # casos, actividades, evidencia y plantilla de bug
.github/workflows/    # CI API y E2E en jobs independientes
requirements.txt      # dependencias directas fijadas
requirements.lock     # conjunto completo instalado y probado
```

| Variable opcional | Uso |
| --- | --- |
| `QA_BANK_DB` | Ruta SQLite alternativa; usa una base independiente por práctica |
| `LAB_CHROMIUM_EXECUTABLE` | Navegador existente para E2E; por defecto Playwright |
| `RUN_E2E`, `LAB_BASE_URL` | Configuradas automáticamente por el runner |

No se requiere `.env` ni tokens. Las dependencias están fijadas para reproducir el MVP; actualízalas en una rama y repite las suites al hacer mantenimiento. CI usa Python 3.12 y Chromium sobre Ubuntu, exige 90% de cobertura de la API y conserva resultados incluso cuando falla un test. Los fallos de E2E incluyen captura/traza; abre una con `python -m playwright show-trace ruta/al/trace.zip`. No incluyas datos personales en capturas.

## 6. Alcance de la validación

Se probó este MVP en el entorno Linux disponible; Windows 11 tiene instrucciones PowerShell, pero **no se ejecutó una máquina Windows**. Firefox, WebKit, accesibilidad formal, carga sostenida, OWASP ZAP y el experimento A/B quedan como prácticas opcionales documentadas. Consulta `docs/resultados.md` para separar aprobado, esperado, omitido y pendiente.
