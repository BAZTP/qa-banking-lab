# Resultados de validación del MVP

Fecha: 21 de octubre de 2026. Rama: `feat/qa-banking-lab-mvp`.

Entorno realmente ejecutado: Debian 13, Python 3.12.14, pytest 8.3.5, FastAPI 0.115.12, Playwright 1.51.0 y Chromium del sistema 154.0.8037.57. Dependencias completas en `requirements.lock`. No se ejecutó Windows 11.

| Comprobación | Resultado observado |
| --- | --- |
| Instalación desde requirements.txt y repetición con requirements.lock | Correcta; segunda instalación reutiliza las versiones fijadas |
| `python -m pip check` | Sin dependencias incompatibles |
| `python -m pytest -m 'not e2e' --cov=app --cov-fail-under=90` | **38 aprobadas**, 4 E2E deseleccionadas; ninguna fallida |
| Desglose suite anterior | 12 unitarias, 24 de integración/API, 2 BDD |
| Cobertura de líneas Python `app/` | **99.35%** (154/155); no incluye JS ni demuestra cobertura de todos los riesgos |
| `LAB_CHROMIUM_EXECUTABLE=/usr/bin/chromium python scripts/run_e2e.py` | **4 aprobadas** con navegador real: login/logout, login inválido, transferencia/historial/XSS y saldo insuficiente |
| `python -m pytest exercises -rx` | **2 XFAIL esperados** de bugs aislados; no son pruebas aprobadas |
| Servidor Uvicorn persistente, peticiones HTTP reales | Salud, login, cuentas con saldos iniciales y logout correctos |
| Inspección frontend | Escritorio 1280 px y móvil 390 px; sin errores JavaScript; sin desbordamiento horizontal del documento a 390 px; captura de escritorio inspeccionada |
| Sintaxis JS/Python y limpieza Git | `node --check`, `compileall`; SQLite, caches y cobertura excluidos de Git |

La suite rápida verifica transferencias atómicas, conservación de saldos, origen propio, recepción por otro usuario, invisibilidad de operaciones internas ajenas, importes límite, entrada maliciosa en login, cabecera de protección, cierre de sesión, persistencia y rechazo de sesiones antiguas tras reiniciar. La concurrencia prueba dos débitos de 600 contra saldo 1000: uno se acepta y el otro se rechaza, sin sobregiro.

Los XML de la ejecución local se generaron en `/tmp/qa-api-results.xml` y `/tmp/qa-e2e-results.xml`; son artefactos de esta máquina. CI genera y sube sus propios XML, cobertura y trazas. También se verificó la ejecución remota: los jobs **api y e2e finalizaron correctamente** en [GitHub Actions, ejecución 39648578457](https://github.com/BAZTP/qa-banking-lab/actions/runs/39648578457), para el commit `3a73c3817566d3f5b978041ee457e4051de37c86`. Los números de la tabla corresponden a la ejecución local, no se infieren de un estado verde remoto. Consulta el PR para el estado de commits posteriores.

## Restricciones observadas

- La descarga del Chromium administrado por Playwright devolvió `403 Domain forbidden`. Se utilizó el Chromium existente mediante la opción documentada; no se desactivó TLS ni se alteraron verificaciones.
- Las consultas REST iniciales de `gh` a `api.github.com` devolvieron `Forbidden`. La lectura y el push Git HTTPS funcionaron, y la operación posterior `gh pr create` sí completó la creación de [PR #1](https://github.com/BAZTP/qa-banking-lab/pull/1), de `feat/qa-banking-lab-mvp` a `main`. No hizo falta solicitar otro token. El cuerpo del PR está en `docs/pull-request.md`.
- Se guardaron en el borrador del entorno `install_script`, `start_skill` y los dominios adicionales `cdn.playwright.dev`, `playwright.download.prss.microsoft.com`, `cdn.playwright.download.prss.microsoft.com` y `api.github.com`. Guardar el borrador no aplica ni publica la configuración; se revisa, guarda y publica desde los ajustes del entorno.
- Aviso de deprecación de Starlette/AnyIO (`BlockingPortal`) durante pytest; no produjo errores. No se ocultó.
- No ejecutados: casos manuales completos, Windows 11, Firefox/WebKit, carga, auditoría ZAP/Burp, auditoría de accesibilidad o experimento A/B. Están diferenciados como actividades futuras.

## Cómo repetir

Consulta README.md para Windows. En esta máquina, desde `/workspace/qa-banking-lab`:

```bash
/workspace/qa-banking-venv/bin/python -m pytest -m 'not e2e' --cov=app --cov-fail-under=90
LAB_CHROMIUM_EXECUTABLE=/usr/bin/chromium /workspace/qa-banking-venv/bin/python scripts/run_e2e.py
/workspace/qa-banking-venv/bin/python -m pytest exercises -rx
```

Los tests de API usan bases nuevas por prueba; E2E crea una nueva por ejecución. Los bugs están excluidos del flujo normal y solo se prueban al seleccionar `exercises` explícitamente.
