"""Reglas de negocio del control de ingreso.

Aisladas de los endpoints a propósito: son las reglas que sustentan el sistema
y se prueban solas, sin levantar la API.
"""

from enum import StrEnum

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.models import AuditoriaNegocio, Dispositivo, TipoRegistro


class TipoMovimiento(StrEnum):
    INGRESO = "Ingreso"
    SALIDA = "Salida"


class EstadoDispositivo(StrEnum):
    DENTRO = "dentro"
    FUERA = "fuera"


class MovimientoInvalido(Exception):
    """El movimiento contradice el estado actual del equipo."""


def ultimo_movimiento(db: Session, id_dispositivo: int) -> AuditoriaNegocio | None:
    return db.scalar(
        select(AuditoriaNegocio)
        .where(AuditoriaNegocio.id_dispositivo == id_dispositivo)
        .order_by(desc(AuditoriaNegocio.id))
        .limit(1)
    )


def estado_actual(db: Session, id_dispositivo: int) -> EstadoDispositivo:
    """Un equipo está dentro si su último movimiento fue un ingreso.

    Sin movimientos se considera fuera: el equipo todavía no ha entrado.
    """
    ultimo = ultimo_movimiento(db, id_dispositivo)
    if ultimo is None or ultimo.tipo_registro.nombre == TipoMovimiento.SALIDA:
        return EstadoDispositivo.FUERA
    return EstadoDispositivo.DENTRO


def validar_transicion(estado: EstadoDispositivo, movimiento: TipoMovimiento) -> None:
    """Rechaza los movimientos imposibles.

    Sin esta validación la minuta digital repite el problema de la de papel:
    un equipo que "sale" dos veces sin haber vuelto a entrar deja el inventario
    mintiendo, y nadie se entera hasta que se pierde algo.
    """
    if movimiento == TipoMovimiento.INGRESO and estado == EstadoDispositivo.DENTRO:
        raise MovimientoInvalido("El equipo ya se encuentra dentro de las instalaciones")
    if movimiento == TipoMovimiento.SALIDA and estado == EstadoDispositivo.FUERA:
        raise MovimientoInvalido("El equipo no ha registrado ingreso: no puede salir")


def registrar(
    db: Session,
    dispositivo: Dispositivo,
    movimiento: TipoMovimiento,
    id_vigilante: int,
    observacion: str | None = None,
) -> AuditoriaNegocio:
    # Bloquea la fila del equipo hasta que termine la transacción. Sin esto, dos
    # peticiones simultáneas del mismo equipo leen ambas "fuera" y ambas
    # registran el ingreso: el equipo entra dos veces y la trazabilidad queda
    # mintiendo. Pasa con dos vigilantes escaneando a la vez, o con un doble clic.
    db.execute(select(Dispositivo.id).where(Dispositivo.id == dispositivo.id).with_for_update())

    validar_transicion(estado_actual(db, dispositivo.id), movimiento)

    tipo = db.scalar(select(TipoRegistro).where(TipoRegistro.nombre == movimiento.value))
    if tipo is None:
        raise MovimientoInvalido(f"El catálogo no tiene el tipo de registro '{movimiento.value}'")

    registro = AuditoriaNegocio(
        id_dispositivo=dispositivo.id,
        id_tipo_registro=tipo.id,
        registrado_por=id_vigilante,
        observacion=observacion,
    )
    db.add(registro)
    db.commit()
    return registro
