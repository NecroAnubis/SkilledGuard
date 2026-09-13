"""Cambio de contraseña propio, restablecimiento por administrador y edición.

Los bordes importan más que el caso feliz: una contraseña se cambia poco, pero
cada camino equivocado entrega una cuenta.
"""

from app.models import Usuario
from app.security import DOMINIO_CORPORATIVO, verificar_contrasena

CLAVE = "clave-segura-123"


def _nueva_sesion(cliente, documento: str, clave: str):
    return cliente.post("/auth/login", data={"username": documento, "password": clave})


def test_cambio_el_usuario_cambia_su_contrasena(cliente, db, admin, encabezados_admin):
    respuesta = cliente.post(
        "/auth/contrasena",
        headers=encabezados_admin,
        json={"contrasena_actual": CLAVE, "contrasena_nueva": "una-clave-nueva-9"},
    )
    assert respuesta.status_code == 204, respuesta.text

    assert _nueva_sesion(cliente, admin.documento, "una-clave-nueva-9").status_code == 200
    assert _nueva_sesion(cliente, admin.documento, CLAVE).status_code == 401


def test_sin_la_contrasena_actual_no_hay_cambio(cliente, db, admin, encabezados_admin):
    """Una sesión abierta no basta: en portería el equipo es compartido."""
    respuesta = cliente.post(
        "/auth/contrasena",
        headers=encabezados_admin,
        json={"contrasena_actual": "la-que-no-es", "contrasena_nueva": "una-clave-nueva-9"},
    )
    assert respuesta.status_code == 400

    db.refresh(admin)
    assert verificar_contrasena(CLAVE, admin.contrasena_hash), "la contraseña no debió cambiar"


def test_el_cambio_exige_sesion(cliente):
    respuesta = cliente.post(
        "/auth/contrasena",
        json={"contrasena_actual": CLAVE, "contrasena_nueva": "una-clave-nueva-9"},
    )
    assert respuesta.status_code == 401


def test_la_contrasena_nueva_no_puede_ser_corta(cliente, encabezados_admin):
    respuesta = cliente.post(
        "/auth/contrasena",
        headers=encabezados_admin,
        json={"contrasena_actual": CLAVE, "contrasena_nueva": "corta"},
    )
    assert respuesta.status_code == 422


def test_el_rastro_del_cambio_nunca_guarda_la_contrasena(cliente, db, encabezados_admin):
    from app.models import LogDetalle

    cliente.post(
        "/auth/contrasena",
        headers=encabezados_admin,
        json={"contrasena_actual": CLAVE, "contrasena_nueva": "una-clave-nueva-9"},
    )
    valores = [
        (d.valor_anterior or "") + (d.valor_nuevo or "") for d in db.query(LogDetalle).all()
    ]
    assert not any("una-clave-nueva-9" in v for v in valores)


def test_el_administrador_restablece_una_contrasena_olvidada(
    cliente, db, admin, encabezados_admin
):
    tipo = admin.id_tipo_documento
    creado = cliente.post(
        "/usuarios",
        headers=encabezados_admin,
        json={
            "nombres": "Olvidadiza",
            "apellidos": "Pérez",
            "id_tipo_documento": tipo,
            "documento": "8000000001",
            "contrasena": "la-vieja-clave-1",
        },
    ).json()

    respuesta = cliente.post(
        f"/usuarios/{creado['id']}/contrasena",
        headers=encabezados_admin,
        json={"contrasena_nueva": "la-nueva-clave-1"},
    )
    assert respuesta.status_code == 204, respuesta.text
    assert _nueva_sesion(cliente, "8000000001", "la-nueva-clave-1").status_code == 200


def test_solo_el_administrador_restablece(cliente, db, admin, encabezados_admin):
    """Un guarda no puede apropiarse de la cuenta de otro."""
    from tests.test_permisos import _cuenta

    ajeno = _cuenta(cliente, db, admin, "8000000002", "Seguridad")
    respuesta = cliente.post(
        f"/usuarios/{admin.id}/contrasena",
        headers=ajeno,
        json={"contrasena_nueva": "la-nueva-clave-1"},
    )
    assert respuesta.status_code == 403


def test_editar_corrige_los_datos_de_una_cuenta(cliente, db, admin, encabezados_admin):
    creado = cliente.post(
        "/usuarios",
        headers=encabezados_admin,
        json={
            "nombres": "Nombre",
            "apellidos": "Malo",
            "id_tipo_documento": admin.id_tipo_documento,
            "documento": "8000000003",
            "contrasena": "clave-para-editar",
        },
    ).json()

    respuesta = cliente.patch(
        f"/usuarios/{creado['id']}",
        headers=encabezados_admin,
        json={"apellidos": "Bueno", "correo": "Nombre.Bueno@SkilledGuard.CO"},
    )
    assert respuesta.status_code == 200, respuesta.text
    assert respuesta.json()["apellidos"] == "Bueno"
    assert respuesta.json()["correo"] == "nombre.bueno@skilledguard.co"


def test_editar_no_puede_sacar_a_un_admin_del_dominio(cliente, db, admin, encabezados_admin):
    """Si no, esta ruta sería la puerta trasera de la regla del correo."""
    respuesta = cliente.patch(
        f"/usuarios/{admin.id}",
        headers=encabezados_admin,
        json={"correo": "personal@gmail.com"},
    )
    assert respuesta.status_code == 422
    assert DOMINIO_CORPORATIVO in respuesta.json()["detail"]

    db.refresh(admin)
    assert admin.correo == "admin@skilledguard.co"


def test_editar_no_permite_repetir_un_correo(cliente, db, admin, encabezados_admin):
    creado = cliente.post(
        "/usuarios",
        headers=encabezados_admin,
        json={
            "nombres": "Otra",
            "apellidos": "Cuenta",
            "id_tipo_documento": admin.id_tipo_documento,
            "documento": "8000000004",
            "contrasena": "clave-para-editar",
        },
    ).json()

    respuesta = cliente.patch(
        f"/usuarios/{creado['id']}", headers=encabezados_admin, json={"correo": admin.correo}
    )
    assert respuesta.status_code == 409


def test_editar_no_toca_el_documento(cliente, db, admin, encabezados_admin):
    """El documento es la identidad: cambiarlo haría de la cuenta otra persona."""
    respuesta = cliente.patch(
        f"/usuarios/{admin.id}", headers=encabezados_admin, json={"documento": "9999999999"}
    )
    db.refresh(admin)
    assert admin.documento != "9999999999"
    assert respuesta.status_code in (200, 422)


def test_solo_el_administrador_edita(cliente, db, admin):
    from tests.test_permisos import _cuenta

    ajeno = _cuenta(cliente, db, admin, "8000000005", "Seguridad")
    assert (
        cliente.patch(f"/usuarios/{admin.id}", headers=ajeno, json={"nombres": "Otro"}).status_code
        == 403
    )
