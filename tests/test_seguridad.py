"""Pruebas de seguridad: manipulación de tokens, contraseñas y concurrencia.

Cada una corresponde a un hallazgo real de la revisión de seguridad.
"""

import threading

import jwt
import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import sessionmaker

from app.models import AuditoriaNegocio, Usuario

SECRETO = "secreto-de-pruebas"


def _con(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


# --- Manipulación de tokens ------------------------------------------------


@pytest.mark.parametrize(
    ("nombre", "payload"),
    [
        ("sin el claim sub", {"documento": "1000000000"}),
        ("con sub no numérico", {"sub": "administrador"}),
        ("con sub nulo", {"sub": None}),
    ],
)
def test_token_malformado_da_401_y_no_500(cliente, admin, nombre, payload):
    """Un token inválido es culpa del cliente, no del servidor.

    Antes respondían 500, lo que además delataba que la firma sí era válida.
    """
    token = jwt.encode(payload, SECRETO, algorithm="HS256")
    assert cliente.get("/usuarios", headers=_con(token)).status_code == 401


def test_token_firmado_con_otra_clave_es_rechazado(cliente, admin):
    token = jwt.encode({"sub": str(admin.id)}, "clave-del-atacante", algorithm="HS256")
    assert cliente.get("/usuarios", headers=_con(token)).status_code == 401


def test_token_con_algoritmo_none_es_rechazado(cliente, admin):
    """El ataque clásico de JWT: pedir que no se verifique la firma."""
    token = jwt.encode({"sub": str(admin.id)}, key="", algorithm="none")
    assert cliente.get("/usuarios", headers=_con(token)).status_code == 401


def test_token_de_usuario_inexistente_es_rechazado(cliente, admin):
    token = jwt.encode({"sub": "99999"}, SECRETO, algorithm="HS256")
    assert cliente.get("/usuarios", headers=_con(token)).status_code == 401


# --- Contraseñas -----------------------------------------------------------


def test_contrasena_de_mas_de_72_bytes_es_rechazada(cliente, db, encabezados_admin):
    """bcrypt ignora lo que pase de 72 bytes; recortar en silencio sería peor."""
    from app.models import TipoDocumento

    tipo = db.query(TipoDocumento).first()
    # 60 caracteres, pero 120 bytes: la ñ ocupa dos.
    respuesta = cliente.post(
        "/usuarios",
        headers=encabezados_admin,
        json={
            "nombres": "A",
            "apellidos": "B",
            "id_tipo_documento": tipo.id,
            "documento": "77001",
            "contrasena": "ñ" * 60,
        },
    )
    assert respuesta.status_code == 422
    assert "72 bytes" in respuesta.text


def test_no_se_puede_inyectar_el_hash_de_la_contrasena(cliente, db, encabezados_admin):
    """Mandar contrasena_hash en el cuerpo no debe reemplazar el hash calculado."""
    from app.models import TipoDocumento

    tipo = db.query(TipoDocumento).first()
    cliente.post(
        "/usuarios",
        headers=encabezados_admin,
        json={
            "nombres": "C",
            "apellidos": "D",
            "id_tipo_documento": tipo.id,
            "documento": "77002",
            "contrasena": "clave-legitima-123",
            "contrasena_hash": "hash-elegido-por-el-atacante",
        },
    )
    guardado = db.query(Usuario).filter_by(documento="77002").one()
    assert guardado.contrasena_hash != "hash-elegido-por-el-atacante"
    assert guardado.contrasena_hash.startswith("$2b$")


# --- Inyección SQL ---------------------------------------------------------


def test_los_filtros_no_permiten_inyeccion_sql(cliente, dispositivo, encabezados_admin):
    respuesta = cliente.get(
        "/movimientos?tipo=Ingreso'; DROP TABLE usuario;--", headers=encabezados_admin
    )
    assert respuesta.status_code == 200
    # Si la inyección hubiera prosperado, este endpoint fallaría.
    assert cliente.get("/usuarios", headers=encabezados_admin).status_code == 200


# --- Concurrencia ----------------------------------------------------------


def test_dos_ingresos_simultaneos_solo_registran_uno(db, dispositivo, admin):
    """Dos guardas escaneando a la vez no deben duplicar el ingreso.

    Cada hilo necesita su propia conexión: el bloqueo se resuelve en la base,
    no en Python.
    """
    from app.porteria import MovimientoInvalido, TipoMovimiento, registrar

    motor = create_engine(db.get_bind().url)
    Sesion = sessionmaker(bind=motor)
    exitos: list[bool] = []
    barrera = threading.Barrier(2)

    def intentar():
        with Sesion() as sesion:
            equipo = sesion.get(type(dispositivo), dispositivo.id)
            barrera.wait()  # los dos hilos arrancan a la vez
            try:
                registrar(sesion, equipo, TipoMovimiento.INGRESO, admin.id)
                # `registrar` ya no confirma: el bloqueo de la fila se sostiene
                # hasta este commit, que es lo que obliga al otro hilo a esperar.
                sesion.commit()
                exitos.append(True)
            except MovimientoInvalido:
                exitos.append(False)

    hilos = [threading.Thread(target=intentar) for _ in range(2)]
    for h in hilos:
        h.start()
    for h in hilos:
        h.join()

    assert sum(exitos) == 1, f"se registraron {sum(exitos)} ingresos, debía ser 1"
    total = db.scalar(
        select(func.count())
        .select_from(AuditoriaNegocio)
        .where(AuditoriaNegocio.id_dispositivo == dispositivo.id)
    )
    assert total == 1
