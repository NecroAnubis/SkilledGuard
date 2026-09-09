"""Modelo de datos de Skilled Guard.

Traducción a SQLAlchemy del DDL original (`Base_de_Datos/`), con tres correcciones:
  1. Los PK eran `INT uniqueidentifier` — dos tipos a la vez, el script no ejecutaba.
     Se resuelve como entero autoincremental, que es lo que el DML ya asumía.
  2. `contrasena` guardaba texto plano; ahora es `contrasena_hash` (bcrypt).
  3. Se agregan UNIQUE en `Usuario.documento` y `Dispositivo.serial`: son
     identificadores del mundo real y duplicarlos rompe la trazabilidad.
"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Timestamps:
    """Las 14 tablas del DDL llevan estas dos columnas."""

    fecha_creado: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    fecha_actualizado: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )


# --------------------------------------------------------------------------
# Catálogos
# --------------------------------------------------------------------------


class TipoDocumento(Timestamps, Base):
    __tablename__ = "tipo_documento"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), unique=True)
    acronimo: Mapped[str | None] = mapped_column(String(10))
    descripcion: Mapped[str | None] = mapped_column(String(255))


class Rol(Timestamps, Base):
    __tablename__ = "rol"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), unique=True)
    descripcion: Mapped[str | None] = mapped_column(String(255))


class TipoDispositivo(Timestamps, Base):
    __tablename__ = "tipo_dispositivo"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), unique=True)
    descripcion: Mapped[str | None] = mapped_column(String(255))


class TipoAccion(Timestamps, Base):
    __tablename__ = "tipo_accion"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), unique=True)
    descripcion: Mapped[str | None] = mapped_column(String(255))


class ObjetoAfectado(Timestamps, Base):
    __tablename__ = "objeto_afectado"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre_tabla: Mapped[str] = mapped_column(String(100), unique=True)
    descripcion: Mapped[str | None] = mapped_column(String(255))


class TipoRegistro(Timestamps, Base):
    __tablename__ = "tipo_registro"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), unique=True)
    descripcion: Mapped[str | None] = mapped_column(String(255))


class TipoReporte(Timestamps, Base):
    __tablename__ = "tipo_reporte"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), unique=True)
    descripcion: Mapped[str | None] = mapped_column(String(255))


# --------------------------------------------------------------------------
# Usuarios y roles
# --------------------------------------------------------------------------


class Usuario(Timestamps, Base):
    __tablename__ = "usuario"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombres: Mapped[str] = mapped_column(String(100))
    apellidos: Mapped[str] = mapped_column(String(100))
    id_tipo_documento: Mapped[int] = mapped_column(ForeignKey("tipo_documento.id"))
    documento: Mapped[str] = mapped_column(String(50), unique=True)
    direccion: Mapped[str | None] = mapped_column(String(255))
    contrasena_hash: Mapped[str] = mapped_column(String(255))

    tipo_documento: Mapped[TipoDocumento] = relationship()
    roles: Mapped[list["UsuarioRol"]] = relationship(back_populates="usuario")

    @property
    def nombre_completo(self) -> str:
        return f"{self.nombres} {self.apellidos}"


class IntentoLogin(Base):
    """Registro de cada intento de inicio de sesión, exitoso o fallido.

    Sostiene el bloqueo temporal por intentos fallidos, y de paso deja
    evidencia de un ataque de fuerza bruta: sin este registro, alguien puede
    probar contraseñas durante días sin que quede rastro de haberlo hecho.

    No usa el mixin Timestamps porque un intento no se actualiza nunca: ocurre
    una vez y queda.
    """

    __tablename__ = "intento_login"

    id: Mapped[int] = mapped_column(primary_key=True)
    # Se guarda el documento tal como lo escribieron, no una llave foránea: los
    # intentos contra un documento inexistente también deben contarse.
    documento: Mapped[str] = mapped_column(String(50), index=True)
    exitoso: Mapped[bool]
    origen: Mapped[str | None] = mapped_column(String(45))  # cabe una IPv6
    fecha_creado: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )


class UsuarioRol(Timestamps, Base):
    __tablename__ = "usuario_rol"
    # Un usuario no puede tener el mismo rol dos veces.
    __table_args__ = (UniqueConstraint("id_usuario", "id_rol"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    id_usuario: Mapped[int] = mapped_column(ForeignKey("usuario.id"))
    id_rol: Mapped[int] = mapped_column(ForeignKey("rol.id"))

    usuario: Mapped[Usuario] = relationship(back_populates="roles")
    rol: Mapped[Rol] = relationship()


# --------------------------------------------------------------------------
# Dispositivos
# --------------------------------------------------------------------------


class Dispositivo(Timestamps, Base):
    __tablename__ = "dispositivo"

    id: Mapped[int] = mapped_column(primary_key=True)
    serial: Mapped[str] = mapped_column(String(50), unique=True)
    marca: Mapped[str] = mapped_column(String(100))
    modelo: Mapped[str] = mapped_column(String(100))
    sistema: Mapped[str | None] = mapped_column(String(50))
    id_tipo_dispositivo: Mapped[int] = mapped_column(ForeignKey("tipo_dispositivo.id"))
    # Nombre de quien trae el equipo, tal como lo anota el registrador. No es
    # una llave foránea a propósito: estudiantes y visitantes no tienen cuenta
    # en el sistema — cuentas solo tienen quienes lo operan, y la trazabilidad
    # de quién registró qué ya la da el vigilante en cada movimiento.
    responsable: Mapped[str] = mapped_column(String(150))
    # Identificador que se codifica en el QR pegado al equipo. Es un token
    # aleatorio y no el serial: el serial está impreso en el chasis a la vista
    # de cualquiera, y además así se puede reemplazar el código sin tocar el
    # inventario si una calcomanía se daña o se filtra.
    qr: Mapped[str] = mapped_column(String(255), unique=True, default=lambda: uuid4().hex)

    tipo_dispositivo: Mapped[TipoDispositivo] = relationship()
    movimientos: Mapped[list["AuditoriaNegocio"]] = relationship(back_populates="dispositivo")


# --------------------------------------------------------------------------
# Auditoría
# --------------------------------------------------------------------------


class Porteria(Timestamps, Base):
    """Las entradas físicas de la sede. Cada movimiento registra por cuál pasó:
    una sede puede tener varias, asignadas por horario o programa educativo."""

    __tablename__ = "porteria"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), unique=True)
    descripcion: Mapped[str | None] = mapped_column(String(255))


class AuditoriaNegocio(Timestamps, Base):
    """Movimientos de equipos: cada ingreso y cada salida por portería.

    Es el registro que reemplaza la minuta en papel. Conserva el nombre del
    modelo original, pero corrige dos cosas que lo hacían inservible para su
    propósito: no tenía forma de saber *qué equipo* se movía (faltaba la
    llave foránea a `dispositivo`), y la columna de detalle se llamaba
    `ejemplo_data`.
    """

    __tablename__ = "auditoria_negocio"

    id: Mapped[int] = mapped_column(primary_key=True)
    id_dispositivo: Mapped[int] = mapped_column(ForeignKey("dispositivo.id"), index=True)
    id_tipo_registro: Mapped[int] = mapped_column(ForeignKey("tipo_registro.id"))
    registrado_por: Mapped[int] = mapped_column(ForeignKey("usuario.id"))
    # Nullable: los movimientos anteriores a esta columna no declararon portería.
    id_porteria: Mapped[int | None] = mapped_column(ForeignKey("porteria.id"))
    observacion: Mapped[str | None] = mapped_column(String(500))

    dispositivo: Mapped[Dispositivo] = relationship(back_populates="movimientos")
    tipo_registro: Mapped[TipoRegistro] = relationship()
    vigilante: Mapped[Usuario] = relationship()
    porteria: Mapped[Porteria | None] = relationship()


class LogSistema(Timestamps, Base):
    __tablename__ = "log_sistema"

    id: Mapped[int] = mapped_column(primary_key=True)
    id_accion: Mapped[int] = mapped_column(ForeignKey("tipo_accion.id"))
    id_usuario: Mapped[int] = mapped_column(ForeignKey("usuario.id"))
    id_objeto_afectado: Mapped[int] = mapped_column(ForeignKey("objeto_afectado.id"))
    iv_firma: Mapped[str | None] = mapped_column(String(255))

    accion: Mapped[TipoAccion] = relationship()
    usuario: Mapped[Usuario] = relationship()
    objeto_afectado: Mapped[ObjetoAfectado] = relationship()
    detalles: Mapped[list["LogDetalle"]] = relationship(back_populates="log")


class LogDetalle(Timestamps, Base):
    __tablename__ = "log_detalle"

    id: Mapped[int] = mapped_column(primary_key=True)
    id_log: Mapped[int] = mapped_column(ForeignKey("log_sistema.id"))
    campo_afectado: Mapped[str] = mapped_column(String(100))
    valor_anterior: Mapped[str | None] = mapped_column(String(255))
    valor_nuevo: Mapped[str | None] = mapped_column(String(255))

    log: Mapped[LogSistema] = relationship(back_populates="detalles")


# --------------------------------------------------------------------------
# Reportes
# --------------------------------------------------------------------------


class Reporte(Timestamps, Base):
    __tablename__ = "reporte"

    id: Mapped[int] = mapped_column(primary_key=True)
    generado_por: Mapped[int] = mapped_column(ForeignKey("usuario.id"))
    filtros_aplicados: Mapped[str | None] = mapped_column(String(255))
    url_archivo: Mapped[str | None] = mapped_column(String(255))
    id_tipo_reporte: Mapped[int] = mapped_column(ForeignKey("tipo_reporte.id"))


class ConsultaReporte(Timestamps, Base):
    __tablename__ = "consulta_reporte"

    id: Mapped[int] = mapped_column(primary_key=True)
    entidad_consultada: Mapped[str] = mapped_column(String(100))
    filtro_aplicado: Mapped[str | None] = mapped_column(String(255))
    id_reporte: Mapped[int] = mapped_column(ForeignKey("reporte.id"))
