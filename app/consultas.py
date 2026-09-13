"""Construcción de la consulta de movimientos, compartida por la API y los reportes.

Vive aparte para que el listado y el reporte apliquen exactamente los mismos
filtros: si se duplicara, el día que alguien agregue un filtro en uno de los
dos, el Excel y la pantalla dejarían de coincidir.
"""

from datetime import date, datetime, time
from zoneinfo import ZoneInfo

from sqlalchemy import Select, desc, select
from sqlalchemy.orm import joinedload

from app.models import AuditoriaNegocio, Dispositivo, TipoRegistro

# Las fechas se guardan en UTC, pero quien filtra piensa en la hora de la
# portería. Sin fijar la zona, los límites del día se interpretaban como UTC y
# todo lo registrado después de las 19:00 hora local caía en el día siguiente:
# el turno de la tarde desaparecía del filtro "hoy". El servidor puede correr en
# cualquier zona —en la plataforma de despliegue corre en UTC—, así que la zona
# del negocio se declara aquí y no se deduce del entorno.
ZONA_LOCAL = ZoneInfo("America/Bogota")


def _limite(dia: date, momento: time) -> datetime:
    """Instante exacto en que empieza o termina un día en la portería."""
    return datetime.combine(dia, momento, tzinfo=ZONA_LOCAL)


def movimientos(
    id_dispositivo: int | None = None,
    responsable: str | None = None,
    tipo: str | None = None,
    desde: date | None = None,
    hasta: date | None = None,
) -> Select[tuple[AuditoriaNegocio]]:
    consulta = select(AuditoriaNegocio).options(
        # Sin esto cada fila dispara cuatro consultas más al leer el equipo, su
        # responsable, el guarda y el tipo: 50 movimientos = 201 consultas.
        joinedload(AuditoriaNegocio.dispositivo),
        joinedload(AuditoriaNegocio.porteria),
        joinedload(AuditoriaNegocio.tipo_registro),
        joinedload(AuditoriaNegocio.guarda),
    )

    if id_dispositivo is not None:
        consulta = consulta.where(AuditoriaNegocio.id_dispositivo == id_dispositivo)
    if responsable is not None:
        consulta = consulta.join(Dispositivo).where(Dispositivo.responsable.ilike(f"%{responsable}%"))
    if tipo is not None:
        consulta = consulta.join(TipoRegistro).where(TipoRegistro.nombre == tipo)
    if desde is not None:
        consulta = consulta.where(AuditoriaNegocio.fecha_creado >= _limite(desde, time.min))
    if hasta is not None:
        # `hasta` es inclusivo: el usuario que filtra "hasta el 8" espera que
        # aparezcan los movimientos del día 8, no los anteriores a su medianoche.
        consulta = consulta.where(AuditoriaNegocio.fecha_creado <= _limite(hasta, time.max))

    return consulta.order_by(desc(AuditoriaNegocio.id))
