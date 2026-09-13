"""documento del responsable del equipo

La portería coteja contra un carné, y en un centro de formación con miles de
personas el nombre solo no distingue a dos homónimos. El equipo pasa a
declarar también el documento de quien responde por él.

Nullable: los equipos registrados antes de esta columna no lo declararon y no
se inventa un dato que nadie tomó. Para los equipos nuevos el documento es
obligatorio — lo exige el esquema de entrada de la API.

Revision ID: c7e41b0d8fa2
Revises: b62d9f3ac714
Create Date: 2026-09-10
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "c7e41b0d8fa2"
down_revision: str | None = "b62d9f3ac714"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

INDICE = "ix_dispositivo_documento_responsable"


def upgrade() -> None:
    op.add_column(
        "dispositivo", sa.Column("documento_responsable", sa.String(length=50), nullable=True)
    )
    # Indexado: "¿qué equipos tiene esta persona?" es una consulta de portería.
    op.create_index(INDICE, "dispositivo", ["documento_responsable"])


def downgrade() -> None:
    op.drop_index(INDICE, table_name="dispositivo")
    op.drop_column("dispositivo", "documento_responsable")
