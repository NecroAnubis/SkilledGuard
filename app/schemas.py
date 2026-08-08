from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class _DesdeORM(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# --- Catálogos -------------------------------------------------------------


class CatalogoCrear(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    descripcion: str | None = Field(default=None, max_length=255)


class CatalogoLeer(_DesdeORM):
    id: int
    nombre: str
    descripcion: str | None
    fecha_creado: datetime


class TipoDocumentoCrear(CatalogoCrear):
    acronimo: str | None = Field(default=None, max_length=10)


class TipoDocumentoLeer(CatalogoLeer):
    acronimo: str | None


# --- Usuarios --------------------------------------------------------------


class UsuarioCrear(BaseModel):
    nombres: str = Field(min_length=1, max_length=100)
    apellidos: str = Field(min_length=1, max_length=100)
    id_tipo_documento: int
    documento: str = Field(min_length=1, max_length=50)
    direccion: str | None = Field(default=None, max_length=255)
    contrasena: str = Field(min_length=8, max_length=72)  # bcrypt trunca en 72 bytes


class UsuarioLeer(_DesdeORM):
    """Nunca expone `contrasena_hash`: no está declarado, así que no se serializa."""

    id: int
    nombres: str
    apellidos: str
    id_tipo_documento: int
    documento: str
    direccion: str | None
    fecha_creado: datetime


class RolAsignar(BaseModel):
    id_rol: int


# --- Autenticación ---------------------------------------------------------


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UsuarioAutenticado(BaseModel):
    id: int
    nombre_completo: str
    documento: str
    roles: list[str]
