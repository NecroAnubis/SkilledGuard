from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Rol, TipoDocumento, Usuario, UsuarioRol
from app.schemas import RolAsignar, UsuarioCrear, UsuarioLeer
from app.security import ROL_ADMINISTRADOR, exige_rol, hashear_contrasena

router = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"],
    dependencies=[Depends(exige_rol(ROL_ADMINISTRADOR))],
)


@router.get("", response_model=list[UsuarioLeer])
def listar(
    db: Annotated[Session, Depends(get_db)],
    limite: int = 50,
    desplazamiento: int = 0,
) -> list[Usuario]:
    return list(db.scalars(select(Usuario).offset(desplazamiento).limit(limite)).all())


@router.get("/{id_usuario}", response_model=UsuarioLeer)
def obtener(id_usuario: int, db: Annotated[Session, Depends(get_db)]) -> Usuario:
    usuario = db.get(Usuario, id_usuario)
    if usuario is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Usuario no encontrado")
    return usuario


@router.post("", response_model=UsuarioLeer, status_code=status.HTTP_201_CREATED)
def crear(datos: UsuarioCrear, db: Annotated[Session, Depends(get_db)]) -> Usuario:
    if db.get(TipoDocumento, datos.id_tipo_documento) is None:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Tipo de documento inexistente")

    usuario = Usuario(
        **datos.model_dump(exclude={"contrasena"}),
        contrasena_hash=hashear_contrasena(datos.contrasena),
    )
    db.add(usuario)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status.HTTP_409_CONFLICT, f"Ya existe un usuario con documento {datos.documento}"
        ) from None
    return usuario


@router.post("/{id_usuario}/roles", status_code=status.HTTP_204_NO_CONTENT)
def asignar_rol(
    id_usuario: int, datos: RolAsignar, db: Annotated[Session, Depends(get_db)]
) -> None:
    if db.get(Usuario, id_usuario) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Usuario no encontrado")
    if db.get(Rol, datos.id_rol) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Rol no encontrado")

    db.add(UsuarioRol(id_usuario=id_usuario, id_rol=datos.id_rol))
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "El usuario ya tiene ese rol") from None
