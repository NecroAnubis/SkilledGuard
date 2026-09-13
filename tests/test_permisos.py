"""Permisos vistos desde afuera: qué alcanza cada rol y qué no.

La interfaz oculta lo que un rol no puede hacer, pero eso es comodidad. Estas
pruebas verifican la única barrera que cuenta: la del servidor.
"""

import pytest

from app.models import Rol, Usuario, UsuarioRol
from app.security import ROL_SEGURIDAD, hashear_contrasena

CATALOGOS = ["/roles", "/porterias", "/tipos-documento", "/tipos-dispositivo"]


def _cuenta(cliente, db, admin, documento: str, rol: str | None) -> dict[str, str]:
    """Crea una cuenta con el rol indicado (o sin ninguno) y devuelve su encabezado."""
    usuario = Usuario(
        nombres="Cuenta",
        apellidos="Prueba",
        id_tipo_documento=admin.id_tipo_documento,
        documento=documento,
        contrasena_hash=hashear_contrasena("clave-de-prueba-1"),
    )
    db.add(usuario)
    db.flush()
    if rol is not None:
        fila = db.query(Rol).filter(Rol.nombre == rol).first() or Rol(nombre=rol)
        db.add(fila)
        db.flush()
        db.add(UsuarioRol(id_usuario=usuario.id, id_rol=fila.id))
    db.commit()

    respuesta = cliente.post(
        "/auth/login", data={"username": documento, "password": "clave-de-prueba-1"}
    )
    assert respuesta.status_code == 200, respuesta.text
    return {"Authorization": f"Bearer {respuesta.json()['access_token']}"}


@pytest.mark.parametrize("ruta", CATALOGOS)
def test_los_catalogos_exigen_sesion(cliente, ruta):
    """No hay datos personales, pero sí el mapa del sistema: cómo se llaman las
    porterías de la sede y qué roles existen."""
    assert cliente.get(ruta).status_code == 401


@pytest.mark.parametrize("ruta", CATALOGOS)
def test_cualquier_sesion_lee_los_catalogos(cliente, db, admin, ruta):
    """Hasta una cuenta sin rol los necesita: son las listas de los formularios."""
    encabezados = _cuenta(cliente, db, admin, "7000000001", None)
    assert cliente.get(ruta, headers=encabezados).status_code == 200


def test_una_cuenta_sin_rol_no_alcanza_nada_del_sistema(cliente, db, admin):
    encabezados = _cuenta(cliente, db, admin, "7000000002", None)
    for ruta in ["/dispositivos", "/movimientos", "/usuarios", "/logs"]:
        assert cliente.get(ruta, headers=encabezados).status_code == 403, ruta


def test_cada_quien_ve_solo_sus_equipos(cliente, db, admin, dispositivo, encabezados_admin):
    """`/dispositivos/mios` se resuelve con el documento de la sesión: no hay
    forma de pedir los equipos de otra persona."""
    ajeno = _cuenta(cliente, db, admin, "7000000003", None)
    assert cliente.get("/dispositivos/mios", headers=ajeno).json() == []

    propio = _cuenta(cliente, db, admin, dispositivo.documento_responsable, None)
    mios = cliente.get("/dispositivos/mios", headers=propio).json()
    assert [e["serial"] for e in mios] == [dispositivo.serial]


def test_los_movimientos_propios_son_solo_los_propios(
    cliente, db, admin, dispositivo, otro_dispositivo, encabezados_admin
):
    cliente.post(
        "/movimientos", headers=encabezados_admin, json={"qr": dispositivo.qr, "tipo": "Ingreso"}
    )
    otro_dispositivo.documento_responsable = "9999999999"
    db.commit()
    cliente.post(
        "/movimientos",
        headers=encabezados_admin,
        json={"qr": otro_dispositivo.qr, "tipo": "Ingreso"},
    )

    propio = _cuenta(cliente, db, admin, dispositivo.documento_responsable, None)
    mios = cliente.get("/movimientos/mios", headers=propio).json()
    assert {m["serial"] for m in mios} == {dispositivo.serial}


def test_seguridad_no_crea_equipos_ni_ve_usuarios(cliente, db, admin, catalogos_porteria):
    encabezados = _cuenta(cliente, db, admin, "7000000004", ROL_SEGURIDAD)
    creacion = cliente.post(
        "/dispositivos",
        headers=encabezados,
        json={
            "serial": "SEG-1",
            "marca": "M",
            "modelo": "M",
            "id_tipo_dispositivo": catalogos_porteria.id,
            "responsable": "R",
            "documento_responsable": "1",
        },
    )
    assert creacion.status_code == 403
    assert cliente.get("/usuarios", headers=encabezados).status_code == 403
    assert cliente.get("/logs", headers=encabezados).status_code == 403
    # Lo que sí necesita para trabajar:
    assert cliente.get("/dispositivos", headers=encabezados).status_code == 200
    assert cliente.get("/movimientos", headers=encabezados).status_code == 200
