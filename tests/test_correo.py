"""Pruebas del correo institucional y de la regla de dominio para administrar.

El inicio de sesión acepta el correo o el documento durante la transición, y el
rol Administrador exige un correo del dominio corporativo.
"""

from app.models import Rol, TipoDocumento
from app.security import DOMINIO_CORPORATIVO, ROL_ADMINISTRADOR


def _crear(cliente, db, encabezados_admin, documento: str, correo: str | None, clave: str):
    tipo = db.query(TipoDocumento).first()
    cuerpo = {
        "nombres": "Ana",
        "apellidos": "Pérez",
        "id_tipo_documento": tipo.id,
        "documento": documento,
        "contrasena": clave,
    }
    if correo is not None:
        cuerpo["correo"] = correo
    return cliente.post("/usuarios", headers=encabezados_admin, json=cuerpo)


def test_se_inicia_sesion_con_el_correo(cliente, db, encabezados_admin):
    _crear(cliente, db, encabezados_admin, "5000000001", "ana@skilledguard.co", "clave-larga-1")
    respuesta = cliente.post(
        "/auth/login", data={"username": "ana@skilledguard.co", "password": "clave-larga-1"}
    )
    assert respuesta.status_code == 200, respuesta.text
    assert respuesta.json()["access_token"]


def test_el_documento_sigue_sirviendo(cliente, db, encabezados_admin):
    """Las cuentas anteriores al correo no pueden quedar fuera del sistema."""
    _crear(cliente, db, encabezados_admin, "5000000002", None, "clave-larga-2")
    respuesta = cliente.post(
        "/auth/login", data={"username": "5000000002", "password": "clave-larga-2"}
    )
    assert respuesta.status_code == 200, respuesta.text


def test_el_correo_no_distingue_mayusculas(cliente, db, encabezados_admin):
    """Se guarda en minúsculas: si no, el índice único admitiría dos cuentas."""
    creado = _crear(
        cliente, db, encabezados_admin, "5000000003", "Ana.Ruiz@SkilledGuard.CO", "clave-larga-3"
    )
    assert creado.json()["correo"] == "ana.ruiz@skilledguard.co"
    respuesta = cliente.post(
        "/auth/login", data={"username": "ANA.RUIZ@skilledguard.co", "password": "clave-larga-3"}
    )
    assert respuesta.status_code == 200, respuesta.text


def test_un_correo_mal_formado_es_rechazado(cliente, db, encabezados_admin):
    creado = _crear(cliente, db, encabezados_admin, "5000000004", "esto-no-es-correo", "clave-l-4")
    assert creado.status_code == 422


def test_dos_usuarios_no_comparten_correo(cliente, db, encabezados_admin):
    _crear(cliente, db, encabezados_admin, "5000000005", "repetido@skilledguard.co", "clave-lar-5")
    segundo = _crear(
        cliente, db, encabezados_admin, "5000000006", "repetido@skilledguard.co", "clave-larga-6"
    )
    assert segundo.status_code == 409


def test_administrar_exige_correo_corporativo(cliente, db, encabezados_admin):
    creado = _crear(cliente, db, encabezados_admin, "5000000007", "juan@gmail.com", "clave-larga-7")
    id_admin = db.query(Rol).filter(Rol.nombre == ROL_ADMINISTRADOR).first().id

    respuesta = cliente.post(
        f"/usuarios/{creado.json()['id']}/roles",
        headers=encabezados_admin,
        json={"id_rol": id_admin},
    )
    assert respuesta.status_code == 422
    assert DOMINIO_CORPORATIVO in respuesta.json()["detail"]


def test_una_cuenta_sin_correo_tampoco_administra(cliente, db, encabezados_admin):
    creado = _crear(cliente, db, encabezados_admin, "5000000008", None, "clave-larga-8")
    id_admin = db.query(Rol).filter(Rol.nombre == ROL_ADMINISTRADOR).first().id

    respuesta = cliente.post(
        f"/usuarios/{creado.json()['id']}/roles",
        headers=encabezados_admin,
        json={"id_rol": id_admin},
    )
    assert respuesta.status_code == 422


def test_el_correo_corporativo_si_administra(cliente, db, encabezados_admin):
    creado = _crear(
        cliente, db, encabezados_admin, "5000000009", "jefe@skilledguard.co", "clave-larga-9"
    )
    id_admin = db.query(Rol).filter(Rol.nombre == ROL_ADMINISTRADOR).first().id

    respuesta = cliente.post(
        f"/usuarios/{creado.json()['id']}/roles",
        headers=encabezados_admin,
        json={"id_rol": id_admin},
    )
    assert respuesta.status_code == 204, respuesta.text


def test_alternar_correo_y_documento_no_duplica_los_intentos(cliente, db, encabezados_admin):
    """El bloqueo cuenta por cuenta, no por la forma de nombrarla.

    Si el conteo fuera por el texto escrito, un atacante tendría cinco intentos
    con el correo y otros cinco con el documento de la misma persona.
    """
    _crear(cliente, db, encabezados_admin, "5000000010", "diez@skilledguard.co", "clave-larga-10")

    for identificador in ["diez@skilledguard.co", "5000000010", "diez@skilledguard.co"]:
        cliente.post("/auth/login", data={"username": identificador, "password": "errada"})
    for identificador in ["5000000010", "diez@skilledguard.co"]:
        cliente.post("/auth/login", data={"username": identificador, "password": "errada"})

    # Ya van cinco fallos contra la misma cuenta: el sexto se bloquea, sin
    # importar con cuál de las dos formas se intente.
    bloqueado = cliente.post(
        "/auth/login", data={"username": "5000000010", "password": "clave-larga-10"}
    )
    assert bloqueado.status_code == 429
