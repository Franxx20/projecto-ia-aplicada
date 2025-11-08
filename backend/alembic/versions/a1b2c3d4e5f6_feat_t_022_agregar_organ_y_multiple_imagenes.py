"""feat(T-022): Agregar organ y soporte para múltiples imágenes

Revision ID: a1b2c3d4e5f6
Revises: 778b31b200bd
Create Date: 2025-10-20 01:00:00.000000

Agrega el campo 'organ' a la tabla imagenes y el campo 'identificacion_id'
para soportar múltiples imágenes por identificación según T-022.

Cambios:
- Agregar columna 'organ' a tabla imagenes (nullable, para órgano de la planta)
- Agregar columna 'identificacion_id' a tabla imagenes (Foreign Key a identificaciones)
- Agregar índices para optimizar queries con organ e identificacion_id
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '778b31b200bd'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Aplica los cambios a la base de datos.
    
    Agrega:
    - Campo organ a tabla imagenes
    - Campo identificacion_id a tabla imagenes
    - Índices para mejora de performance
    """
    # Agregar columna 'organ' a tabla imagenes
    op.add_column(
        'imagenes',
        sa.Column(
            'organ',
            sa.String(length=50),
            nullable=True,
            comment="Tipo de órgano de la planta: flower, leaf, fruit, bark, habit, other"
        )
    )
    
    # Agregar columna 'identificacion_id' a tabla imagenes
    op.add_column(
        'imagenes',
        sa.Column(
            'identificacion_id',
            sa.Integer(),
            nullable=True,
            comment="ID de la identificación asociada (si forma parte de una identificación múltiple)"
        )
    )
    
    # Crear Foreign Key para identificacion_id
    op.create_foreign_key(
        'fk_imagenes_identificacion_id',  # Nombre de la constraint
        'imagenes',  # Tabla fuente
        'identificaciones',  # Tabla destino
        ['identificacion_id'],  # Columnas fuente
        ['id'],  # Columnas destino
        ondelete='SET NULL'  # Acción al eliminar
    )
    
    # Crear índice para organ
    op.create_index(
        'idx_imagenes_organ',
        'imagenes',
        ['organ'],
        unique=False
    )
    
    # Crear índice para identificacion_id
    op.create_index(
        'idx_imagenes_identificacion',
        'imagenes',
        ['identificacion_id'],
        unique=False
    )
    
    print("✅ Migración T-022 aplicada exitosamente")
    print("   - Agregado campo 'organ' a tabla imagenes")
    print("   - Agregado campo 'identificacion_id' a tabla imagenes")
    print("   - Creados índices para optimización")


def downgrade() -> None:
    """
    Revierte los cambios de la migración.
    
    ADVERTENCIA: Esto eliminará los datos de organ e identificacion_id.
    """
    # Eliminar índices
    op.drop_index('idx_imagenes_identificacion', table_name='imagenes')
    op.drop_index('idx_imagenes_organ', table_name='imagenes')
    
    # Eliminar Foreign Key
    op.drop_constraint('fk_imagenes_identificacion_id', 'imagenes', type_='foreignkey')
    
    # Eliminar columnas
    op.drop_column('imagenes', 'identificacion_id')
    op.drop_column('imagenes', 'organ')
    
    print("⚠️  Migración T-022 revertida")
    print("   - Eliminado campo 'organ' de tabla imagenes")
    print("   - Eliminado campo 'identificacion_id' de tabla imagenes")
    print("   - Eliminados índices asociados")
