"""Plantilla base para generar migraciones

merge: consolidate migration branches

Revision ID: 61e80e3d1aa5
Revises: 003_add_complete_models, b2c3d4e5f6g7, d5e6f7g8h9i0
Create Date: 2025-11-08 03:06:16.851012

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '61e80e3d1aa5'
down_revision = ('003_add_complete_models', 'b2c3d4e5f6g7', 'd5e6f7g8h9i0')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass