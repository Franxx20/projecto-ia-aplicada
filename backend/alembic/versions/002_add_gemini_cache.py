"""Add Gemini response cache table

Revision ID: 002_add_gemini_cache
Revises: 001_initial_schema
Create Date: 2025-11-14 00:00:00.000000

Descripción:
    Agrega tabla para caché de respuestas de Gemini AI:
    - gemini_response_cache: Almacena respuestas frecuentes para reducir costos de API
    
    Beneficios:
    - Reduce costos de API reutilizando respuestas comunes
    - Mejora tiempos de respuesta (sin llamada a API)
    - Tracking de ahorro de tokens
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import func

# revision identifiers, used by Alembic.
revision = '002_add_gemini_cache'
down_revision = '001_initial_schema'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Crea la tabla gemini_response_cache con sus índices.
    """
    
    # ============================================================================
    # TABLA: gemini_response_cache
    # ============================================================================
    op.create_table(
        'gemini_response_cache',
        sa.Column('id', sa.Integer(), nullable=False, comment='Identificador único del registro de caché'),
        sa.Column('query_hash', sa.String(length=64), nullable=False, comment='Hash SHA-256 de la pregunta + contexto para identificación única'),
        sa.Column('pregunta', sa.Text(), nullable=False, comment='Pregunta original del usuario'),
        sa.Column('contexto_resumido', sa.Text(), nullable=True, comment='Resumen del contexto usado (especie de planta, problema común, etc.)'),
        sa.Column('respuesta', sa.Text(), nullable=False, comment='Respuesta cacheada de Gemini AI'),
        sa.Column('hits', sa.Integer(), nullable=False, server_default='0', comment='Número de veces que se ha reutilizado este caché'),
        sa.Column('tokens_ahorrados', sa.Integer(), nullable=False, server_default='0', comment='Total de tokens ahorrados con este caché'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=func.now(), comment='Fecha y hora de creación del caché'),
        sa.Column('last_used_at', sa.DateTime(), nullable=False, server_default=func.now(), comment='Última vez que se usó este caché'),
        sa.Column('expires_at', sa.DateTime(), nullable=True, comment='Fecha de expiración del caché (NULL = nunca expira)'),
        sa.PrimaryKeyConstraint('id', name='pk_gemini_response_cache'),
        sa.UniqueConstraint('query_hash', name='uq_gemini_cache_query_hash')
    )
    
    # Índices para búsquedas eficientes
    op.create_index(
        'idx_query_hash_active',
        'gemini_response_cache',
        ['query_hash', 'expires_at'],
        unique=False
    )
    
    op.create_index(
        'idx_created_hits',
        'gemini_response_cache',
        ['created_at', 'hits'],
        unique=False
    )
    
    op.create_index(
        'idx_gemini_cache_created_at',
        'gemini_response_cache',
        ['created_at'],
        unique=False
    )
    
    op.create_index(
        'idx_gemini_cache_expires_at',
        'gemini_response_cache',
        ['expires_at'],
        unique=False
    )


def downgrade() -> None:
    """
    Elimina la tabla gemini_response_cache y sus índices.
    """
    # Eliminar índices
    op.drop_index('idx_gemini_cache_expires_at', table_name='gemini_response_cache')
    op.drop_index('idx_gemini_cache_created_at', table_name='gemini_response_cache')
    op.drop_index('idx_created_hits', table_name='gemini_response_cache')
    op.drop_index('idx_query_hash_active', table_name='gemini_response_cache')
    
    # Eliminar tabla
    op.drop_table('gemini_response_cache')
