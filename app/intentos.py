"""Bloqueo temporal del inicio de sesión tras varios intentos fallidos.

Sin este control, alguien puede probar contraseñas indefinidamente: bcrypt hace
lenta cada verificación, pero no impide reintentar millones de veces.

**Se cuenta por documento, no por dirección IP.** En una portería todos los
guardas de seguridad usan la misma red, así que bloquear por IP dejaría fuera a todo el
turno por culpa de un solo error de tecleo de una persona.

El contador vive en la base y no en memoria del proceso: así sobrevive a un
reinicio del contenedor, funciona si mañana hay más de una instancia de la API,
y deja evidencia de un intento de fuerza bruta.
"""

from datetime import UTC, datetime, timedelta

from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.models import IntentoLogin

MAX_FALLIDOS = 5
VENTANA = timedelta(minutes=15)


class DemasiadosIntentos(Exception):
    """El documento está bloqueado temporalmente."""

    def __init__(self, segundos_restantes: int) -> None:
        self.segundos_restantes = segundos_restantes
        minutos = max(1, round(segundos_restantes / 60))
        super().__init__(f"Demasiados intentos fallidos. Intente de nuevo en {minutos} minuto(s).")


def _inicio_del_conteo(db: Session, documento: str, ahora: datetime) -> datetime:
    """Desde cuándo contar los fallos.

    Un inicio de sesión exitoso borra la cuenta: si el usuario ya demostró que
    conoce la contraseña, los fallos previos fueron dedos torpes, no un ataque.
    """
    desde = ahora - VENTANA
    ultimo_exito = db.scalar(
        select(IntentoLogin.fecha_creado)
        .where(
            IntentoLogin.documento == documento,
            IntentoLogin.exitoso.is_(True),
            IntentoLogin.fecha_creado >= desde,
        )
        .order_by(desc(IntentoLogin.fecha_creado))
        .limit(1)
    )
    return max(desde, ultimo_exito) if ultimo_exito else desde


def fallidos_recientes(db: Session, documento: str, ahora: datetime | None = None) -> int:
    ahora = ahora or datetime.now(UTC)
    return db.scalar(
        select(func.count())
        .select_from(IntentoLogin)
        .where(
            IntentoLogin.documento == documento,
            IntentoLogin.exitoso.is_(False),
            IntentoLogin.fecha_creado >= _inicio_del_conteo(db, documento, ahora),
        )
    )


def verificar_bloqueo(db: Session, documento: str, ahora: datetime | None = None) -> None:
    """Lanza DemasiadosIntentos si el documento superó el límite."""
    ahora = ahora or datetime.now(UTC)
    if fallidos_recientes(db, documento, ahora) < MAX_FALLIDOS:
        return

    primer_fallo = db.scalar(
        select(IntentoLogin.fecha_creado)
        .where(
            IntentoLogin.documento == documento,
            IntentoLogin.exitoso.is_(False),
            IntentoLogin.fecha_creado >= _inicio_del_conteo(db, documento, ahora),
        )
        .order_by(IntentoLogin.fecha_creado)
        .limit(1)
    )
    # El bloqueo se levanta cuando el fallo más antiguo sale de la ventana.
    restantes = (primer_fallo + VENTANA - ahora).total_seconds() if primer_fallo else 0
    raise DemasiadosIntentos(max(1, int(restantes)))


def registrar_intento(db: Session, documento: str, exitoso: bool, origen: str | None) -> None:
    db.add(IntentoLogin(documento=documento, exitoso=exitoso, origen=origen))
    db.commit()


# ponytail: la tabla crece sin purga. Con el volumen de una portería tarda años
# en pesar; si llegara a importar, un borrado periódico de lo anterior a la
# ventana lo resuelve.
