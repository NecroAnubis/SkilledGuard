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
