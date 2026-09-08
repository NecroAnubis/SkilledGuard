"""Pruebas de la API de equipos, código QR y validación en portería."""


def test_crear_dispositivo_genera_su_codigo_qr(
    cliente, catalogos_porteria, admin, encabezados_admin
):
    respuesta = cliente.post(
        "/dispositivos",
        headers=encabezados_admin,
        json={
            "serial": "MB-99999",
            "marca": "Lenovo",
            "modelo": "ThinkPad",
            "id_tipo_dispositivo": catalogos_porteria.id,
            "responsable": "Laura Vargas",
        },
    )
    assert respuesta.status_code == 201, respuesta.text
    assert respuesta.json()["qr"], "el equipo debe quedar con un código QR asignado"


def test_dos_equipos_no_comparten_codigo_qr(cliente, dispositivo, otro_dispositivo):
    assert dispositivo.qr != otro_dispositivo.qr


def test_el_codigo_qr_no_es_el_serial(dispositivo):
    """El serial está impreso en el chasis: no sirve como identificador secreto."""
    assert dispositivo.qr != dispositivo.serial


def test_serial_duplicado_da_409(
    cliente, catalogos_porteria, admin, dispositivo, encabezados_admin
):
    respuesta = cliente.post(
        "/dispositivos",
        headers=encabezados_admin,
        json={
            "serial": dispositivo.serial,
            "marca": "Otra",
            "modelo": "Otro",
            "id_tipo_dispositivo": catalogos_porteria.id,
            "responsable": "Laura Vargas",
        },
    )
    assert respuesta.status_code == 409


def test_el_endpoint_de_qr_devuelve_una_imagen_png(cliente, dispositivo, encabezados_admin):
    respuesta = cliente.get(f"/dispositivos/{dispositivo.id}/qr", headers=encabezados_admin)
    assert respuesta.status_code == 200
    assert respuesta.headers["content-type"] == "image/png"
    # Firma de un archivo PNG válido.
    assert respuesta.content.startswith(b"\x89PNG\r\n\x1a\n")


def test_estado_inicial_del_equipo_es_fuera(cliente, dispositivo, encabezados_admin):
    datos = cliente.get(f"/dispositivos/{dispositivo.id}/estado", headers=encabezados_admin).json()
    assert datos["estado"] == "fuera"
    assert datos["ultimo_movimiento"] is None


def test_equipo_inexistente_da_404(cliente, encabezados_admin):
    assert cliente.get("/dispositivos/9999", headers=encabezados_admin).status_code == 404


def test_el_listado_incluye_el_estado_de_cada_equipo(
    cliente, dispositivo, otro_dispositivo, encabezados_admin
):
    """El listado trae el estado ya resuelto: sin esto la interfaz lo pediría
    equipo por equipo, convirtiendo una pantalla en una consulta por fila."""
    cliente.post(
        "/movimientos", headers=encabezados_admin, json={"qr": dispositivo.qr, "tipo": "Ingreso"}
    )

    equipos = cliente.get("/dispositivos", headers=encabezados_admin).json()
    por_serial = {e["serial"]: e["estado"] for e in equipos}

    assert por_serial[dispositivo.serial] == "dentro"
    assert por_serial[otro_dispositivo.serial] == "fuera"


def test_el_listado_de_equipos_cuesta_pocas_consultas(db, dispositivo, otro_dispositivo, admin):
    """Regresión de N+1: el estado de todos debe resolverse de una vez."""
    from sqlalchemy import event

    from app.porteria import TipoMovimiento, estados_de_todos, registrar

    registrar(db, dispositivo, TipoMovimiento.INGRESO, admin.id)

    ejecutadas: list[str] = []
    db.expire_all()

    def contar(conn, cursor, sentencia, *args):
        ejecutadas.append(sentencia)

    event.listen(db.get_bind(), "before_cursor_execute", contar)
    try:
        estados = estados_de_todos(db)
    finally:
        event.remove(db.get_bind(), "before_cursor_execute", contar)

    assert estados[dispositivo.id] == "dentro"
    assert len(ejecutadas) == 1, f"se esperaba 1 consulta, se ejecutaron {len(ejecutadas)}"


def test_existe_el_catalogo_de_tipos_de_dispositivo(cliente, catalogos_porteria, encabezados_admin):
    tipos = cliente.get("/tipos-dispositivo", headers=encabezados_admin).json()
    assert "Computador" in [t["nombre"] for t in tipos]


# --- Portería --------------------------------------------------------------


def _mover(cliente, encabezados, qr, tipo, observacion=None):
    return cliente.post(
        "/movimientos",
        headers=encabezados,
        json={"qr": qr, "tipo": tipo, "observacion": observacion},
    )


def test_registrar_ingreso_por_qr(cliente, dispositivo, encabezados_admin):
    respuesta = _mover(cliente, encabezados_admin, dispositivo.qr, "Ingreso")

    assert respuesta.status_code == 201, respuesta.text
    cuerpo = respuesta.json()
    assert cuerpo["tipo"] == "Ingreso"
    assert cuerpo["serial"] == dispositivo.serial
    assert cuerpo["registrado_por"] == "Johan Restrepo"


def test_el_ingreso_actualiza_el_estado(cliente, dispositivo, encabezados_admin):
    _mover(cliente, encabezados_admin, dispositivo.qr, "Ingreso")
    datos = cliente.get(f"/dispositivos/{dispositivo.id}/estado", headers=encabezados_admin).json()
    assert datos["estado"] == "dentro"
    assert datos["ultimo_movimiento"] is not None


def test_no_permite_dos_ingresos_seguidos(cliente, dispositivo, encabezados_admin):
    _mover(cliente, encabezados_admin, dispositivo.qr, "Ingreso")
    repetido = _mover(cliente, encabezados_admin, dispositivo.qr, "Ingreso")

    assert repetido.status_code == 409
    assert "ya se encuentra dentro" in repetido.json()["detail"]


def test_no_permite_salir_sin_haber_ingresado(cliente, dispositivo, encabezados_admin):
    respuesta = _mover(cliente, encabezados_admin, dispositivo.qr, "Salida")
    assert respuesta.status_code == 409
    assert "no ha registrado ingreso" in respuesta.json()["detail"]


def test_qr_desconocido_da_404(cliente, dispositivo, encabezados_admin):
    assert _mover(cliente, encabezados_admin, "codigo-que-no-existe", "Ingreso").status_code == 404


def test_tipo_de_movimiento_invalido_es_rechazado(cliente, dispositivo, encabezados_admin):
    respuesta = _mover(cliente, encabezados_admin, dispositivo.qr, "Paseo")
    assert respuesta.status_code == 422


def test_la_trazabilidad_lista_del_mas_reciente_al_mas_antiguo(
    cliente, dispositivo, encabezados_admin
):
    _mover(cliente, encabezados_admin, dispositivo.qr, "Ingreso")
    _mover(cliente, encabezados_admin, dispositivo.qr, "Salida")

    movimientos = cliente.get("/movimientos", headers=encabezados_admin).json()
    assert [m["tipo"] for m in movimientos] == ["Salida", "Ingreso"]


def test_la_trazabilidad_se_filtra_por_equipo(
    cliente, dispositivo, otro_dispositivo, encabezados_admin
):
    _mover(cliente, encabezados_admin, dispositivo.qr, "Ingreso")
    _mover(cliente, encabezados_admin, otro_dispositivo.qr, "Ingreso")

    del_primero = cliente.get(
        f"/movimientos?id_dispositivo={dispositivo.id}", headers=encabezados_admin
    ).json()
    assert len(del_primero) == 1
    assert del_primero[0]["serial"] == dispositivo.serial


def test_registrar_movimiento_exige_autenticacion(cliente, dispositivo):
    respuesta = cliente.post("/movimientos", json={"qr": dispositivo.qr, "tipo": "Ingreso"})
    assert respuesta.status_code == 401
