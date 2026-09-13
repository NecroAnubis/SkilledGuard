"""porterías: por cuál entrada pasó cada movimiento

La sede tiene varias entradas físicas, asignadas por horario o programa
educativo. Cada movimiento registra la suya; los movimientos anteriores a esta
columna quedan sin portería (nullable) — no se inventa un dato que no se tomó.

Se siembran tres porterías genéricas para que el selector no arranque vacío;
el administrador puede crear más por la API y los nombres reales se ajustan
con un UPDATE cuando la sede los defina.

Revision ID: a4c8e17f52b9
Revises: f1b7d2e94a03
Create Date: 2026-09-09
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "a4c8e17f52b9"
down_revision: str | None = "f1b7d2e94a03"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "porteria",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nombre", sa.String(length=100), nullable=False),
        sa.Column("descripcion", sa.String(length=255), nullable=True),
        sa.Column(
            "fecha_creado", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("fecha_actualizado", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("nombre"),
    )
    op.add_column(
        "auditoria_negocio",
        sa.Column("id_porteria", sa.Integer(), sa.ForeignKey("porteria.id"), nullable=True),
    )
    op.execute(
        "INSERT INTO porteria (nombre, descripcion) VALUES "
        "('Portería 1', 'Entrada principal'), "
        "('Portería 2', 'Segunda entrada'), "
        "('Portería 3', 'Tercera entrada')"
    )


def downgrade() -> None:
    op.drop_column("auditoria_negocio", "id_porteria")
    op.drop_table("porteria")
