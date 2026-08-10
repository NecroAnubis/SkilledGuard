<!-- refreshed: 2026-08-09 -->
# Codebase Structure

**Analysis Date:** 2026-08-09

## Directory Layout

```
SkilledGuard/
├── app/                           # Main application code
│   ├── __init__.py
│   ├── main.py                    # FastAPI app, router registration
│   ├── config.py                  # Pydantic settings (env-based config)
│   ├── database.py                # SQLAlchemy engine & session factory
│   ├── models.py                  # 14 SQLAlchemy ORM entities
│   ├── schemas.py                 # Pydantic request/response schemas
│   ├── security.py                # JWT, bcrypt, role-based access control
│   ├── porteria.py                # Device state machine & movement validation
│   ├── auditoria.py               # Audit logging for all data changes
│   ├── consultas.py               # Shared movement query builder
│   ├── reportes.py                # Excel & PDF report generation
│   ├── qr.py                      # QR code PNG generation
│   ├── seed.py                    # Initialize DB with roles & admin user
│   ├── routers/                   # Endpoint handlers by domain
│   │   ├── __init__.py
│   │   ├── auth.py                # POST /auth/login, GET /auth/yo
│   │   ├── usuarios.py            # CRUD users, assign roles
│   │   ├── dispositivos.py        # CRUD devices, generate QR
│   │   ├── movimientos.py         # Register entry/exit, list with audit
│   │   ├── catalogos.py           # CRUD roles, document types, device types
│   │   ├── reportes.py            # Download Excel/PDF of movements
│   │   └── logs.py                # View system action audit logs
│   └── static/                    # Web frontend (served by StaticFiles)
│       ├── index.html             # Portería interface (QR scanner)
│       ├── app.js                 # QR scanning & API client
│       ├── estilo.css             # Styling
│       └── jsQR.js                # QR decoding library
│
├── alembic/                       # Database migrations (Alembic)
│   ├── versions/                  # Migration SQL files
│   ├── env.py                     # Alembic configuration
│   └── script.py.mako             # Migration template
├── alembic.ini                    # Alembic config (sqlalchemy.url, etc.)
│
├── tests/                         # pytest test suite
│   ├── __init__.py
│   ├── conftest.py                # Pytest fixtures & setup (in-memory DB)
│   ├── test_auth.py               # Login, token validation
│   ├── test_usuarios.py           # User CRUD, role assignment
│   ├── test_dispositivos.py       # Device CRUD, QR generation, state
│   ├── test_porteria.py           # State machine validation (pure logic)
│   ├── test_movimientos.py        # Entry/exit registration, audit trail
│   ├── test_catalogos.py          # Catalog CRUD
│   ├── test_reportes.py           # Excel/PDF generation
│   ├── test_auditoria.py          # Audit logging
│   ├── test_seguridad.py          # Password hashing, JWT
│   └── test_seed.py               # Initial data loading
│
├── docs/                          # Project documentation
│   ├── Plan_de_Trabajo.md         # Scrum backlog & sprint plan
│   ├── Plan_de_Pruebas.md         # Test strategy & coverage
│   └── ...                        # Other docs (historical)
│
├── .github/
│   └── workflows/
│       └── ci.yml                 # GitHub Actions: pytest + ruff
│
├── .planning/
│   └── codebase/                  # This directory (architecture docs)
│
├── Dockerfile                      # Container image definition
├── docker-compose.yml              # Docker Compose: api + PostgreSQL
├── .dockerignore
├── pyproject.toml                 # Python project metadata (ruff config)
├── requirements.txt               # Production dependencies
├── requirements-dev.txt           # Dev dependencies (pytest, etc.)
├── .env.example                   # Environment variable template
├── .env                           # Local .env (git-ignored)
├── .gitignore
├── README.md                      # Project overview
│
└── Base_de_Datos/                 # Legacy SQL scripts (historical)
    └── *.sql                      # Original DDL (no longer used)
```

## Directory Purposes

**app/**
- Purpose: All application code
- Contains: Handlers, business logic, models, configuration
- Key files: main.py (entry point), models.py (data model)

**app/routers/**
- Purpose: HTTP endpoint handlers grouped by domain
- Contains: One Python file per API domain (auth, usuarios, dispositivos, etc.)
- Naming: kebab-case filenames (e.g., `dispositivos.py` for `/dispositivos` routes)
- Pattern: Each defines a `router = APIRouter(prefix=..., tags=...)` that main.py includes

**app/static/**
- Purpose: Frontend web interface (HTML, CSS, JS)
- Contains: Single-page app for QR scanning in portería
- Entry: `index.html` served when client requests root path `/`
- Note: Mounted last in main.py so it catches all unmatched requests (fallback to SPA)

**alembic/**
- Purpose: Database schema versioning and migrations
- Contains: SQL migration files (auto-generated or hand-written)
- Workflow: `alembic revision --autogenerate -m "..."` creates a new migration
- Entry point: `env.py` defines migration rules; read by `alembic upgrade head`

**tests/**
- Purpose: Automated test suite (pytest)
- Contains: One test file per app module/router
- Naming: `test_*.py` (pytest discovery pattern)
- Fixture: `conftest.py` defines reusable setup (in-memory SQLite, test client)

**docs/**
- Purpose: Project documentation (Plan of Work, Test Plan, etc.)
- Contains: Markdown files, not code

**.github/workflows/**
- Purpose: CI pipeline automation
- Contains: `ci.yml` (runs pytest + ruff on every PR)

## Key File Locations

**Entry Points:**
- `app/main.py` — FastAPI app initialization, router registration, static file mounting
- `app/seed.py` — CLI to populate initial data (roles, document types, admin user)

**Configuration:**
- `app/config.py` — Pydantic BaseSettings; reads DATABASE_URL, JWT_SECRET, etc. from .env
- `.env` — Runtime variables (git-ignored)
- `pyproject.toml` — Ruff configuration (formatter/linter)
- `alembic.ini` — Alembic migration engine config

**Core Logic:**
- `app/models.py` — SQLAlchemy entity definitions (14 tables: usuario, dispositivo, rol, logs, etc.)
- `app/database.py` — Connection pooling and session factory
- `app/security.py` — JWT, bcrypt, role checking

**Business Rules:**
- `app/porteria.py` — Device state machine (entrada/salida validation, race condition prevention)
- `app/auditoria.py` — Log every data modification with user & changed fields
- `app/consultas.py` — Query builder for movement filtering (used by API and reports)
- `app/reportes.py` — Excel/PDF generation (in-memory, no disk)

**API Handlers:**
- `app/routers/auth.py` — `/auth/login`, `/auth/yo`
- `app/routers/usuarios.py` — `/usuarios` (CRUD, assign roles)
- `app/routers/dispositivos.py` — `/dispositivos` (CRUD, QR generation)
- `app/routers/movimientos.py` — `/movimientos` (entry/exit registration)
- `app/routers/catalogos.py` — `/roles`, `/tipos-documento`, `/tipos-dispositivo`
- `app/routers/reportes.py` — `/reportes/movimientos.xlsx|pdf`
- `app/routers/logs.py` — `/logs` (view audit actions)

**Testing:**
- `tests/conftest.py` — Pytest setup (in-memory DB fixture, test client)

## Naming Conventions

**Files:**
- Modules: snake_case.py (e.g., `porteria.py`, `consultas.py`)
- Test files: `test_*.py` (e.g., `test_porteria.py`)
- Migration files: `alembic/versions/[timestamp]_[description].py` (auto-generated)

**Directories:**
- Package directories: snake_case (e.g., `app/`, `tests/`, `alembic/`)
- Static assets: kebab-case or snake_case (e.g., `app/static/`)

**Database tables:**
- snake_case (e.g., `usuario`, `dispositivo`, `auditoria_negocio`)
- Singular nouns (e.g., `usuario` not `usuarios`)

**Python code:**
- Classes (models): PascalCase (Usuario, Dispositivo, AuditoriaNegocio)
- Functions: snake_case (crear_token, registrar_accion)
- Constants: SCREAMING_SNAKE_CASE (MAX_BYTES_CONTRASENA, MAXIMO_FILAS)
- Enums (StrEnum): PascalCase (TipoMovimiento, EstadoDispositivo, Accion)

**API endpoints:**
- Kebab-case paths (e.g., `/tipos-documento`, `/tipos-dispositivo`)
- Resource-oriented (e.g., `/dispositivos/{id}` not `/get-device`)

## Where to Add New Code

**New API Endpoint (new domain):**
1. Create router file: `app/routers/[domain].py`
   - Define `router = APIRouter(prefix="/[domain]", tags=["Domain Name"])`
   - Implement endpoint functions with Depends(get_db) and Depends(usuario_actual)
   - Use Depends(exige_rol(...)) for role guards
2. Register router in `app/main.py`: `app.include_router([domain].router)`
3. Add test file: `tests/test_[domain].py` (use conftest fixtures)
4. If modifying data, call `registrar_accion()` explicitly before db.commit()

**New Business Logic Module:**
1. Create module: `app/[feature].py`
   - Import models and Session
   - Define pure functions (or classes) that take db: Session as parameter
   - Do NOT import from routers (only the opposite is allowed)
   - Add docstring explaining purpose
2. Use from routers: `from app import [feature]` then call functions
3. Test directly: `tests/test_[feature].py` (test without FastAPI context)

**New Database Entity:**
1. Add class to `app/models.py` (inherit from Base and optionally Timestamps)
   - Define `__tablename__` (snake_case)
   - Use Mapped[...] for all columns with proper SQLAlchemy types
   - Add relationships if needed (back_populates for bidirectional)
2. Add Pydantic schemas to `app/schemas.py` (NameCrear, NameLeer for CRUD)
3. Create Alembic migration: `alembic revision --autogenerate -m "Add [entity]"`
4. Verify the migration SQL, then `alembic upgrade head` to apply locally

**New API Schema (request/response):**
1. Add to `app/schemas.py`
   - Name pattern: `[Entity]Crear` (create request), `[Entity]Leer` (response)
   - Inherit from BaseModel (or _DesdeORM if reading from ORM objects)
   - Add validation via @field_validator if needed
2. Use in router: `response_model=YourSchema`

**New Test:**
1. File location: `tests/test_[feature].py`
2. Use fixtures from `conftest.py` (db, client, usuario_admin, etc.)
3. No framework needed: plain pytest with assert statements
4. For routers: use `client: TestClient` to call endpoints (e.g., `client.post("/auth/login", ...)`)
5. For business logic: import the module and call functions directly with db session

**New Migration:**
1. After changing `app/models.py`, run:
   ```bash
   alembic revision --autogenerate -m "Describe what changed"
   ```
2. Review the generated SQL in `alembic/versions/[timestamp]_*.py`
3. Apply locally:
   ```bash
   alembic upgrade head
   ```
4. The container runs migrations automatically on startup (see docker-compose healthcheck)

## Special Directories

**app/static/**
- Purpose: Frontend web interface (HTML, CSS, JS)
- Generated: No (hand-written)
- Committed: Yes (part of the application)
- Served by: `app.mount("/", StaticFiles(directory=ESTATICOS, html=True), name="interfaz")`
- Note: Mounted last so unmatched requests fall through to index.html (SPA fallback)

**alembic/versions/**
- Purpose: Store database migration scripts
- Generated: Yes (via `alembic revision --autogenerate`)
- Committed: Yes (part of schema version control)
- Never edit manually: Let Alembic generate, then review and commit

**.pytest_cache/**
- Purpose: pytest cache (test results, performance data)
- Generated: Yes
- Committed: No (in .gitignore)

**.env**
- Purpose: Environment variables for local development
- Generated: No (copy from .env.example)
- Committed: No (git-ignored; contains secrets)
- Content: DATABASE_URL, JWT_SECRET, etc.

**Base_de_Datos/**
- Purpose: Legacy SQL scripts from original project (historical reference)
- Generated: No (from old .NET backend)
- Committed: Yes (kept for reference, not used)
- Note: Do not use these; the Python migration system (Alembic) is the source of truth

## Quick Patterns

**Create a new endpoint that reads data:**
```python
# In app/routers/[new_domain].py
@router.get("/[path]", response_model=list[YourSchema])
def list_things(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[Usuario, Depends(usuario_actual)],
) -> list[YourSchema]:
    things = db.scalars(select(Thing)).all()
    return things
```

**Create an endpoint that modifies data:**
```python
# In app/routers/[new_domain].py
from app.auditoria import Accion, registrar_accion

@router.post("", response_model=YourSchema, status_code=status.HTTP_201_CREATED)
def create_thing(
    datos: YourCrearSchema,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[Usuario, Depends(usuario_actual)],
) -> Thing:
    thing = Thing(**datos.model_dump())
    db.add(thing)
    db.commit()
    
    # Must log every write
    registrar_accion(
        db, user.id, Accion.CREACION, "thing_table_name",
        detalles_de_creacion(datos.model_dump())
    )
    db.commit()
    return thing
```

**Guard endpoint to admin-only:**
```python
_admin_only = [Depends(exige_rol(ROL_ADMINISTRADOR))]

@router.post("", dependencies=_admin_only)
def admin_function(...):
    ...
```

---

*Structure analysis: 2026-08-09*
