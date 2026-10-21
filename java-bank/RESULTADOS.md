# Resultados del módulo Java

Validación local del 21 de octubre de 2026 en Debian 13, JDK Temurin 21.0.12.1+1, Maven 3.9.9, Spring Boot 3.5.0 y Chromium del sistema 154.0.8037.57.

| Comprobación ejecutada | Resultado |
| --- | --- |
| Maven Wrapper `clean verify` | Compilación, pruebas y JAR correctos |
| JUnit: MoneyTest | 12 aprobadas; conversión exacta y valores inválidos |
| JUnit + REST Assured: BankApiTest | 15 aprobadas; servidor HTTP real, login/logout, retiro, transferencia, autorización, validación, visibilidad y concurrencia |
| JUnit: PersistenceTest | 1 aprobada; dos arranques sobre base temporal conservan saldo e historial |
| JUnit: TrainingModeTest | 2 aprobadas; impide bugs sin perfil aislado y con base persistente |
| JUnit: TrainingBugsTest | 2 aprobadas **como reproducción de defectos conocidos**, no como cumplimiento de negocio |
| Total Maven | **32 ejecutadas, 0 fallidas, 0 errores, 0 omitidas**; 30 verifican funcionalidad/aislamiento y 2 reproducen los bugs didácticos |
| Navegador normal | Recorrido aprobado: login inválido/válido, retiro 50, transferencia 10.25, saldos 939.75/260.25, historial, concepto HTML como texto, rechazo por saldo insuficiente, recarga, móvil y logout |
| Navegador training | Recorrido aprobado como reproducción: aviso visible, retiro del saldo exacto rechazado incorrectamente y misma cuenta aceptada incorrectamente; sin activar bugs en la banca normal |
| Servidor JAR en modo normal | Arranque correcto; salud, sesión, saldo inicial y logout comprobados por HTTP; trainingBugs=false |
| Sintaxis frontend | `node --check` correcto; navegador sin errores JavaScript; sin desbordamiento del documento a 390 px |

Los reportes JUnit están en `target/surefire-reports/`. Las capturas de los recorridos están en `test-results/java-browser/` desde la raíz del repositorio. Son salidas locales ignoradas en Git. CI está configurada para guardar sus propios reportes y capturas como artefactos.

## Correcciones de entorno realizadas

La máquina tenía Java Runtime pero no un JDK completo. Se instaló Temurin 21 en `/workspace/tools/` después de verificar SHA-256 contra la publicación oficial de Adoptium. Maven necesita el proxy existente del entorno y el almacén de confianza Java del sistema. Se configuraron ambos localmente, sin copiar credenciales ni desactivar TLS. El Maven Wrapper fija Maven 3.9.9 y verifica SHA-256 de su distribución.

El script reutilizable del entorno conserva estas activaciones. En Windows con JDK 21 y acceso normal a Internet no necesitas la configuración de proxy específica de esta máquina; sigue README.md.

## No ejecutado o pendiente

Windows 11, colección de Postman en la aplicación de escritorio, lectores de pantalla, auditoría profesional de seguridad y pruebas de carga sostenida no se ejecutaron. Las instrucciones y casos se entregan para tu práctica. Los resultados remotos de CI se consultan por commit en el pull request; la tabla anterior documenta ejecuciones locales.

Los dos errores solo existen cuando se combinan `training` y `lab.training-bugs=true`. Nunca se usaron datos reales ni se habilitaron bugs en la banca persistente normal.
