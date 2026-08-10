# Coding Conventions

**Analysis Date:** 2026-08-09

## Language & Documentation

**All source code comments, docstrings, and function names are in Spanish by design.** This is a deliberate convention, not a defect. The system's domain and stakeholders operate in Spanish (Colombian business context), so code readability for the team takes priority over English-only conventions.

## Naming Patterns

**Files:**
- `snake_case.py` for all Python modules
- Example: `app/auditoria.py`, `app/porteria.py`, `app/schemas.py`
- Routers in `app/routers/[domain].py` where domain names are Spanish: `dispositivos.py`, `usuarios.py`, `movimientos.py`

**Functions & Methods:**
- `snake_case` for all functions, methods, and local variables
- Spanish names reflecting business domain: `listar()`, `obtener()`, `crear()`, `registrar_accion()`, `validar_transicion()`
- Verb-first naming for actions: `hashear_contrasena()`, `generar_png()`, `estado_actual()`
- Private functions prefixed with `_`: `_obtener()`, `_catalogo()`, `_crear_dispositivo()`

**Classes:**
- `PascalCase` for all class names
- Models: `Usuario`, `Dispositivo`, `AuditoriaNegocio`, `LogSistema`, `UsuarioRol`
- Pydantic schemas: `UsuarioCrear`, `UsuarioLeer`, `DispositivoCrear`, `DispositivoEstado`
- Enums: `TipoMovimiento`, `EstadoDispositivo`, `Accion`
- Custom exceptions: `MovimientoInvalido`

**Variables & Constants:**
- `snake_case` for local/instance variables: `id_usuario`, `email_hash`, `ultimo_movimiento`
- `UPPER_SNAKE_CASE` for module-level constants: `ROL_ADMINISTRADOR`, `ROL_SEGURIDAD`, `MAX_BYTES_CONTRASENA`
- Spanish names for meaningful constants that reflect the domain

**Database & ORM:**
- Table names: `snake_case`, Spanish: `usuario`, `dispositivo`, `tipo_documento`, `auditoria_negocio`
- Column names: `snake_case`, Spanish: `contrasena_hash`, `fecha_creado`, `fecha_actualizado`
- Foreign keys: `id_[tabla_singular]`: `id_usuario`, `id_dispositivo`, `id_tipo_documento`
- Enum fields use StrEnum (Python 3.11+): `TipoMovimiento`, `EstadoDispositivo`

## Code Style

**Formatting:**
- Tool: Ruff (linter + formatter)
- Config: `pyproject.toml`
- Line length: 100 characters
- Python target: 3.12

**Linting Rules (Ruff):**
- `E` (Pycodestyle errors)
- `F` (Pyflakes)
- `I` (isort import sorting)
- `UP` (pyupgrade, Python 3.12+ idioms)
- `B` (flake8-bugbear, prevents common bugs)
- `SIM` (flake8-simplify, readability)

**Run checks:**
```bash
ruff check app/ tests/
ruff format app/ tests/
```

## Import Organization

**Order (enforced by Ruff's isort rules):**
1. Standard library (`pathlib`, `datetime`, `enum`, `collections`, `typing`)
2. Third-party packages (`fastapi`, `sqlalchemy`, `pydantic`, `jwt`, `bcrypt`)
3. Local/relative imports (`from app.models import ...`, `from app.database import ...`)

**Path Aliases:**
- None configured — use relative imports from `app/` package
- Imports from sibling modules: `from app.models import Usuario`
- Imports from submodules: `from app.routers.usuarios import router`
- Imports with type annotation: `from typing import Annotated, Literal`

**Pattern - Do NOT use wildcard imports:**
```python
# Good
from app.models import Usuario, Dispositivo, Rol
from app.schemas import UsuarioCrear, UsuarioLeer

# Avoid
from app.models import *
```

## Type Hints

**Convention: Always use type hints for function signatures and class attributes.**

**Patterns used throughout:**
- Modern union syntax: `str | None` instead of `Optional[str]`
- Annotated for FastAPI dependencies: `Annotated[str, Depends(get_db)]`
- SQLAlchemy ORM types: `Mapped[str]`, `Mapped[int]`, `Mapped[list["ChildModel"]]`
- Dict/List types: `dict[str, str]`, `list[Usuario]` (using PEP 585)
- Literal for restricted strings: `Literal["Ingreso", "Salida"]`

Example from `app/routers/usuarios.py`:
```python
def listar(
    db: Annotated[Session, Depends(get_db)],
    limite: Annotated[int, Query(ge=1, le=200)] = 50,
    desplazamiento: Annotated[int, Query(ge=0)] = 0,
) -> list[Usuario]:
```

## Error Handling

**Primary Pattern: HTTPException with status codes**
- `HTTPException` from FastAPI for all HTTP errors
- Always include status code and detail message
- Detail messages in Spanish, user-facing

```python
# From app/routers/usuarios.py
if usuario is None:
    raise HTTPException(status.HTTP_404_NOT_FOUND, "Usuario no encontrado")

# From app/security.py - Suppress internal details with `from None`
except jwt.PyJWTError:
    raise no_autorizado from None
```

**Database Constraint Errors:**
- Catch `IntegrityError` for duplicate keys or constraint violations
- Convert to `HTTPException(status.HTTP_409_CONFLICT, ...)`
- Always rollback the session: `db.rollback()`
- Suppress the exception chain: `raise HTTPException(...) from None`

```python
try:
    db.commit()
except IntegrityError:
    db.rollback()
    raise HTTPException(
        status.HTTP_409_CONFLICT, 
        f"Ya existe un usuario con documento {datos.documento}"
    ) from None
```

**Custom Business Logic Exceptions:**
- Define custom exceptions inheriting from `Exception`: `class MovimientoInvalido(Exception)`
- Use them in business logic (not HTTP endpoints)
- HTTP layer catches and converts to `HTTPException`

**Sentinel Values:**
- Never use `None` to represent "not found" in database queries
- Always check explicitly: `if usuario is None: raise HTTPException(...)`

## Comments & Documentation

**When to Comment (Spanish):**
- Explain "why", not "what" — code shows the what, comments explain the why
- Complex algorithm or non-obvious business rule: see `app/porteria.py`, `app/auditoria.py`
- Security or performance considerations that aren't obvious
- Known limitations or workarounds

**Example from `app/main.py`:**
```python
# Se monta al final: una ruta montada en "/" captura todo lo que no coincida
# con un endpoint anterior, así que declararla antes dejaría la API inalcanzable.
```

**JSDoc/TSDoc (Docstrings):**
- Use triple-quoted docstrings for all modules, functions, and classes
- One-liner for simple functions; multi-line for complex ones
- Spanish language, explaining purpose and key behavior

```python
def estado_actual(db: Session, id_dispositivo: int) -> EstadoDispositivo:
    """Un equipo está dentro si su último movimiento fue un ingreso.
    
    Sin movimientos se considera fuera: el equipo todavía no ha entrado.
    """
```

## Function Design

**Size:** Keep functions focused on a single responsibility
- Prefer small, testable functions
- Helper functions prefixed with `_`: `_obtener()`, `_catalogo()`

**Parameters:**
- Use Annotated with FastAPI dependency injection for common patterns
- Query parameters with validation: `Query(ge=1, le=200)`
- Use dataclasses/Pydantic models for complex input: `UsuarioCrear`, `DispositivoCrear`

**Return Values:**
- Explicit return type annotations on all functions
- No implicit None returns; if a function doesn't return data, declare `-> None`
- Return domain objects (ORM models) from routers and let Pydantic serialize them via `response_model`

## Module Design

**Exports:**
- Group related functions/classes in logical modules
- `app/porteria.py` — business logic for equipment tracking (no HTTP layer)
- `app/auditoria.py` — audit trail functions, separate from HTTP
- `app/routers/` — HTTP endpoints grouped by domain
- `app/schemas.py` — Pydantic models for request/response validation
- `app/models.py` — SQLAlchemy ORM definitions

**Layering:**
- **HTTP Layer** (`app/routers/`): FastAPI endpoints, dependency injection, error handling
- **Business Logic Layer** (`app/porteria.py`, `app/auditoria.py`): Domain rules, isolated from HTTP
- **Data Layer** (`app/models.py`, `app/database.py`): ORM models and session management
- **Configuration** (`app/config.py`, `app/security.py`): Settings and security utilities

**Barrel Files (Index Imports):**
- Not used; explicit imports from specific modules preferred for clarity

## Dependency Injection

**FastAPI Dependencies pattern:**
- Use `Depends()` for database session injection: `Depends(get_db)`
- Use `Depends()` for security/auth: `Depends(usuario_actual)`, `Depends(exige_rol(...))`
- Pre-compute dependencies at module level for reuse:

```python
# From app/routers/dispositivos.py
_consulta = [Depends(exige_rol(ROL_ADMINISTRADOR, ROL_SEGURIDAD))]
_gestion = [Depends(exige_rol(ROL_ADMINISTRADOR))]

@router.get("", response_model=list[DispositivoLeer], dependencies=_consulta)
def listar(...):
```

## Security Patterns

**Password Handling:**
- Hash passwords with bcrypt: `hashear_contrasena(contrasena)`
- Never expose `contrasena_hash` in responses (omit from Pydantic schemas)
- Validate password length in bytes (not characters) due to bcrypt 72-byte limit
- Include bcrypt hash validation in Pydantic validators

**JWT Tokens:**
- Create tokens with user ID and roles: `crear_token(usuario, roles)`
- Verify token and return user object: `usuario_actual()` dependency
- Custom exceptions converted to 401 Unauthorized

**Role-Based Access Control:**
- Define role constants: `ROL_ADMINISTRADOR`, `ROL_SEGURIDAD`, `ROL_USUARIO`
- Use dependency: `Depends(exige_rol(ROL_ADMINISTRADOR))`
- Routes can require multiple roles: `exige_rol(ROL_ADMINISTRADOR, ROL_SEGURIDAD)`

## Database Patterns

**Session Management:**
- Use context manager with FastAPI dependency: `Depends(get_db)`
- Always commit or rollback explicitly: `db.commit()`, `db.rollback()`
- Flush for intermediate operations that need IDs: `db.flush()`

**Query Patterns:**
- Use SQLAlchemy `select()` with type hints over `.query()`
- Use `db.get(Model, id)` for simple lookups by primary key
- Use relationships for lazy-loaded associations
- Avoid N+1 queries: batch queries where possible (see `estados_de_todos()` in `app/porteria.py`)

**Transactions:**
- Each endpoint is a transaction by default (auto-commit or auto-rollback)
- For multi-step operations: commit explicitly after each logical step
- Use pessimistic locking for concurrent access: `with_for_update()`

## Testing Conventions

**See TESTING.md for full testing patterns. Key points for conventions:**
- Test names in Spanish, prefixed with `test_`
- Test files mirror source structure: `tests/test_[module].py`
- Fixtures in `tests/conftest.py` for shared test data
- Mock/override dependencies via `app.dependency_overrides`

---

*Convention analysis: 2026-08-09*
