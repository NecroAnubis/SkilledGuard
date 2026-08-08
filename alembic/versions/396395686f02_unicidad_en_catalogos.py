"""unicidad en catalogos

Los catálogos son listas cerradas (tipos de documento, roles, tipos de
dispositivo). Sin restricción de unicidad se podían insertar dos filas con el
mismo nombre, y a partir de ahí el sistema ya no sabe cuál de las dos usar.

Las restricciones se nombran de forma explícita: Alembic las genera sin nombre,
y entonces el downgrade queda inservible porque no hay qué soltar.

Revision ID: 396395686f02
Revises: 94451af50953
Create Date: 2026-08-08
"""

from collections.abc import Sequence

from alembic import op

revision: str = "396395686f02"
down_revision: str | None = "94451af50953"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# (tabla, columna) de cada catálogo que debe tener nombre único.
CATALOGOS = [
    ("objeto_afectado", "nombre_tabla"),
    ("tipo_accion", "nombre"),
    ("tipo_dispositivo", "nombre"),
    ("tipo_documento", "nombre"),
    ("tipo_registro", "nombre"),
    ("tipo_reporte", "nombre"),
]


def _nombre_restriccion(tabla: str, columna: str) -> str:
    return f"uq_{tabla}_{columna}"


def upgrade() -> None:
    for tabla, columna in CATALOGOS:
        op.create_unique_constraint(_nombre_restriccion(tabla, columna), tabla, [columna])


def downgrade() -> None:
    for tabla, columna in reversed(CATALOGOS):
        op.drop_constraint(_nombre_restriccion(tabla, columna), tabla, type_="unique")
