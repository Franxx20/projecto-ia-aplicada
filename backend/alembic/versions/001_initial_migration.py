"""Crear tabla usuarios inicial - T-002

Revision ID: 001_initial_migration
Revises: 
Create Date: 2025-10-05 12:00:00.000000
Sprint: Sprint 1 - Épica 1: Fundación de la Aplicación

Descripción:
    Migración inicial para crear la tabla de usuarios del sistema.
    Incluye campos para autenticación JWT, hashing de contraseñas con bcrypt,
    y gestión de estado de usuarios.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import func

# revision identifiers, used by Alembic.
revision = '001_initial_migration'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Crear tabla usuarios con todos los campos necesarios para autenticación.
    
    Cambios:
        - Crear tabla usuarios con campos: id, email, password_hash, nombre,
          created_at, updated_at, is_active, is_superuser
        - Crear índices para optimizar queries por email y fecha de creación
        - Crear índice compuesto para email + is_active
    """
    # Crear tabla usuarios
    op.create_table(
        'usuarios',
        # Campo ID - Primary Key
        sa.Column(
            'id', 
            sa.Integer(), 
            nullable=False,
            comment='Identificador único del usuario'
        ),
        
        # Campo Email - Único e indexado
        sa.Column(
            'email', 
            sa.String(length=255), 
            nullable=False,
            comment='Correo electrónico único del usuario'
        ),
        
        # Campo Password Hash - Bcrypt
        sa.Column(
            'password_hash', 
            sa.String(length=255), 
            nullable=False,
            comment='Contraseña hasheada con bcrypt'
        ),
        
        # Campo Nombre - Opcional
        sa.Column(
            'nombre', 
            sa.String(length=255), 
            nullable=True,
            comment='Nombre completo del usuario'
        ),
        
        # Campos de timestamps
        sa.Column(
            'created_at', 
            sa.DateTime(), 
            nullable=False,
            server_default=func.now(),
            comment='Fecha y hora de creación de la cuenta'
        ),
        sa.Column(
            'updated_at', 
            sa.DateTime(), 
            nullable=False,
            server_default=func.now(),
            onupdate=func.now(),
            comment='Fecha y hora de última actualización'
        ),
        
        # Campos de estado
        sa.Column(
            'is_active', 
            sa.Boolean(), 
            nullable=False, 
            server_default='true',
            comment='Estado de activación de la cuenta'
        ),
        sa.Column(
            'is_superuser', 
            sa.Boolean(), 
            nullable=False, 
            server_default='false',
            comment='Indica si el usuario tiene privilegios de administrador'
        ),
        
        # Constraints
        sa.PrimaryKeyConstraint('id', name='pk_usuarios'),
        sa.UniqueConstraint('email', name='uq_usuarios_email')
    )
    
    # Crear índices para optimización de queries
    op.create_index(
        'ix_usuarios_id', 
        'usuarios', 
        ['id'], 
        unique=False
    )
    op.create_index(
        'ix_usuarios_email', 
        'usuarios', 
        ['email'], 
        unique=True
    )
    op.create_index(
        'idx_email_active', 
        'usuarios', 
        ['email', 'is_active'], 
        unique=False
    )
    op.create_index(
        'idx_created_at', 
        'usuarios', 
        ['created_at'], 
        unique=False
    )


def downgrade() -> None:
    """
    Eliminar tabla usuarios y todos sus índices.
    
    ADVERTENCIA: Esta operación eliminará TODOS los datos de usuarios.
    """
    # Eliminar índices en orden inverso
    op.drop_index('idx_created_at', table_name='usuarios')
    op.drop_index('idx_email_active', table_name='usuarios')
    op.drop_index('ix_usuarios_email', table_name='usuarios')
    op.drop_index('ix_usuarios_id', table_name='usuarios')
    
    # Eliminar tabla
    op.drop_table('usuarios')