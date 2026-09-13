from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auditoria import Accion, detalles_de_creacion, registrar_accion
from app.database import get_db
from app.models import Rol, TipoDocumento, Usuario, UsuarioRol
from app.schemas import (
    ContrasenaRestablecida,
    RolAsignar,
    UsuarioCrear,
    UsuarioEditar,
    UsuarioLeer,
)
from app.security import (
    DOMINIO_CORPORATIVO,
    ROL_ADMINISTRADOR,
    es_corporativo,
    exige_rol,
    roles_de,
    hashear_contrasena,
    usuario_actual,
)

router = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"],
    dependencies=[Depends(exige_rol(ROL_ADMINISTRADOR))],
)


@router.get("", response_model=list[UsuarioLeer])
def listar(
    db: Annotated[Session, Depends(get_db)],
    # Con tope: sin él, un solo cliente puede pedir la tabla completa en una llamada.
    limite: Annotated[int, Query(ge=1, le=200)] = 50,
    desplazamiento: Annotated[int, Query(ge=0)] = 0,
) -> list[UsuarioLeer]:
    usuarios = list(db.scalars(select(Usuario).offset(desplazamiento).limit(limite)).all())

    # Los roles de todos en una sola consulta: pedirlos usuario por usuario
    # convertiría este listado en una consulta por fila.
    filas = db.execute(
        select(UsuarioRol.id_usuario, Rol.nombre)
        .join(Rol, Rol.id == UsuarioRol.id_rol)
        .where(UsuarioRol.id_usuario.in_([u.id for u in usuarios]))
    ).all() if usuarios else []
    por_usuario: dict[int, list[str]] = {}
    for id_usuario, nombre in filas:
        por_usuario.setdefault(id_usuario, []).append(nombre)

    return [
        UsuarioLeer.model_validate(u).model_copy(update={"roles": por_usuario.get(u.id, [])})
        for u in usuarios
    ]


@router.get("/{id_usuario}", response_model=UsuarioLeer)
def obtener(id_usuario: int, db: Annotated[Session, Depends(get_db)]) -> Usuario:
    usuario = db.get(Usuario, id_usuario)
    if usuario is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Usuario no encontrado")
    return usuario


@router.post("", response_model=UsuarioLeer, status_code=status.HTTP_201_CREATED)
def crear(
    datos: UsuarioCrear,
    db: Annotated[Session, Depends(get_db)],
    autor: Annotated[Usuario, Depends(usuario_actual)],
) -> Usuario:
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
            status.HTTP_409_CONFLICT,
            "Ya existe un usuario con ese documento o ese correo",
        ) from None

    # La contraseña se omite del rastro: un log de auditoría no es lugar para
    # un secreto, ni siquiera hasheado.
    registrar_accion(
        db,
        autor.id,
        Accion.CREACION,
        "usuario",
        detalles_de_creacion(datos.model_dump(), omitir={"contrasena"}),
    )
    db.commit()
    return usuario


@router.patch("/{id_usuario}", response_model=UsuarioLeer)
def editar(
    id_usuario: int,
    datos: UsuarioEditar,
    db: Annotated[Session, Depends(get_db)],
    autor: Annotated[Usuario, Depends(usuario_actual)],
) -> Usuario:
    """Corrige los datos de una cuenta. El documento no se toca: es la identidad."""
    usuario = db.get(Usuario, id_usuario)
    if usuario is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Usuario no encontrado")

    cambios = datos.model_dump(exclude_unset=True)

    # Si la cuenta administra, su correo sigue teniendo que ser corporativo:
    # de lo contrario esta ruta sería la puerta trasera de la regla que el
    # endpoint de roles hace cumplir.
    if "correo" in cambios and ROL_ADMINISTRADOR in roles_de(db, usuario.id):
        if not es_corporativo(cambios["correo"]):
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                f"Una cuenta con rol Administrador exige un correo @{DOMINIO_CORPORATIVO}",
            )

    detalles = {}
    for campo, nuevo in cambios.items():
        anterior = getattr(usuario, campo)
        if anterior != nuevo:
            detalles[campo] = (str(anterior) if anterior is not None else None, str(nuevo))
            setattr(usuario, campo, nuevo)

    if not detalles:
        return usuario

    try:
        registrar_accion(db, autor.id, Accion.ACTUALIZACION, "usuario", detalles)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status.HTTP_409_CONFLICT, "Ya existe un usuario con ese correo"
        ) from None
    return usuario


@router.post("/{id_usuario}/contrasena", status_code=status.HTTP_204_NO_CONTENT)
def restablecer_contrasena(
    id_usuario: int,
    datos: ContrasenaRestablecida,
    db: Annotated[Session, Depends(get_db)],
    autor: Annotated[Usuario, Depends(usuario_actual)],
) -> None:
    """Restablece la contraseña de otra cuenta sin exigir la anterior.

    Es la salida para quien la olvidó. Queda en el rastro quién la restableció
    y a quién: un administrador puede devolverle el acceso a una cuenta, pero
    no puede hacerlo en silencio.
    """
    usuario = db.get(Usuario, id_usuario)
    if usuario is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Usuario no encontrado")

    usuario.contrasena_hash = hashear_contrasena(datos.contrasena_nueva)
    registrar_accion(
        db,
        autor.id,
        Accion.ACTUALIZACION,
        "usuario",
        {"contrasena_restablecida_a": (None, usuario.documento)},
    )
    db.commit()


@router.post("/{id_usuario}/roles", status_code=status.HTTP_204_NO_CONTENT)
def asignar_rol(
    id_usuario: int,
    datos: RolAsignar,
    db: Annotated[Session, Depends(get_db)],
    autor: Annotated[Usuario, Depends(usuario_actual)],
) -> None:
    usuario = db.get(Usuario, id_usuario)
    if usuario is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Usuario no encontrado")
    rol = db.get(Rol, datos.id_rol)
    if rol is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Rol no encontrado")

    # Administrar el sistema exige pertenecer a la organización, y el correo
    # institucional es la prueba de esa pertenencia. La regla se aplica aquí
    # —no solo al crear la cuenta— porque el rol se puede otorgar después.
    if rol.nombre == ROL_ADMINISTRADOR and not es_corporativo(usuario.correo):
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            f"Solo un correo @{DOMINIO_CORPORATIVO} puede tener el rol Administrador",
        )

    db.add(UsuarioRol(id_usuario=id_usuario, id_rol=datos.id_rol))
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "El usuario ya tiene ese rol") from None

    registrar_accion(
        db,
        autor.id,
        Accion.ACTUALIZACION,
        "usuario",
        {"rol": (None, str(datos.id_rol))},
    )
    db.commit()
