"""intentos de login

Crea `intento_login`, la bitácora que sostiene el bloqueo temporal tras varios
intentos fallidos (ver `app/intentos.py`). El conteo vive en la base y no en
memoria del proceso para que sobreviva a un reinicio y sirva con más de una
instancia de la API.

Los índices no son decorativos: cada intento de inicio de sesión consulta la
tabla filtrando por documento y fecha, y sin ellos el login degrada a medida que
la bitácora crece.

Revision ID: b7c41d92f30a
Revises: 6475ab25c811
Create Date: 2026-08-09
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "b7c41d92f30a"
down_revision: str | None = "6475ab25c811"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

IX_INTENTO_DOCUMENTO = "ix_intento_login_documento"
IX_INTENTO_FECHA = "ix_intento_login_fecha_creado"


def upgrade() -> None:
    op.create_table(
        "intento_login",
        sa.Column("id", sa.Integer(), nullable=False),
        # Sin llave foránea a usuario: los intentos contra un documento que no
        # existe también deben contarse, y son justo los de un ataque.
        sa.Column("documento", sa.String(length=50), nullable=False),
        sa.Column("exitoso", sa.Boolean(), nullable=False),
        sa.Column("origen", sa.String(length=45), nullable=True),  # cabe una IPv6
        sa.Column(
            "fecha_creado",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(IX_INTENTO_DOCUMENTO, "intento_login", ["documento"])
    op.create_index(IX_INTENTO_FECHA, "intento_login", ["fecha_creado"])


def downgrade() -> None:
    op.drop_index(IX_INTENTO_FECHA, table_name="intento_login")
    op.drop_index(IX_INTENTO_DOCUMENTO, table_name="intento_login")
    op.drop_table("intento_login")
