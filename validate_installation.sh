#!/bin/bash

# Script para validar que todo funciona correctamente después del setup

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔍 Validando instalación...${NC}"
echo ""

FAILED=0

# Verificar contenedores
echo "1. Verificando contenedores..."
CONTAINERS=$(docker-compose ps --services 2>/dev/null)
REQUIRED=("db" "backend" "frontend")

for service in "${REQUIRED[@]}"; do
    if echo "$CONTAINERS" | grep -q "$service"; then
        if docker-compose ps "$service" 2>/dev/null | grep -q "Up"; then
            echo -e "${GREEN}✅ $service está funcionando${NC}"
        else
            echo -e "${RED}❌ $service no está funcionando${NC}"
            FAILED=1
        fi
    else
        echo -e "${YELLOW}⚠️  $service no está en ejecución${NC}"
    fi
done

# Verificar endpoints
echo ""
echo "2. Verificando endpoints..."

check_endpoint() {
    URL=$1
    NAME=$2
    MAX_RETRIES=3
    
    for i in $(seq 1 $MAX_RETRIES); do
        HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$URL" 2>/dev/null)
        if [ "$HTTP_CODE" -eq "200" ]; then
            echo -e "${GREEN}✅ $NAME responde correctamente (HTTP $HTTP_CODE)${NC}"
            return 0
        fi
        
        if [ $i -lt $MAX_RETRIES ]; then
            echo -e "${YELLOW}⏳ Reintentando $NAME (intento $i/$MAX_RETRIES)...${NC}"
            sleep 2
        fi
    done
    
    echo -e "${RED}❌ $NAME no responde (HTTP $HTTP_CODE)${NC}"
    FAILED=1
    return 1
}

if command -v curl &> /dev/null; then
    check_endpoint "http://localhost:8000/health" "Backend Health"
    check_endpoint "http://localhost:8000/docs" "API Docs"
    check_endpoint "http://localhost:4200" "Frontend"
else
    echo -e "${YELLOW}⚠️  curl no está disponible, omitiendo verificación de endpoints${NC}"
fi

# Verificar base de datos
echo ""
echo "3. Verificando base de datos..."
DB_CHECK=$(docker-compose exec -T db psql -U postgres -d asistente_plantitas -c "SELECT 1" 2>/dev/null)
if echo "$DB_CHECK" | grep -q "1 row"; then
    echo -e "${GREEN}✅ Base de datos accesible${NC}"
else
    echo -e "${RED}❌ Base de datos no accesible${NC}"
    FAILED=1
fi

# Verificar migraciones
echo ""
echo "4. Verificando migraciones..."
MIGRATION_CHECK=$(docker-compose exec backend alembic current 2>/dev/null)
if [ -n "$MIGRATION_CHECK" ] && [ "$MIGRATION_CHECK" != " " ]; then
    echo -e "${GREEN}✅ Migraciones aplicadas${NC}"
    echo "   Revisión actual: $(echo "$MIGRATION_CHECK" | head -1)"
else
    echo -e "${YELLOW}⚠️  Sin migraciones aplicadas o error al verificar${NC}"
fi

# Verificar volúmenes
echo ""
echo "5. Verificando volúmenes..."
VOLUMES=$(docker volume ls -q | grep -E "postgres|redis" || true)
if [ -n "$VOLUMES" ]; then
    echo -e "${GREEN}✅ Volúmenes de datos creados${NC}"
else
    echo -e "${YELLOW}⚠️  No se encontraron volúmenes de datos${NC}"
fi

# Verificar directorios
echo ""
echo "6. Verificando directorios..."
DIRS=("data" "logs" "uploads" "backups")
for DIR in "${DIRS[@]}"; do
    if [ -d "$DIR" ]; then
        echo -e "${GREEN}✅ Directorio $DIR existe${NC}"
    else
        echo -e "${YELLOW}⚠️  Directorio $DIR no encontrado${NC}"
    fi
done

# Verificar .env
echo ""
echo "7. Verificando configuración..."
if [ -f ".env" ]; then
    echo -e "${GREEN}✅ Archivo .env existe${NC}"
    
    # Verificar variables críticas
    CRITICAL_VARS=("POSTGRES_PASSWORD" "SECRET_KEY" "DATABASE_URL")
    for VAR in "${CRITICAL_VARS[@]}"; do
        if grep -q "^$VAR=" .env 2>/dev/null; then
            echo -e "${GREEN}✅ Variable $VAR configurada${NC}"
        else
            echo -e "${YELLOW}⚠️  Variable $VAR no encontrada en .env${NC}"
        fi
    done
else
    echo -e "${RED}❌ Archivo .env no encontrado${NC}"
    FAILED=1
fi

# Resumen final
echo ""
echo "================================================================"
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ Validación completada exitosamente${NC}"
    echo ""
    echo -e "${BLUE}🎉 El sistema está listo para usar${NC}"
    echo ""
    echo "URLs disponibles:"
    echo "  - Frontend: http://localhost:4200"
    echo "  - Backend:  http://localhost:8000"
    echo "  - API Docs: http://localhost:8000/docs"
    echo "  - Adminer:  http://localhost:8080 (si está habilitado)"
    echo ""
    exit 0
else
    echo -e "${RED}❌ Validación completada con errores${NC}"
    echo ""
    echo "Acciones sugeridas:"
    echo "  1. Verifica los logs: ./manage.sh logs"
    echo "  2. Reinicia los servicios: ./manage.sh restart"
    echo "  3. Revisa el archivo .env"
    echo "  4. Ejecuta las migraciones: ./manage.sh db-migrate"
    echo ""
    exit 1
fi
