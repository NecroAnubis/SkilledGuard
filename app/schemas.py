from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.security import MAX_BYTES_CONTRASENA


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
    contrasena: str = Field(min_length=8)

    @field_validator("contrasena")
    @classmethod
    def cabe_en_bcrypt(cls, valor: str) -> str:
        """bcrypt ignora lo que pase de 72 bytes; mejor rechazarlo que recortarlo."""
        if len(valor.encode()) > MAX_BYTES_CONTRASENA:
            raise ValueError(
                f"La contraseña supera {MAX_BYTES_CONTRASENA} bytes "
                "(las tildes y la ñ ocupan dos cada una)"
            )
        return valor


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


# --- Dispositivos ----------------------------------------------------------


class DispositivoCrear(BaseModel):
    serial: str = Field(min_length=1, max_length=50)
    marca: str = Field(min_length=1, max_length=100)
    modelo: str = Field(min_length=1, max_length=100)
    sistema: str | None = Field(default=None, max_length=50)
    id_tipo_dispositivo: int
    id_usuario: int


class DispositivoLeer(_DesdeORM):
    id: int
    serial: str
    marca: str
    modelo: str
    sistema: str | None
    id_tipo_dispositivo: int
    id_usuario: int
    qr: str
    fecha_creado: datetime


class DispositivoEstado(BaseModel):
    id_dispositivo: int
    serial: str
    estado: str
    ultimo_movimiento: datetime | None


# --- Portería --------------------------------------------------------------


class MovimientoRegistrar(BaseModel):
    """El vigilante escanea el QR del equipo y declara si entra o sale."""

    qr: str = Field(min_length=1, max_length=255)
    tipo: Literal["Ingreso", "Salida"]
    observacion: str | None = Field(default=None, max_length=500)


class LogLeer(BaseModel):
    """Una entrada del rastro de auditoría, con el detalle de lo que cambió."""

    id: int
    accion: str
    tabla: str
    usuario: str
    fecha: datetime
    cambios: dict[str, dict[str, str | None]]


class MovimientoLeer(_DesdeORM):
    id: int
    id_dispositivo: int
    tipo: str
    serial: str
    equipo: str
    responsable: str
    registrado_por: str
    observacion: str | None
    fecha: datetime


# --- Autenticación ---------------------------------------------------------


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UsuarioAutenticado(BaseModel):
    id: int
    nombre_completo: str
    documento: str
    roles: list[str]
