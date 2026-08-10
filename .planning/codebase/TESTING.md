# Testing Patterns

**Analysis Date:** 2026-08-09

## Test Framework

**Runner:**
- pytest 8.3.4
- Config: `pyproject.toml` with `testpaths = ["tests"]`
- Run all tests: `pytest`
- Run with verbose output: `pytest -v`
- Run specific test: `pytest tests/test_usuarios.py::test_crear_usuario`
- Watch mode: `pytest --watch` (with pytest-watch plugin, if installed)

**Assertion Library:**
- pytest built-in assertions
- `assert` statements with optional messages
- `pytest.raises()` for exception testing

**HTTP Testing:**
- FastAPI's `TestClient` from `fastapi.testclient`
- HTTP methods: `cliente.get()`, `cliente.post()`, `cliente.patch()`, `cliente.delete()`
- Assertions on `status_code` and `.json()` response bodies

## Test File Organization

**Location:**
- Co-located in `tests/` directory parallel to `app/`
- One test file per module: `tests/test_[module].py`

**Naming:**
- Test files: `test_*.py` or `*_test.py` (uses `test_*` convention)
- Test functions: `test_[what_is_being_tested]()` — in Spanish, reflecting the behavior tested
- Example: `test_crear_usuario()`, `test_la_respuesta_nunca_expone_la_contrasena()`

**Structure:**
```
tests/
├── conftest.py              # Shared fixtures and setup
├── test_auditoria.py        # Audit trail tests
├── test_auth.py             # Authentication & authorization tests
├── test_catalogos.py        # Catalog CRUD tests
├── test_dispositivos.py     # Equipment API tests
├── test_porteria.py         # Entry control business logic tests
├── test_reportes.py         # Report generation tests
├── test_seed.py             # Data seeding tests
├── test_seguridad.py        # Security tests
└── test_usuarios.py         # User management tests
```

## Test Structure

**Suite Organization:**

Tests are organized by feature/module, not by type (unit/integration). Each file contains related tests:

```python
# From tests/test_porteria.py - organized by concern
# --- La máquina de estados, sin base de datos -------
def test_un_equipo_fuera_puede_ingresar():
    validar_transicion(EstadoDispositivo.FUERA, TipoMovimiento.INGRESO)

# --- Contra la base de datos --------
def test_un_equipo_nuevo_esta_fuera(db, dispositivo):
    assert estado_actual(db, dispositivo.id) == EstadoDispositivo.FUERA
```

**Patterns:**

**Setup (Fixtures from conftest):**
- `db` — clean database session per test
- `cliente` — TestClient with dependency overrides
- `admin` — Usuario with Administrador role
- `token_admin` — JWT token for admin user
- `encabezados_admin` — HTTP headers with Authorization
- `catalogos_porteria` — TipoDispositivo + entry/exit types
- `dispositivo`, `otro_dispositivo` — sample equipment

Example usage:
```python
def test_crear_usuario(cliente, db, encabezados_admin):
    tipo = db.query(TipoDocumento).first()
    respuesta = cliente.post(
        "/usuarios",
        headers=encabezados_admin,
        json={...},
    )
    assert respuesta.status_code == 201
```

**Teardown:**
- Implicit via fixture scope
- `db` fixture drops and recreates all tables before each test
- `cliente` clears dependency overrides after each test

## Test Implementation Details

### Database Setup (conftest.py)

```python
@pytest.fixture
def db():
    """Base limpia por prueba: sin esto una prueba hereda los datos de la anterior."""
    Base.metadata.drop_all(motor)
    Base.metadata.create_all(motor)
    with SesionPrueba() as sesion:
        yield sesion
```

**Key pattern:**
- Each test starts with a fresh database schema
- Uses SQLAlchemy metadata to drop/create tables
- Returns a session, tests can query directly

### HTTP Client Setup

```python
@pytest.fixture
def cliente(db):
    app.dependency_overrides[get_db] = lambda: db
    yield TestClient(app)
    app.dependency_overrides.clear()
```

**Key pattern:**
- Override the `get_db` dependency to inject test session
- Use FastAPI's TestClient for HTTP testing
- Clear overrides after test (cleanup)

### Test Data Fixtures

**Admin User:**
```python
@pytest.fixture
def admin(db) -> Usuario:
    """Usuario con rol Administrador y contraseña conocida."""
    tipo = TipoDocumento(nombre="Cédula de ciudadanía", acronimo="CC")
    rol = Rol(nombre=ROL_ADMINISTRADOR, descripcion="Gestión total del sistema")
    db.add_all([tipo, rol])
    db.flush()
    usuario = Usuario(
        nombres="Johan",
        apellidos="Restrepo",
        id_tipo_documento=tipo.id,
        documento="1002003001",
        contrasena_hash=hashear_contrasena("clave-segura-123"),
    )
    db.add(usuario)
    db.flush()
    db.add(UsuarioRol(id_usuario=usuario.id, id_rol=rol.id))
    db.commit()
    return usuario
```

**Token and Headers:**
```python
@pytest.fixture
def token_admin(cliente, admin) -> str:
    respuesta = cliente.post(
        "/auth/login", data={"username": admin.documento, "password": "clave-segura-123"}
    )
    assert respuesta.status_code == 200, respuesta.text
    return respuesta.json()["access_token"]

@pytest.fixture
def encabezados_admin(token_admin) -> dict[str, str]:
    return {"Authorization": f"Bearer {token_admin}"}
```

**Catalog Data (for portería tests):**
```python
@pytest.fixture
def catalogos_porteria(db):
    """Tipos de registro Ingreso/Salida, que la portería busca por nombre."""
    tipo_equipo = TipoDispositivo(nombre="Computador", descripcion="Portátil o escritorio")
    db.add_all([
        tipo_equipo,
        TipoRegistro(nombre=TipoMovimiento.INGRESO.value, descripcion="Entrada"),
        TipoRegistro(nombre=TipoMovimiento.SALIDA.value, descripcion="Salida"),
    ])
    db.commit()
    return tipo_equipo
```

**Equipment Fixtures:**
```python
def _crear_dispositivo(db, tipo_equipo, admin, serial: str) -> Dispositivo:
    dispositivo = Dispositivo(
        serial=serial,
        marca="HP",
        modelo="Pavilion",
        sistema="Windows 11",
        id_tipo_dispositivo=tipo_equipo.id,
        id_usuario=admin.id,
    )
    db.add(dispositivo)
    db.commit()
    return dispositivo

@pytest.fixture
def dispositivo(db, catalogos_porteria, admin) -> Dispositivo:
    return _crear_dispositivo(db, catalogos_porteria, admin, "PC-12345")

@pytest.fixture
def otro_dispositivo(db, catalogos_porteria, admin) -> Dispositivo:
    return _crear_dispositivo(db, catalogos_porteria, admin, "PC-67890")
```

**Pattern: Use helper functions for fixture composition, avoid duplication**

## Mocking

**Framework:** Manual dependency overrides via `app.dependency_overrides`

**Pattern:**
```python
# In conftest.py
@pytest.fixture
def cliente(db):
    app.dependency_overrides[get_db] = lambda: db
    yield TestClient(app)
    app.dependency_overrides.clear()
```

**What to Mock:**
- Database session: Always — inject test session via dependency override
- External APIs (if they existed): Mock at the client library level
- Configuration: Override via environment variables in conftest

**What NOT to Mock:**
- Business logic functions (they're testable, test them)
- ORM query results (use real database with transactions)
- Password hashing (it's fast, use real hashing)
- JWT generation (it's deterministic, use real tokens)

## Fixtures and Factories

**Test Data Pattern:**

Fixtures in `tests/conftest.py` provide:
1. Database session (`db`)
2. HTTP client with overrides (`cliente`)
3. Authenticated user (`admin`)
4. JWT token (`token_admin`)
5. HTTP headers with auth (`encabezados_admin`)
6. Business domain fixtures (`catalogos_porteria`, `dispositivo`, `otro_dispositivo`)

**Location:**
- `tests/conftest.py` — shared fixtures for all tests
- Fixtures are auto-discovered by pytest

**Composition:**
Fixtures depend on other fixtures (pytest resolves the dependency graph):
```python
@pytest.fixture
def encabezados_admin(token_admin) -> dict[str, str]:
    return {"Authorization": f"Bearer {token_admin}"}
```

## Coverage

**Requirements:** Not enforced (no coverage threshold configured)

**View Coverage (if coverage.py installed):**
```bash
pytest --cov=app --cov-report=html tests/
# Open htmlcov/index.html in browser
```

**Current Focus:**
- All HTTP endpoints tested (happy path + error cases)
- Business logic functions tested with and without database
- Security checks tested (auth, role-based access)
- Edge cases and constraint violations tested

## Test Types

**Unit Tests (Business Logic, No Database):**

Isolated testing of pure functions and state machines:

```python
# From tests/test_porteria.py
def test_un_equipo_dentro_no_puede_volver_a_ingresar():
    with pytest.raises(MovimientoInvalido, match="ya se encuentra dentro"):
        validar_transicion(EstadoDispositivo.DENTRO, TipoMovimiento.INGRESO)
```

**Scope:** Single function, no database, no HTTP
**Approach:** Direct function calls, verify outputs and exceptions

**Integration Tests (HTTP + Database):**

End-to-end testing through the HTTP layer:

```python
# From tests/test_usuarios.py
def test_crear_usuario(cliente, db, encabezados_admin):
    tipo = db.query(TipoDocumento).first()
    respuesta = cliente.post(
        "/usuarios",
        headers=encabezados_admin,
        json={
            "nombres": "María",
            "apellidos": "Gómez",
            "id_tipo_documento": tipo.id,
            "documento": "1002003002",
            "contrasena": "otra-clave-segura",
        },
    )
    assert respuesta.status_code == 201, respuesta.text
    assert respuesta.json()["documento"] == "1002003002"
```

**Scope:** Full request cycle (HTTP → validation → database → response)
**Approach:** Use TestClient, assert on status codes and response bodies

**E2E Tests:**
- Not present in current codebase
- Could test browser interactions if UI existed (Selenium, Playwright)

## Common Patterns

**Async Testing:**
- Not used — FastAPI endpoints are sync (no `async def`)
- Database operations are sync via SQLAlchemy ORM

**Error Testing:**

Test exceptions and error responses:

```python
def test_usuario_inexistente_da_404(cliente, encabezados_admin):
    respuesta = cliente.get("/usuarios/9999", headers=encabezados_admin)
    assert respuesta.status_code == 404

def test_un_equipo_fuera_no_puede_salir():
    with pytest.raises(MovimientoInvalido, match="no ha registrado ingreso"):
        validar_transicion(EstadoDispositivo.FUERA, TipoMovimiento.SALIDA)
```

**Pattern:**
- HTTP errors: check `status_code` and optional detail message in response
- Business logic errors: use `pytest.raises()` with optional `match` for message validation

**Security Testing:**

Verify authentication, authorization, and data protection:

```python
# Authentication required
def test_endpoint_protegido_sin_token_da_401(cliente):
    assert cliente.get("/usuarios").status_code == 401

# Role-based access control
def test_usuario_sin_rol_admin_no_puede_listar(cliente, db, admin, encabezados_admin):
    # Create non-admin user
    tipo = db.query(TipoDocumento).first()
    cliente.post(
        "/usuarios",
        headers=encabezados_admin,
        json={...},
    )
    # Try to access admin endpoint
    token = cliente.post(
        "/auth/login", data={"username": "1002003007", "password": "clave-vigilante-1"}
    ).json()["access_token"]
    respuesta = cliente.get("/usuarios", headers={"Authorization": f"Bearer {token}"})
    assert respuesta.status_code == 403

# Sensitive data not exposed
def test_la_respuesta_nunca_expone_la_contrasena(cliente, db, encabezados_admin):
    tipo = db.query(TipoDocumento).first()
    cuerpo = cliente.post(
        "/usuarios",
        headers=encabezados_admin,
        json={...},
    ).json()
    assert "contrasena" not in cuerpo
    assert "contrasena_hash" not in cuerpo
```

**Constraint Testing:**

Verify database constraints and business rule validation:

```python
# Duplicate key
def test_documento_duplicado_da_409(cliente, db, admin, encabezados_admin):
    tipo = db.query(TipoDocumento).first()
    respuesta = cliente.post(
        "/usuarios",
        headers=encabezados_admin,
        json={
            "nombres": "Otro",
            "apellidos": "Usuario",
            "id_tipo_documento": tipo.id,
            "documento": admin.documento,  # Already exists
            "contrasena": "clave-segura-123",
        },
    )
    assert respuesta.status_code == 409

# Validation error
def test_contrasena_corta_es_rechazada(cliente, db, encabezados_admin):
    tipo = db.query(TipoDocumento).first()
    respuesta = cliente.post(
        "/usuarios",
        headers=encabezados_admin,
        json={
            "nombres": "Corta",
            "apellidos": "Clave",
            "id_tipo_documento": tipo.id,
            "documento": "1002003005",
            "contrasena": "corta",  # Too short
        },
    )
    assert respuesta.status_code == 422
```

**Performance Testing:**

Test N+1 query prevention and efficient queries:

```python
# From tests/test_dispositivos.py
def test_el_listado_incluye_el_estado_de_cada_equipo(
    cliente, dispositivo, otro_dispositivo, encabezados_admin
):
    """El listado trae el estado ya resuelto: sin esto la interfaz lo pediría
    equipo por equipo, convirtiendo una pantalla en una consulta por fila."""
    cliente.post(
        "/movimientos", headers=encabezados_admin, json={"qr": dispositivo.qr, "tipo": "Ingreso"}
    )
    equipos = cliente.get("/dispositivos", headers=encabezados_admin).json()
    por_serial = {e["serial"]: e["estado"] for e in equipos}
    assert por_serial[dispositivo.serial] == "dentro"
    assert por_serial[otro_dispositivo.serial] == "fuera"
```

**Binary Response Testing:**

Test image and file responses:

```python
def test_el_endpoint_de_qr_devuelve_una_imagen_png(cliente, dispositivo, encabezados_admin):
    respuesta = cliente.get(f"/dispositivos/{dispositivo.id}/qr", headers=encabezados_admin)
    assert respuesta.status_code == 200
    assert respuesta.headers["content-type"] == "image/png"
    # Firma de un archivo PNG válido.
    assert respuesta.content.startswith(b"\x89PNG\r\n\x1a\n")
```

## Test Naming Philosophy

**Test names describe the behavior being verified, not the implementation:**

```python
# Good — describes what should happen
test_crear_usuario()
test_la_respuesta_nunca_expone_la_contrasena()
test_documento_duplicado_da_409()
test_un_equipo_dentro_no_puede_volver_a_ingresar()
test_el_listado_incluye_el_estado_de_cada_equipo()

# Avoid — too implementation-focused
test_post_usuarios_endpoint()
test_check_field_not_in_response()
```

**Docstrings in test functions explain intent when non-obvious:**

```python
def test_login_de_usuario_inexistente_da_el_mismo_error(cliente, admin):
    """No debe revelar si el documento existe o no."""
    inexistente = cliente.post(
        "/auth/login", data={"username": "0000000000", "password": "clave-segura-123"}
    )
    errada = cliente.post(
        "/auth/login", data={"username": admin.documento, "password": "equivocada"}
    )
    assert inexistente.status_code == errada.status_code == 401
```

---

*Testing analysis: 2026-08-09*
