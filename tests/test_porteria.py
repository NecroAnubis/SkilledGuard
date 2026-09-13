"""Reglas del control de ingreso, probadas sin levantar la API."""

import pytest

from app.porteria import (
    EstadoDispositivo,
    MovimientoInvalido,
    TipoMovimiento,
    estado_actual,
    registrar,
    validar_transicion,
)

# --- La máquina de estados, sin base de datos -----------------------------


def test_un_equipo_fuera_puede_ingresar():
    validar_transicion(EstadoDispositivo.FUERA, TipoMovimiento.INGRESO)


def test_un_equipo_dentro_puede_salir():
    validar_transicion(EstadoDispositivo.DENTRO, TipoMovimiento.SALIDA)


def test_un_equipo_dentro_no_puede_volver_a_ingresar():
    with pytest.raises(MovimientoInvalido, match="ya se encuentra dentro"):
        validar_transicion(EstadoDispositivo.DENTRO, TipoMovimiento.INGRESO)


def test_un_equipo_fuera_no_puede_salir():
    with pytest.raises(MovimientoInvalido, match="no ha registrado ingreso"):
        validar_transicion(EstadoDispositivo.FUERA, TipoMovimiento.SALIDA)


# --- Contra la base de datos ----------------------------------------------


def test_un_equipo_nuevo_esta_fuera(db, dispositivo):
    assert estado_actual(db, dispositivo.id) == EstadoDispositivo.FUERA


def test_el_ingreso_cambia_el_estado_a_dentro(db, dispositivo, admin):
    registrar(db, dispositivo, TipoMovimiento.INGRESO, admin.id)
    assert estado_actual(db, dispositivo.id) == EstadoDispositivo.DENTRO


def test_ciclo_completo_ingreso_salida_ingreso(db, dispositivo, admin):
    registrar(db, dispositivo, TipoMovimiento.INGRESO, admin.id)
    registrar(db, dispositivo, TipoMovimiento.SALIDA, admin.id)
    assert estado_actual(db, dispositivo.id) == EstadoDispositivo.FUERA

    registrar(db, dispositivo, TipoMovimiento.INGRESO, admin.id)
    assert estado_actual(db, dispositivo.id) == EstadoDispositivo.DENTRO


def test_no_permite_dos_ingresos_seguidos(db, dispositivo, admin):
    registrar(db, dispositivo, TipoMovimiento.INGRESO, admin.id)
    with pytest.raises(MovimientoInvalido):
        registrar(db, dispositivo, TipoMovimiento.INGRESO, admin.id)


def test_el_estado_de_un_equipo_no_afecta_a_otro(db, dispositivo, otro_dispositivo, admin):
    """Regresión: el estado debe consultarse por equipo, no globalmente."""
    registrar(db, dispositivo, TipoMovimiento.INGRESO, admin.id)
    assert estado_actual(db, otro_dispositivo.id) == EstadoDispositivo.FUERA


def test_el_movimiento_declara_su_porteria(cliente, db, dispositivo, encabezados_admin):
    """La sede tiene varias entradas: el movimiento registra por cuál pasó."""
    from app.models import Porteria

    porteria = db.query(Porteria).first()
    if porteria is None:
        porteria = Porteria(nombre="Portería 1", descripcion="Entrada principal")
        db.add(porteria)
        db.commit()

    respuesta = cliente.post(
        "/movimientos",
        headers=encabezados_admin,
        json={"qr": dispositivo.qr, "tipo": "Ingreso", "id_porteria": porteria.id},
    )
    assert respuesta.status_code == 201, respuesta.text
    assert respuesta.json()["porteria"] == porteria.nombre


def test_una_porteria_inexistente_es_rechazada(cliente, dispositivo, encabezados_admin):
    respuesta = cliente.post(
        "/movimientos",
        headers=encabezados_admin,
        json={"qr": dispositivo.qr, "tipo": "Ingreso", "id_porteria": 9999},
    )
    assert respuesta.status_code == 422


def test_un_movimiento_sin_porteria_sigue_siendo_valido(cliente, dispositivo, encabezados_admin):
    """No se frena el registro por un dato que la sede puede no haber definido."""
    respuesta = cliente.post(
        "/movimientos", headers=encabezados_admin, json={"qr": dispositivo.qr, "tipo": "Ingreso"}
    )
    assert respuesta.status_code == 201
    assert respuesta.json()["porteria"] is None
