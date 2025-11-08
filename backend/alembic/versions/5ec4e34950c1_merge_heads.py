"""Plantilla base para generar migraciones

merge_heads

Revision ID: 5ec4e34950c1
Revises: 3ab5c396ba90, a1b2c3d4e5f6
Create Date: 2025-10-20 01:39:31.197361

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5ec4e34950c1'
down_revision = ('3ab5c396ba90', 'a1b2c3d4e5f6')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass