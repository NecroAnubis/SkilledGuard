"""Registro de equipos y generación de su código QR."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auditoria import Accion, detalles_de_creacion, registrar_accion
from app.database import get_db
from app.models import Dispositivo, TipoDispositivo, Usuario
from app.porteria import estado_actual, ultimo_movimiento
from app.qr import generar_png
from app.schemas import DispositivoCrear, DispositivoEstado, DispositivoLeer
from app.security import ROL_ADMINISTRADOR, ROL_SEGURIDAD, exige_rol, usuario_actual

router = APIRouter(prefix="/dispositivos", tags=["Dispositivos"])

# Seguridad necesita consultar equipos en portería, pero no crearlos.
_consulta = [Depends(exige_rol(ROL_ADMINISTRADOR, ROL_SEGURIDAD))]
_gestion = [Depends(exige_rol(ROL_ADMINISTRADOR))]


def _obtener(db: Session, id_dispositivo: int) -> Dispositivo:
    dispositivo = db.get(Dispositivo, id_dispositivo)
    if dispositivo is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Equipo no encontrado")
    return dispositivo


@router.get("", response_model=list[DispositivoLeer], dependencies=_consulta)
def listar(
    db: Annotated[Session, Depends(get_db)],
    limite: Annotated[int, Query(ge=1, le=200)] = 50,
    desplazamiento: Annotated[int, Query(ge=0)] = 0,
) -> list[Dispositivo]:
    return list(db.scalars(select(Dispositivo).offset(desplazamiento).limit(limite)).all())


@router.get("/{id_dispositivo}", response_model=DispositivoLeer, dependencies=_consulta)
def obtener(id_dispositivo: int, db: Annotated[Session, Depends(get_db)]) -> Dispositivo:
    return _obtener(db, id_dispositivo)


@router.post(
    "", response_model=DispositivoLeer, status_code=status.HTTP_201_CREATED, dependencies=_gestion
)
def crear(
    datos: DispositivoCrear,
    db: Annotated[Session, Depends(get_db)],
    autor: Annotated[Usuario, Depends(usuario_actual)],
) -> Dispositivo:
    if db.get(TipoDispositivo, datos.id_tipo_dispositivo) is None:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Tipo de dispositivo inexistente")
    if db.get(Usuario, datos.id_usuario) is None:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Usuario responsable inexistente")

    dispositivo = Dispositivo(**datos.model_dump())
    db.add(dispositivo)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status.HTTP_409_CONFLICT, f"Ya existe un equipo con serial {datos.serial}"
        ) from None

    registrar_accion(
        db, autor.id, Accion.CREACION, "dispositivo", detalles_de_creacion(datos.model_dump())
    )
    db.commit()
    return dispositivo


@router.get("/{id_dispositivo}/estado", response_model=DispositivoEstado, dependencies=_consulta)
def estado(id_dispositivo: int, db: Annotated[Session, Depends(get_db)]) -> DispositivoEstado:
    """Indica si el equipo está dentro o fuera de las instalaciones."""
    dispositivo = _obtener(db, id_dispositivo)
    ultimo = ultimo_movimiento(db, dispositivo.id)
    return DispositivoEstado(
        id_dispositivo=dispositivo.id,
        serial=dispositivo.serial,
        estado=estado_actual(db, dispositivo.id),
        ultimo_movimiento=ultimo.fecha_creado if ultimo else None,
    )


@router.get(
    "/{id_dispositivo}/qr",
    dependencies=_consulta,
    response_class=Response,
    responses={200: {"content": {"image/png": {}}, "description": "Código QR del equipo"}},
)
def codigo_qr(id_dispositivo: int, db: Annotated[Session, Depends(get_db)]) -> Response:
    """Devuelve el QR en PNG, para imprimir y pegar en el equipo."""
    dispositivo = _obtener(db, id_dispositivo)
    return Response(content=generar_png(dispositivo.qr), media_type="image/png")
