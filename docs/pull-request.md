El repositorio estaba vacío. Este MVP permite practicar QA con una aplicación educativa local: login de demostración, cuentas y saldos ficticios, transferencias atómicas e historial con FastAPI, SQLite y frontend HTML/CSS/JavaScript en español.

Incluye módulos separados para API, persistencia y dinero en centavos; autorización por usuario; fixtures y datos ficticios; pytest unitario e integración/API; Playwright E2E; smoke, sanity, regresión, data-driven y escenarios BDD. Los bugs didácticos están aislados en `exercises/` y nunca se importan en la aplicación. GitHub Actions ejecuta API/BDD y E2E en jobs separados, con cobertura y artefactos.

El README incluye instalación en Windows 11, comandos de pruebas, contrato API, limitaciones y ruta de aprendizaje. La documentación añade 14 casos manuales, criterios de aceptación, matriz de conceptos de testing, plantilla de defectos y actividades progresivas de seguridad, usabilidad, A/B y alpha/beta.

Validación local: 38 pruebas rápidas aprobadas (99.35% de cobertura Python), 4 E2E aprobadas con Chromium del sistema, 2 XFAIL esperados en ejercicios, `pip check` correcto y arranque Uvicorn con peticiones funcionales verificadas. Detalles en `docs/resultados.md`.

Pendiente de validar: CI remota, Windows 11 y actividades opcionales de rendimiento, compatibilidad y auditoría. La descarga del Chromium administrado está restringida en el entorno actual; el runner permite usar una instalación existente. No se emplearon datos bancarios reales ni secretos. Es un laboratorio de un solo proceso, sin garantías ni controles completos de producción.
