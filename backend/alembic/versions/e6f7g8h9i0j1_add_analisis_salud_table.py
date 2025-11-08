"""add analisis_salud table for health check feature

Revision ID: e6f7g8h9i0j1
Revises: d5e6f7g8h9i0
Create Date: 2025-11-08 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import Index


# revision identifiers, used by Alembic.
revision: str = 'e6f7g8h9i0j1'
down_revision: Union[str, None] = 'd5e6f7g8h9i0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Crea la tabla analisis_salud para almacenar análisis de salud de plantas con Gemini AI.
    
    Esta tabla registra:
    - Diagnósticos de salud realizados por Gemini AI
    - Problemas detectados en las plantas
    - Recomendaciones de cuidado
    - Metadatos del análisis (modelo usado, tiempo, confianza)
    """
    op.create_table(
        'analisis_salud',
        # Primary Key
        sa.Column('id', sa.Integer(), nullable=False, comment='Identificador único del análisis'),
        
        # Foreign Keys
        sa.Column('planta_id', sa.Integer(), nullable=False, comment='ID de la planta analizada'),
        sa.Column('usuario_id', sa.Integer(), nullable=False, comment='ID del usuario que solicitó el análisis'),
        sa.Column('imagen_id', sa.Integer(), nullable=True, comment='ID de la imagen analizada (opcional)'),
        
        # Datos del análisis
        sa.Column('estado_salud', sa.String(length=50), nullable=False, 
                  comment='Estado: excelente, saludable, necesita_atencion, enfermedad, plaga, critica'),
        sa.Column('confianza', sa.Integer(), nullable=False, 
                  comment='Nivel de confianza del diagnóstico (0-100)'),
        sa.Column('resumen_diagnostico', sa.Text(), nullable=False, 
                  comment='Resumen del diagnóstico en lenguaje natural'),
        sa.Column('diagnostico_detallado', sa.Text(), nullable=True, 
                  comment='Diagnóstico técnico detallado (opcional)'),
        sa.Column('problemas_detectados', sa.Text(), nullable=False, server_default='[]',
                  comment='JSON con lista de problemas detectados'),
        sa.Column('recomendaciones', sa.Text(), nullable=False, server_default='[]',
                  comment='JSON con lista de recomendaciones'),
        
        # Metadatos del análisis
        sa.Column('modelo_ia_usado', sa.String(length=100), nullable=False, 
                  comment='Modelo de IA usado (ej: gemini-2.5-flash, gemini-2.5-pro)'),
        sa.Column('tiempo_analisis_ms', sa.Integer(), nullable=False, 
                  comment='Tiempo de análisis en milisegundos'),
        sa.Column('version_prompt', sa.String(length=20), nullable=False, server_default='v1',
                  comment='Versión del prompt usado'),
        sa.Column('con_imagen', sa.Boolean(), nullable=False, server_default=sa.false(),
                  comment='Indica si el análisis incluyó imagen'),
        
        # Timestamps
        sa.Column('fecha_analisis', sa.DateTime(), nullable=False, server_default=sa.func.now(),
                  comment='Fecha y hora del análisis'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now(),
                  comment='Fecha de creación del registro'),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now(),
                  comment='Fecha de última actualización'),
        
        # Constraints
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['planta_id'], ['plantas.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['imagen_id'], ['imagenes.id'], ondelete='SET NULL'),
    )
    
    # Crear índices para optimización de queries
    op.create_index('idx_analisis_planta_fecha', 'analisis_salud', ['planta_id', 'fecha_analisis'])
    op.create_index('idx_analisis_usuario_fecha', 'analisis_salud', ['usuario_id', 'fecha_analisis'])
    op.create_index('idx_analisis_estado', 'analisis_salud', ['estado_salud'])
    op.create_index('idx_analisis_planta_estado', 'analisis_salud', ['planta_id', 'estado_salud'])
    
    # Índices simples (ya se crean automáticamente en la FK, pero los declaramos explícitamente)
    op.create_index(op.f('ix_analisis_salud_id'), 'analisis_salud', ['id'], unique=False)
    op.create_index(op.f('ix_analisis_salud_planta_id'), 'analisis_salud', ['planta_id'], unique=False)
    op.create_index(op.f('ix_analisis_salud_usuario_id'), 'analisis_salud', ['usuario_id'], unique=False)
    op.create_index(op.f('ix_analisis_salud_imagen_id'), 'analisis_salud', ['imagen_id'], unique=False)
    op.create_index(op.f('ix_analisis_salud_fecha_analisis'), 'analisis_salud', ['fecha_analisis'], unique=False)


def downgrade() -> None:
    """
    Elimina la tabla analisis_salud y todos sus índices.
    """
    # Eliminar índices
    op.drop_index(op.f('ix_analisis_salud_fecha_analisis'), table_name='analisis_salud')
    op.drop_index(op.f('ix_analisis_salud_imagen_id'), table_name='analisis_salud')
    op.drop_index(op.f('ix_analisis_salud_usuario_id'), table_name='analisis_salud')
    op.drop_index(op.f('ix_analisis_salud_planta_id'), table_name='analisis_salud')
    op.drop_index(op.f('ix_analisis_salud_id'), table_name='analisis_salud')
    op.drop_index('idx_analisis_planta_estado', table_name='analisis_salud')
    op.drop_index('idx_analisis_estado', table_name='analisis_salud')
    op.drop_index('idx_analisis_usuario_fecha', table_name='analisis_salud')
    op.drop_index('idx_analisis_planta_fecha', table_name='analisis_salud')
    
    # Eliminar tabla
    op.drop_table('analisis_salud')
