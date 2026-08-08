"""movimientos de porteria

`auditoria_negocio` debía registrar los ingresos y salidas de equipos, pero no
tenía forma de indicar *qué equipo* se movía. Se agrega la llave foránea a
`dispositivo` y se renombra `ejemplo_data` por `observacion`.

También se vuelve obligatorio y único el código QR del equipo: es el
identificador con el que la portería lo reconoce.

Revision ID: e95b4bc6eebf
Revises: 396395686f02
Create Date: 2026-08-08
"""

from collections.abc import Sequence
from uuid import uuid4

import sqlalchemy as sa

from alembic import op

revision: str = "e95b4bc6eebf"
down_revision: str | None = "396395686f02"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

FK_MOVIMIENTO_DISPOSITIVO = "fk_auditoria_negocio_dispositivo"
UQ_DISPOSITIVO_QR = "uq_dispositivo_qr"
IX_MOVIMIENTO_DISPOSITIVO = "ix_auditoria_negocio_id_dispositivo"


def upgrade() -> None:
    conexion = op.get_bind()

    # Los registros previos no indican a qué equipo pertenecen: la columna no
    # existía. No hay forma de deducirlo, así que se descartan en vez de
    # inventarles un dispositivo.
    conexion.execute(sa.text("DELETE FROM auditoria_negocio"))

    op.add_column("auditoria_negocio", sa.Column("id_dispositivo", sa.Integer(), nullable=False))
    op.add_column(
        "auditoria_negocio", sa.Column("observacion", sa.String(length=500), nullable=True)
    )
    op.create_index(IX_MOVIMIENTO_DISPOSITIVO, "auditoria_negocio", ["id_dispositivo"])
    op.create_foreign_key(
        FK_MOVIMIENTO_DISPOSITIVO, "auditoria_negocio", "dispositivo", ["id_dispositivo"], ["id"]
    )
    op.drop_column("auditoria_negocio", "ejemplo_data")

    # Los equipos ya registrados no tienen código: se les asigna uno antes de
    # declarar la columna obligatoria, o la migración falla con filas existentes.
    for (id_dispositivo,) in conexion.execute(
        sa.text("SELECT id FROM dispositivo WHERE qr IS NULL")
    ):
        conexion.execute(
            sa.text("UPDATE dispositivo SET qr = :qr WHERE id = :id"),
            {"qr": uuid4().hex, "id": id_dispositivo},
        )

    op.alter_column("dispositivo", "qr", existing_type=sa.VARCHAR(length=255), nullable=False)
    op.create_unique_constraint(UQ_DISPOSITIVO_QR, "dispositivo", ["qr"])


def downgrade() -> None:
    op.drop_constraint(UQ_DISPOSITIVO_QR, "dispositivo", type_="unique")
    op.alter_column("dispositivo", "qr", existing_type=sa.VARCHAR(length=255), nullable=True)

    op.add_column(
        "auditoria_negocio", sa.Column("ejemplo_data", sa.VARCHAR(length=500), nullable=True)
    )
    op.drop_constraint(FK_MOVIMIENTO_DISPOSITIVO, "auditoria_negocio", type_="foreignkey")
    op.drop_index(IX_MOVIMIENTO_DISPOSITIVO, table_name="auditoria_negocio")
    op.drop_column("auditoria_negocio", "observacion")
    op.drop_column("auditoria_negocio", "id_dispositivo")
