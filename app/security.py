"""Hash de contraseñas (bcrypt) y autenticación por JWT con control de roles."""

import re
from datetime import UTC, datetime, timedelta
from typing import Annotated

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import Rol, Usuario, UsuarioRol

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

ROL_ADMINISTRADOR = "Administrador"
ROL_SEGURIDAD = "Seguridad"
ROL_USUARIO = "Usuario"
# Sesión de la tablet de autoservicio en la entrada: el dueño del equipo
# registra su propio ingreso. Solo ingresos — la salida exige a un guarda de seguridad.
ROL_ENTRADA = "Entrada"


# bcrypt solo considera los primeros 72 bytes y descarta el resto en silencio:
# dos contraseñas distintas con el mismo prefijo autentican igual. Se valida el
# largo en bytes (no en caracteres: "ñ" ocupa dos) para que el recorte sea
# imposible en vez de invisible.
MAX_BYTES_CONTRASENA = 72

# Solo estos correos pueden administrar el sistema. Es una regla del negocio,
# no una preferencia de formato: quien administra pertenece a la organización,
# y un correo personal no prueba pertenencia.
DOMINIO_CORPORATIVO = "skilledguard.co"

# Validación deliberadamente simple: la puerta real es el dominio, no la
# gramática del correo. Evita sumar una dependencia para lo que aquí no decide.
_FORMA_CORREO = re.compile(r"^[^@\s]+@[^@\s]+\.[a-z]{2,}$")


def correo_valido(correo: str) -> bool:
    return bool(_FORMA_CORREO.match(correo.strip().lower()))


def es_corporativo(correo: str | None) -> bool:
    return bool(correo) and correo.strip().lower().endswith(f"@{DOMINIO_CORPORATIVO}")


def hashear_contrasena(contrasena: str) -> str:
    return bcrypt.hashpw(contrasena.encode(), bcrypt.gensalt()).decode()


def verificar_contrasena(contrasena: str, hash_guardado: str) -> bool:
    return bcrypt.checkpw(contrasena.encode(), hash_guardado.encode())


def crear_token(usuario: Usuario, roles: list[str]) -> str:
    expira = datetime.now(UTC) + timedelta(minutes=settings.jwt_expiracion_minutos)
    payload = {
        "sub": str(usuario.id),
        "documento": usuario.documento,
        "roles": roles,
        "exp": expira,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def roles_de(db: Session, id_usuario: int) -> list[str]:
    return list(
        db.scalars(
            select(Rol.nombre).join(UsuarioRol).where(UsuarioRol.id_usuario == id_usuario)
        ).all()
    )


def usuario_actual(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> Usuario:
    no_autorizado = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        # Un token con firma válida pero sin `sub`, o con un `sub` que no es un
        # número, es un token inválido — no un error del servidor. Sin este
        # control la API respondía 500 y filtraba que el token sí se descifró.
        id_usuario = int(payload["sub"])
    except (jwt.PyJWTError, KeyError, TypeError, ValueError):
        raise no_autorizado from None

    usuario = db.get(Usuario, id_usuario)
    if usuario is None:
        raise no_autorizado
    return usuario


def exige_rol(*permitidos: str):
    """Dependencia que restringe un endpoint a los roles indicados."""

    def verificar(
        usuario: Annotated[Usuario, Depends(usuario_actual)],
        db: Annotated[Session, Depends(get_db)],
    ) -> Usuario:
        if not set(permitidos) & set(roles_de(db, usuario.id)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requiere uno de estos roles: {', '.join(permitidos)}",
            )
        return usuario

    return verificar
