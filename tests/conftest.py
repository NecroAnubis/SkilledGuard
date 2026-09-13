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
from app.models import Base, Dispositivo, Rol, TipoDocumento, Usuario, UsuarioRol  # noqa: E402
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
        correo="admin@skilledguard.co",
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


@pytest.fixture
def catalogos_porteria(db):
    """Tipos de registro Ingreso/Salida, que la portería busca por nombre."""
    from app.models import TipoDispositivo, TipoRegistro
    from app.porteria import TipoMovimiento

    tipo_equipo = TipoDispositivo(nombre="Computador", descripcion="Portátil o escritorio")
    db.add_all(
        [
            tipo_equipo,
            TipoRegistro(nombre=TipoMovimiento.INGRESO.value, descripcion="Entrada"),
            TipoRegistro(nombre=TipoMovimiento.SALIDA.value, descripcion="Salida"),
        ]
    )
    db.commit()
    return tipo_equipo


def _crear_dispositivo(db, tipo_equipo, admin, serial: str) -> Dispositivo:
    dispositivo = Dispositivo(
        serial=serial,
        marca="HP",
        modelo="Pavilion",
        sistema="Windows 11",
        id_tipo_dispositivo=tipo_equipo.id,
        responsable="Laura Vargas",
        documento_responsable="1098765432",
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
