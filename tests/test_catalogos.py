"""Pruebas de los catálogos y del endpoint de salud.

Cubren los defectos encontrados en la revisión del Sprint 1: catálogos que
admitían duplicados, paginación sin tope y un /salud que no miraba la base.
"""

from app.models import TipoDocumento


def _crear_tipo(cliente, encabezados, nombre="Pasaporte", acronimo="PA"):
    return cliente.post(
        "/tipos-documento",
        headers=encabezados,
        json={"nombre": nombre, "acronimo": acronimo},
    )


def test_crear_tipo_documento(cliente, encabezados_admin):
    assert _crear_tipo(cliente, encabezados_admin).status_code == 201


def test_no_permite_catalogos_duplicados(cliente, db, encabezados_admin):
    _crear_tipo(cliente, encabezados_admin)
    repetido = _crear_tipo(cliente, encabezados_admin)

    assert repetido.status_code == 409
    assert db.query(TipoDocumento).filter_by(nombre="Pasaporte").count() == 1


def test_no_permite_roles_duplicados(cliente, encabezados_admin):
    cuerpo = {"nombre": "Auditor", "descripcion": "Consulta de auditorías"}
    assert cliente.post("/roles", headers=encabezados_admin, json=cuerpo).status_code == 201
    assert cliente.post("/roles", headers=encabezados_admin, json=cuerpo).status_code == 409


def test_crear_catalogo_exige_rol_administrador(cliente):
    """Sin token no se puede escribir en un catálogo."""
    assert cliente.post("/roles", json={"nombre": "Intruso"}).status_code == 401


def test_el_limite_de_paginacion_esta_acotado(cliente, encabezados_admin):
    assert cliente.get("/usuarios?limite=999999", headers=encabezados_admin).status_code == 422
    assert cliente.get("/usuarios?limite=0", headers=encabezados_admin).status_code == 422
    assert cliente.get("/usuarios?limite=200", headers=encabezados_admin).status_code == 200


def test_salud_reporta_el_estado_de_la_base(cliente):
    assert cliente.get("/salud").json() == {"estado": "ok", "base_de_datos": "ok"}
