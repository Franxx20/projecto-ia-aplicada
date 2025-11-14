#!/bin/bash
# =============================================================================
# Script de Arranque para Azure App Service
# Proyecto: Asistente Plantitas - Backend
# =============================================================================

set -e  # Detener ejecución si hay errores

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║     🚀 Iniciando Asistente Plantitas Backend             ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""
echo "📍 Entorno: Azure App Service"
echo "⏰ Inicio: $(date)"
echo ""

# =============================================================================
# 1. VERIFICAR VARIABLES DE ENTORNO CRÍTICAS
# =============================================================================

echo "🔍 Verificando configuración..."

if [ -z "$DATABASE_URL" ]; then
    echo "❌ ERROR: DATABASE_URL no está configurado"
    echo "   Configure DATABASE_URL en App Service Settings"
    exit 1
fi

if [ -z "$JWT_SECRET_KEY" ]; then
    echo "⚠️  ADVERTENCIA: JWT_SECRET_KEY no está configurado"
    echo "   Se usará un secret por defecto (NO SEGURO PARA PRODUCCIÓN)"
fi

if [ -z "$AZURE_STORAGE_CONNECTION_STRING" ]; then
    echo "⚠️  ADVERTENCIA: AZURE_STORAGE_CONNECTION_STRING no está configurado"
    echo "   Las imágenes no podrán subirse a Blob Storage"
fi

echo "✅ Variables de entorno verificadas"
echo ""

# =============================================================================
# 2. VERIFICAR ESTRUCTURA DE DIRECTORIOS
# =============================================================================

echo "📁 Verificando directorios..."

# App Service monta el código en /home/site/wwwroot por defecto
WORK_DIR="/home/site/wwwroot"

if [ -d "$WORK_DIR" ]; then
    cd "$WORK_DIR"
    echo "✅ Directorio de trabajo: $WORK_DIR"
else
    echo "⚠️  Directorio $WORK_DIR no existe, usando directorio actual"
    WORK_DIR=$(pwd)
fi

# Crear directorio de uploads si no existe
if [ ! -d "uploads" ]; then
    mkdir -p uploads
    echo "✅ Directorio 'uploads' creado"
fi

echo ""

# =============================================================================
# 3. EJECUTAR MIGRACIONES DE BASE DE DATOS
# =============================================================================

echo "📦 Ejecutando migraciones de base de datos..."

# Verificar que Alembic está disponible
if command -v alembic &> /dev/null; then
    
    # Intentar ejecutar migraciones
    if alembic upgrade head; then
        echo "✅ Migraciones ejecutadas exitosamente"
    else
        echo "⚠️  Advertencia: Las migraciones fallaron"
        echo "   Revisa los logs para más detalles"
        echo "   El servidor continuará iniciándose..."
    fi
else
    echo "⚠️  Alembic no encontrado, saltando migraciones"
fi

echo ""

# =============================================================================
# 4. INFORMACIÓN DEL SISTEMA
# =============================================================================

echo "📊 Información del sistema:"
echo "   Python: $(python --version 2>&1)"
echo "   Pip: $(pip --version 2>&1 | head -n 1)"
echo "   Directorio: $(pwd)"
echo "   Usuario: $(whoami)"

# Mostrar algunas variables de entorno (sin valores sensibles)
echo ""
echo "🔧 Configuración de la aplicación:"
echo "   ENTORNO: ${ENTORNO:-desarrollo}"
echo "   DEBUG: ${DEBUG:-true}"
echo "   CORS_ORIGINS: ${ORIGENES_CORS:-[default]}"
echo "   AZURE_STORAGE_USE_EMULATOR: ${AZURE_STORAGE_USE_EMULATOR:-false}"

echo ""

# =============================================================================
# 5. INICIAR SERVIDOR GUNICORN CON UVICORN WORKERS
# =============================================================================

echo "🌟 Iniciando servidor Gunicorn + Uvicorn..."
echo "   Workers: 1 (App Service F1 Free tier)"
echo "   Puerto: 8000"
echo "   Timeout: 120 segundos"
echo ""

# Configuración de Gunicorn optimizada para App Service F1 (Free tier)
# - 1 worker: El tier F1 tiene recursos limitados (1 GB RAM, 60 min CPU/día)
# - uvicorn.workers.UvicornWorker: Worker ASGI para FastAPI
# - bind 0.0.0.0:8000: Escuchar en todas las interfaces
# - timeout 120: Timeout para requests largos (identificación de plantas)
# - access-logfile/error-logfile '-': Logs a stdout para Azure Logs
# - log-level info: Nivel de log apropiado para producción

exec gunicorn app.main:app \
    --worker-class uvicorn.workers.UvicornWorker \
    --workers 1 \
    --bind 0.0.0.0:8000 \
    --timeout 120 \
    --access-logfile '-' \
    --error-logfile '-' \
    --log-level info \
    --capture-output \
    --enable-stdio-inheritance

# Nota: El comando 'exec' reemplaza el proceso actual con Gunicorn
# Esto es importante para que las señales (SIGTERM, etc.) se manejen correctamente
