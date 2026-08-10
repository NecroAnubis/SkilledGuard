<!-- GSD:project-start source:PROJECT.md -->

## Project

**Skilled Guard**

Sistema que digitaliza el control de ingreso y salida de equipos tecnológicos en
portería, reemplazando la minuta en papel: los equipos se identifican con un
código QR y cada movimiento queda registrado, auditado y consultable. Sus
usuarios son el vigilante que escanea en la puerta y el administrador que
gestiona usuarios, equipos y reportes.

Es el proyecto de grado de Johan S. Restrepo para el Tecnólogo en Análisis y
Desarrollo de Software (ADSO) del SENA. El producto ya funciona; este ciclo no
es de construir, es de **entregar y sustentar**.

**Core Value:** Que el proyecto se pueda sustentar y aprobar: un sistema desplegado y accesible,
la documentación que exige el programa, y una demo que funcione en vivo delante
del instructor.

### Constraints

- **Presupuesto**: cero estricto — solo capas gratuitas; el proyecto no puede
  depender de nada que se cobre

- **Timeline**: sin fecha de sustentación definida — el roadmap se ordena por
  dependencias, no por calendario

- **Despliegue**: PaaS gratuito + PostgreSQL gestionado, sin servidor propio
  que administrar

- **Stack**: Python 3.12 / FastAPI / PostgreSQL — ya decidido y construido; no
  se reabre

- **Evaluación**: el criterio real lo fija la rúbrica del instructor, que
  todavía no está en nuestras manos

- **Idioma**: código, comentarios y documentación en español, por convención
  del repositorio y porque el evaluador lee en español
<!-- GSD:project-end -->

<!-- GSD:stack-start source:codebase/STACK.md -->

## Technology Stack

## Languages

- Python 3.12 - Backend API and business logic
- None (frontend is static HTML/CSS/JavaScript served as static files)

## Runtime

- Python 3.12-slim (Docker base image per `Dockerfile`)
- pip (Python package installer)
- Lockfile: `requirements.txt` (pinned versions) and `requirements-dev.txt`

## Frameworks

- FastAPI 0.115.6 - HTTP API framework with automatic OpenAPI documentation
- Uvicorn 0.34.0 - ASGI server to run FastAPI application
- SQLAlchemy 2.0.36 - ORM for database access and models
- Alembic 1.14.0 - Database schema versioning and migrations
- pytest 8.3.4 - Test runner and framework (dev only)
- httpx 0.28.1 - HTTP client for testing (dev only)
- Ruff 0.8.6 - Python linter and formatter

## Key Dependencies

- psycopg[binary] 3.2.3 - PostgreSQL adapter for Python; enables SQLAlchemy database connection
- pydantic 2.10.4 - Data validation and serialization for request/response schemas
- pydantic-settings 2.7.0 - Environment configuration management (reads from `.env`)
- bcrypt 4.2.1 - Password hashing (used in `app/security.py`)
- PyJWT 2.10.1 - JWT token creation and verification for stateless authentication
- qrcode[pil] 8.0 - QR code generation (used in `app/qr.py`)
- openpyxl 3.1.5 - Excel spreadsheet generation for reports (used in `app/reportes.py`)
- fpdf2 2.8.2 - PDF report generation (used in `app/reportes.py`)
- python-multipart 0.0.20 - Multipart form data parsing for file uploads

## Configuration

- Method: `.env` file via `pydantic-settings`
- Location: `.env` (not committed; use `.env.example` as template)
- Critical variables:
- Dockerfile uses Python 3.12-slim base
- Multi-layer build optimized for Docker caching
- Non-root user (`appuser`) for security isolation

## Platform Requirements

- Python 3.12
- Docker + Docker Compose (for local PostgreSQL)
- pip/virtualenv
- Python 3.12 runtime or Docker container
- PostgreSQL 16+ (database server)
- Environment variables configured via deployment platform

## Database

- PostgreSQL 16-alpine (per `docker-compose.yml`)
- Default local: `postgresql+psycopg://skilledguard:skilledguard@db:5432/skilledguard`
- Production: Configure via `DATABASE_URL` environment variable
- Pool configuration: `pool_pre_ping=True` (tests connection before use)
- Managed by SQLAlchemy ORM models in `app/models.py`
- Migrations tracked in `alembic/versions/` directory
- Auto-migration on startup: `alembic upgrade head` (per `docker-compose.yml`)

## Health Checks

- `GET /salud` - Returns `{"estado": "ok", "base_de_datos": "ok"}` only if database is reachable
- Used by Docker healthcheck (interval: 15s, start_period: 30s, retries: 3)

<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->

## Conventions

## Language & Documentation

## Naming Patterns

- `snake_case.py` for all Python modules
- Example: `app/auditoria.py`, `app/porteria.py`, `app/schemas.py`
- Routers in `app/routers/[domain].py` where domain names are Spanish: `dispositivos.py`, `usuarios.py`, `movimientos.py`
- `snake_case` for all functions, methods, and local variables
- Spanish names reflecting business domain: `listar()`, `obtener()`, `crear()`, `registrar_accion()`, `validar_transicion()`
- Verb-first naming for actions: `hashear_contrasena()`, `generar_png()`, `estado_actual()`
- Private functions prefixed with `_`: `_obtener()`, `_catalogo()`, `_crear_dispositivo()`
- `PascalCase` for all class names
- Models: `Usuario`, `Dispositivo`, `AuditoriaNegocio`, `LogSistema`, `UsuarioRol`
- Pydantic schemas: `UsuarioCrear`, `UsuarioLeer`, `DispositivoCrear`, `DispositivoEstado`
- Enums: `TipoMovimiento`, `EstadoDispositivo`, `Accion`
- Custom exceptions: `MovimientoInvalido`
- `snake_case` for local/instance variables: `id_usuario`, `email_hash`, `ultimo_movimiento`
- `UPPER_SNAKE_CASE` for module-level constants: `ROL_ADMINISTRADOR`, `ROL_SEGURIDAD`, `MAX_BYTES_CONTRASENA`
- Spanish names for meaningful constants that reflect the domain
- Table names: `snake_case`, Spanish: `usuario`, `dispositivo`, `tipo_documento`, `auditoria_negocio`
- Column names: `snake_case`, Spanish: `contrasena_hash`, `fecha_creado`, `fecha_actualizado`
- Foreign keys: `id_[tabla_singular]`: `id_usuario`, `id_dispositivo`, `id_tipo_documento`
- Enum fields use StrEnum (Python 3.11+): `TipoMovimiento`, `EstadoDispositivo`

## Code Style

- Tool: Ruff (linter + formatter)
- Config: `pyproject.toml`
- Line length: 100 characters
- Python target: 3.12
- `E` (Pycodestyle errors)
- `F` (Pyflakes)
- `I` (isort import sorting)
- `UP` (pyupgrade, Python 3.12+ idioms)
- `B` (flake8-bugbear, prevents common bugs)
- `SIM` (flake8-simplify, readability)

## Import Organization

- None configured — use relative imports from `app/` package
- Imports from sibling modules: `from app.models import Usuario`
- Imports from submodules: `from app.routers.usuarios import router`
- Imports with type annotation: `from typing import Annotated, Literal`

## Type Hints

- Modern union syntax: `str | None` instead of `Optional[str]`
- Annotated for FastAPI dependencies: `Annotated[str, Depends(get_db)]`
- SQLAlchemy ORM types: `Mapped[str]`, `Mapped[int]`, `Mapped[list["ChildModel"]]`
- Dict/List types: `dict[str, str]`, `list[Usuario]` (using PEP 585)
- Literal for restricted strings: `Literal["Ingreso", "Salida"]`

## Error Handling

- `HTTPException` from FastAPI for all HTTP errors
- Always include status code and detail message
- Detail messages in Spanish, user-facing
- Catch `IntegrityError` for duplicate keys or constraint violations
- Convert to `HTTPException(status.HTTP_409_CONFLICT, ...)`
- Always rollback the session: `db.rollback()`
- Suppress the exception chain: `raise HTTPException(...) from None`
- Define custom exceptions inheriting from `Exception`: `class MovimientoInvalido(Exception)`
- Use them in business logic (not HTTP endpoints)
- HTTP layer catches and converts to `HTTPException`
- Never use `None` to represent "not found" in database queries
- Always check explicitly: `if usuario is None: raise HTTPException(...)`

## Comments & Documentation

- Explain "why", not "what" — code shows the what, comments explain the why
- Complex algorithm or non-obvious business rule: see `app/porteria.py`, `app/auditoria.py`
- Security or performance considerations that aren't obvious
- Known limitations or workarounds
- Use triple-quoted docstrings for all modules, functions, and classes
- One-liner for simple functions; multi-line for complex ones
- Spanish language, explaining purpose and key behavior

## Function Design

- Prefer small, testable functions
- Helper functions prefixed with `_`: `_obtener()`, `_catalogo()`
- Use Annotated with FastAPI dependency injection for common patterns
- Query parameters with validation: `Query(ge=1, le=200)`
- Use dataclasses/Pydantic models for complex input: `UsuarioCrear`, `DispositivoCrear`
- Explicit return type annotations on all functions
- No implicit None returns; if a function doesn't return data, declare `-> None`
- Return domain objects (ORM models) from routers and let Pydantic serialize them via `response_model`

## Module Design

- Group related functions/classes in logical modules
- `app/porteria.py` — business logic for equipment tracking (no HTTP layer)
- `app/auditoria.py` — audit trail functions, separate from HTTP
- `app/routers/` — HTTP endpoints grouped by domain
- `app/schemas.py` — Pydantic models for request/response validation
- `app/models.py` — SQLAlchemy ORM definitions
- **HTTP Layer** (`app/routers/`): FastAPI endpoints, dependency injection, error handling
- **Business Logic Layer** (`app/porteria.py`, `app/auditoria.py`): Domain rules, isolated from HTTP
- **Data Layer** (`app/models.py`, `app/database.py`): ORM models and session management
- **Configuration** (`app/config.py`, `app/security.py`): Settings and security utilities
- Not used; explicit imports from specific modules preferred for clarity

## Dependency Injection

- Use `Depends()` for database session injection: `Depends(get_db)`
- Use `Depends()` for security/auth: `Depends(usuario_actual)`, `Depends(exige_rol(...))`
- Pre-compute dependencies at module level for reuse:

## Security Patterns

- Hash passwords with bcrypt: `hashear_contrasena(contrasena)`
- Never expose `contrasena_hash` in responses (omit from Pydantic schemas)
- Validate password length in bytes (not characters) due to bcrypt 72-byte limit
- Include bcrypt hash validation in Pydantic validators
- Create tokens with user ID and roles: `crear_token(usuario, roles)`
- Verify token and return user object: `usuario_actual()` dependency
- Custom exceptions converted to 401 Unauthorized
- Define role constants: `ROL_ADMINISTRADOR`, `ROL_SEGURIDAD`, `ROL_USUARIO`
- Use dependency: `Depends(exige_rol(ROL_ADMINISTRADOR))`
- Routes can require multiple roles: `exige_rol(ROL_ADMINISTRADOR, ROL_SEGURIDAD)`

## Database Patterns

- Use context manager with FastAPI dependency: `Depends(get_db)`
- Always commit or rollback explicitly: `db.commit()`, `db.rollback()`
- Flush for intermediate operations that need IDs: `db.flush()`
- Use SQLAlchemy `select()` with type hints over `.query()`
- Use `db.get(Model, id)` for simple lookups by primary key
- Use relationships for lazy-loaded associations
- Avoid N+1 queries: batch queries where possible (see `estados_de_todos()` in `app/porteria.py`)
- Each endpoint is a transaction by default (auto-commit or auto-rollback)
- For multi-step operations: commit explicitly after each logical step
- Use pessimistic locking for concurrent access: `with_for_update()`

## Testing Conventions

- Test names in Spanish, prefixed with `test_`
- Test files mirror source structure: `tests/test_[module].py`
- Fixtures in `tests/conftest.py` for shared test data
- Mock/override dependencies via `app.dependency_overrides`

<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->

## Architecture

## System Overview

```text

```

## Component Responsibilities

| Component | Responsibility | File |
|-----------|----------------|------|
| Router: Auth | JWT login, token validation, user self-info | `app/routers/auth.py` |
| Router: Usuarios | CRUD users, role assignment, admin-only | `app/routers/usuarios.py` |
| Router: Dispositivos | Register devices, list with state, generate QR, admin-only | `app/routers/dispositivos.py` |
| Router: Movimientos | Register entry/exit via QR, audit trail, security role | `app/routers/movimientos.py` |
| Router: Catálogos | Roles, document types, device types (read public, write admin) | `app/routers/catalogos.py` |
| Router: Reportes | Excel/PDF downloads of movements, filtered, security role | `app/routers/reportes.py` |
| Router: Logs | System action logs, admin-only view | `app/routers/logs.py` |
| Portería Module | Validates device state transitions, prevents double-entry/exit | `app/porteria.py` |
| Auditoría Module | Logs every data change (create/update/delete) with user and details | `app/auditoria.py` |
| Consultas Module | Shared query builder for movement filters, used by API and reports | `app/consultas.py` |
| Reportes Module | Excel/PDF generation from movement data, in-memory (no disk) | `app/reportes.py` |
| Security Module | JWT token creation/verification, bcrypt password hashing, role checks | `app/security.py` |
| Models | 14 SQLAlchemy entities with relationships and timestamps | `app/models.py` |
| Database | SQLAlchemy engine, session factory, dependency injection | `app/database.py` |
| Config | Environment-based settings (database URL, JWT secret, etc.) | `app/config.py` |

## Pattern Overview

- **Explicit over implicit:** Business logic lives in pure modules testable without API (porteria, auditoria, consultas)
- **Single responsibility:** Routers call business modules; modules don't know about HTTP
- **Audit-first:** Every write operation explicitly calls `registrar_accion()` — audit trail is visible in the code
- **State machine validation:** Device movements are validated before recording (no double-entry, no orphaned exits)
- **Role-based access control:** `exige_rol()` dependency guards endpoints (Admin, Seguridad/Security, Usuario)
- **Query deduplication:** `consultas.movimientos()` is the single source of truth for filtering — API and reports use the same query

## Layers

- Purpose: Handle HTTP requests, validate schemas, call business logic, log actions
- Location: `app/routers/`
- Contains: One router per domain (auth, usuarios, dispositivos, movimientos, catalogos, reportes, logs)
- Depends on: business modules, models, security, database
- Used by: Client (web UI, mobile, external APIs)
- Purpose: Core rules and calculations independent of HTTP
- Location: `app/` (porteria.py, auditoria.py, consultas.py, reportes.py, qr.py, security.py)
- Contains: State validation, audit recording, query building, report generation, password/token handling
- Depends on: models, database session
- Used by: routers, other business modules
- Purpose: Database access via ORM
- Location: `app/models.py` (entities), `app/database.py` (session), `alembic/` (migrations)
- Contains: 14 SQLAlchemy models (Usuario, Dispositivo, AuditoriaNegocio, Rol, LogSistema, etc.) with relationships
- Depends on: SQLAlchemy, PostgreSQL driver
- Used by: business logic, routers
- Configuration: `app/config.py` (Pydantic BaseSettings)
- Entry point: `app/main.py` (FastAPI app, router registration, healthcheck)
- Frontend: `app/static/` (HTML, CSS, JS with QR scanner)

## Data Flow

### Primary Request Path: Device Entry via QR

### Secondary Flow: Report Generation

### Authentication Flow

- **No global state:** Each request gets a fresh SQLAlchemy session via `Depends(get_db)`
- **Per-request devices state:** Queried from DB on each endpoint, not cached
- **Transaction isolation:** `db.commit()` is explicit in each endpoint; `db.rollback()` on IntegrityError
- **Device row-level locking:** `with_for_update()` in porteria to serialize simultaneous movements of same device

## Key Abstractions

- Purpose: Restricts movement types to entrada/salida only
- Examples: `TipoMovimiento.INGRESO`, `TipoMovimiento.SALIDA`
- Pattern: StrEnum — validates at API boundary, propagates as string to DB
- Purpose: Represents computed state (dentro/fuera) derived from last movement
- Examples: `EstadoDispositivo.DENTRO`, `EstadoDispositivo.FUERA`
- Pattern: Never stored in DB; always computed from AuditoriaNegocio history
- Purpose: Signals state machine violation
- Raised by: `validar_transicion()` if movement contradicts current state
- Caught by: router, converted to HTTP 409 Conflict
- Purpose: Audit action types
- Examples: `Accion.CREACION`, `Accion.ACTUALIZACION`, `Accion.ELIMINACION`, `Accion.CONSULTA`
- Pattern: Used by `registrar_accion()` to classify every write
- Purpose: Every table has `fecha_creado` and `fecha_actualizado` columns
- Pattern: SQLAlchemy mixin (app/models.py:22-30) with server-side defaults

## Entry Points

- Location: `app/main.py:15-54`
- Triggers: Container startup → FastAPI listens on 0.0.0.0:8000
- Responsibilities: Mount routers, serve static files, healthcheck
- Location: `GET /salud` (`app/main.py:35-49`)
- Triggers: Docker orchestrator health check (default every 10s)
- Checks: Database connectivity (executes `SELECT 1`)
- Returns: 200 if DB is reachable; 503 if not (fails the container)
- Location: `app/seed.py`
- Triggers: `python -m app.seed` from container
- Responsibilities: Create initial roles, document types, admin user

## Architectural Constraints

- **Threading:** FastAPI runs with Uvicorn worker pool (usually 4–8 workers). No global mutable state per worker; SQLAlchemy sessions are thread-safe per-request.
- **Global state:** None. Config is read once at startup (`app.config.settings`), never mutated. Database connections are pooled (SQLAlchemy pool_pre_ping=True).
- **Circular imports:** None detected. Layering is strict: routers → business logic → models → database.
- **Database row locking:** `porteria.registrar()` uses `with_for_update()` on the device row to serialize competing movements.
- **Report size limits:** `MAXIMO_FILAS = 5000` in reportes router prevents accidental full-table exports.

## Anti-Patterns

### QR Token vs. Serial Number

### No Stored Reports

### Explicit Audit Logging

### Single Shared Query for Movements

## Error Handling

- **Invalid state:** `MovimientoInvalido` (porteria) → 409 Conflict
- **Not found:** `HTTPException(404)` (routers) → 404 Not Found
- **Integrity violation:** `IntegrityError` (SQLAlchemy) caught and converted to 409 Conflict (unique constraint)
- **Invalid auth:** Bad token or expired → 401 Unauthorized
- **Insufficient role:** User lacks required role → 403 Forbidden
- **Validation:** Pydantic schema validation fails → 422 Unprocessable Entity

## Cross-Cutting Concerns

- Pydantic schemas at API boundaries (UsuarioCrear, DispositivoCrear, MovimientoRegistrar)
- Custom validators for password byte-length (bcrypt truncates at 72 bytes)
- Business rule validation in modules (porteria state machine)

<!-- GSD:architecture-end -->

<!-- GSD:skills-start source:skills/ -->

## Project Skills

No project skills found. Add skills to any of: `.claude/skills/`, `.agents/skills/`, `.cursor/skills/`, `.github/skills/`, or `.codex/skills/` with a `SKILL.md` index file.
<!-- GSD:skills-end -->

<!-- GSD:workflow-start source:GSD defaults -->

## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:

- `/gsd-quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd-debug` for investigation and bug fixing
- `/gsd-execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->

<!-- GSD:profile-start -->

## Developer Profile

> Profile not yet configured. Run `/gsd-profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
