"""el rol Kiosco pasa a llamarse Entrada

El nombre es visible para el administrador (pastillas de rol, selector al
crear usuarios) y "Kiosco" es jerga técnica; "Entrada" describe la función.

Revision ID: f1b7d2e94a03
Revises: e9a2c05b81f4
Create Date: 2026-09-09
"""

from collections.abc import Sequence

from alembic import op

revision: str = "f1b7d2e94a03"
down_revision: str | None = "e9a2c05b81f4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        "UPDATE rol SET nombre = 'Entrada', "
        "descripcion = 'Autoservicio de ingreso en la entrada; no puede registrar salidas' "
        "WHERE nombre = 'Kiosco'"
    )


def downgrade() -> None:
    op.execute("UPDATE rol SET nombre = 'Kiosco' WHERE nombre = 'Entrada'")
