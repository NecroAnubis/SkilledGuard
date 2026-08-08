"""CRUD de los catálogos simples (rol, tipo de documento).

Roles y tipos de documento comparten forma, así que comparten el mismo constructor
de router en vez de duplicar dos archivos casi idénticos.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Base, Rol, TipoDocumento
from app.schemas import (
    CatalogoCrear,
    CatalogoLeer,
    TipoDocumentoCrear,
    TipoDocumentoLeer,
)
from app.security import ROL_ADMINISTRADOR, exige_rol


def _router_catalogo(
    modelo: type[Base], esquema_crear: type, esquema_leer: type, prefijo: str, etiqueta: str
) -> APIRouter:
    router = APIRouter(prefix=prefijo, tags=[etiqueta])

    @router.get("", response_model=list[esquema_leer])
    def listar(db: Annotated[Session, Depends(get_db)]):
        return list(db.scalars(select(modelo)).all())

    @router.post(
        "",
        response_model=esquema_leer,
        status_code=status.HTTP_201_CREATED,
        dependencies=[Depends(exige_rol(ROL_ADMINISTRADOR))],
    )
    def crear(datos: esquema_crear, db: Annotated[Session, Depends(get_db)]):
        registro = modelo(**datos.model_dump())
        db.add(registro)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status.HTTP_409_CONFLICT, f"Ya existe un registro con nombre {datos.nombre}"
            ) from None
        return registro

    return router


roles = _router_catalogo(Rol, CatalogoCrear, CatalogoLeer, "/roles", "Roles")
tipos_documento = _router_catalogo(
    TipoDocumento, TipoDocumentoCrear, TipoDocumentoLeer, "/tipos-documento", "Tipos de documento"
)
