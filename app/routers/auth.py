from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Usuario
from app.schemas import Token, UsuarioAutenticado
from app.security import crear_token, roles_de, usuario_actual, verificar_contrasena

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/login", response_model=Token)
def login(
    datos: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)],
) -> Token:
    """`username` es el número de documento del usuario."""
    usuario = db.scalar(select(Usuario).where(Usuario.documento == datos.username))

    # Mismo mensaje para usuario inexistente y contraseña errada: distinguirlos
    # le confirma a un atacante qué documentos están registrados.
    if usuario is None or not verificar_contrasena(datos.password, usuario.contrasena_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Documento o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return Token(access_token=crear_token(usuario, roles_de(db, usuario.id)))


@router.get("/yo", response_model=UsuarioAutenticado)
def yo(
    usuario: Annotated[Usuario, Depends(usuario_actual)],
    db: Annotated[Session, Depends(get_db)],
) -> UsuarioAutenticado:
    return UsuarioAutenticado(
        id=usuario.id,
        nombre_completo=usuario.nombre_completo,
        documento=usuario.documento,
        roles=roles_de(db, usuario.id),
    )
