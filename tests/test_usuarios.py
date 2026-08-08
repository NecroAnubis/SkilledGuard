"""Pruebas del CRUD de usuarios y de la asignación de roles."""

from app.models import Rol, TipoDocumento, Usuario


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


def test_la_respuesta_nunca_expone_la_contrasena(cliente, db, encabezados_admin):
    tipo = db.query(TipoDocumento).first()
    cuerpo = cliente.post(
        "/usuarios",
        headers=encabezados_admin,
        json={
            "nombres": "Juan",
            "apellidos": "Martínez",
            "id_tipo_documento": tipo.id,
            "documento": "1002003003",
            "contrasena": "clave-de-juan-123",
        },
    ).json()
    assert "contrasena" not in cuerpo
    assert "contrasena_hash" not in cuerpo


def test_la_contrasena_se_guarda_hasheada(cliente, db, encabezados_admin):
    tipo = db.query(TipoDocumento).first()
    cliente.post(
        "/usuarios",
        headers=encabezados_admin,
        json={
            "nombres": "Ana",
            "apellidos": "Díaz",
            "id_tipo_documento": tipo.id,
            "documento": "1002003004",
            "contrasena": "clave-en-claro-123",
        },
    )
    guardado = db.query(Usuario).filter_by(documento="1002003004").one()
    assert guardado.contrasena_hash != "clave-en-claro-123"
    assert guardado.contrasena_hash.startswith("$2b$")


def test_documento_duplicado_da_409(cliente, db, admin, encabezados_admin):
    tipo = db.query(TipoDocumento).first()
    respuesta = cliente.post(
        "/usuarios",
        headers=encabezados_admin,
        json={
            "nombres": "Otro",
            "apellidos": "Usuario",
            "id_tipo_documento": tipo.id,
            "documento": admin.documento,
            "contrasena": "clave-segura-123",
        },
    )
    assert respuesta.status_code == 409


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
            "contrasena": "corta",
        },
    )
    assert respuesta.status_code == 422


def test_tipo_documento_inexistente_da_422(cliente, encabezados_admin):
    respuesta = cliente.post(
        "/usuarios",
        headers=encabezados_admin,
        json={
            "nombres": "Sin",
            "apellidos": "Tipo",
            "id_tipo_documento": 999,
            "documento": "1002003006",
            "contrasena": "clave-segura-123",
        },
    )
    assert respuesta.status_code == 422


def test_asignar_rol_duplicado_da_409(cliente, db, admin, encabezados_admin):
    rol = db.query(Rol).one()
    respuesta = cliente.post(
        f"/usuarios/{admin.id}/roles", headers=encabezados_admin, json={"id_rol": rol.id}
    )
    assert respuesta.status_code == 409


def test_usuario_sin_rol_admin_no_puede_listar(cliente, db, admin, encabezados_admin):
    """El control por rol debe rechazar a un autenticado sin el rol requerido."""
    tipo = db.query(TipoDocumento).first()
    cliente.post(
        "/usuarios",
        headers=encabezados_admin,
        json={
            "nombres": "Vigilante",
            "apellidos": "Portería",
            "id_tipo_documento": tipo.id,
            "documento": "1002003007",
            "contrasena": "clave-vigilante-1",
        },
    )
    token = cliente.post(
        "/auth/login", data={"username": "1002003007", "password": "clave-vigilante-1"}
    ).json()["access_token"]

    respuesta = cliente.get("/usuarios", headers={"Authorization": f"Bearer {token}"})
    assert respuesta.status_code == 403
