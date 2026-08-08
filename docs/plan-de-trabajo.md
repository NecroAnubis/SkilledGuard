# Skilled Guard — Plan de trabajo

**Proyecto de grado — Tecnólogo en Análisis y Desarrollo de Software (ADSO), SENA**
**Autor:** Johan S. Restrepo
**Repositorio:** https://github.com/NecroAnubis/SkilledGuard
**Periodo:** 2026-08-07 → 2026-10-07 (8 semanas / 4 sprints)
**Versión:** 0.1 — borrador, pendiente de ajustar al formato oficial del instructor

---

## 1. Decisiones tomadas

| Decisión | Elección | Razón |
|---|---|---|
| Lenguaje | Python 3.12 | Requisito del autor |
| Framework | FastAPI | Genera Swagger/OpenAPI automáticamente — el README original ya declaraba "Pruebas: Postman + Swagger", así que la estrategia de pruebas no cambia |
| ORM / migraciones | SQLAlchemy 2.0 + Alembic | Las migraciones dejan rastro versionado de cada cambio de esquema: evidencia directa para el SENA |
| Base de datos | PostgreSQL en Supabase | Free tier amplio, dashboard visual para sustentar en vivo, escala a plan pago sin migrar |
| Entorno local | Docker + docker-compose | Postgres local idéntico a producción; y `docker compose up` es toda la instalación el día de la sustentación |
| Alcance funcional | El del README original | Se conserva el dominio (usuarios/roles, dispositivos, QR, auditoría, reportes); se descarta el código .NET |

**Lo que se descarta:** el backend .NET 9 (hoy: 1 endpoint de 14 entidades modeladas). **Lo que se conserva:** el modelo de datos y el alcance funcional, corrigiendo el bug de tipos del DDL.

---

## 2. Stack técnico

**Backend**
- Python 3.12 · FastAPI · Uvicorn
- SQLAlchemy 2.0 (ORM) · Alembic (migraciones) · Pydantic v2 (validación)

**Base de datos**
- PostgreSQL 16 — Supabase en la nube, contenedor Docker en local

**Funcionalidades específicas**
- Autenticación: JWT + roles (Administrador / Seguridad / Usuario) — `python-jose` + `passlib[bcrypt]`
- QR: `qrcode` + `pillow`
- Reportes: `openpyxl` (Excel) · `WeasyPrint` (PDF)

**Calidad**
- `pytest` + `httpx` (pruebas de API) · `ruff` (lint + formato) · GitHub Actions (CI en cada push)

**Entrega**
- `Dockerfile` + `docker-compose.yml` · variables de entorno vía `.env` (nunca en el repo)

---

## 3. Metodología: Scrum simulado

4 sprints de 2 semanas. Tablero en **GitHub Projects** (gratis, y queda como evidencia verificable con fechas reales).

**Artefactos por sprint**
- *Product Backlog* — historias de usuario priorizadas
- *Sprint Backlog* — lo comprometido en el sprint
- *Sprint Review* — demo de lo terminado
- *Retrospectiva* — qué mejorar
- *Definition of Done* (abajo)

**Roles** (proyecto individual, así que se declaran explícitamente para la documentación)
- Product Owner: Johan S. Restrepo
- Scrum Master: Johan S. Restrepo
- Development Team: Johan S. Restrepo
- Stakeholder: instructor SENA

**Definition of Done** — una historia está terminada solo si:
1. El código está en `main` vía Pull Request (no push directo)
2. Tiene pruebas automatizadas y CI en verde
3. El endpoint aparece documentado en Swagger
4. La migración de BD está versionada en Alembic
5. La evidencia quedó registrada en el Drive del proyecto

---

## 4. Sprints

### Sprint 1 — Fundación (semanas 1–2)
- Estructura del proyecto Python + Docker + docker-compose
- Modelo de datos corregido (`INT IDENTITY` → `SERIAL`/`Identity` en Postgres) traducido a modelos SQLAlchemy
- Migraciones iniciales con Alembic + conexión a Supabase
- CRUD de usuarios, roles y tipos de documento
- Autenticación JWT + control de acceso por rol
- CI en GitHub Actions

**Entregable:** API que levanta con `docker compose up`, con login funcional.

### Sprint 2 — Núcleo del negocio (semanas 3–4)
- CRUD de dispositivos y tipos de dispositivo
- Generación de código QR por dispositivo
- Registro de entrada y salida (validación en portería)
- Consulta de trazabilidad por dispositivo y por usuario

**Entregable:** el flujo completo de portería funcionando — es el corazón del proyecto.

### Sprint 3 — Auditoría y reportes (semanas 5–6)
- Log de sistema y log de detalle (registro automático de acciones)
- Auditoría de negocio
- Reportes en PDF y Excel con filtros
- Optimización: índices, paginación, consultas N+1

**Entregable:** trazabilidad completa + reportes descargables.

### Sprint 4 — Calidad y entrega (semanas 7–8)
- Cobertura de pruebas y corrección de defectos
- Despliegue y verificación en Supabase
- Documentación final: manual técnico, manual de usuario, plan de pruebas ejecutado
- Preparación de la sustentación (guion de demo, plan B sin internet)

**Entregable:** proyecto sustentable.

---

## 5. Documentación para el SENA

🟡 **Provisional.** Esta lista sale de la estructura típica del programa ADSO, **no** de la rúbrica de tu ficha. Se ajusta en cuanto aparezca el formato oficial en tu Drive.

| Documento | Sprint |
|---|---|
| Anteproyecto (problema, justificación, objetivos, alcance, marco teórico) | 1 |
| Requisitos funcionales y no funcionales | 1 |
| Historias de usuario | 1 |
| Modelo entidad-relación (MER) | 1 |
| Diagrama de casos de uso | 1 |
| Diagrama de clases | 2 |
| Diagrama de despliegue | 4 |
| Plan de pruebas (ya redactado) | 3 |
| Manual técnico | 4 |
| Manual de usuario | 4 |
| Documento final de sustentación | 4 |

---

## 6. Riesgos

| Riesgo | Impacto | Mitigación |
|---|---|---|
| El instructor exige .NET u otro stack | 🔴 Alto — se pierde el trabajo | Confirmar con el instructor **antes del Sprint 1** |
| El formato oficial pide entregables no contemplados | 🟡 Medio | Conseguir el formato esta semana |
| Falla el internet en la sustentación | 🟡 Medio | Docker local con datos de demo cargados como plan B |
| Alcance demasiado grande para 8 semanas | 🟡 Medio | Sprints 1 y 2 son el mínimo sustentable; 3 y 4 son incrementales |

---

## 7. Pendientes inmediatos

1. **Confirmar con el instructor** que Python + FastAPI es aceptable
2. Conseguir el formato oficial de documentación del programa
3. Documentar el levantamiento de información y los requerimientos
4. Sprint 2: dispositivos, generación de QR y registro de portería
