"""
Agregar tablas completas: Especies, Identificaciones, Plantas y actualizar Imagenes

Migración para completar el modelo de datos del sistema Asistente Plantitas.
Agrega las tablas faltantes y actualiza la tabla imagenes con campos necesarios.

Revision ID: 003_add_complete_models
Revises: 002_add_imagenes_table
Create Date: 2025-11-03

Sprint: Sprint 1-2 - Consolidación de modelos
"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision = '003_add_complete_models'
down_revision = '002_add_imagenes_table'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Crea las tablas especies, identificaciones, plantas y actualiza imagenes.
    NOTA: Esta migración se omite porque las tablas ya fueron creadas en migraciones posteriores (778b31b200bd, 040ab409674b, etc.)
    """
    
    # Skip - Las tablas ya existen en migraciones más recientes
    print("⏭️  Saltando migración 003 - Las tablas ya fueron creadas en migraciones posteriores")
    pass


def downgrade() -> None:
    """
    Revierte la migración (skip también en downgrade)
    """
    print("⏭️  Saltando downgrade de migración 003")
    pass
