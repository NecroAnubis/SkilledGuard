"""Pruebas de autenticación y control de acceso por rol."""


def test_salud_no_requiere_token(cliente):
    assert cliente.get("/salud").status_code == 200


def test_login_correcto_devuelve_token(cliente, admin):
    respuesta = cliente.post(
        "/auth/login", data={"username": admin.documento, "password": "clave-segura-123"}
    )
    assert respuesta.status_code == 200
    assert respuesta.json()["token_type"] == "bearer"


def test_login_con_contrasena_errada_falla(cliente, admin):
    respuesta = cliente.post(
        "/auth/login", data={"username": admin.documento, "password": "equivocada"}
    )
    assert respuesta.status_code == 401


def test_login_de_usuario_inexistente_da_el_mismo_error(cliente, admin):
    """No debe revelar si el documento existe o no."""
    inexistente = cliente.post(
        "/auth/login", data={"username": "0000000000", "password": "clave-segura-123"}
    )
    errada = cliente.post(
        "/auth/login", data={"username": admin.documento, "password": "equivocada"}
    )
    assert inexistente.status_code == errada.status_code == 401
    assert inexistente.json()["detail"] == errada.json()["detail"]


def test_yo_devuelve_los_roles(cliente, encabezados_admin):
    datos = cliente.get("/auth/yo", headers=encabezados_admin).json()
    assert datos["documento"] == "1002003001"
    assert datos["roles"] == ["Administrador"]


def test_endpoint_protegido_sin_token_da_401(cliente):
    assert cliente.get("/usuarios").status_code == 401


def test_token_invalido_da_401(cliente):
    respuesta = cliente.get("/usuarios", headers={"Authorization": "Bearer no-es-un-token"})
    assert respuesta.status_code == 401
