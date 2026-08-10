"""Pruebas del bloqueo temporal por intentos fallidos de inicio de sesión."""

from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import func, select

from app.intentos import (
    MAX_FALLIDOS,
    VENTANA,
    DemasiadosIntentos,
    fallidos_recientes,
    registrar_intento,
    verificar_bloqueo,
)
from app.models import IntentoLogin

CLAVE = "clave-segura-123"


def _fallar(cliente, documento="1002003001", veces=1):
    for _ in range(veces):
        respuesta = cliente.post(
            "/auth/login", data={"username": documento, "password": "equivocada"}
        )
    return respuesta


def _entrar(cliente, documento="1002003001", clave=CLAVE):
    return cliente.post("/auth/login", data={"username": documento, "password": clave})


# --- A través de la API ----------------------------------------------------


def test_los_primeros_fallos_devuelven_401(cliente, admin):
    for _ in range(MAX_FALLIDOS):
        assert _fallar(cliente).status_code == 401


def test_al_superar_el_limite_se_bloquea_con_429(cliente, admin):
    _fallar(cliente, veces=MAX_FALLIDOS)
    respuesta = _fallar(cliente)

    assert respuesta.status_code == 429
    assert "Demasiados intentos" in respuesta.json()["detail"]
    assert int(respuesta.headers["Retry-After"]) > 0


def test_el_bloqueo_aplica_aunque_la_contrasena_sea_correcta(cliente, admin):
    """Si no, bastaría con seguir probando hasta acertar."""
    _fallar(cliente, veces=MAX_FALLIDOS)
    assert _entrar(cliente).status_code == 429


def test_un_inicio_de_sesion_exitoso_reinicia_la_cuenta(cliente, admin):
    """Cuatro dedos torpes y luego acertar no deben dejar al usuario a un fallo del bloqueo."""
    _fallar(cliente, veces=MAX_FALLIDOS - 1)
    assert _entrar(cliente).status_code == 200

    for _ in range(MAX_FALLIDOS):
        assert _fallar(cliente).status_code == 401


def test_el_bloqueo_no_afecta_a_otros_usuarios(cliente, db, admin, encabezados_admin):
    """Bloquear un documento no debe dejar fuera al resto de la portería."""
    from app.models import TipoDocumento

    tipo = db.query(TipoDocumento).first()
    cliente.post(
        "/usuarios",
        headers=encabezados_admin,
        json={
            "nombres": "Vigilante",
            "apellidos": "Turno",
            "id_tipo_documento": tipo.id,
            "documento": "9009001",
            "contrasena": "clave-del-vigilante",
        },
    )
    _fallar(cliente, documento="9009001", veces=MAX_FALLIDOS + 1)

    assert _entrar(cliente).status_code == 200


def test_los_intentos_contra_documentos_inexistentes_tambien_cuentan(cliente, admin):
    """Un atacante no debe poder sondear documentos sin límite."""
    respuesta = _fallar(cliente, documento="0000000000", veces=MAX_FALLIDOS + 1)
    assert respuesta.status_code == 429


def test_cada_intento_queda_registrado(cliente, db, admin):
    _fallar(cliente, veces=2)
    _entrar(cliente)

    total = db.scalar(select(func.count()).select_from(IntentoLogin))
    exitosos = db.scalar(
        select(func.count()).select_from(IntentoLogin).where(IntentoLogin.exitoso.is_(True))
    )
    assert total == 3
    assert exitosos == 1


# --- La regla, sin pasar por la API ---------------------------------------


def test_los_fallos_viejos_salen_de_la_ventana(db):
    """El bloqueo se levanta solo: no requiere intervención del administrador."""
    ahora = datetime.now(UTC)
    for _ in range(MAX_FALLIDOS):
        registrar_intento(db, "7001", exitoso=False, origen=None)

    with pytest.raises(DemasiadosIntentos):
        verificar_bloqueo(db, "7001", ahora=ahora)

    # Un instante después de que expire la ventana, ya no hay bloqueo.
    despues = ahora + VENTANA + timedelta(seconds=1)
    assert fallidos_recientes(db, "7001", ahora=despues) == 0
    verificar_bloqueo(db, "7001", ahora=despues)


def test_el_mensaje_indica_cuanto_falta(db):
    for _ in range(MAX_FALLIDOS):
        registrar_intento(db, "7002", exitoso=False, origen=None)

    with pytest.raises(DemasiadosIntentos) as error:
        verificar_bloqueo(db, "7002")

    assert error.value.segundos_restantes > 0
    assert "minuto" in str(error.value)
