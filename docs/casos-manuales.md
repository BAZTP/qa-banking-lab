# Plan manual y criterios de aceptación

Precondiciones: servidor local, SQLite recién creado, navegador sin sesión, datos exclusivamente ficticios. Restablece la base entre casos que necesiten los saldos iniciales. Si continúas sin restablecer, registra tus saldos de partida.

| Criterio | Aceptación observable | Cobertura automatizada |
| --- | --- | --- |
| CA-01 Autenticación | Login correcto abre cuentas propias; incorrecto responde 401 sin acceso | smoke API, E2E login y negativos |
| CA-02 Privacidad | Ana no consulta cuentas ajenas ni usa el origen de Bruno | security API |
| CA-03 Importes | 0 y negativos rechazados; 0.01 y saldo exacto aceptados; fracciones de centavo rechazadas | unit + data-driven |
| CA-04 Atomicidad | Se debita origen, acredita destino y agrega un registro juntos; rechazo no cambia estado | sanity, regression, BDD |
| CA-05 Historial | Emisor y receptor ven operación, concepto y fecha UTC; un tercero no ve otras operaciones | API visibilidad y E2E persistencia |
| CA-06 Concurrencia | Dos solicitudes de 600 con saldo 1000: una 201 y otra 409, saldo final 400 | integration concurrente |
| CA-07 Persistencia | Reiniciar conserva balances/historial y requiere iniciar sesión nuevamente | persistencia API; sesión efímera por diseño |
| CA-08 Interfaz | Etiquetas asociadas a controles, mensajes legibles, uso móvil y teclado | HTML + checklist manual (no auditoría WCAG) |
| CA-09 Aislamiento | Bugs de ejercicios nunca se importan ni se habilitan en la aplicación | separación de módulos; suite productiva independiente |

## Casos reproducibles

| ID / tipo | Pasos | Resultado esperado |
| --- | --- | --- |
| TC-01 Smoke positivo | Entrar como ana / Demo123! | Dos cuentas, 1000.00 y 250.00 USD-DEMO; historial vacío |
| TC-02 Negativo | Entrar como ana / incorrecta | Mensaje de credenciales incorrectas, formulario visible, sin cuentas |
| TC-03 Funcional | Desde LAB-ANA-01 transferir 10.25 a LAB-ANA-02, concepto «Práctica» | Mensaje de éxito, 989.75 y 260.25, un registro de 10.25 con concepto y fecha |
| TC-04 Saldo insuficiente | Con base nueva, transferir 1000.01 | 409 en API, aviso «Saldo insuficiente», 1000.00 y 250.00 sin historial |
| TC-05 Límite | Con base nueva, transferir 1000.00 | 201, origen 0.00 y destino 1250.00; una operación |
| TC-06 Validación | Probar 0, -1, 1.001 y misma cuenta | UI impide importes inválidos; enviarlos por API devuelve 422; misma cuenta devuelve 422; no hay cambios |
| TC-07 Autorización | Por API usar LAB-BRU-01 como origen mientras Ana está autenticada | 404 y ningún cambio; la UI solo ofrece orígenes propios |
| TC-08 Logout | Entrar, cerrar sesión y consultar /api/accounts | Formulario visible y API 401; recargar no recupera la sesión cerrada |
| TC-09 Destino ausente | Transferir a LAB-NO-01 | 404 y mensaje «Cuenta de destino no disponible», no cambia estado |
| TC-10 Recepción | Ana envía 10.25 a LAB-BRU-01; salir; entrar como bruno | Bruno solo ve su cuenta con 760.25 e historial recibido |
| TC-11 Usabilidad | Navegar con Tab/Shift+Tab/Enter, zoom 200%, ancho 390 px | Foco visible, controles etiquetados, sin bloqueo; tabla permite desplazamiento horizontal |
| TC-12 Seguridad UI | Usar `<img src=x onerror=alert(1)>` como concepto | Aparece como texto literal, sin imagen ni ejecución de script |
| TC-13 Persistencia | Hacer transferencia, detener servidor, arrancar e iniciar sesión | Conserva saldos e historial; no vuelve a sembrar saldos iniciales |
| TC-14 Sesión inválida | Borrar cookie desde DevTools y solicitar cuentas | 401; al operar desde UI se muestra login |

## Registro de ejecución

No marques «pass» antes de ejecutar. Copia la tabla para tu sesión:

| Caso | Versión/commit | Plataforma | Observado | Estado (pass/fail/blocked/not run) | Evidencia/bug |
| --- | --- | --- | --- | --- | --- |
| TC-… | … | … | … | … | … |

Prioriza regresión por riesgo: dinero simulado e integridad de datos > autorización > login > mensajes > cosmética. Reporta el comportamiento observable y los datos iniciales; no confundas un entorno caído con un fallo de negocio.
