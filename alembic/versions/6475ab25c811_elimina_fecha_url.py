"""elimina fecha_url

La columna venía del DDL original con nombre de fecha pero tipo texto, y nadie
en el equipo pudo explicar qué guardaba. Una columna sin propósito conocido no
se documenta ni se mantiene: se elimina. Si más adelante hace falta guardar la
foto del equipo, se agrega con ese nombre y ese propósito.


Revision ID: 6475ab25c811
Revises: e95b4bc6eebf
Create Date: 2026-08-08 05:57:58.861260
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "6475ab25c811"
down_revision: str | None = "e95b4bc6eebf"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_column("dispositivo", "fecha_url")


def downgrade() -> None:
    op.add_column(
        "dispositivo",
        sa.Column("fecha_url", sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    )
