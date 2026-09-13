"""correo institucional del usuario

El inicio de sesión migra del número de documento al correo institucional, y
administrar el sistema exige un correo del dominio corporativo.

La columna es nullable: las cuentas creadas antes de esta migración no tienen
correo y deben seguir entrando con su documento hasta que se les asigne uno.
El índice único impide dos cuentas con el mismo correo; se guarda siempre en
minúsculas (lo normaliza el esquema de entrada) para que "Admin@" y "admin@"
no puedan coexistir.

Revision ID: b62d9f3ac714
Revises: a4c8e17f52b9
Create Date: 2026-09-10
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "b62d9f3ac714"
down_revision: str | None = "a4c8e17f52b9"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

INDICE = "ix_usuario_correo"


def upgrade() -> None:
    op.add_column("usuario", sa.Column("correo", sa.String(length=150), nullable=True))
    op.create_index(INDICE, "usuario", ["correo"], unique=True)


def downgrade() -> None:
    op.drop_index(INDICE, table_name="usuario")
    op.drop_column("usuario", "correo")
