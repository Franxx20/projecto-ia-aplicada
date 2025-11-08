"""feat: agregar es_favorita y es_regalo a plantas

Revision ID: c4d5e6f7g8h9
Revises: b2c3d4e5f6g7
Create Date: 2025-11-07 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c4d5e6f7g8h9'
down_revision: Union[str, None] = '5ec4e34950c1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Agrega columnas es_favorita y es_regalo a la tabla plantas.
    
    Estos campos permiten:
    - es_favorita: Marcar plantas como favoritas para mostrarlas primero en el dashboard
    - es_regalo: Identificar plantas que fueron regaladas al usuario
    """
    # Agregar columna es_favorita
    op.add_column('plantas', sa.Column('es_favorita', sa.Boolean(), nullable=False, server_default='false', comment='Indica si la planta ha sido marcada como favorita por el usuario'))
    
    # Agregar columna es_regalo
    op.add_column('plantas', sa.Column('es_regalo', sa.Boolean(), nullable=False, server_default='false', comment='Indica si la planta fue un regalo'))
    
    # Crear índice para optimizar queries de favoritas
    op.create_index('idx_usuario_favoritas', 'plantas', ['usuario_id', 'es_favorita'], unique=False)


def downgrade() -> None:
    """
    Revierte los cambios eliminando las columnas es_favorita y es_regalo.
    """
    # Eliminar índice
    op.drop_index('idx_usuario_favoritas', table_name='plantas')
    
    # Eliminar columnas
    op.drop_column('plantas', 'es_regalo')
    op.drop_column('plantas', 'es_favorita')
