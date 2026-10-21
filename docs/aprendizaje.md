# Actividades del laboratorio

## De principiante a una estrategia de QA

1. Lee los criterios de aceptación y construye particiones: importe negativo, cero, positivo válido, mayor al saldo, precisión inválida y límite máximo. Distingue smoke (¿vale la pena seguir probando?) de sanity (¿funciona el cambio específico?).
2. Usa DevTools → Network para relacionar un clic con método, JSON, estado y respuesta. Intenta cambiar `source` en una petición; la API debe autorizar por usuario y no confiar en el selector HTML.
3. Escribe un caso antes de automatizarlo: precondición, pasos, esperado y limpieza. Traduce un caso a pytest y otro a Gherkin. Evita escenarios BDD que solo repiten nombres internos de funciones.
4. Compara capas: unidad detecta errores de conversión; integración detecta transacción rota; E2E detecta un botón que no envía la petición. Diseña una pirámide con más pruebas rápidas que recorridos de navegador.

## Bugs intencionales aislados

`exercises/buggy_rules.py` contiene BUG-01 (acepta cero) y BUG-02 (rechaza saldo exacto). Son funciones independientes sin importación desde `app/`. No cambies la API para activarlos.

En una rama de práctica: ejecuta `python -m pytest exercises --runxfail`, registra ambos fallos, escribe su impacto, corrige las reglas y retira XFAIL. Ejecuta la regresión del MVP después. Los XFAIL documentan defectos conocidos; no deben usarse para esconder nuevos fallos.

## Seguridad y usabilidad

Solo sobre esta instancia local de práctica:

- Prueba login inválido e intento de SQL injection. Espera 401 y ausencia de acceso.
- Compara cuentas de Ana y Bruno. Nunca debes obtener un saldo ajeno ni debitar un origen ajeno.
- Cambia/elimina `X-Lab-Request` en POST autenticado: debe responder 403.
- Introduce etiquetas HTML como concepto: deben mostrarse como texto. Comprueba con E2E que no se crea un elemento HTML.
- Evalúa mensajes de error, foco, etiquetas, contraste, teclado, tamaños de pantalla y lector de pantalla si lo tienes. Registra navegador y versión. Un checklist no acredita cumplimiento WCAG.
- OWASP ZAP o Burp Suite son herramientas opcionales para una fase posterior; configura exclusivamente tu instancia local y no un banco real. El MVP no incluye auditoría automatizada de estas herramientas.

## No funcional: rendimiento y compatibilidad

No uses tiempos absolutos como criterio universal. En tu equipo registra SO, CPU, Python, navegador, número de solicitudes, concurrencia, tasa de error, p50 y p95. Define una hipótesis antes de medir: por ejemplo, «lectura de cuentas con 5 usuarios de práctica concurrentes mantiene 0 errores». Empieza con pocas peticiones y aumenta gradualmente. Este MVP usa un proceso y SQLite; no promete escalabilidad productiva.

Diseña un script de carga solo de lectura sobre `/api/accounts` después de autenticar. Separa fallos HTTP de tiempos altos y compara varias repeticiones. No midas únicamente `/api/health` y concluyas que las transferencias son rápidas. Añadir Locust es una actividad futura; no está instalado ni ejecutado por la CI actual.

Repite TC-01/03/11 en Edge/Chrome y Firefox sobre Windows 11. Playwright incluye Chromium en CI; otros navegadores requieren instalación y validación adicionales. No declares compatibilidad con una plataforma que no ejecutaste.

## A/B testing (diseño, opcional)

Hipótesis: el texto «Simular transferencia» hace más claro el carácter educativo que «Enviar».

Diseña versiones A/B en una rama aparte, asignación aleatoria consistente por participante ficticio, consentimiento de tus compañeros y métricas (finalización correcta, errores, tiempo y comprensión). Define muestra y criterio de decisión antes del experimento. No concluyas que una variante es mejor por una sola sesión; evita capturar datos personales. El MVP no implementa variantes ni analítica.

## Alpha y beta

Alpha: tú y un compañero ejecutan smoke y todos los criterios monetarios antes de compartir la versión. Beta: un pequeño grupo de compañeros prueba recorridos con datos ficticios y entrega feedback estructurado. Documenta consentimiento, alcance y versión. No implica usuarios de una entidad bancaria ni lanzamiento real.

## Keyword-driven y modularidad

Transforma TC-03 en una tabla:

| Keyword | Objetivo | Dato |
| --- | --- | --- |
| LOGIN | usuario | ana |
| SELECT_SOURCE | origen | LAB-ANA-01 |
| FILL_DESTINATION | destino | LAB-ANA-02 |
| TRANSFER | importe | 10.25 |
| ASSERT_BALANCE | origen | 989.75 |

Implementar un intérprete de esta tabla o migrar a Robot Framework es un ejercicio avanzado. No ejecutes palabras como código arbitrario; usa un mapa de acciones explícitas. Reutiliza helpers del dominio en vez de copiar recorridos. Compara coste de mantenimiento con pytest/Playwright antes de añadir otro framework.

## Definition of Done de una práctica

- Caso ligado a criterio, datos ficticios y resultado esperado claro.
- Fallo reproducible antes de corregir y evidencia después.
- Pruebas seleccionadas realmente ejecutadas; omisiones y XFAIL separados.
- Sin credenciales reales, bases ni capturas sensibles en Git.
- PR pequeño con validación, limitaciones y revisión de un compañero.
