"""feat(T-024): Hacer imagen_id nullable en identificaciones

Revision ID: b2c3d4e5f6g7
Revises: a1b2c3d4e5f6
Create Date: 2025-10-20 03:56:00.000000

Modifica el campo 'imagen_id' en la tabla identificaciones para permitir NULL.
Esto es necesario para soportar identificaciones con múltiples imágenes donde
no hay una única imagen asociada directamente.

Cambios:
- Modificar columna 'imagen_id' a nullable=True en tabla identificaciones
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b2c3d4e5f6g7'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Aplica los cambios a la base de datos.
    
    Modifica:
    - Campo imagen_id en tabla identificaciones para permitir NULL
    
    Usa batch mode para compatibilidad con SQLite.
    """
    # Modificar columna imagen_id para ser nullable usando batch mode
    with op.batch_alter_table('identificaciones', schema=None) as batch_op:
        batch_op.alter_column(
            'imagen_id',
            existing_type=sa.Integer(),
            nullable=True,
            comment="ID de la imagen (NULL para identificaciones con múltiples imágenes)"
        )
    
    print("✅ Migración T-024 aplicada exitosamente")
    print("   - Campo 'imagen_id' en tabla identificaciones ahora es nullable")


def downgrade() -> None:
    """
    Revierte los cambios de la migración.
    
    ADVERTENCIA: Esto fallará si existen identificaciones con imagen_id NULL.
    Usa batch mode para compatibilidad con SQLite.
    """
    # Revertir columna imagen_id a NOT NULL usando batch mode
    with op.batch_alter_table('identificaciones', schema=None) as batch_op:
        batch_op.alter_column(
            'imagen_id',
            existing_type=sa.Integer(),
            nullable=False,
            comment="ID de la imagen"
        )
    
    print("⚠️  Migración T-024 revertida")
    print("   - Campo 'imagen_id' en tabla identificaciones ya no es nullable")
