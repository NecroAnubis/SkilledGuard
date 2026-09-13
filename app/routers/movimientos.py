"""Validación en portería: registro de ingresos y salidas, y trazabilidad."""

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import consultas
from app.auditoria import Accion, registrar_accion
from app.database import get_db
from app.models import AuditoriaNegocio, Dispositivo, Porteria, Usuario
from app.porteria import MovimientoInvalido, TipoMovimiento, registrar
from app.schemas import MovimientoLeer, MovimientoRegistrar
from app.security import (
    ROL_ADMINISTRADOR,
    ROL_ENTRADA,
    ROL_SEGURIDAD,
    exige_rol,
    roles_de,
    usuario_actual,
)

router = APIRouter(prefix="/movimientos", tags=["Portería"])

_porteria = [Depends(exige_rol(ROL_ADMINISTRADOR, ROL_SEGURIDAD))]
# El kiosco de autoservicio puede CREAR movimientos (la validación de que solo
# sean ingresos vive en el handler), pero no consultar el historial.
_registro = [Depends(exige_rol(ROL_ADMINISTRADOR, ROL_SEGURIDAD, ROL_ENTRADA))]


def a_esquema(movimiento: AuditoriaNegocio) -> MovimientoLeer:
    dispositivo = movimiento.dispositivo
    return MovimientoLeer(
        id=movimiento.id,
        id_dispositivo=dispositivo.id,
        tipo=movimiento.tipo_registro.nombre,
        serial=dispositivo.serial,
        equipo=f"{dispositivo.marca} {dispositivo.modelo}",
        responsable=dispositivo.responsable,
        documento_responsable=dispositivo.documento_responsable,
        registrado_por=movimiento.guarda.nombre_completo,
        porteria=movimiento.porteria.nombre if movimiento.porteria else None,
        observacion=movimiento.observacion,
        fecha=movimiento.fecha_creado,
    )


@router.post(
    "", response_model=MovimientoLeer, status_code=status.HTTP_201_CREATED, dependencies=_registro
)
def registrar_movimiento(
    datos: MovimientoRegistrar,
    db: Annotated[Session, Depends(get_db)],
    guarda: Annotated[Usuario, Depends(usuario_actual)],
) -> MovimientoLeer:
    """Registra el ingreso o la salida de un equipo a partir de su código QR."""
    dispositivo = db.scalar(select(Dispositivo).where(Dispositivo.qr == datos.qr))
    if dispositivo is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "El código QR no corresponde a un equipo")

    # El kiosco es autoservicio del dueño: puede registrar su ingreso, nunca
    # una salida — la salida exige el cotejo físico de un guarda de seguridad. La regla
    # vive en el servidor porque ocultar el botón en la tablet no es seguridad.
    roles = set(roles_de(db, guarda.id))
    if datos.tipo != TipoMovimiento.INGRESO.value and roles == {ROL_ENTRADA}:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            "El autoservicio solo registra ingresos; la salida la registra el personal de seguridad",
        )

    if datos.id_porteria is not None and db.get(Porteria, datos.id_porteria) is None:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Portería inexistente")

    try:
        movimiento = registrar(
            db,
            dispositivo,
            TipoMovimiento(datos.tipo),
            guarda.id,
            datos.observacion,
            datos.id_porteria,
        )
    except MovimientoInvalido as error:
        raise HTTPException(status.HTTP_409_CONFLICT, str(error)) from None

    registrar_accion(
        db,
        guarda.id,
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
