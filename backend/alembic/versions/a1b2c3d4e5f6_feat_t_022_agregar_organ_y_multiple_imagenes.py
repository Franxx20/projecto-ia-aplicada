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
    - Campo organ a tabla imagenes (si no existe)
    - Campo identificacion_id a tabla imagenes (si no existe)
    - Índices para mejora de performance
    
    NOTA: Esta migración verifica si las columnas ya existen antes de crearlas
    para evitar conflictos con la migración 003_add_complete_models que también
    las crea en una rama paralela del árbol de migraciones.
    """
    from sqlalchemy import inspect
    
    # Obtener conexión y inspector para verificar estructura actual
    conn = op.get_bind()
    inspector = inspect(conn)
    
    # Obtener lista de columnas existentes en la tabla imagenes
    existing_columns = [col['name'] for col in inspector.get_columns('imagenes')]
    
    # Obtener lista de foreign keys existentes
    existing_fks = [fk['name'] for fk in inspector.get_foreign_keys('imagenes')]
    
    # Obtener lista de índices existentes
    existing_indexes = [idx['name'] for idx in inspector.get_indexes('imagenes')]
    
    # === Agregar columna 'organ' si no existe ===
    if 'organ' not in existing_columns:
        op.add_column(
            'imagenes',
            sa.Column(
                'organ',
                sa.String(length=50),
                nullable=True,
                comment="Tipo de órgano de la planta: flower, leaf, fruit, bark, habit, other"
            )
        )
        print("✅ Agregado campo 'organ' a tabla imagenes")
    else:
        print("ℹ️  Campo 'organ' ya existe en tabla imagenes, omitiendo...")
    
    # === Agregar columna 'identificacion_id' si no existe ===
    if 'identificacion_id' not in existing_columns:
        op.add_column(
            'imagenes',
            sa.Column(
                'identificacion_id',
                sa.Integer(),
                nullable=True,
                comment="ID de la identificación asociada (si forma parte de una identificación múltiple)"
            )
        )
        print("✅ Agregado campo 'identificacion_id' a tabla imagenes")
    else:
        print("ℹ️  Campo 'identificacion_id' ya existe en tabla imagenes, omitiendo...")
    
    # === Crear Foreign Key si no existe ===
    if 'fk_imagenes_identificacion_id' not in existing_fks:
        # Usar batch mode para compatibilidad con SQLite
        with op.batch_alter_table('imagenes', schema=None) as batch_op:
            batch_op.create_foreign_key(
                'fk_imagenes_identificacion_id',  # Nombre de la constraint
                'identificaciones',  # Tabla destino
                ['identificacion_id'],  # Columnas fuente
                ['id'],  # Columnas destino
                ondelete='SET NULL'  # Acción al eliminar
            )
        print("✅ Creada Foreign Key 'fk_imagenes_identificacion_id'")
    else:
        print("ℹ️  Foreign Key 'fk_imagenes_identificacion_id' ya existe, omitiendo...")
    
    # === Crear índice para organ si no existe ===
    if 'idx_imagenes_organ' not in existing_indexes:
        op.create_index(
            'idx_imagenes_organ',
            'imagenes',
            ['organ'],
            unique=False
        )
        print("✅ Creado índice 'idx_imagenes_organ'")
    else:
        print("ℹ️  Índice 'idx_imagenes_organ' ya existe, omitiendo...")
    
    # === Crear índice para identificacion_id si no existe ===
    if 'idx_imagenes_identificacion' not in existing_indexes:
        op.create_index(
            'idx_imagenes_identificacion',
            'imagenes',
            ['identificacion_id'],
            unique=False
        )
        print("✅ Creado índice 'idx_imagenes_identificacion'")
    else:
        print("ℹ️  Índice 'idx_imagenes_identificacion' ya existe, omitiendo...")
    
    print("✅ Migración T-022 aplicada exitosamente (idempotente)")


def downgrade() -> None:
    """
    Revierte los cambios de la migración.
    
    ADVERTENCIA: Esto eliminará los datos de organ e identificacion_id.
    """
    # Eliminar índices
    op.drop_index('idx_imagenes_identificacion', table_name='imagenes')
    op.drop_index('idx_imagenes_organ', table_name='imagenes')
    
    # Eliminar Foreign Key usando batch mode para compatibilidad con SQLite
    with op.batch_alter_table('imagenes', schema=None) as batch_op:
        batch_op.drop_constraint('fk_imagenes_identificacion_id', type_='foreignkey')
    
    # Eliminar columnas
    op.drop_column('imagenes', 'identificacion_id')
    op.drop_column('imagenes', 'organ')
    
    print("⚠️  Migración T-022 revertida")
    print("   - Eliminado campo 'organ' de tabla imagenes")
    print("   - Eliminado campo 'identificacion_id' de tabla imagenes")
    print("   - Eliminados índices asociados")
