"""Descarga de reportes de movimientos en Excel y PDF."""

from datetime import date, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session

from app import consultas
from app.auditoria import Accion, registrar_accion
from app.database import get_db
from app.models import Usuario
from app.reportes import generar_excel, generar_pdf
from app.security import ROL_ADMINISTRADOR, ROL_SEGURIDAD, exige_rol, usuario_actual

router = APIRouter(prefix="/reportes", tags=["Reportes"])

_consulta = [Depends(exige_rol(ROL_ADMINISTRADOR, ROL_SEGURIDAD))]

EXCEL = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

# Tope alto pero finito: un reporte sin límite se convierte en una forma
# accidental de tumbar el servidor pidiendo la tabla entera.
MAXIMO_FILAS = 5000


def _descarga(contenido: bytes, tipo: str, extension: str) -> Response:
    nombre = f"movimientos_{datetime.now():%Y%m%d_%H%M}.{extension}"
    return Response(
        content=contenido,
        media_type=tipo,
        headers={"Content-Disposition": f'attachment; filename="{nombre}"'},
    )


def _consultar(db: Session, id_dispositivo, responsable, tipo, desde, hasta):
    consulta = consultas.movimientos(id_dispositivo, responsable, tipo, desde, hasta)
    return list(db.scalars(consulta.limit(MAXIMO_FILAS)).unique().all())


@router.get(
    "/movimientos.xlsx",
    dependencies=_consulta,
    response_class=Response,
    responses={200: {"content": {EXCEL: {}}, "description": "Reporte en Excel"}},
)
def movimientos_excel(
    db: Annotated[Session, Depends(get_db)],
    usuario: Annotated[Usuario, Depends(usuario_actual)],
    id_dispositivo: int | None = None,
    responsable: str | None = None,
    tipo: Annotated[str | None, Query(description="Ingreso o Salida")] = None,
    desde: date | None = None,
    hasta: date | None = None,
) -> Response:
    movimientos = _consultar(db, id_dispositivo, responsable, tipo, desde, hasta)
    registrar_accion(db, usuario.id, Accion.CONSULTA, "reporte", {"formato": (None, "xlsx")})
    db.commit()
    return _descarga(generar_excel(movimientos), EXCEL, "xlsx")


@router.get(
    "/movimientos.pdf",
    dependencies=_consulta,
    response_class=Response,
    responses={200: {"content": {"application/pdf": {}}, "description": "Reporte en PDF"}},
)
def movimientos_pdf(
    db: Annotated[Session, Depends(get_db)],
    usuario: Annotated[Usuario, Depends(usuario_actual)],
    id_dispositivo: int | None = None,
    responsable: str | None = None,
    tipo: Annotated[str | None, Query(description="Ingreso o Salida")] = None,
    desde: date | None = None,
    hasta: date | None = None,
) -> Response:
    movimientos = _consultar(db, id_dispositivo, responsable, tipo, desde, hasta)
    registrar_accion(db, usuario.id, Accion.CONSULTA, "reporte", {"formato": (None, "pdf")})
    db.commit()
    return _descarga(generar_pdf(movimientos), "application/pdf", "pdf")
