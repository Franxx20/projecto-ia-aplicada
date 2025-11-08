#!/bin/bash
# Script para ejecutar tests en contenedor Docker con PostgreSQL

set -e  # Exit on error

echo "🧪 Ejecutando tests en Docker con PostgreSQL..."
echo "================================================"

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Función para limpiar al salir
cleanup() {
    echo -e "\n${YELLOW}🧹 Limpiando contenedores de test...${NC}"
    docker-compose -f docker-compose.test.yml down -v 2>/dev/null || true
}

# Registrar cleanup al salir
trap cleanup EXIT

# Verificar que docker-compose.test.yml existe
if [ ! -f "../docker-compose.test.yml" ]; then
    echo -e "${RED}❌ Error: docker-compose.test.yml no encontrado${NC}"
    exit 1
fi

# Levantar servicios de test (PostgreSQL)
echo -e "${YELLOW}🐘 Levantando PostgreSQL de test...${NC}"
cd ..
docker-compose -f docker-compose.test.yml up -d db_test

# Esperar a que PostgreSQL esté listo
echo -e "${YELLOW}⏳ Esperando a que PostgreSQL esté listo...${NC}"
sleep 5

# Ejecutar migraciones
echo -e "${YELLOW}🔄 Ejecutando migraciones...${NC}"
docker-compose -f docker-compose.test.yml run --rm backend_test alembic upgrade head

# Ejecutar tests
echo -e "${GREEN}🧪 Ejecutando suite de tests...${NC}"
if [ "$1" == "coverage" ]; then
    echo -e "${YELLOW}📊 Modo: Cobertura${NC}"
    docker-compose -f docker-compose.test.yml run --rm backend_test pytest tests/ \
        --cov=app \
        --cov-report=html \
        --cov-report=term-missing \
        -v
elif [ "$1" == "health" ]; then
    echo -e "${YELLOW}🏥 Modo: Solo tests de salud${NC}"
    docker-compose -f docker-compose.test.yml run --rm backend_test pytest tests/test_health_endpoints.py -v
else
    echo -e "${YELLOW}⚡ Modo: Tests rápidos${NC}"
    docker-compose -f docker-compose.test.yml run --rm backend_test pytest tests/ -v
fi

# Capturar código de salida
TEST_EXIT_CODE=$?

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "\n${GREEN}✅ Todos los tests pasaron exitosamente!${NC}"
else
    echo -e "\n${RED}❌ Algunos tests fallaron (código: $TEST_EXIT_CODE)${NC}"
fi

exit $TEST_EXIT_CODE
