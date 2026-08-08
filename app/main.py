from fastapi import FastAPI

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
def salud() -> dict[str, str]:
    """Verificación de que el servicio está arriba (usada por Docker healthcheck)."""
    return {"estado": "ok"}
