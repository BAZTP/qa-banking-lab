# Mini Banca Java: tu sistema para practicar QA

Aplicación funcional con **Java 21 + Spring Boot**, frontend HTML/CSS/JavaScript y base H2 local. Puedes iniciar sesión, consultar saldos, retirar dinero ficticio, transferir entre cuentas y cerrar sesión. Las operaciones quedan en un historial. No mueve dinero real ni necesita secretos.

También usarás **Java para automatizar pruebas** con JUnit 5 y REST Assured: herramientas habituales en equipos QA que prueban APIs. El lenguaje del sistema y el de las pruebas pueden ser diferentes; aquí ambos usan Java para facilitar tu práctica.

El laboratorio Python anterior permanece en la raíz. Este módulo es independiente; ejecuta sus comandos desde `java-bank/`.

## 1. Arrancar en Windows 11

1. Instala Git y un **JDK 21**, por ejemplo Temurin 21 desde [Adoptium](https://adoptium.net/temurin/releases/?version=21). Selecciona agregar Java al PATH y configurar JAVA_HOME en el instalador. Cierra y abre PowerShell.
2. Comprueba `java -version`: debe mostrar 21. Si tienes varios JDK, configura `JAVA_HOME` al JDK 21 y su carpeta `bin` en PATH.
3. Descarga el repositorio o actualiza tu copia. Mientras esta versión esté en revisión:

```powershell
git clone https://github.com/BAZTP/qa-banking-lab.git
cd qa-banking-lab
git switch feat/java-mini-banking
cd java-bank
.\mvnw.cmd --version
.\mvnw.cmd clean verify
java -jar .\target\java-banking-lab-0.1.0.jar
```

Si ya tienes el repositorio, usa `git fetch origin` y `git switch feat/java-mini-banking` desde su raíz, luego `cd java-bank`. No sobrescribas cambios locales.

El Maven Wrapper incluido descarga la versión fijada de Maven y las dependencias la primera vez; no necesitas instalar Maven ni Node. Requiere Internet hacia Maven Central. La descarga de Maven verifica SHA-256. Si falla una verificación, no la desactives: vuelve a descargar desde la fuente oficial o consulta el proxy de tu red.

Abre **http://127.0.0.1:8080** en tu navegador local. Detén el servidor con `Ctrl+C`. Si 8080 está ocupado, arranca con `java -jar .\target\java-banking-lab-0.1.0.jar --server.port=8082` y usa ese puerto en las peticiones.

En Linux/macOS: `./mvnw clean verify` y `java -jar target/java-banking-lab-0.1.0.jar`.

### Usuarios y datos iniciales

| Usuario | Contraseña pública | Cuentas y saldo inicial USD-DEMO |
| --- | --- | --- |
| ana | Demo123! | LAB-ANA-01: 1000.00; LAB-ANA-02: 250.00 |
| bruno | Demo123! | LAB-BRU-01: 750.00 |

El modo normal guarda datos en `java-bank/data/java-bank.mv.db`. Reiniciar conserva saldos e historial y exige iniciar sesión otra vez. Para restablecerlos, **detén el servidor** y borra solo `data/java-bank.mv.db`; al arrancar se recrea. Esto borra tu práctica. No borres una base mientras esté abierta.

No uses información real. La contraseña pública y la autenticación simplificada son exclusivamente demostrativas. No hay registro, MFA, bloqueo por intentos ni recuperación de contraseña. No publiques este servidor en Internet.

## 2. Tu primera sesión como QA: modo normal

Precondición de la tabla: base nueva; restaura entre casos que dependan del saldo inicial. Registra esperado, observado, estado y evidencia. **No marques aprobado antes de probarlo.**

| ID / tipo | Pasos | Resultado esperado |
| --- | --- | --- |
| J-01 / smoke | Entrar como ana / Demo123! | Aparecen dos cuentas: 1000.00 y 250.00 |
| J-02 / negativo | Entrar con contraseña incorrecta | Mensaje de error, sin acceso al saldo; API 401 |
| J-03 / retiro | Retirar 50.00 de LAB-ANA-01 | Saldo 950.00; historial con un retiro de 50.00; API 201 |
| J-04 / límite | Con base nueva, retirar 1000.00 de LAB-ANA-01 | Saldo 0.00; retiro aceptado; API 201 |
| J-05 / saldo insuficiente | Con base nueva, retirar 1000.01 | Aviso de saldo insuficiente; API 409; sin cambios ni historial |
| J-06 / transferencia | Enviar 10.25 de LAB-ANA-01 a LAB-ANA-02 | Saldos 989.75 y 260.25; una transferencia en historial; API 201 |
| J-07 / reglas | Transferir a la misma cuenta | Rechazo 422; sin cambios en saldos ni historial |
| J-08 / validación | En API enviar 0, -1 o 1.001 como importe | Rechazo 422; sin cambios. El navegador también impide importes inválidos |
| J-09 / autorización | Como Bruno, intentar retirar de LAB-ANA-01 por API | Rechazo 404; ninguna cuenta cambia |
| J-10 / destino | Enviar a LAB-NO-01 | Rechazo 404; saldos e historial intactos |
| J-11 / sesión | Cerrar sesión e intentar GET /api/accounts | Formulario de login; API 401 |
| J-12 / recepción | Ana envía a LAB-BRU-01; iniciar sesión como Bruno | Bruno ve el abono y su saldo actualizado, sin operaciones internas de Ana |
| J-13 / persistencia | Hacer un retiro, reiniciar, iniciar sesión | Saldo e historial conservados; no se vuelven a sumar fondos iniciales |

Criterios: solo se gasta desde cuentas propias; no hay sobregiros; retirar todo el saldo está permitido; transferencia origen/destino deben ser distintos; los importes usan centavos enteros y se rechazan fracciones de centavo. Una operación rechazada no crea historial. Dos retiros simultáneos de 600 con saldo 1000 deben dar un éxito y un rechazo, con saldo final 400.

## 3. Activar errores para encontrarlos como QA

Primero prueba el modo normal. Después, en **otra terminal**, ejecuta:

```powershell
java -jar .\target\java-banking-lab-0.1.0.jar --spring.profiles.active=training --lab.training-bugs=true --server.port=8081
```

Abre **http://127.0.0.1:8081**. La cabecera debe decir **«ENTRENAMIENTO · BUGS INTENCIONALES ACTIVOS»** y `GET /api/health` devuelve `trainingBugs: true`.

Este modo usa una **base H2 en memoria propia**, no la base de la banca normal. Al detenerlo pierde sus operaciones. También usa otra cookie de sesión. La aplicación se niega a activar los bugs si falta el perfil `training` o si se configura una base persistente. Arrancar solo con `--spring.profiles.active=training` mantiene los bugs desactivados: hacen falta ambas opciones.

### Actividad A: descubre los bugs sin leer la solución

Ejecuta J-03, J-04, J-06 y J-07 sobre una instancia training nueva. Usa los resultados esperados del modo normal como criterio. Hay **dos defectos intencionales**. Intenta responder:

1. ¿El error aparece en frontend, API o ambos?
2. ¿Qué valor límite o regla lo dispara?
3. ¿Cambió el saldo? ¿Se creó un registro incorrecto?
4. ¿Qué prueba de regresión escribirías?

<details><summary>Solución y pasos para reproducir</summary>

**BUG-J01 — No permite retirar el saldo exacto.** Con training recién arrancado, Ana tiene 1000.00 en LAB-ANA-01. Retira 1000.00: devuelve 409 «Saldo insuficiente», aunque debería aceptar el retiro y dejar saldo 0.00. Si retiraste antes, reinicia training o retira el saldo actual exacto.

**BUG-J02 — Acepta transferir a la misma cuenta.** Transfiere 10.00 de LAB-ANA-01 a LAB-ANA-01. Devuelve 201 y crea una operación; debería devolver 422 y no crear historial. El saldo queda igual porque debita y acredita la misma cuenta; revisar solo el saldo no detecta este defecto.

Estos comportamientos no están habilitados en el modo normal. Las comprobaciones específicas están en `TrainingBugsTest`: verifican que el defecto de entrenamiento es reproducible; no certifican que ese comportamiento sea correcto para el negocio.

</details>

Para salir del modo defectuoso: detén ese servidor y vuelve a abrir el puerto normal. Si arrancas otra vez sin las dos opciones, los bugs permanecen apagados.

## 4. Probar la API con PowerShell o Postman

Usa una base nueva si quieres comparar exactamente con los ejemplos. Los `amount` se envían como texto decimal para evitar ambigüedad monetaria.

```powershell
$base = 'http://127.0.0.1:8080' # cambia a 8081 para el entrenamiento
Invoke-RestMethod "$base/api/health"
Invoke-RestMethod "$base/api/login" -Method Post -ContentType 'application/json' -Body '{"username":"ana","password":"Demo123!"}' -SessionVariable sesion
Invoke-RestMethod "$base/api/accounts" -WebSession $sesion

# Retirar 50: esperar 201, saldo 950.00
Invoke-RestMethod "$base/api/withdrawals" -Method Post -ContentType 'application/json' -WebSession $sesion -Headers @{'X-Lab-Request'='1'} -Body '{"source":"LAB-ANA-01","amount":"50.00"}'

# Transferir 10.25 después del retiro: saldos 939.75 y 260.25
Invoke-RestMethod "$base/api/transfers" -Method Post -ContentType 'application/json' -WebSession $sesion -Headers @{'X-Lab-Request'='1'} -Body '{"source":"LAB-ANA-01","destination":"LAB-ANA-02","amount":"10.25","note":"Mi prueba QA"}'
Invoke-RestMethod "$base/api/history" -WebSession $sesion
Invoke-RestMethod "$base/api/logout" -Method Post -WebSession $sesion -Headers @{'X-Lab-Request'='1'}
```

En PowerShell 5.1 un HTTP 4xx aparece como error de `Invoke-RestMethod`: es lo esperado en un caso negativo. Revisa el estado y cuerpo de respuesta, no solo el texto de la terminal. En Postman es más sencillo observar ambos.

En Postman: importa `qa/postman_collection.json`, configura `baseUrl` (8080 o 8081), mantén activo el cookie jar, ejecuta login y luego las demás peticiones. No copies cookies reales ni tokens a la colección. Puedes usar también `qa/api.http` con REST Client de VS Code.

| Ruta | Entrada / salida |
| --- | --- |
| GET /api/health | Estado y bandera trainingBugs; no exige sesión |
| POST /api/login | username, password; crea cookie de sesión |
| GET /api/accounts | Cuentas del usuario y saldo como texto decimal |
| POST /api/withdrawals | source, amount; requiere sesión y X-Lab-Request: 1 |
| POST /api/transfers | source, destination, amount, note opcional; misma cabecera |
| GET /api/history | Retiros y transferencias enviadas/recibidas; más recientes primero, fechas UTC |
| POST /api/logout | Invalida sesión; requiere X-Lab-Request: 1 |

401: falta sesión o credenciales incorrectas. 403: falta cabecera de protección. 404: origen ajeno o cuenta inexistente. 409: saldo insuficiente. 422: datos/regla inválidos. No existe endpoint de depósito para fabricar saldo; restablece únicamente la base local si necesitas empezar otra vez.

## 5. Automatizar en Java

```powershell
.\mvnw.cmd test
.\mvnw.cmd '-Dtest=MoneyTest' test
.\mvnw.cmd '-Dtest=BankApiTest' test
.\mvnw.cmd '-Dgroups=smoke' test
.\mvnw.cmd '-Dgroups=regression' test
.\mvnw.cmd '-Dgroups=sanity' test
.\mvnw.cmd '-Dtest=TrainingBugsTest' test
```

`MoneyTest`: unitarias y valores límite. `BankApiTest`: JUnit + REST Assured contra un servidor Spring Boot real en puerto aleatorio, con base temporal. Incluye retiros, transferencias, permisos, historial y concurrencia. Los tags seleccionan smoke, sanity, regression y security. Las pruebas parametrizadas son data-driven.

`TrainingModeTest` comprueba el bloqueo de configuración insegura; `TrainingBugsTest` arranca su propio perfil aislado y reproduce los dos defectos. Un resultado verde de esta última suite significa «el ejercicio se reproduce», no «el negocio funciona correctamente con bugs». Las pruebas normales sí usan el comportamiento correcto como oráculo.

Los tests de Maven no modifican tu base `data/java-bank.mv.db`. Los reportes están en `target/surefire-reports/`. `clean verify` compila, ejecuta las pruebas y genera el JAR. El workflow `.github/workflows/java.yml` realiza la misma validación en CI.

`PersistenceTest` abre y cierra dos veces la aplicación sobre un archivo temporal para comprobar que no se pierden operaciones ni se vuelven a sembrar saldos.

### Navegador automatizado (opcional)

Las pruebas de API están en Java. Para los recorridos de navegador se reutiliza Playwright/Python del laboratorio existente. Desde `java-bank/`, con Python 3.12 instalado:

```powershell
py -3.12 -m venv ..\.venv
..\.venv\Scripts\python.exe -m pip install -r ..\requirements.lock
..\.venv\Scripts\python.exe -m playwright install chromium
..\.venv\Scripts\python.exe qa/browser_check.py
..\.venv\Scripts\python.exe qa/browser_check.py --training
```

Cada comando inicia su propio JAR en puerto libre y base temporal, ejecuta el recorrido y detiene el proceso. El normal verifica login incorrecto/correcto, retiro, transferencia, historial, texto HTML escapado, saldo insuficiente y logout. El de training reproduce los dos defectos aislados. Las capturas se guardan en `test-results/java-browser/` desde la raíz del repo. Ambos prueban ancho móvil de 390 px y ausencia de errores JavaScript. No equivalen a una auditoría de accesibilidad.

Para practicar BDD, convierte J-03 en: **Dado** que Ana tiene 1000.00, **Cuando** retira 50.00, **Entonces** quedan 950.00 y existe un retiro. Este módulo usa JUnit y REST Assured; no instala Cucumber. El laboratorio Python mantiene sus escenarios BDD ejecutables.

## 6. Qué entregar como QA

Para cada defecto usa la [plantilla de reporte](../docs/plantilla-bug.md): entorno, versión, precondición, pasos, esperado, observado, severidad, prioridad y evidencia. Adjunta estado HTTP y saldo/historial antes y después. Después de una corrección, repite el caso y la regresión.

Actividad progresiva: manual → API en Postman → parametrización en JUnit → autorización → dos peticiones concurrentes → revisión de CI. Añade un test de destino inexistente o un importe nuevo antes de modificar reglas.

Limitaciones educativas: un proceso local, sesiones de 30 minutos, sin dinero real, sin servicios bancarios ni idempotencia (reenviar una petición válida crea otra operación). Autenticación simplificada con credenciales públicas, HTTP local sin TLS, sin auditoría profesional ni controles financieros productivos. H2 es distinta de la SQLite del módulo Python. Windows 11 tiene instrucciones, pero la validación ejecutada se documenta en [RESULTADOS.md](RESULTADOS.md).
