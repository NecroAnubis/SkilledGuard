"""Pruebas del rastro de auditoría del sistema."""

from sqlalchemy import func, select

from app.models import LogDetalle, LogSistema, TipoDocumento


def _contar_logs(db) -> int:
    return db.scalar(select(func.count()).select_from(LogSistema))


def test_crear_un_equipo_deja_rastro(cliente, db, catalogos_porteria, admin, encabezados_admin):
    cliente.post(
        "/dispositivos",
        headers=encabezados_admin,
        json={
            "serial": "PC-AUDIT",
            "marca": "Dell",
            "modelo": "Latitude",
            "id_tipo_dispositivo": catalogos_porteria.id,
            "id_usuario": admin.id,
        },
    )
    logs = cliente.get("/logs", headers=encabezados_admin).json()

    assert len(logs) == 1
    assert logs[0]["accion"] == "Creación"
    assert logs[0]["tabla"] == "dispositivo"
    assert logs[0]["usuario"] == "Johan Restrepo"
    assert logs[0]["cambios"]["serial"]["despues"] == "PC-AUDIT"


def test_el_rastro_nunca_guarda_la_contrasena(cliente, db, encabezados_admin):
    """Un log de auditoría no es lugar para un secreto, ni siquiera hasheado."""
    tipo = db.query(TipoDocumento).first()
    cliente.post(
        "/usuarios",
        headers=encabezados_admin,
        json={
            "nombres": "Nuevo",
            "apellidos": "Usuario",
            "id_tipo_documento": tipo.id,
            "documento": "5550001",
            "contrasena": "clave-secretisima-99",
        },
    )
    campos = db.scalars(select(LogDetalle.campo_afectado)).all()
    valores = db.scalars(select(LogDetalle.valor_nuevo)).all()

    assert "contrasena" not in campos
    assert not any("clave-secretisima-99" in (v or "") for v in valores)


def test_registrar_un_movimiento_deja_rastro(cliente, db, dispositivo, encabezados_admin):
    cliente.post(
        "/movimientos", headers=encabezados_admin, json={"qr": dispositivo.qr, "tipo": "Ingreso"}
    )
    logs = cliente.get("/logs?tabla=auditoria_negocio", headers=encabezados_admin).json()

    assert len(logs) == 1
    assert logs[0]["cambios"]["tipo"]["despues"] == "Ingreso"


def test_una_operacion_fallida_no_deja_rastro(cliente, db, dispositivo, encabezados_admin):
    """Si el movimiento se rechaza, no debe aparecer en el rastro como si hubiera ocurrido."""
    cliente.post(
        "/movimientos", headers=encabezados_admin, json={"qr": dispositivo.qr, "tipo": "Ingreso"}
    )
    antes = _contar_logs(db)

    rechazado = cliente.post(
        "/movimientos", headers=encabezados_admin, json={"qr": dispositivo.qr, "tipo": "Ingreso"}
    )

    assert rechazado.status_code == 409
    assert _contar_logs(db) == antes


def test_el_rastro_solo_lo_ve_el_administrador(cliente, db, admin, encabezados_admin):
    tipo = db.query(TipoDocumento).first()
    cliente.post(
        "/usuarios",
        headers=encabezados_admin,
        json={
            "nombres": "Vigilante",
            "apellidos": "Turno",
            "id_tipo_documento": tipo.id,
            "documento": "5550002",
            "contrasena": "clave-vigilante-77",
        },
    )
    token = cliente.post(
        "/auth/login", data={"username": "5550002", "password": "clave-vigilante-77"}
    ).json()["access_token"]

    respuesta = cliente.get("/logs", headers={"Authorization": f"Bearer {token}"})
    assert respuesta.status_code == 403
