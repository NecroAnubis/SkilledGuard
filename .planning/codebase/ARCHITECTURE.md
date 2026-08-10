<!-- refreshed: 2026-08-09 -->
# Architecture

**Analysis Date:** 2026-08-09

## System Overview

```text
┌──────────────────────────────────────────────────────────────┐
│                    FastAPI Application                       │
│                   (app/main.py:8000)                          │
├──────────┬───────────┬──────────┬───────────┬────────────────┤
│   Auth   │  Usuarios │Dispositivos│Movimientos│ Catálogos    │
│ Routers  │ Routers   │ Routers   │ Routers   │ Reportes Logs │
│app/      │app/       │app/       │app/       │app/routers/  │
└────┬─────┴────┬──────┴──────┬────┴────┬──────┴────┬──────────┘
     │          │             │        │         │
     └──────────┴─────────────┴────────┴─────────┘
              │
     ┌────────▼────────────────────────────────────────────────┐
     │          Business Logic Modules                         │
     │  porteria.py | auditoria.py | consultas.py              │
     │  reportes.py | qr.py | security.py | config.py          │
     │                   (app/)                                 │
     └─────────────┬────────────────────────────────────────────┘
                   │
     ┌─────────────▼────────────────────────────────────────────┐
     │            SQLAlchemy ORM Layer                          │
     │  Models: Usuario, Dispositivo, AuditoriaNegocio, etc.   │
     │            (app/models.py)                               │
     │                                                           │
     │  Database Session: SessionLocal, get_db()                │
     │            (app/database.py)                             │
     └─────────────┬────────────────────────────────────────────┘
                   │
     ┌─────────────▼────────────────────────────────────────────┐
     │         PostgreSQL (RDS or Supabase)                     │
     │  14 tables: usuario, dispositivo, rol, logs, etc.        │
     │  Migrations via Alembic (alembic/)                       │
     └──────────────────────────────────────────────────────────┘
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

**Overall:** Layered API with separated business logic.

**Key Characteristics:**
- **Explicit over implicit:** Business logic lives in pure modules testable without API (porteria, auditoria, consultas)
- **Single responsibility:** Routers call business modules; modules don't know about HTTP
- **Audit-first:** Every write operation explicitly calls `registrar_accion()` — audit trail is visible in the code
- **State machine validation:** Device movements are validated before recording (no double-entry, no orphaned exits)
- **Role-based access control:** `exige_rol()` dependency guards endpoints (Admin, Seguridad/Security, Usuario)
- **Query deduplication:** `consultas.movimientos()` is the single source of truth for filtering — API and reports use the same query

## Layers

**Presentation Layer (Routers):**
- Purpose: Handle HTTP requests, validate schemas, call business logic, log actions
- Location: `app/routers/`
- Contains: One router per domain (auth, usuarios, dispositivos, movimientos, catalogos, reportes, logs)
- Depends on: business modules, models, security, database
- Used by: Client (web UI, mobile, external APIs)

**Business Logic Layer:**
- Purpose: Core rules and calculations independent of HTTP
- Location: `app/` (porteria.py, auditoria.py, consultas.py, reportes.py, qr.py, security.py)
- Contains: State validation, audit recording, query building, report generation, password/token handling
- Depends on: models, database session
- Used by: routers, other business modules

**Data Layer:**
- Purpose: Database access via ORM
- Location: `app/models.py` (entities), `app/database.py` (session), `alembic/` (migrations)
- Contains: 14 SQLAlchemy models (Usuario, Dispositivo, AuditoriaNegocio, Rol, LogSistema, etc.) with relationships
- Depends on: SQLAlchemy, PostgreSQL driver
- Used by: business logic, routers

**Infrastructure:**
- Configuration: `app/config.py` (Pydantic BaseSettings)
- Entry point: `app/main.py` (FastAPI app, router registration, healthcheck)
- Frontend: `app/static/` (HTML, CSS, JS with QR scanner)

## Data Flow

### Primary Request Path: Device Entry via QR

1. **Client scans QR in portería** (`app/static/index.html`)
   - Calls `POST /movimientos` with QR code

2. **Router entry point** (`app/routers/movimientos.py:41-66`)
   - Validates request schema (MovimientoRegistrar: `qr`, `tipo`, `observacion`)
   - Checks role (`exige_rol(ROL_ADMINISTRADOR, ROL_SEGURIDAD)`)
   - Looks up device by QR code (`Dispositivo.qr`)

3. **Business logic: state validation** (`app/porteria.py:90-117`)
   - Locks device row (FOR UPDATE) to prevent race conditions
   - Checks current state (last movement: entrada or salida?)
   - Validates transition (can't enter twice, can't exit if never entered)
   - Creates AuditoriaNegocio record if valid, raises MovimientoInvalido otherwise

4. **Audit recording** (`app/auditoria.py:45-77`)
   - Logs the action: who (vigilante), what (device serial, movement type), when (timestamp auto)

5. **Response** (`app/routers/movimientos.py:66`)
   - Returns MovimientoLeer schema (device info, who registered it, timestamp)

### Secondary Flow: Report Generation

1. **User requests Excel export** (`GET /reportes/movimientos.xlsx`)
   - Filters: device_id, user_id (owner), type (entrada/salida), date range
   
2. **Query building** (`app/consultas.py:16-48`)
   - Single reusable function `movimientos()` applies all filters
   - Eager-loads device, user (owner), vigilante to avoid N+1
   - Ordered by most recent first

3. **Report generation** (`app/reportes.py:36-119`)
   - Converts to Excel or PDF in memory (BytesIO)
   - Never touches disk; file is streamed to client
   - Each format has identical data (ENCABEZADOS, _filas)

4. **Audit log** (`app/auditoria.py`)
   - Records `Accion.CONSULTA` for report access

### Authentication Flow

1. **User logs in** (`POST /auth/login` with username=documento, password)

2. **Verify password** (`app/security.py:35-36`)
   - bcrypt.checkpw() against stored hash
   - Same error message for user not found or wrong password (timing attack mitigation)

3. **Create token** (`app/security.py:39-47`)
   - JWT payload: user.id, documento, list of role names, expiry
   - Signed with HS256 + JWT_SECRET from environment

4. **Protected endpoints** (`app/security.py:58-79`)
   - Dependency `usuario_actual` decodes and validates token
   - Re-fetches user from DB (handles deleted users)

5. **Role checks** (`app/security.py:82-96`)
   - Dependency `exige_rol(ROL_ADMINISTRADOR, ...)` checks if user has any of the allowed roles
   - Raises 403 if not

**State Management:**
- **No global state:** Each request gets a fresh SQLAlchemy session via `Depends(get_db)`
- **Per-request devices state:** Queried from DB on each endpoint, not cached
- **Transaction isolation:** `db.commit()` is explicit in each endpoint; `db.rollback()` on IntegrityError
- **Device row-level locking:** `with_for_update()` in porteria to serialize simultaneous movements of same device

## Key Abstractions

**TipoMovimiento (Enum):**
- Purpose: Restricts movement types to entrada/salida only
- Examples: `TipoMovimiento.INGRESO`, `TipoMovimiento.SALIDA`
- Pattern: StrEnum — validates at API boundary, propagates as string to DB

**EstadoDispositivo (Enum):**
- Purpose: Represents computed state (dentro/fuera) derived from last movement
- Examples: `EstadoDispositivo.DENTRO`, `EstadoDispositivo.FUERA`
- Pattern: Never stored in DB; always computed from AuditoriaNegocio history

**MovimientoInvalido (Exception):**
- Purpose: Signals state machine violation
- Raised by: `validar_transicion()` if movement contradicts current state
- Caught by: router, converted to HTTP 409 Conflict

**Accion (Enum):**
- Purpose: Audit action types
- Examples: `Accion.CREACION`, `Accion.ACTUALIZACION`, `Accion.ELIMINACION`, `Accion.CONSULTA`
- Pattern: Used by `registrar_accion()` to classify every write

**Timestamps mixin:**
- Purpose: Every table has `fecha_creado` and `fecha_actualizado` columns
- Pattern: SQLAlchemy mixin (app/models.py:22-30) with server-side defaults

## Entry Points

**HTTP Entry Point:**
- Location: `app/main.py:15-54`
- Triggers: Container startup → FastAPI listens on 0.0.0.0:8000
- Responsibilities: Mount routers, serve static files, healthcheck

**Healthcheck Endpoint:**
- Location: `GET /salud` (`app/main.py:35-49`)
- Triggers: Docker orchestrator health check (default every 10s)
- Checks: Database connectivity (executes `SELECT 1`)
- Returns: 200 if DB is reachable; 503 if not (fails the container)

**CLI Entry Point:**
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

**What happens:** Device.qr stores a UUID4, not the serial number. Serial is printed on the device (visible to anyone).

**Why it's correct:** Serial is printed on the chassis at purchase, changing it requires phoning the vendor. QR is a sticker that can be replaced without touching inventory. If the sticker is damaged or leaked, you replace it without modifying the serial.

### No Stored Reports

**What happens:** Reportes are generated in memory (BytesIO) and streamed to the client. They are never written to disk or database.

**Why it's correct:** A report is a snapshot of a query at one instant. Storing it means deciding when to delete it, and the file goes stale as soon as data changes. On-demand generation is faster than disk I/O for ~200 rows.

### Explicit Audit Logging

**What happens:** `registrar_accion()` is called explicitly in every endpoint that modifies data. Not hooked to SQLAlchemy events.

**Why it's correct:** The audit trail is visible in the code where it's produced. A future developer can see at a glance which endpoints log and which don't. SQLAlchemy hooks are implicit and hard to trace.

### Single Shared Query for Movements

**What happens:** `consultas.movimientos()` builds the filter query once, and both the API list endpoint and the report endpoints call it.

**Why it's correct:** Prevents drift. If someone adds a date filter to the API, the reports stay in sync. If the query lived twice, the next developer adds the filter in one place and forgets the other, and Excel shows different data than the screen.

## Error Handling

**Strategy:** Fail fast and explicit. Invalid operations raise exceptions that convert to HTTP status codes with clear messages.

**Patterns:**
- **Invalid state:** `MovimientoInvalido` (porteria) → 409 Conflict
- **Not found:** `HTTPException(404)` (routers) → 404 Not Found
- **Integrity violation:** `IntegrityError` (SQLAlchemy) caught and converted to 409 Conflict (unique constraint)
- **Invalid auth:** Bad token or expired → 401 Unauthorized
- **Insufficient role:** User lacks required role → 403 Forbidden
- **Validation:** Pydantic schema validation fails → 422 Unprocessable Entity

## Cross-Cutting Concerns

**Logging:** Explicit audit via `registrar_accion()` on writes. No debug/info logs in code (intentional: minimizes noise in production). Docker logs capture Uvicorn startup messages.

**Validation:** 
- Pydantic schemas at API boundaries (UsuarioCrear, DispositivoCrear, MovimientoRegistrar)
- Custom validators for password byte-length (bcrypt truncates at 72 bytes)
- Business rule validation in modules (porteria state machine)

**Authentication:** JWT tokens with 60-minute expiry (default). Roles are embedded in token at login time; no role-change takes effect until next login.

**Database migrations:** Alembic (alembic/versions/) with `alembic upgrade head` on container startup (handled in docker-compose healthcheck).

---

*Architecture analysis: 2026-08-09*
