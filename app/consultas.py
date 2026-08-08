"""Construcción de la consulta de movimientos, compartida por la API y los reportes.

Vive aparte para que el listado y el reporte apliquen exactamente los mismos
filtros: si se duplicara, el día que alguien agregue un filtro en uno de los
dos, el Excel y la pantalla dejarían de coincidir.
"""

from datetime import date, datetime, time

from sqlalchemy import Select, desc, select
from sqlalchemy.orm import joinedload

from app.models import AuditoriaNegocio, Dispositivo, TipoRegistro


def movimientos(
    id_dispositivo: int | None = None,
    id_usuario: int | None = None,
    tipo: str | None = None,
    desde: date | None = None,
    hasta: date | None = None,
) -> Select[tuple[AuditoriaNegocio]]:
    consulta = select(AuditoriaNegocio).options(
        # Sin esto cada fila dispara cuatro consultas más al leer el equipo, su
        # responsable, el vigilante y el tipo: 50 movimientos = 201 consultas.
        joinedload(AuditoriaNegocio.dispositivo).joinedload(Dispositivo.usuario),
        joinedload(AuditoriaNegocio.tipo_registro),
        joinedload(AuditoriaNegocio.vigilante),
    )

    if id_dispositivo is not None:
        consulta = consulta.where(AuditoriaNegocio.id_dispositivo == id_dispositivo)
    if id_usuario is not None:
        consulta = consulta.join(Dispositivo).where(Dispositivo.id_usuario == id_usuario)
    if tipo is not None:
        consulta = consulta.join(TipoRegistro).where(TipoRegistro.nombre == tipo)
    if desde is not None:
        consulta = consulta.where(
            AuditoriaNegocio.fecha_creado >= datetime.combine(desde, time.min)
        )
    if hasta is not None:
        # `hasta` es inclusivo: el usuario que filtra "hasta el 8" espera que
        # aparezcan los movimientos del día 8, no los anteriores a su medianoche.
        consulta = consulta.where(
            AuditoriaNegocio.fecha_creado <= datetime.combine(hasta, time.max)
        )

    return consulta.order_by(desc(AuditoriaNegocio.id))
