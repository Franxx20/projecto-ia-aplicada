"""merge health check and main branch

Revision ID: f7g8h9i0j1k2
Revises: 61e80e3d1aa5, e6f7g8h9i0j1
Create Date: 2025-11-08 01:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f7g8h9i0j1k2'
down_revision: Union[str, None] = ('61e80e3d1aa5', 'e6f7g8h9i0j1')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Merge de las ramas: rama principal (61e80e3d1aa5) y rama de health check (e6f7g8h9i0j1).
    No hay cambios adicionales, solo consolida las dos ramas.
    """
    pass


def downgrade() -> None:
    """
    No hay cambios para revertir en esta migración de merge.
    """
    pass
