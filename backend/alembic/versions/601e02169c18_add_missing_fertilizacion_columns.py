"""Plantilla base para generar migraciones

add_missing_fertilizacion_columns

Revision ID: 601e02169c18
Revises: d49a9a0a3939
Create Date: 2025-11-21 19:46:20.258295

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '601e02169c18'
down_revision = 'd49a9a0a3939'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Agregar columnas de fertilización que faltaban en la base de datos
    op.add_column('plantas', sa.Column('fecha_ultima_fertilizacion', sa.DateTime(), nullable=True, 
                                       comment='Fecha y hora de la última fertilización'))
    op.add_column('plantas', sa.Column('frecuencia_fertilizacion_dias', sa.Integer(), nullable=True, 
                                       comment='Frecuencia de fertilización en días'))


def downgrade() -> None:
    # Remover las columnas agregadas
    op.drop_column('plantas', 'frecuencia_fertilizacion_dias')
    op.drop_column('plantas', 'fecha_ultima_fertilizacion')