"""Plantilla base para generar migraciones

add_condiciones_ambientales_column

Revision ID: 80813eae949e
Revises: 601e02169c18
Create Date: 2025-11-21 19:48:57.253490

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '80813eae949e'
down_revision = '601e02169c18'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Agregar columna condiciones_ambientales_recomendadas que faltaba
    op.add_column('plantas', sa.Column('condiciones_ambientales_recomendadas', sa.Text(), nullable=True, 
                                       comment='JSON con condiciones ambientales ideales (luz, temperatura, humedad) según análisis inicial'))


def downgrade() -> None:
    # Remover la columna agregada
    op.drop_column('plantas', 'condiciones_ambientales_recomendadas')