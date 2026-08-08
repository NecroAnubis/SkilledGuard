"""Registro de acciones sobre el sistema (quién hizo qué y cuándo).

Es distinto de `AuditoriaNegocio`, que registra movimientos de equipos por
portería. Este módulo registra los cambios sobre los *datos*: quién creó un
usuario, quién modificó un equipo.

Se llama de forma explícita desde cada endpoint que modifica datos, en lugar
de engancharse a los eventos de SQLAlchemy. Es más código, pero el rastro de
auditoría queda a la vista en el endpoint que lo produce, en vez de aparecer
por arte de magia desde otra capa. Las pruebas verifican que ningún endpoint
de escritura se quede sin registrar.
"""

from enum import StrEnum

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import LogDetalle, LogSistema, ObjetoAfectado, TipoAccion


class Accion(StrEnum):
    CREACION = "Creación"
    ACTUALIZACION = "Actualización"
    ELIMINACION = "Eliminación"
    CONSULTA = "Consulta"


def _catalogo(db: Session, modelo, **campos):
    """Devuelve la fila del catálogo, creándola si no existe.

    El tipo de acción y la tabla afectada son metadatos, no datos del negocio.
    Si faltara uno, abortar la operación dejaría al usuario sin poder crear un
    equipo por una fila de catálogo ausente; y peor, en un sistema de auditoría
    lo grave sería seguir adelante sin registrar nada.
    """
    registro = db.scalar(select(modelo).filter_by(**campos))
    if registro is None:
        registro = modelo(**campos)
        db.add(registro)
        db.flush()
    return registro


def registrar_accion(
    db: Session,
    id_usuario: int,
    accion: Accion,
    tabla: str,
    detalles: dict[str, tuple[str | None, str | None]] | None = None,
) -> LogSistema:
    """Deja constancia de una acción.

    `detalles` mapea cada campo afectado a (valor anterior, valor nuevo). En una
    creación el valor anterior es None; en una eliminación lo es el nuevo.
    """
    tipo_accion = _catalogo(db, TipoAccion, nombre=accion.value)
    objeto = _catalogo(db, ObjetoAfectado, nombre_tabla=tabla)

    log = LogSistema(
        id_accion=tipo_accion.id,
        id_usuario=id_usuario,
        id_objeto_afectado=objeto.id,
    )
    db.add(log)
    db.flush()  # necesario para que los detalles tengan el id del log

    for campo, (anterior, nuevo) in (detalles or {}).items():
        db.add(
            LogDetalle(
                id_log=log.id,
                campo_afectado=campo,
                valor_anterior=anterior,
                valor_nuevo=nuevo,
            )
        )
    return log


def detalles_de_creacion(datos: dict, omitir: set[str] | None = None) -> dict:
    """Convierte los datos de un registro nuevo al formato de `detalles`.

    `omitir` sirve para no dejar secretos en el rastro de auditoría: una
    contraseña no debe quedar escrita en los logs ni siquiera hasheada.
    """
    omitir = omitir or set()
    return {
        campo: (None, str(valor))
        for campo, valor in datos.items()
        if campo not in omitir and valor is not None
    }
