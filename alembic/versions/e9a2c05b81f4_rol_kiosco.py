"""rol kiosco

Crea el rol Kiosco para la tablet de autoservicio de la portería: el dueño del
equipo registra su propio ingreso. La restricción de que solo pueda crear
ingresos vive en el código; este rol solo existe como dato.

Va en una migración (y no solo en la semilla) porque la semilla de producción
corre únicamente cuando hay credenciales de administrador presentes — un rol
nuevo debe llegar con el despliegue, sin depender de eso.

Revision ID: e9a2c05b81f4
Revises: d3f8a91c47e2
Create Date: 2026-09-09
"""

from collections.abc import Sequence

from alembic import op

revision: str = "e9a2c05b81f4"
down_revision: str | None = "d3f8a91c47e2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        "INSERT INTO rol (nombre, descripcion) "
        "SELECT 'Kiosco', 'Autoservicio de ingreso en portería; no puede registrar salidas' "
        "WHERE NOT EXISTS (SELECT 1 FROM rol WHERE nombre = 'Kiosco')"
    )


def downgrade() -> None:
    op.execute(
        "DELETE FROM usuario_rol WHERE id_rol IN (SELECT id FROM rol WHERE nombre = 'Kiosco')"
    )
    op.execute("DELETE FROM rol WHERE nombre = 'Kiosco'")
