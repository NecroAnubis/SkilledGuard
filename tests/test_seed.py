"""El seed debe poder correrse dos veces sin duplicar datos."""

from sqlalchemy import func, select

from app.models import Rol, TipoDocumento, Usuario
from app.seed import sembrar


def _contar(db, modelo) -> int:
    return db.scalar(select(func.count()).select_from(modelo))


def test_seed_crea_los_datos_base(db):
    sembrar(db, "1000000000", "clave-del-admin-1")

    assert _contar(db, TipoDocumento) == 3
    assert _contar(db, Rol) == 4
    admin = db.scalar(select(Usuario).where(Usuario.documento == "1000000000"))
    assert admin is not None
    assert admin.contrasena_hash.startswith("$2b$")


def test_seed_es_idempotente(db):
    sembrar(db, "1000000000", "clave-del-admin-1")
    sembrar(db, "1000000000", "clave-del-admin-1")

    assert _contar(db, TipoDocumento) == 3
    assert _contar(db, Rol) == 4
    assert _contar(db, Usuario) == 1


def test_el_admin_sembrado_puede_iniciar_sesion(cliente, db):
    sembrar(db, "1000000000", "clave-del-admin-1")

    token = cliente.post(
        "/auth/login", data={"username": "1000000000", "password": "clave-del-admin-1"}
    ).json()["access_token"]
    roles = cliente.get("/auth/yo", headers={"Authorization": f"Bearer {token}"}).json()["roles"]
    assert roles == ["Administrador"]
