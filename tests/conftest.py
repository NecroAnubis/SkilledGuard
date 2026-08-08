import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Debe fijarse antes de importar la app, que lee la configuración al importarse.
os.environ.setdefault("JWT_SECRET", "secreto-de-pruebas")
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg://skilledguard:skilledguard@localhost:5432/skilledguard_test",
)

from app.database import get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Base, Rol, TipoDocumento, Usuario, UsuarioRol  # noqa: E402
from app.security import ROL_ADMINISTRADOR, hashear_contrasena  # noqa: E402

motor = create_engine(os.environ["DATABASE_URL"])
SesionPrueba = sessionmaker(bind=motor, expire_on_commit=False)


@pytest.fixture
def db():
    """Base limpia por prueba: sin esto una prueba hereda los datos de la anterior."""
    Base.metadata.drop_all(motor)
    Base.metadata.create_all(motor)
    with SesionPrueba() as sesion:
        yield sesion


@pytest.fixture
def cliente(db):
    app.dependency_overrides[get_db] = lambda: db
    yield TestClient(app)
    app.dependency_overrides.clear()


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
