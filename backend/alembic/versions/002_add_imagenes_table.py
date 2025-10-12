"""
Add imagenes table

Migración para crear la tabla de imágenes que almacena metadata
de archivos subidos a Azure Blob Storage.

Revision ID: 002
Revises: 001
Create Date: 2025-10-12

Sprint: Sprint 1 - T-004
"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision = '002_add_imagenes_table'
down_revision = '001_initial_migration'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Crea la tabla imagenes con todos sus campos y relaciones.
    """
    op.create_table(
        'imagenes',
        
        # Campos principales
        sa.Column('id', sa.Integer(), nullable=False, comment='Identificador único de la imagen'),
        sa.Column('usuario_id', sa.Integer(), nullable=False, comment='ID del usuario propietario de la imagen'),
        sa.Column('nombre_archivo', sa.String(length=255), nullable=False, comment='Nombre original del archivo subido'),
        sa.Column('nombre_blob', sa.String(length=255), nullable=False, comment='Nombre único del blob en Azure Storage (UUID + extensión)'),
        sa.Column('url_blob', sa.Text(), nullable=False, comment='URL completa del blob en Azure Storage'),
        sa.Column('container_name', sa.String(length=100), nullable=False, server_default='plantitas-imagenes', comment='Nombre del contenedor de Azure donde está almacenada'),
        sa.Column('content_type', sa.String(length=100), nullable=False, comment='Tipo MIME del archivo (image/jpeg, image/png, etc.)'),
        sa.Column('tamano_bytes', sa.Integer(), nullable=False, comment='Tamaño del archivo en bytes'),
        sa.Column('descripcion', sa.Text(), nullable=True, comment='Descripción opcional de la imagen'),
        
        # Campos de auditoría
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), comment='Fecha y hora de subida de la imagen'),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), comment='Fecha y hora de última actualización'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.text('FALSE'), comment='Soft delete - indica si la imagen fue eliminada lógicamente'),
        
        # Constraints
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('nombre_blob', name='uq_imagenes_nombre_blob')
    )
    
    # Crear índices para optimización
    op.create_index('ix_imagenes_id', 'imagenes', ['id'])
    op.create_index('ix_imagenes_usuario_id', 'imagenes', ['usuario_id'])
    op.create_index('ix_imagenes_nombre_blob', 'imagenes', ['nombre_blob'])
    op.create_index('idx_usuario_created', 'imagenes', ['usuario_id', 'created_at'])
    op.create_index('idx_usuario_deleted', 'imagenes', ['usuario_id', 'is_deleted'])
    op.create_index('idx_imagenes_created_at', 'imagenes', ['created_at'])


def downgrade() -> None:
    """
    Revierte la migración eliminando la tabla imagenes.
    """
    # Eliminar índices primero
    op.drop_index('idx_imagenes_created_at', table_name='imagenes')
    op.drop_index('idx_usuario_deleted', table_name='imagenes')
    op.drop_index('idx_usuario_created', table_name='imagenes')
    op.drop_index('ix_imagenes_nombre_blob', table_name='imagenes')
    op.drop_index('ix_imagenes_usuario_id', table_name='imagenes')
    op.drop_index('ix_imagenes_id', table_name='imagenes')
    
    # Eliminar tabla
    op.drop_table('imagenes')
