"""rename es_regalo to fue_regada_hoy

Revision ID: d5e6f7g8h9i0
Revises: c4d5e6f7g8h9
Create Date: 2025-11-07 13:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd5e6f7g8h9i0'
down_revision: Union[str, None] = 'c4d5e6f7g8h9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Renombra la columna es_regalo a fue_regada_hoy.
    """
    op.alter_column('plantas', 'es_regalo', new_column_name='fue_regada_hoy')


def downgrade() -> None:
    """
    Revierte el cambio renombrando fue_regada_hoy a es_regalo.
    """
    op.alter_column('plantas', 'fue_regada_hoy', new_column_name='es_regalo')
