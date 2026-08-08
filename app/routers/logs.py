"""Consulta del rastro de auditoría del sistema."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc, select
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import LogSistema
from app.schemas import LogLeer
from app.security import ROL_ADMINISTRADOR, exige_rol

# Solo el administrador ve el rastro: es el registro de quién hizo qué, y
# permitir que cada usuario lo consulte le entrega el mapa de la operación.
router = APIRouter(
    prefix="/logs",
    tags=["Auditoría del sistema"],
    dependencies=[Depends(exige_rol(ROL_ADMINISTRADOR))],
)


@router.get("", response_model=list[LogLeer])
def listar(
    db: Annotated[Session, Depends(get_db)],
    id_usuario: int | None = None,
    tabla: Annotated[str | None, Query(description="Nombre de la tabla afectada")] = None,
    limite: Annotated[int, Query(ge=1, le=200)] = 50,
    desplazamiento: Annotated[int, Query(ge=0)] = 0,
) -> list[LogLeer]:
    consulta = select(LogSistema).options(
        joinedload(LogSistema.accion),
        joinedload(LogSistema.usuario),
        joinedload(LogSistema.objeto_afectado),
        joinedload(LogSistema.detalles),
    )
    if id_usuario is not None:
        consulta = consulta.where(LogSistema.id_usuario == id_usuario)
    if tabla is not None:
        consulta = consulta.where(LogSistema.objeto_afectado.has(nombre_tabla=tabla))

    logs = (
        db.scalars(consulta.order_by(desc(LogSistema.id)).offset(desplazamiento).limit(limite))
        .unique()
        .all()
    )
    return [
        LogLeer(
            id=log.id,
            accion=log.accion.nombre,
            tabla=log.objeto_afectado.nombre_tabla,
            usuario=log.usuario.nombre_completo,
            fecha=log.fecha_creado,
            cambios={
                d.campo_afectado: {"antes": d.valor_anterior, "despues": d.valor_nuevo}
                for d in log.detalles
            },
        )
        for log in logs
    ]
