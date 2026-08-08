from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import get_db
from app.routers import auth, catalogos, usuarios

app = FastAPI(
    title="Skilled Guard",
    description=(
        "Sistema de automatización para el control de ingreso de equipos tecnológicos. "
        "Proyecto de grado — Tecnólogo en Análisis y Desarrollo de Software, SENA."
    ),
    version="0.1.0",
)

app.include_router(auth.router)
app.include_router(usuarios.router)
app.include_router(catalogos.roles)
app.include_router(catalogos.tipos_documento)


@app.get("/salud", tags=["Sistema"])
def salud(db: Annotated[Session, Depends(get_db)]) -> dict[str, str]:
    """Estado del servicio, usado por el healthcheck de Docker.

    Consulta la base de datos a propósito: una API que responde "ok" mientras
    Postgres está caído es peor que una que no responde, porque el orquestador
    la da por sana y le sigue enviando tráfico.
    """
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError:
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE, "Sin conexión a la base de datos"
        ) from None
    return {"estado": "ok", "base_de_datos": "ok"}
