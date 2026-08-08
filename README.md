# 🛡️ Skilled Guard

Sistema de Automatización para el Control de Ingreso de Equipos Tecnológicos

**Proyecto de grado — Tecnólogo en Análisis y Desarrollo de Software (ADSO), SENA**
Autor: Johan S. Restrepo

---

## Problema que soluciona

El ingreso y salida de equipos tecnológicos se registra hoy de forma manual en minutas, lo que genera:

- Procesos lentos (promedio 10 minutos por usuario)
- Pérdida de trazabilidad
- Riesgo de fraude o pérdida de bienes

Skilled Guard digitaliza el registro de usuarios y equipos, y permite validación rápida en portería mediante código QR.

---

## Estado actual

| Módulo | Estado |
|---|---|
| Autenticación JWT + roles | ✅ Sprint 1 |
| Usuarios, roles, tipos de documento | ✅ Sprint 1 |
| Migraciones versionadas (Alembic) | ✅ Sprint 1 |
| Docker + docker-compose | ✅ Sprint 1 |
| CI automatizado | ✅ Sprint 1 |
| Dispositivos y generación de QR | 🔜 Sprint 2 |
| Registro de entrada/salida | 🔜 Sprint 2 |
| Auditoría y trazabilidad | 🔜 Sprint 3 |
| Reportes PDF / Excel | 🔜 Sprint 3 |

---

## Tecnologías

| Capa | Herramienta |
|---|---|
| Lenguaje | Python 3.12 |
| API | FastAPI (documentación OpenAPI automática) |
| ORM | SQLAlchemy 2.0 |
| Migraciones | Alembic |
| Base de datos | PostgreSQL 16 (local en Docker, producción en Supabase) |
| Seguridad | JWT (PyJWT) + bcrypt |
| Pruebas | pytest + httpx |
| Calidad | ruff + GitHub Actions |
| Despliegue | Docker + docker-compose |

---

## Ejecutar el proyecto

Requisito único: **Docker**.

```bash
git clone https://github.com/NecroAnubis/SkilledGuard.git
cd SkilledGuard
cp .env.example .env          # ajustar JWT_SECRET
docker compose up --build
```

Cargar los datos iniciales (roles, tipos de documento y el primer administrador):

```bash
docker compose exec -e ADMIN_CONTRASENA='tu-clave-segura' api python -m app.seed
```

| Recurso | URL |
|---|---|
| Documentación interactiva (Swagger) | http://localhost:8000/docs |
| Documentación alterna (ReDoc) | http://localhost:8000/redoc |
| Verificación de estado | http://localhost:8000/salud |

---

## Ejecutar las pruebas

```bash
docker compose up -d db
pip install -r requirements-dev.txt
export DATABASE_URL="postgresql+psycopg://skilledguard:skilledguard@localhost:5432/skilledguard_test"
export JWT_SECRET="secreto-de-pruebas"
pytest -q
```

Las mismas pruebas corren automáticamente en cada Pull Request (ver `.github/workflows/ci.yml`).

---

## Estructura

```
app/
├── main.py          # Aplicación FastAPI
├── config.py        # Configuración por variables de entorno
├── database.py      # Motor y sesión de base de datos
├── models.py        # Modelo de datos (15 entidades)
├── schemas.py       # Validación de entrada y salida
├── security.py      # JWT, hash de contraseñas, control de roles
├── seed.py          # Datos iniciales
└── routers/         # Endpoints por área
alembic/             # Migraciones versionadas
tests/               # Pruebas automatizadas
docs/                # Documentación del proyecto
Base_de_Datos/       # Scripts SQL originales (histórico)
```

---

## Metodología

Scrum simulado, 4 sprints de 2 semanas. El plan de trabajo, el plan de pruebas y la documentación del proyecto viven en `docs/`.

**Definition of Done:** todo cambio entra por Pull Request, con pruebas automatizadas, CI en verde, endpoint documentado en Swagger y migración versionada.
