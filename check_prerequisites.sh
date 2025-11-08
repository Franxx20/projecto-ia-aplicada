#!/bin/bash

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "🔍 Verificando prerequisitos..."
echo ""

# Verificar Docker
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker no está instalado${NC}"
        echo "   Instala Docker desde: https://docs.docker.com/get-docker/"
        return 1
    fi
    
    DOCKER_VERSION=$(docker --version | grep -oP '\d+\.\d+\.\d+' | head -1)
    echo -e "${GREEN}✅ Docker ${DOCKER_VERSION}${NC}"
    return 0
}

# Verificar Docker Compose
check_docker_compose() {
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        echo -e "${RED}❌ Docker Compose no está instalado${NC}"
        return 1
    fi
    
    if docker compose version &> /dev/null; then
        COMPOSE_VERSION=$(docker compose version | grep -oP '\d+\.\d+\.\d+' | head -1)
        echo -e "${GREEN}✅ Docker Compose ${COMPOSE_VERSION}${NC}"
    else
        COMPOSE_VERSION=$(docker-compose --version | grep -oP '\d+\.\d+\.\d+' | head -1)
        echo -e "${GREEN}✅ Docker Compose ${COMPOSE_VERSION}${NC}"
    fi
    return 0
}

# Verificar Git
check_git() {
    if ! command -v git &> /dev/null; then
        echo -e "${YELLOW}⚠️  Git no está instalado (opcional)${NC}"
        return 0
    fi
    
    GIT_VERSION=$(git --version | grep -oP '\d+\.\d+\.\d+' | head -1)
    echo -e "${GREEN}✅ Git ${GIT_VERSION}${NC}"
    return 0
}

# Verificar puertos disponibles
check_ports() {
    echo ""
    echo "🔌 Verificando puertos..."
    
    PORTS=(4200 8000 5432 8080)
    PORT_NAMES=("Frontend" "Backend" "PostgreSQL" "Adminer")
    ALL_FREE=true
    
    for i in "${!PORTS[@]}"; do
        PORT=${PORTS[$i]}
        NAME=${PORT_NAMES[$i]}
        
        if command -v lsof &> /dev/null; then
            if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
                echo -e "${RED}❌ Puerto $PORT ($NAME) está ocupado${NC}"
                ALL_FREE=false
            else
                echo -e "${GREEN}✅ Puerto $PORT ($NAME) disponible${NC}"
            fi
        elif command -v netstat &> /dev/null; then
            if netstat -tuln | grep -q ":$PORT "; then
                echo -e "${RED}❌ Puerto $PORT ($NAME) está ocupado${NC}"
                ALL_FREE=false
            else
                echo -e "${GREEN}✅ Puerto $PORT ($NAME) disponible${NC}"
            fi
        else
            echo -e "${YELLOW}⚠️  No se puede verificar puerto $PORT (lsof/netstat no disponible)${NC}"
        fi
    done
    
    if [ "$ALL_FREE" = false ]; then
        echo -e "${YELLOW}⚠️  Algunos puertos están ocupados. Modifica .env para cambiar puertos${NC}"
    fi
    
    return 0
}

# Verificar permisos de escritura
check_permissions() {
    echo ""
    echo "📁 Verificando permisos de directorios..."
    
    DIRS=("data" "logs" "uploads" "backups" "certs")
    
    for DIR in "${DIRS[@]}"; do
        if [ ! -d "$DIR" ]; then
            mkdir -p "$DIR" 2>/dev/null
            if [ $? -eq 0 ]; then
                echo -e "${GREEN}✅ Directorio $DIR creado${NC}"
            else
                echo -e "${RED}❌ No se pudo crear directorio $DIR${NC}"
                return 1
            fi
        else
            if [ -w "$DIR" ]; then
                echo -e "${GREEN}✅ Directorio $DIR con permisos de escritura${NC}"
            else
                echo -e "${RED}❌ Sin permisos de escritura en $DIR${NC}"
                return 1
            fi
        fi
    done
    
    return 0
}

# Verificar espacio en disco
check_disk_space() {
    echo ""
    echo "💾 Verificando espacio en disco..."
    
    if command -v df &> /dev/null; then
        AVAILABLE=$(df -BG . | tail -1 | awk '{print $4}' | sed 's/G//')
        REQUIRED=2
        
        if [ "$AVAILABLE" -lt "$REQUIRED" ]; then
            echo -e "${RED}❌ Espacio insuficiente: ${AVAILABLE}GB disponibles (requerido: ${REQUIRED}GB)${NC}"
            return 1
        else
            echo -e "${GREEN}✅ Espacio suficiente: ${AVAILABLE}GB disponibles${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  No se puede verificar espacio en disco (df no disponible)${NC}"
    fi
    
    return 0
}

# Verificar archivo .env
check_env_file() {
    echo ""
    echo "⚙️  Verificando configuración..."
    
    if [ ! -f ".env" ]; then
        echo -e "${YELLOW}⚠️  Archivo .env no encontrado${NC}"
        echo "   Se copiará desde .env.example durante el setup"
        return 0
    else
        echo -e "${GREEN}✅ Archivo .env encontrado${NC}"
        
        # Verificar variables críticas
        CRITICAL_VARS=("POSTGRES_PASSWORD" "SECRET_KEY")
        MISSING_VARS=()
        
        for VAR in "${CRITICAL_VARS[@]}"; do
            if ! grep -q "^$VAR=" .env; then
                MISSING_VARS+=("$VAR")
            fi
        done
        
        if [ ${#MISSING_VARS[@]} -gt 0 ]; then
            echo -e "${YELLOW}⚠️  Variables faltantes en .env:${NC}"
            for VAR in "${MISSING_VARS[@]}"; do
                echo "   - $VAR"
            done
        fi
    fi
    
    return 0
}

# Ejecutar todas las verificaciones
main() {
    FAILED=0
    
    check_docker || FAILED=1
    check_docker_compose || FAILED=1
    check_git
    check_ports
    check_permissions || FAILED=1
    check_disk_space || FAILED=1
    check_env_file
    
    echo ""
    echo "================================================================"
    
    if [ $FAILED -eq 0 ]; then
        echo -e "${GREEN}✅ Todos los prerequisitos están cumplidos${NC}"
        echo ""
        echo "Puedes continuar con: ./manage.sh setup"
        return 0
    else
        echo -e "${RED}❌ Algunos prerequisitos no están cumplidos${NC}"
        echo "   Revisa los errores arriba antes de continuar"
        return 1
    fi
}

main
exit $?
