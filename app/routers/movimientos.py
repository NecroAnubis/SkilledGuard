"""Validación en portería: registro de ingresos y salidas, y trazabilidad."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import AuditoriaNegocio, Dispositivo, Usuario
from app.porteria import MovimientoInvalido, TipoMovimiento, registrar
from app.schemas import MovimientoLeer, MovimientoRegistrar
from app.security import ROL_ADMINISTRADOR, ROL_SEGURIDAD, exige_rol, usuario_actual

router = APIRouter(prefix="/movimientos", tags=["Portería"])

_porteria = [Depends(exige_rol(ROL_ADMINISTRADOR, ROL_SEGURIDAD))]


def _a_esquema(movimiento: AuditoriaNegocio) -> MovimientoLeer:
    dispositivo = movimiento.dispositivo
    return MovimientoLeer(
        id=movimiento.id,
        id_dispositivo=dispositivo.id,
        tipo=movimiento.tipo_registro.nombre,
        serial=dispositivo.serial,
        equipo=f"{dispositivo.marca} {dispositivo.modelo}",
        responsable=dispositivo.usuario.nombre_completo,
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

    return _a_esquema(movimiento)


@router.get("", response_model=list[MovimientoLeer], dependencies=_porteria)
def listar(
    db: Annotated[Session, Depends(get_db)],
    id_dispositivo: int | None = None,
    id_usuario: Annotated[int | None, Query(description="Responsable del equipo")] = None,
    limite: Annotated[int, Query(ge=1, le=200)] = 50,
    desplazamiento: Annotated[int, Query(ge=0)] = 0,
) -> list[MovimientoLeer]:
    """Trazabilidad: historial de movimientos, del más reciente al más antiguo."""
    consulta = select(AuditoriaNegocio).order_by(desc(AuditoriaNegocio.id))
    if id_dispositivo is not None:
        consulta = consulta.where(AuditoriaNegocio.id_dispositivo == id_dispositivo)
    if id_usuario is not None:
        consulta = consulta.join(Dispositivo).where(Dispositivo.id_usuario == id_usuario)

    movimientos = db.scalars(consulta.offset(desplazamiento).limit(limite)).all()
    return [_a_esquema(m) for m in movimientos]
