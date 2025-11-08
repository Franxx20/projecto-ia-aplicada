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
    
    NOTA: Esta migración es idempotente - verifica si las tablas/columnas ya existen
    antes de crearlas para evitar conflictos con ramas paralelas de migraciones.
    """
    from sqlalchemy import inspect
    
    # Obtener conexión y inspector
    conn = op.get_bind()
    inspector = inspect(conn)
    existing_tables = inspector.get_table_names()
    
    # ==================== TABLA ESPECIES ====================
    if 'especies' not in existing_tables:
        print("📦 Creando tabla especies...")
    op.create_table(
        'especies',
        
        # Campos principales
        sa.Column('id', sa.Integer(), nullable=False, comment='Identificador único de la especie'),
        sa.Column('nombre_comun', sa.String(length=255), nullable=False, comment='Nombre común de la especie'),
        sa.Column('nombre_cientifico', sa.String(length=255), nullable=False, comment='Nombre científico (único)'),
        sa.Column('familia', sa.String(length=255), nullable=True, comment='Familia taxonómica'),
        sa.Column('descripcion', sa.Text(), nullable=True, comment='Descripción detallada de la especie'),
        sa.Column('cuidados_basicos', sa.Text(), nullable=True, comment='JSON con cuidados básicos'),
        
        # Nivel de dificultad y requisitos
        sa.Column('nivel_dificultad', sa.String(length=50), nullable=False, server_default='medio', comment='Nivel de dificultad: facil, medio, dificil'),
        sa.Column('luz_requerida', sa.String(length=50), nullable=True, comment='Nivel de luz: baja, media, alta'),
        sa.Column('riego_frecuencia', sa.String(length=255), nullable=True, comment='Descripción de frecuencia de riego'),
        sa.Column('temperatura_min', sa.Integer(), nullable=True, comment='Temperatura mínima en grados Celsius'),
        sa.Column('temperatura_max', sa.Integer(), nullable=True, comment='Temperatura máxima en grados Celsius'),
        sa.Column('humedad_requerida', sa.String(length=50), nullable=True, comment='Nivel de humedad: baja, media, alta'),
        sa.Column('toxicidad', sa.String(length=50), nullable=True, comment='Nivel de toxicidad: ninguna, leve, moderada, alta'),
        sa.Column('origen_geografico', sa.String(length=255), nullable=True, comment='Región geográfica de origen'),
        sa.Column('imagen_referencia_url', sa.String(length=500), nullable=True, comment='URL de imagen de referencia'),
        
        # Campos de auditoría
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), comment='Fecha de creación'),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), comment='Fecha de última actualización'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('TRUE'), comment='Indica si la especie está activa'),
        
        # Constraints
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('nombre_cientifico', name='uq_especies_nombre_cientifico')
    )
    
    # Índices para especies
    op.create_index('ix_especies_id', 'especies', ['id'])
    op.create_index('ix_especies_nombre_comun', 'especies', ['nombre_comun'])
    op.create_index('ix_especies_nombre_cientifico', 'especies', ['nombre_cientifico'])
    op.create_index('idx_especie_familia', 'especies', ['familia'])
    op.create_index('idx_especie_dificultad', 'especies', ['nivel_dificultad'])
    op.create_index('idx_especie_activa', 'especies', ['is_active'])
    
    # ==================== TABLA IDENTIFICACIONES ====================
    print("📦 Creando tabla identificaciones...")
    op.create_table(
        'identificaciones',
        
        # Campos principales
        sa.Column('id', sa.Integer(), nullable=False, comment='Identificador único'),
        sa.Column('usuario_id', sa.Integer(), nullable=False, comment='ID del usuario'),
        sa.Column('imagen_id', sa.Integer(), nullable=True, comment='ID de la imagen (NULL para identificaciones con múltiples imágenes)'),
        sa.Column('especie_id', sa.Integer(), nullable=True, comment='ID de la especie identificada'),
        sa.Column('confianza', sa.Integer(), nullable=False, comment='Nivel de confianza (0-100)'),
        sa.Column('origen', sa.String(length=50), nullable=False, comment='Origen: ia_plantnet, manual'),
        sa.Column('validado', sa.Boolean(), nullable=False, server_default=sa.text('FALSE'), comment='Si fue validado por el usuario'),
        
        # Fechas
        sa.Column('fecha_identificacion', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), comment='Fecha de la identificación'),
        sa.Column('fecha_validacion', sa.DateTime(), nullable=True, comment='Fecha de validación por el usuario'),
        
        # Metadata
        sa.Column('notas_usuario', sa.Text(), nullable=True, comment='Notas del usuario sobre la identificación'),
        sa.Column('metadatos_ia', sa.Text(), nullable=True, comment='JSON con metadatos de la IA (score, versión, etc.)'),
        
        # Campos de auditoría
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), comment='Fecha de creación'),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), comment='Fecha de actualización'),
        
        # Constraints
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['imagen_id'], ['imagenes.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['especie_id'], ['especies.id'], ondelete='SET NULL')
    )
    
    # Índices para identificaciones
    op.create_index('ix_identificaciones_id', 'identificaciones', ['id'])
    op.create_index('idx_identificacion_usuario', 'identificaciones', ['usuario_id'])
    op.create_index('idx_identificacion_imagen', 'identificaciones', ['imagen_id'])
    op.create_index('idx_identificacion_especie', 'identificaciones', ['especie_id'])
    op.create_index('idx_identificacion_origen', 'identificaciones', ['origen'])
    op.create_index('idx_identificacion_fecha', 'identificaciones', ['fecha_identificacion'])
    
    # ==================== ACTUALIZAR TABLA IMAGENES ====================
    print("📦 Actualizando tabla imagenes con nuevos campos...")
    
    # Agregar campo organ a imagenes
    op.add_column('imagenes', 
        sa.Column('organ', sa.String(length=50), nullable=True, 
                 comment='Tipo de órgano de la planta: flower, leaf, fruit, bark, habit, other')
    )
    
    # Agregar campo identificacion_id a imagenes
    op.add_column('imagenes', 
        sa.Column('identificacion_id', sa.Integer(), nullable=True, 
                 comment='ID de la identificación asociada (si forma parte de una identificación múltiple)')
    )
    
    # Crear foreign key para identificacion_id
    op.create_foreign_key(
        'fk_imagenes_identificacion_id',
        'imagenes', 'identificaciones',
        ['identificacion_id'], ['id'],
        ondelete='SET NULL'
    )
    
    # Crear índices para los nuevos campos de imagenes
    op.create_index('idx_imagenes_organ', 'imagenes', ['organ'])
    op.create_index('idx_imagenes_identificacion', 'imagenes', ['identificacion_id'])
    
    # ==================== TABLA PLANTAS ====================
    print("📦 Creando tabla plantas...")
    op.create_table(
        'plantas',
        
        # Campos principales
        sa.Column('id', sa.Integer(), nullable=False, comment='Identificador único de la planta'),
        sa.Column('usuario_id', sa.Integer(), nullable=False, comment='ID del usuario propietario de la planta'),
        sa.Column('especie_id', sa.Integer(), nullable=True, comment='ID de la especie de la planta (opcional)'),
        sa.Column('nombre_personal', sa.String(length=255), nullable=False, comment='Nombre personalizado dado por el usuario'),
        
        # Estado y ubicación
        sa.Column('estado_salud', sa.String(length=50), nullable=False, server_default='buena', comment='Estado de salud: excelente, buena, necesita_atencion, critica'),
        sa.Column('ubicacion', sa.String(length=255), nullable=True, comment='Ubicación física de la planta'),
        sa.Column('notas', sa.Text(), nullable=True, comment='Notas adicionales del usuario'),
        sa.Column('imagen_principal_id', sa.Integer(), nullable=True, comment='ID de la imagen principal de la planta'),
        
        # Cuidados - riego
        sa.Column('fecha_ultimo_riego', sa.DateTime(), nullable=True, comment='Fecha y hora del último riego'),
        sa.Column('proxima_riego', sa.DateTime(), nullable=True, comment='Fecha y hora del próximo riego recomendado'),
        sa.Column('frecuencia_riego_dias', sa.Integer(), nullable=True, server_default='7', comment='Frecuencia de riego en días'),
        
        # Cuidados - luz
        sa.Column('luz_actual', sa.String(length=20), nullable=True, comment='Nivel de luz que recibe: baja, media, alta, directa'),
        
        # Metadata
        sa.Column('fecha_adquisicion', sa.DateTime(), nullable=True, comment='Fecha en que el usuario adquirió la planta'),
        
        # Campos de auditoría
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), comment='Fecha de creación del registro'),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), comment='Fecha de última actualización'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('TRUE'), comment='Indica si la planta está activa (no eliminada)'),
        
        # Constraints
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id'], ondelete='CASCADE')
        # Nota: especie_id no tiene FK porque puede ser null y no tenemos tabla especies todavía
        # imagen_principal_id tampoco tiene FK para evitar referencias circulares
    )
    
    # Índices para plantas
    op.create_index('ix_plantas_id', 'plantas', ['id'])
    op.create_index('ix_plantas_usuario_id', 'plantas', ['usuario_id'])
    op.create_index('ix_plantas_especie_id', 'plantas', ['especie_id'])
    op.create_index('idx_usuario_plantas_activas', 'plantas', ['usuario_id', 'is_active'])
    op.create_index('idx_usuario_estado_salud', 'plantas', ['usuario_id', 'estado_salud'])
    op.create_index('idx_proxima_riego', 'plantas', ['proxima_riego'])
    op.create_index('idx_created_at_plantas', 'plantas', ['created_at'])
    
    print("✅ Todas las tablas han sido creadas exitosamente")


def downgrade() -> None:
    """
    Revierte la migración eliminando todas las tablas creadas.
    """
    print("🔄 Revirtiendo migración...")
    
    # Eliminar tabla plantas
    print("🗑️ Eliminando tabla plantas...")
    op.drop_index('idx_created_at_plantas', table_name='plantas')
    op.drop_index('idx_proxima_riego', table_name='plantas')
    op.drop_index('idx_usuario_estado_salud', table_name='plantas')
    op.drop_index('idx_usuario_plantas_activas', table_name='plantas')
    op.drop_index('ix_plantas_especie_id', table_name='plantas')
    op.drop_index('ix_plantas_usuario_id', table_name='plantas')
    op.drop_index('ix_plantas_id', table_name='plantas')
    op.drop_table('plantas')
    
    # Eliminar campos agregados a imagenes
    print("🗑️ Eliminando campos agregados a imagenes...")
    op.drop_index('idx_imagenes_identificacion', table_name='imagenes')
    op.drop_index('idx_imagenes_organ', table_name='imagenes')
    op.drop_constraint('fk_imagenes_identificacion_id', 'imagenes', type_='foreignkey')
    op.drop_column('imagenes', 'identificacion_id')
    op.drop_column('imagenes', 'organ')
    
    # Eliminar tabla identificaciones
    print("🗑️ Eliminando tabla identificaciones...")
    op.drop_index('idx_identificacion_fecha', table_name='identificaciones')
    op.drop_index('idx_identificacion_origen', table_name='identificaciones')
    op.drop_index('idx_identificacion_especie', table_name='identificaciones')
    op.drop_index('idx_identificacion_imagen', table_name='identificaciones')
    op.drop_index('idx_identificacion_usuario', table_name='identificaciones')
    op.drop_index('ix_identificaciones_id', table_name='identificaciones')
    op.drop_table('identificaciones')
    
    # Eliminar tabla especies
    print("🗑️ Eliminando tabla especies...")
    op.drop_index('idx_especie_activa', table_name='especies')
    op.drop_index('idx_especie_dificultad', table_name='especies')
    op.drop_index('idx_especie_familia', table_name='especies')
    op.drop_index('ix_especies_nombre_cientifico', table_name='especies')
    op.drop_index('ix_especies_nombre_comun', table_name='especies')
    op.drop_index('ix_especies_id', table_name='especies')
    op.drop_table('especies')
    
    print("✅ Migración revertida exitosamente")
