"""Plantilla base para generar migraciones

rename_estado_salud_to_estado

Revision ID: d3cf68a263f3
Revises: 80813eae949e
Create Date: 2025-11-21 19:59:32.642675

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd3cf68a263f3'
down_revision = '80813eae949e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Renombrar columna estado_salud a estado en tabla analisis_salud
    op.alter_column('analisis_salud', 'estado_salud', new_column_name='estado')


def downgrade() -> None:
    # Revertir el cambio
    op.alter_column('analisis_salud', 'estado', new_column_name='estado_salud')