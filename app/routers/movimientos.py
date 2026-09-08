"""Validación en portería: registro de ingresos y salidas, y trazabilidad."""

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import consultas
from app.auditoria import Accion, registrar_accion
from app.database import get_db
from app.models import AuditoriaNegocio, Dispositivo, Usuario
from app.porteria import MovimientoInvalido, TipoMovimiento, registrar
from app.schemas import MovimientoLeer, MovimientoRegistrar
from app.security import ROL_ADMINISTRADOR, ROL_SEGURIDAD, exige_rol, usuario_actual

router = APIRouter(prefix="/movimientos", tags=["Portería"])

_porteria = [Depends(exige_rol(ROL_ADMINISTRADOR, ROL_SEGURIDAD))]


def a_esquema(movimiento: AuditoriaNegocio) -> MovimientoLeer:
    dispositivo = movimiento.dispositivo
    return MovimientoLeer(
        id=movimiento.id,
        id_dispositivo=dispositivo.id,
        tipo=movimiento.tipo_registro.nombre,
        serial=dispositivo.serial,
        equipo=f"{dispositivo.marca} {dispositivo.modelo}",
        responsable=dispositivo.responsable,
        registrado_por=movimiento.vigilante.nombre_completo,
        observacion=movimiento.observacion,
        fecha=movimiento.fecha_creado,
    )


@router.post(
    "", response_model=MovimientoLeer, status_code=status.HTTP_201_CREATED, dependencies=_porteria
)
def registrar_movimiento(
    datos: MovimientoRegistrar,
    db: Annotated[Session, Depends(get_db)],
    vigilante: Annotated[Usuario, Depends(usuario_actual)],
) -> MovimientoLeer:
    """Registra el ingreso o la salida de un equipo a partir de su código QR."""
    dispositivo = db.scalar(select(Dispositivo).where(Dispositivo.qr == datos.qr))
    if dispositivo is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "El código QR no corresponde a un equipo")

    try:
        movimiento = registrar(
            db, dispositivo, TipoMovimiento(datos.tipo), vigilante.id, datos.observacion
        )
    except MovimientoInvalido as error:
        raise HTTPException(status.HTTP_409_CONFLICT, str(error)) from None

    registrar_accion(
        db,
        vigilante.id,
        Accion.CREACION,
        "auditoria_negocio",
        {"tipo": (None, datos.tipo), "serial": (None, dispositivo.serial)},
    )
    db.commit()
    return a_esquema(movimiento)


@router.get("", response_model=list[MovimientoLeer], dependencies=_porteria)
def listar(
    db: Annotated[Session, Depends(get_db)],
    id_dispositivo: int | None = None,
    responsable: Annotated[str | None, Query(description="Responsable del equipo")] = None,
    tipo: Annotated[str | None, Query(description="Ingreso o Salida")] = None,
    desde: date | None = None,
    hasta: date | None = None,
    limite: Annotated[int, Query(ge=1, le=200)] = 50,
    desplazamiento: Annotated[int, Query(ge=0)] = 0,
) -> list[MovimientoLeer]:
    """Trazabilidad: historial de movimientos, del más reciente al más antiguo."""
    consulta = consultas.movimientos(id_dispositivo, responsable, tipo, desde, hasta)
    movimientos = db.scalars(consulta.offset(desplazamiento).limit(limite)).unique().all()
    return [a_esquema(m) for m in movimientos]
