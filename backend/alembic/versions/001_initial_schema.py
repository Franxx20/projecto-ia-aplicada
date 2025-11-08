"""Initial database schema - Consolidated migration

Revision ID: 001_initial_schema
Revises: 
Create Date: 2025-11-08 00:00:00.000000

Descripción:
    Migración inicial consolidada que crea todas las tablas del sistema:
    - usuarios: Gestión de usuarios y autenticación
    - imagenes: Almacenamiento de imágenes en Azure Blob Storage
    - especies: Catálogo de especies de plantas
    - identificaciones: Identificaciones de plantas por IA
    - plantas: Plantas del usuario
    - analisis_salud: Análisis de salud de plantas con IA
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import func

# revision identifiers, used by Alembic.
revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Crea todas las tablas del sistema con sus relaciones e índices.
    """
    
    # ============================================================================
    # TABLA: usuarios
    # ============================================================================
    op.create_table(
        'usuarios',
        sa.Column('id', sa.Integer(), nullable=False, comment='Identificador único del usuario'),
        sa.Column('email', sa.String(length=255), nullable=False, comment='Correo electrónico único del usuario'),
        sa.Column('password_hash', sa.String(length=255), nullable=False, comment='Contraseña hasheada con bcrypt'),
        sa.Column('nombre', sa.String(length=255), nullable=True, comment='Nombre completo del usuario'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=func.now(), comment='Fecha y hora de creación de la cuenta'),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=func.now(), comment='Fecha y hora de última actualización'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true', comment='Estado de activación de la cuenta'),
        sa.Column('is_superuser', sa.Boolean(), nullable=False, server_default='false', comment='Indica si el usuario tiene privilegios de administrador'),
        sa.PrimaryKeyConstraint('id', name='pk_usuarios'),
        sa.UniqueConstraint('email', name='uq_usuarios_email')
    )
    
    # Índices para usuarios
    op.create_index('ix_usuarios_id', 'usuarios', ['id'], unique=False)
    op.create_index('ix_usuarios_email', 'usuarios', ['email'], unique=True)
    op.create_index('idx_email_active', 'usuarios', ['email', 'is_active'], unique=False)
    op.create_index('idx_created_at', 'usuarios', ['created_at'], unique=False)
    
    # ============================================================================
    # TABLA: imagenes
    # ============================================================================
    op.create_table(
        'imagenes',
        sa.Column('id', sa.Integer(), nullable=False, comment='Identificador único de la imagen'),
        sa.Column('usuario_id', sa.Integer(), nullable=False, comment='ID del usuario propietario de la imagen'),
        sa.Column('nombre_archivo', sa.String(length=255), nullable=False, comment='Nombre original del archivo subido'),
        sa.Column('nombre_blob', sa.String(length=255), nullable=False, comment='Nombre único del blob en Azure Storage (UUID + extensión)'),
        sa.Column('url_blob', sa.Text(), nullable=False, comment='URL completa del blob en Azure Storage'),
        sa.Column('container_name', sa.String(length=100), nullable=False, server_default='plantitas-imagenes', comment='Nombre del contenedor de Azure donde está almacenada'),
        sa.Column('content_type', sa.String(length=100), nullable=False, comment='Tipo MIME del archivo (image/jpeg, image/png, etc.)'),
        sa.Column('tamano_bytes', sa.Integer(), nullable=False, comment='Tamaño del archivo en bytes'),
        sa.Column('descripcion', sa.Text(), nullable=True, comment='Descripción opcional de la imagen'),
        sa.Column('organ', sa.String(length=50), nullable=True, comment='Tipo de órgano de la planta: flower, leaf, fruit, bark, habit, other'),
        sa.Column('identificacion_id', sa.Integer(), nullable=True, comment='ID de la identificación asociada (si forma parte de una identificación múltiple)'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), comment='Fecha y hora de subida de la imagen'),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), comment='Fecha y hora de última actualización'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.text('FALSE'), comment='Soft delete - indica si la imagen fue eliminada lógicamente'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('nombre_blob', name='uq_imagenes_nombre_blob')
    )
    
    # Índices para imagenes (nota: identificacion_id FK se crea después de crear tabla identificaciones)
    op.create_index('ix_imagenes_id', 'imagenes', ['id'], unique=False)
    op.create_index('ix_imagenes_usuario_id', 'imagenes', ['usuario_id'], unique=False)
    op.create_index('ix_imagenes_nombre_blob', 'imagenes', ['nombre_blob'], unique=True)
    op.create_index('idx_usuario_created', 'imagenes', ['usuario_id', 'created_at'], unique=False)
    op.create_index('idx_usuario_deleted', 'imagenes', ['usuario_id', 'is_deleted'], unique=False)
    op.create_index('idx_imagenes_created_at', 'imagenes', ['created_at'], unique=False)
    op.create_index('idx_imagenes_organ', 'imagenes', ['organ'], unique=False)
    
    # ============================================================================
    # TABLA: especies
    # ============================================================================
    op.create_table(
        'especies',
        sa.Column('id', sa.Integer(), nullable=False, comment='Identificador único de la especie'),
        sa.Column('nombre_comun', sa.String(length=255), nullable=False, comment='Nombre común de la planta'),
        sa.Column('nombre_cientifico', sa.String(length=255), nullable=False, comment='Nombre científico de la especie (único)'),
        sa.Column('familia', sa.String(length=100), nullable=True, comment='Familia botánica'),
        sa.Column('descripcion', sa.Text(), nullable=True, comment='Descripción general de la planta'),
        sa.Column('cuidados_basicos', sa.Text(), nullable=True, comment='Instrucciones básicas de cuidado en formato JSON'),
        sa.Column('nivel_dificultad', sa.String(length=20), nullable=False, comment='Nivel de dificultad: facil, medio, dificil'),
        sa.Column('luz_requerida', sa.String(length=20), nullable=True, comment='Requerimientos de luz: baja, media, alta, directa'),
        sa.Column('riego_frecuencia', sa.String(length=100), nullable=True, comment='Frecuencia de riego recomendada'),
        sa.Column('temperatura_min', sa.Integer(), nullable=True, comment='Temperatura mínima tolerable en °C'),
        sa.Column('temperatura_max', sa.Integer(), nullable=True, comment='Temperatura máxima tolerable en °C'),
        sa.Column('humedad_requerida', sa.String(length=20), nullable=True, comment='Nivel de humedad: baja, media, alta'),
        sa.Column('toxicidad', sa.String(length=20), nullable=True, comment='Nivel de toxicidad: no_toxica, leve, moderada, alta'),
        sa.Column('origen_geografico', sa.String(length=255), nullable=True, comment='Región de origen de la especie'),
        sa.Column('imagen_referencia_url', sa.String(length=500), nullable=True, comment='URL de imagen de referencia de la especie'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=func.now(), comment='Fecha de creación del registro'),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=func.now(), comment='Fecha de última actualización'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true', comment='Indica si la especie está activa en el catálogo'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Índices para especies
    op.create_index('ix_especies_id', 'especies', ['id'], unique=False)
    op.create_index('ix_especies_nombre_comun', 'especies', ['nombre_comun'], unique=False)
    op.create_index('ix_especies_nombre_cientifico', 'especies', ['nombre_cientifico'], unique=True)
    op.create_index('ix_especies_familia', 'especies', ['familia'], unique=False)
    op.create_index('idx_especies_active', 'especies', ['is_active'], unique=False)
    op.create_index('idx_nivel_dificultad', 'especies', ['nivel_dificultad'], unique=False)
    
    # ============================================================================
    # TABLA: identificaciones
    # ============================================================================
    op.create_table(
        'identificaciones',
        sa.Column('id', sa.Integer(), nullable=False, comment='Identificador único de la identificación'),
        sa.Column('usuario_id', sa.Integer(), nullable=False, comment='ID del usuario que realizó/recibió la identificación'),
        sa.Column('imagen_id', sa.Integer(), nullable=True, comment='ID de la imagen (NULL para identificaciones con múltiples imágenes)'),
        sa.Column('especie_id', sa.Integer(), nullable=False, comment='ID de la especie identificada'),
        sa.Column('confianza', sa.Integer(), nullable=False, comment='Nivel de confianza de la identificación (0-100)'),
        sa.Column('origen', sa.String(length=50), nullable=False, comment='Origen: ia_plantnet, ia_local, manual'),
        sa.Column('validado', sa.Boolean(), nullable=False, server_default='false', comment='Indica si fue validada por el usuario'),
        sa.Column('notas_usuario', sa.Text(), nullable=True, comment='Notas adicionales del usuario'),
        sa.Column('metadatos_ia', sa.Text(), nullable=True, comment='Metadatos del proceso de IA en formato JSON'),
        sa.Column('fecha_identificacion', sa.DateTime(), nullable=False, server_default=func.now(), comment='Fecha y hora de la identificación'),
        sa.Column('fecha_validacion', sa.DateTime(), nullable=True, comment='Fecha y hora de validación por usuario'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=func.now(), comment='Fecha de creación del registro'),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=func.now(), comment='Fecha de última actualización'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['especie_id'], ['especies.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['imagen_id'], ['imagenes.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id'], ondelete='CASCADE')
    )
    
    # Índices para identificaciones
    op.create_index('ix_identificaciones_id', 'identificaciones', ['id'], unique=False)
    op.create_index('ix_identificaciones_usuario_id', 'identificaciones', ['usuario_id'], unique=False)
    op.create_index('ix_identificaciones_imagen_id', 'identificaciones', ['imagen_id'], unique=False)
    op.create_index('ix_identificaciones_especie_id', 'identificaciones', ['especie_id'], unique=False)
    op.create_index('idx_usuario_identificacion', 'identificaciones', ['usuario_id', 'fecha_identificacion'], unique=False)
    op.create_index('idx_validado', 'identificaciones', ['validado'], unique=False)
    op.create_index('idx_origen', 'identificaciones', ['origen'], unique=False)
    
    # Ahora crear la FK de imagenes.identificacion_id hacia identificaciones
    op.create_foreign_key(
        'fk_imagenes_identificacion_id',
        'imagenes',
        'identificaciones',
        ['identificacion_id'],
        ['id'],
        ondelete='SET NULL'
    )
    op.create_index('idx_imagenes_identificacion', 'imagenes', ['identificacion_id'], unique=False)
    
    # ============================================================================
    # TABLA: plantas
    # ============================================================================
    op.create_table(
        'plantas',
        sa.Column('id', sa.Integer(), nullable=False, comment='Identificador único de la planta'),
        sa.Column('usuario_id', sa.Integer(), nullable=False, comment='ID del usuario propietario de la planta'),
        sa.Column('especie_id', sa.Integer(), nullable=True, comment='ID de la especie de la planta (opcional)'),
        sa.Column('nombre_personal', sa.String(length=255), nullable=False, comment='Nombre personalizado dado por el usuario'),
        sa.Column('estado_salud', sa.String(length=50), nullable=False, server_default='buena', comment='Estado de salud: excelente, saludable, necesita_atencion, enfermedad, plaga, critica'),
        sa.Column('ubicacion', sa.String(length=255), nullable=True, comment='Ubicación física de la planta'),
        sa.Column('notas', sa.Text(), nullable=True, comment='Notas adicionales del usuario'),
        sa.Column('imagen_principal_id', sa.Integer(), nullable=True, comment='ID de la imagen principal de la planta'),
        sa.Column('fecha_ultimo_riego', sa.DateTime(), nullable=True, comment='Fecha y hora del último riego'),
        sa.Column('proxima_riego', sa.DateTime(), nullable=True, comment='Fecha y hora del próximo riego recomendado'),
        sa.Column('frecuencia_riego_dias', sa.Integer(), nullable=True, comment='Frecuencia de riego en días'),
        sa.Column('luz_actual', sa.String(length=20), nullable=True, comment='Nivel de luz que recibe: baja, media, alta, directa'),
        sa.Column('fecha_adquisicion', sa.DateTime(), nullable=True, comment='Fecha en que el usuario adquirió la planta'),
        sa.Column('es_favorita', sa.Boolean(), nullable=False, server_default='false', comment='Indica si la planta ha sido marcada como favorita por el usuario'),
        sa.Column('fue_regada_hoy', sa.Boolean(), nullable=False, server_default='false', comment='Indica si la planta fue regada hoy'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=func.now(), comment='Fecha de creación del registro'),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=func.now(), comment='Fecha de última actualización'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true', comment='Indica si la planta está activa (no eliminada)'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['especie_id'], ['especies.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['imagen_principal_id'], ['imagenes.id'], ondelete='SET NULL')
    )
    
    # Índices para plantas
    op.create_index('ix_plantas_id', 'plantas', ['id'], unique=False)
    op.create_index('ix_plantas_usuario_id', 'plantas', ['usuario_id'], unique=False)
    op.create_index('ix_plantas_especie_id', 'plantas', ['especie_id'], unique=False)
    op.create_index('idx_usuario_plantas_activas', 'plantas', ['usuario_id', 'is_active'], unique=False)
    op.create_index('idx_usuario_estado_salud', 'plantas', ['usuario_id', 'estado_salud'], unique=False)
    op.create_index('idx_proxima_riego', 'plantas', ['proxima_riego'], unique=False)
    op.create_index('idx_created_at_plantas', 'plantas', ['created_at'], unique=False)
    op.create_index('idx_usuario_favoritas', 'plantas', ['usuario_id', 'es_favorita'], unique=False)
    
    # ============================================================================
    # TABLA: analisis_salud
    # ============================================================================
    op.create_table(
        'analisis_salud',
        sa.Column('id', sa.Integer(), nullable=False, comment='Identificador único del análisis'),
        sa.Column('planta_id', sa.Integer(), nullable=False, comment='ID de la planta analizada'),
        sa.Column('usuario_id', sa.Integer(), nullable=False, comment='ID del usuario que solicitó el análisis'),
        sa.Column('imagen_id', sa.Integer(), nullable=True, comment='ID de la imagen analizada (opcional)'),
        sa.Column('estado_salud', sa.String(length=50), nullable=False, comment='Estado: excelente, saludable, necesita_atencion, enfermedad, plaga, critica'),
        sa.Column('confianza', sa.Integer(), nullable=False, comment='Nivel de confianza del diagnóstico (0-100)'),
        sa.Column('resumen_diagnostico', sa.Text(), nullable=False, comment='Resumen del diagnóstico en lenguaje natural'),
        sa.Column('diagnostico_detallado', sa.Text(), nullable=True, comment='Diagnóstico técnico detallado (opcional)'),
        sa.Column('problemas_detectados', sa.Text(), nullable=False, server_default='[]', comment='JSON con lista de problemas detectados'),
        sa.Column('recomendaciones', sa.Text(), nullable=False, server_default='[]', comment='JSON con lista de recomendaciones'),
        sa.Column('modelo_ia_usado', sa.String(length=100), nullable=False, comment='Modelo de IA usado (ej: gemini-2.5-flash, gemini-2.5-pro)'),
        sa.Column('tiempo_analisis_ms', sa.Integer(), nullable=False, comment='Tiempo de análisis en milisegundos'),
        sa.Column('version_prompt', sa.String(length=20), nullable=False, server_default='v1', comment='Versión del prompt usado'),
        sa.Column('con_imagen', sa.Boolean(), nullable=False, server_default=sa.false(), comment='Indica si el análisis incluyó imagen'),
        sa.Column('fecha_analisis', sa.DateTime(), nullable=False, server_default=func.now(), comment='Fecha y hora del análisis'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=func.now(), comment='Fecha de creación del registro'),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=func.now(), comment='Fecha de última actualización'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['planta_id'], ['plantas.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['imagen_id'], ['imagenes.id'], ondelete='SET NULL')
    )
    
    # Índices para analisis_salud
    op.create_index('ix_analisis_salud_id', 'analisis_salud', ['id'], unique=False)
    op.create_index('ix_analisis_salud_planta_id', 'analisis_salud', ['planta_id'], unique=False)
    op.create_index('ix_analisis_salud_usuario_id', 'analisis_salud', ['usuario_id'], unique=False)
    op.create_index('ix_analisis_salud_imagen_id', 'analisis_salud', ['imagen_id'], unique=False)
    op.create_index('ix_analisis_salud_fecha_analisis', 'analisis_salud', ['fecha_analisis'], unique=False)
    op.create_index('idx_analisis_planta_fecha', 'analisis_salud', ['planta_id', 'fecha_analisis'], unique=False)
    op.create_index('idx_analisis_usuario_fecha', 'analisis_salud', ['usuario_id', 'fecha_analisis'], unique=False)
    op.create_index('idx_analisis_estado', 'analisis_salud', ['estado_salud'], unique=False)
    op.create_index('idx_analisis_planta_estado', 'analisis_salud', ['planta_id', 'estado_salud'], unique=False)
    
    print("✅ Schema inicial creado exitosamente")
    print("   - Tabla usuarios")
    print("   - Tabla imagenes")
    print("   - Tabla especies")
    print("   - Tabla identificaciones")
    print("   - Tabla plantas")
    print("   - Tabla analisis_salud")


def downgrade() -> None:
    """
    Elimina todas las tablas en orden inverso respetando las foreign keys.
    
    ADVERTENCIA: Esta operación eliminará TODOS los datos.
    """
    # Eliminar tablas en orden inverso (respetando foreign keys)
    op.drop_table('analisis_salud')
    op.drop_table('plantas')
    
    # Eliminar FK de imagenes hacia identificaciones antes de eliminar identificaciones
    op.drop_constraint('fk_imagenes_identificacion_id', 'imagenes', type_='foreignkey')
    
    op.drop_table('identificaciones')
    op.drop_table('especies')
    op.drop_table('imagenes')
    op.drop_table('usuarios')
    
    print("⚠️  Schema inicial eliminado")
