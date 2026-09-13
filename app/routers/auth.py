from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.intentos import DemasiadosIntentos, registrar_intento, verificar_bloqueo
from app.models import Usuario
from app.schemas import Token, UsuarioAutenticado
from app.security import crear_token, roles_de, usuario_actual, verificar_contrasena

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/login", response_model=Token)
def login(
    peticion: Request,
    datos: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)],
) -> Token:
    """`username` es el correo institucional o el número de documento."""
    identificador = datos.username.strip()
    origen = peticion.client.host if peticion.client else None

    # Se aceptan las dos formas: el correo es el identificador al que migra el
    # sistema, y el documento sigue sirviendo mientras haya cuentas sin correo.
    usuario = db.scalar(
        select(Usuario).where(
            or_(Usuario.documento == identificador, Usuario.correo == identificador.lower())
        )
    )

    # El conteo de intentos se lleva por el documento del usuario cuando la
    # cuenta existe: contarlo por lo que se escribió le daría a un atacante
    # cinco intentos por el correo y otros cinco por el documento de la misma
    # persona. Se recorta al ancho de la columna porque un correo inexistente
    # puede ser más largo que cualquier documento.
    llave = (usuario.documento if usuario else identificador)[:50]

    try:
        verificar_bloqueo(db, llave)
    except DemasiadosIntentos as bloqueo:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(bloqueo),
            headers={"Retry-After": str(bloqueo.segundos_restantes)},
        ) from None

    valido = usuario is not None and verificar_contrasena(datos.password, usuario.contrasena_hash)
    registrar_intento(db, llave, valido, origen)

    # Mismo mensaje para usuario inexistente y contraseña errada: distinguirlos
    # le confirma a un atacante qué cuentas están registradas.
    if not valido:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
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
