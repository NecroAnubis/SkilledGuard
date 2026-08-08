"""CRUD de los catálogos: roles y tipos de documento.

Se escriben los dos routers de forma explícita en lugar de generarlos con una
factoría: son solo dos, y el código explícito se lee y se depura sin tener que
seguir un closure.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Rol, TipoDocumento
from app.schemas import (
    CatalogoCrear,
    CatalogoLeer,
    TipoDocumentoCrear,
    TipoDocumentoLeer,
)
from app.security import ROL_ADMINISTRADOR, exige_rol

roles = APIRouter(prefix="/roles", tags=["Roles"])
tipos_documento = APIRouter(prefix="/tipos-documento", tags=["Tipos de documento"])

_solo_admin = [Depends(exige_rol(ROL_ADMINISTRADOR))]


def _guardar(db: Session, registro, nombre: str):
    """Inserta y traduce el choque de unicidad a un 409 legible."""
    db.add(registro)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status.HTTP_409_CONFLICT, f"Ya existe un registro con nombre '{nombre}'"
        ) from None
    return registro


@roles.get("", response_model=list[CatalogoLeer])
def listar_roles(db: Annotated[Session, Depends(get_db)]) -> list[Rol]:
    return list(db.scalars(select(Rol)).all())


@roles.post(
    "", response_model=CatalogoLeer, status_code=status.HTTP_201_CREATED, dependencies=_solo_admin
)
def crear_rol(datos: CatalogoCrear, db: Annotated[Session, Depends(get_db)]) -> Rol:
    return _guardar(db, Rol(**datos.model_dump()), datos.nombre)


@tipos_documento.get("", response_model=list[TipoDocumentoLeer])
def listar_tipos_documento(db: Annotated[Session, Depends(get_db)]) -> list[TipoDocumento]:
    return list(db.scalars(select(TipoDocumento)).all())


@tipos_documento.post(
    "",
    response_model=TipoDocumentoLeer,
    status_code=status.HTTP_201_CREATED,
    dependencies=_solo_admin,
)
def crear_tipo_documento(
    datos: TipoDocumentoCrear, db: Annotated[Session, Depends(get_db)]
) -> TipoDocumento:
    return _guardar(db, TipoDocumento(**datos.model_dump()), datos.nombre)
