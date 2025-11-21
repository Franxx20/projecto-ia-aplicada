"""Plantilla base para generar migraciones

add_missing_analisis_salud_columns

Revision ID: 9b4e887ffb4b
Revises: d3cf68a263f3
Create Date: 2025-11-21 20:03:02.721025

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9b4e887ffb4b'
down_revision = 'd3cf68a263f3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Agregar columnas faltantes en analisis_salud
    op.add_column('analisis_salud', sa.Column('notas_usuario', sa.Text(), nullable=True, 
                                              comment='Notas adicionales del usuario sobre el análisis'))
    op.add_column('analisis_salud', sa.Column('metadatos_ia', sa.JSON(), nullable=True, 
                                              comment='Metadatos adicionales del análisis de IA en formato JSON'))


def downgrade() -> None:
    # Remover las columnas agregadas
    op.drop_column('analisis_salud', 'metadatos_ia')
    op.drop_column('analisis_salud', 'notas_usuario')