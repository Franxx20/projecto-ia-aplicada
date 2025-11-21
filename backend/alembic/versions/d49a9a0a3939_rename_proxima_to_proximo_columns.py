"""Plantilla base para generar migraciones

rename_proxima_to_proximo_columns

Revision ID: d49a9a0a3939
Revises: 002_add_gemini_cache
Create Date: 2025-11-21 19:39:32.384099

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd49a9a0a3939'
down_revision = '002_add_gemini_cache'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Renombrar proxima_riego a proximo_riego (existe en la base de datos)
    op.alter_column('plantas', 'proxima_riego', new_column_name='proximo_riego')
    
    # Agregar columna proxima_fertilizacion si no existe (será renombrada inmediatamente)
    # Esta columna debería haber sido creada en la migración inicial pero falta
    op.add_column('plantas', sa.Column('proxima_fertilizacion', sa.DateTime(), nullable=True, 
                                       comment='Fecha y hora de la próxima fertilización recomendada'))


def downgrade() -> None:
    # Revertir los cambios
    op.alter_column('plantas', 'proximo_riego', new_column_name='proxima_riego')
    op.drop_column('plantas', 'proxima_fertilizacion')