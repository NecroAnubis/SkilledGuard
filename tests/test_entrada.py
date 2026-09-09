"""Pruebas del rol Entrada: autoservicio de ingreso.

El kiosco puede registrar ingresos (el dueño escanea su propio equipo) pero
nunca salidas ni consultas del historial: la salida exige el cotejo físico de
un vigilante, y la restricción vive en el servidor — ocultar botones en la
tablet no es seguridad.
"""

import pytest

from app.models import Rol, Usuario, UsuarioRol
from app.security import ROL_ENTRADA, hashear_contrasena


@pytest.fixture
def encabezados_kiosco(cliente, db, admin) -> dict[str, str]:
    """Sesión de la tablet de autoservicio, con el rol Entrada y nada más."""
    rol = Rol(nombre=ROL_ENTRADA, descripcion="Autoservicio de ingreso")
    db.add(rol)
    db.flush()
    kiosco = Usuario(
        nombres="Tablet",
        apellidos="Portería",
        id_tipo_documento=admin.id_tipo_documento,
        documento="2000000000",
        contrasena_hash=hashear_contrasena("clave-del-kiosco-1"),
    )
    db.add(kiosco)
    db.flush()
    db.add(UsuarioRol(id_usuario=kiosco.id, id_rol=rol.id))
    db.commit()

    respuesta = cliente.post(
        "/auth/login", data={"username": "2000000000", "password": "clave-del-kiosco-1"}
    )
    assert respuesta.status_code == 200, respuesta.text
    return {"Authorization": f"Bearer {respuesta.json()['access_token']}"}


def test_el_kiosco_registra_un_ingreso(cliente, dispositivo, encabezados_kiosco):
    respuesta = cliente.post(
        "/movimientos",
        headers=encabezados_kiosco,
        json={"qr": dispositivo.qr, "tipo": "Ingreso"},
    )
    assert respuesta.status_code == 201, respuesta.text


def test_el_kiosco_no_puede_registrar_salidas(cliente, dispositivo, encabezados_kiosco):
    """Ni siquiera de un equipo que está dentro: la salida es del vigilante."""
    cliente.post(
        "/movimientos", headers=encabezados_kiosco, json={"qr": dispositivo.qr, "tipo": "Ingreso"}
    )
    respuesta = cliente.post(
        "/movimientos",
        headers=encabezados_kiosco,
        json={"qr": dispositivo.qr, "tipo": "Salida"},
    )
    assert respuesta.status_code == 403
    assert "autoservicio" in respuesta.json()["detail"].lower()


def test_el_kiosco_no_ve_el_historial(cliente, encabezados_kiosco):
    assert cliente.get("/movimientos", headers=encabezados_kiosco).status_code == 403


def test_el_kiosco_puede_resolver_un_qr(cliente, dispositivo, encabezados_kiosco):
    """Necesita el listado de equipos para saber a qué equipo pertenece el QR."""
    assert cliente.get("/dispositivos", headers=encabezados_kiosco).status_code == 200


def test_el_kiosco_no_gestiona_equipos_ni_usuarios(cliente, encabezados_kiosco):
    creacion = cliente.post(
        "/dispositivos",
        headers=encabezados_kiosco,
        json={
            "serial": "X",
            "marca": "X",
            "modelo": "X",
            "id_tipo_dispositivo": 1,
            "responsable": "X",
        },
    )
    assert creacion.status_code == 403
    assert cliente.get("/usuarios", headers=encabezados_kiosco).status_code == 403


def test_un_vigilante_si_registra_salidas(cliente, db, dispositivo, encabezados_admin):
    """La regla restringe al kiosco, no a los roles de siempre."""
    cliente.post(
        "/movimientos", headers=encabezados_admin, json={"qr": dispositivo.qr, "tipo": "Ingreso"}
    )
    respuesta = cliente.post(
        "/movimientos",
        headers=encabezados_admin,
        json={"qr": dispositivo.qr, "tipo": "Salida", "observacion": "Serial cotejado físicamente"},
    )
    assert respuesta.status_code == 201, respuesta.text
