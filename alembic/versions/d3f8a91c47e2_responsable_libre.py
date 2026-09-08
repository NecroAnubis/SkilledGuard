"""responsable libre en dispositivo

El responsable de un equipo pasa de llave foránea a `usuario` a un nombre en
texto libre: estudiantes y visitantes traen equipos sin tener cuenta en el
sistema, y exigirla obligaba a crear usuarios ficticios. La trazabilidad de
quién registró cada movimiento no se pierde — la lleva el vigilante en la
auditoría de negocio.

Los responsables existentes se conservan copiando el nombre completo del
usuario al que apuntaba la llave, antes de eliminarla.

Revision ID: d3f8a91c47e2
Revises: b7c41d92f30a
Create Date: 2026-09-08
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "d3f8a91c47e2"
down_revision: str | None = "b7c41d92f30a"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Nullable solo mientras se rellena: ningún equipo debe quedar sin responsable.
    op.add_column("dispositivo", sa.Column("responsable", sa.String(length=150), nullable=True))
    op.execute(
        "UPDATE dispositivo SET responsable = u.nombres || ' ' || u.apellidos "
        "FROM usuario u WHERE u.id = dispositivo.id_usuario"
    )
    op.alter_column("dispositivo", "responsable", nullable=False)
    op.drop_column("dispositivo", "id_usuario")


def downgrade() -> None:
    # La llave foránea vuelve pero queda en NULL: el nombre libre no permite
    # reconstruir a qué usuario apuntaba (puede ni existir como usuario).
    op.add_column(
        "dispositivo",
        sa.Column("id_usuario", sa.Integer(), sa.ForeignKey("usuario.id"), nullable=True),
    )
    op.drop_column("dispositivo", "responsable")
