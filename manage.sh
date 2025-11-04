#!/bin/bash

# ============================================
# SCRIPT DE GESTIÓN DEL PROYECTO DOCKER
# ============================================

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para mostrar mensajes
print_message() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar si .env existe
check_env_file() {
    if [ ! -f .env ]; then
        print_warning "Archivo .env no encontrado. Copiando desde .env.example..."
        cp .env.example .env
        print_warning "Por favor, edita el archivo .env con tus configuraciones específicas."
        return 1
    fi
    return 0
}

# Crear directorios necesarios
create_directories() {
    print_message "Creando directorios necesarios..."
    mkdir -p data/postgres
    mkdir -p data/redis
    mkdir -p logs
    mkdir -p uploads
    mkdir -p backups
    mkdir -p certs
}

# Función para mostrar ayuda
show_help() {
    echo -e "${BLUE}Uso: ./manage.sh [COMANDO]${NC}"
    echo ""
    echo "Comandos disponibles:"
    echo "  setup           - Configuración inicial del proyecto (incluye migraciones)"
    echo "  dev             - Levantar entorno de desarrollo con hot reload"
    echo "  prod            - Levantar entorno de producción"
    echo "  stop            - Detener todos los servicios"
    echo "  restart         - Reiniciar todos los servicios"
    echo "  logs [servicio] - Ver logs (opcional: especificar servicio)"
    echo "  shell [servicio]- Acceder al shell de un servicio"
    echo "  db-migrate      - Aplicar migraciones de base de datos"
    echo "  db-backup       - Crear backup de la base de datos"
    echo "  db-restore      - Restaurar backup de la base de datos"
    echo "  clean           - Limpiar contenedores, imágenes y volúmenes"
    echo "  build           - Rebuild de todas las imágenes"
    echo "  test            - Ejecutar tests"
    echo "  help            - Mostrar esta ayuda"
    echo ""
    echo "Ejemplos:"
    echo "  ./manage.sh setup"
    echo "  ./manage.sh dev"
    echo "  ./manage.sh db-migrate"
    echo "  ./manage.sh logs backend"
    echo "  ./manage.sh shell backend"
}

# Configuración inicial
setup() {
    print_message "Iniciando configuración del proyecto..."
    
    check_env_file
    create_directories
    
    print_message "Construyendo imágenes Docker..."
    docker-compose build --no-cache
    
    echo ""
    print_message "Levantando servicios para configurar la base de datos..."
    docker-compose up -d db
    print_message "Esperando a que la base de datos esté lista..."
    sleep 5
    
    echo ""
    print_message "Creando base de datos si no existe..."
    DB_EXISTS=$(docker-compose exec -T db psql -U postgres -tc "SELECT 1 FROM pg_database WHERE datname = 'asistente_plantitas'" | grep -c 1 || true)
    if [ "$DB_EXISTS" -eq "0" ]; then
        print_message "Creando base de datos asistente_plantitas..."
        docker-compose exec -T db psql -U postgres -c "CREATE DATABASE asistente_plantitas;"
    else
        print_message "Base de datos asistente_plantitas ya existe"
    fi
    
    echo ""
    print_message "Aplicando migraciones de base de datos..."
    docker-compose up -d backend
    sleep 3
    docker-compose exec backend python run_migrations.py || {
        print_warning "Hubo un problema al aplicar las migraciones. Puedes ejecutar './manage.sh db-migrate' manualmente."
    }
    
    echo ""
    print_message "Deteniendo servicios temporales..."
    docker-compose down
    
    echo ""
    print_message "Configuración completada!"
    print_warning "Recuerda editar el archivo .env con tus configuraciones."
}

# Entorno de desarrollo
dev() {
    check_env_file || exit 1
    create_directories
    
    print_message "Levantando entorno de desarrollo..."
    docker-compose -f docker-compose.dev.yml up --build
}

# Entorno de producción
prod() {
    check_env_file || exit 1
    create_directories
    
    print_message "Levantando entorno de producción..."
    docker-compose up -d --build
    
    print_message "Servicios levantados. URLs disponibles:"
    echo "  Frontend: http://localhost:$(grep FRONTEND_PORT .env | cut -d'=' -f2 | head -1)"
    echo "  Backend:  http://localhost:$(grep BACKEND_PORT .env | cut -d'=' -f2 | head -1)"
    echo "  Adminer:  http://localhost:$(grep ADMINER_PORT .env | cut -d'=' -f2 | head -1)"
}

# Detener servicios
stop() {
    print_message "Deteniendo servicios..."
    docker-compose down
    docker-compose -f docker-compose.dev.yml down 2>/dev/null || true
}

# Reiniciar servicios
restart() {
    print_message "Reiniciando servicios..."
    stop
    sleep 2
    prod
}

# Ver logs
logs() {
    if [ -n "$1" ]; then
        docker-compose logs -f "$1"
    else
        docker-compose logs -f
    fi
}

# Acceder al shell
shell() {
    if [ -z "$1" ]; then
        print_error "Especifica el servicio: backend, frontend, db"
        exit 1
    fi
    
    case "$1" in
        backend)
            docker-compose exec backend bash
            ;;
        frontend)
            docker-compose exec frontend sh
            ;;
        db)
            docker-compose exec db psql -U postgres -d proyecto_ia_db
            ;;
        *)
            docker-compose exec "$1" sh
            ;;
    esac
}

# Backup de base de datos
db_backup() {
    print_message "Creando backup de la base de datos..."
    timestamp=$(date +%Y%m%d_%H%M%S)
    docker-compose exec db pg_dump -U postgres proyecto_ia_db > "./backups/backup_${timestamp}.sql"
    print_message "Backup creado: ./backups/backup_${timestamp}.sql"
}

# Restaurar base de datos
db_restore() {
    if [ -z "$1" ]; then
        print_error "Especifica el archivo de backup: ./manage.sh db-restore backup_file.sql"
        exit 1
    fi
    
    print_warning "Esto sobrescribirá la base de datos actual. ¿Continuar? (y/N)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        print_message "Restaurando base de datos..."
        docker-compose exec -T db psql -U postgres -d proyecto_ia_db < "$1"
        print_message "Base de datos restaurada"
    else
        print_message "Operación cancelada"
    fi
}

# Aplicar migraciones de base de datos
db_migrate() {
    print_message "Aplicando migraciones de base de datos..."
    docker-compose up -d db backend
    print_message "Esperando a que los servicios estén listos..."
    sleep 5
    
    echo ""
    docker-compose exec backend python run_migrations.py || {
        print_error "Error al aplicar las migraciones"
        exit 1
    }
    print_message "Migraciones aplicadas correctamente"
}

# Limpiar Docker
clean() {
    print_warning "Esto eliminará TODOS los contenedores, imágenes y volúmenes del proyecto. ¿Continuar? (y/N)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        print_message "Limpiando Docker..."
        docker-compose down -v --rmi all --remove-orphans
        docker system prune -f
        print_message "Limpieza completada"
    else
        print_message "Operación cancelada"
    fi
}

# Rebuild
build() {
    print_message "Reconstruyendo todas las imágenes..."
    docker-compose build --no-cache
    print_message "Rebuild completado"
}

# Ejecutar tests
test() {
    print_message "Ejecutando tests..."
    
    # Tests del backend
    print_message "Ejecutando tests del backend..."
    docker-compose exec backend python -m pytest tests/ -v
    
    # Tests del frontend (si existen)
    print_message "Ejecutando tests del frontend..."
    docker-compose exec frontend npm test -- --watch=false --browsers=ChromeHeadless
}

# Main script
case "$1" in
    setup)
        setup
        ;;
    dev)
        dev
        ;;
    prod)
        prod
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    logs)
        logs "$2"
        ;;
    shell)
        shell "$2"
        ;;
    db-migrate)
        db_migrate
        ;;
    db-backup)
        db_backup
        ;;
    db-restore)
        db_restore "$2"
        ;;
    clean)
        clean
        ;;
    build)
        build
        ;;
    test)
        test
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Comando no reconocido: $1"
        show_help
        exit 1
        ;;
esac