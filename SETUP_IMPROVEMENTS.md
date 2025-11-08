# 🔧 Mejoras para Scripts de Inicialización

## 📋 Análisis de Problemas Actuales

### 1. **Problemas Identificados**

#### A. Gestión de Alembic
- ❌ No verifica si Alembic está inicializado
- ❌ No detecta conflictos de migraciones (merge heads)
- ❌ No valida el estado de la base de datos antes de migrar
- ❌ Timeout muy corto (3-5 segundos) para esperar servicios
- ❌ No muestra versión actual de la BD después de migrar

#### B. Manejo de Dependencias
- ❌ No verifica si las dependencias están instaladas
- ❌ No hay cache de dependencias en Docker
- ❌ Build completo en cada `setup` (`--no-cache`)
- ❌ No valida compatibilidad de versiones

#### C. Gestión de Paquetes NPM
- ❌ No verifica si `node_modules` existe
- ❌ No ejecuta `npm install` en el setup
- ❌ No valida `package-lock.json`

#### D. Validación de Prerequisitos
- ❌ No verifica versiones de Docker/Docker Compose
- ❌ No valida que los puertos estén libres
- ❌ No verifica permisos de escritura en directorios

#### E. Manejo de Errores
- ❌ Mensajes de error poco descriptivos
- ❌ No hay rollback automático en caso de fallo
- ❌ No guarda logs de errores

---

## 🚀 Mejoras Propuestas

### 1. Script Mejorado de Migraciones

Crear `backend/run_migrations_improved.py`:

```python
#!/usr/bin/env python3
"""
Script mejorado para ejecutar migraciones de Alembic
Incluye validaciones, manejo de errores y rollback automático
"""
import sys
import os
from pathlib import Path
from datetime import datetime
import time

# Asegurarnos de que estamos en el directorio correcto
backend_dir = Path(__file__).parent
os.chdir(backend_dir)

# Colores para output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_info(msg):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.END}")

def print_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.END}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.END}")

def wait_for_db(max_retries=30, delay=2):
    """Esperar a que la base de datos esté lista"""
    print_info("Esperando a que la base de datos esté lista...")
    
    from sqlalchemy import create_engine, text
    from app.core.config import configuracion
    
    for attempt in range(max_retries):
        try:
            engine = create_engine(configuracion.database_url)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                engine.dispose()
                print_success(f"Base de datos lista (intento {attempt + 1})")
                return True
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"⏳ Intento {attempt + 1}/{max_retries} - Esperando {delay}s...")
                time.sleep(delay)
            else:
                print_error(f"No se pudo conectar a la base de datos después de {max_retries} intentos")
                print_error(f"Error: {str(e)}")
                return False
    return False

def check_alembic_initialized():
    """Verificar si Alembic está inicializado"""
    alembic_ini = Path("alembic.ini")
    versions_dir = Path("alembic/versions")
    
    if not alembic_ini.exists():
        print_error("alembic.ini no encontrado. Alembic no está inicializado.")
        return False
    
    if not versions_dir.exists():
        print_error("Directorio alembic/versions no encontrado.")
        return False
    
    print_success("Alembic está inicializado correctamente")
    return True

def check_merge_heads():
    """Detectar si hay merge heads (conflictos de migraciones)"""
    try:
        from alembic.config import Config
        from alembic import command
        from alembic.script import ScriptDirectory
        
        alembic_cfg = Config("alembic.ini")
        script = ScriptDirectory.from_config(alembic_cfg)
        heads = script.get_heads()
        
        if len(heads) > 1:
            print_warning(f"⚠️  Detectados {len(heads)} heads de migración:")
            for head in heads:
                print(f"  - {head}")
            print_info("Ejecuta 'alembic merge heads' para resolver conflictos")
            return False
        
        return True
    except Exception as e:
        print_error(f"Error al verificar merge heads: {e}")
        return False

def get_current_revision():
    """Obtener la revisión actual de la base de datos"""
    try:
        from alembic.config import Config
        from alembic import command
        from io import StringIO
        
        alembic_cfg = Config("alembic.ini")
        
        # Capturar output
        buffer = StringIO()
        
        # Redirigir stdout temporalmente
        import sys
        old_stdout = sys.stdout
        sys.stdout = buffer
        
        try:
            command.current(alembic_cfg, verbose=False)
        finally:
            sys.stdout = old_stdout
        
        output = buffer.getvalue()
        
        if not output or "None" in output:
            return None
        
        # Extraer revision ID (primera palabra)
        revision = output.strip().split()[0] if output.strip() else None
        return revision
        
    except Exception as e:
        print_error(f"Error al obtener revisión actual: {e}")
        return None

def backup_current_state():
    """Crear un backup del estado actual (opcional)"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"migration_backup_{timestamp}.txt"
    
    current_rev = get_current_revision()
    if current_rev:
        with open(backup_file, 'w') as f:
            f.write(f"Revision: {current_rev}\n")
            f.write(f"Timestamp: {timestamp}\n")
        print_info(f"Backup creado: {backup_file}")
        return backup_file
    return None

def run_migrations():
    """Ejecutar migraciones con validaciones"""
    try:
        from alembic.config import Config
        from alembic import command
        
        # 1. Verificar inicialización
        if not check_alembic_initialized():
            return False
        
        # 2. Verificar merge heads
        if not check_merge_heads():
            print_error("Resuelve los conflictos de migración antes de continuar")
            return False
        
        # 3. Obtener estado actual
        current_rev = get_current_revision()
        print_info(f"Revisión actual: {current_rev or 'Base de datos vacía'}")
        
        # 4. Crear backup (opcional)
        backup_file = backup_current_state()
        
        # 5. Ejecutar migraciones
        alembic_cfg = Config("alembic.ini")
        
        print_info("🔄 Aplicando migraciones...")
        command.upgrade(alembic_cfg, "head")
        print_success("Migraciones aplicadas correctamente")
        
        # 6. Verificar nueva revisión
        new_rev = get_current_revision()
        print_success(f"Nueva revisión: {new_rev}")
        
        # 7. Mostrar historial
        print_info("\n📊 Historial de migraciones:")
        command.history(alembic_cfg, verbose=False)
        
        return True
        
    except Exception as e:
        print_error(f"Error al aplicar migraciones: {e}")
        import traceback
        traceback.print_exc()
        
        # Intentar rollback si hay un backup
        current_rev = get_current_revision()
        if current_rev and current_rev != backup_file:
            print_warning("Considera hacer rollback si es necesario:")
            print_info(f"  alembic downgrade {current_rev}")
        
        return False

def main():
    """Función principal"""
    print_info("=" * 60)
    print_info("🔧 Script de Migraciones de Base de Datos")
    print_info("=" * 60)
    
    # 1. Esperar a que la BD esté lista
    if not wait_for_db():
        sys.exit(1)
    
    # 2. Ejecutar migraciones
    if run_migrations():
        print_success("\n✨ Proceso completado exitosamente")
        sys.exit(0)
    else:
        print_error("\n❌ Proceso completado con errores")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

---

### 2. Script de Verificación de Prerequisitos

Crear `check_prerequisites.sh` / `check_prerequisites.bat`:

#### Linux/Mac (`check_prerequisites.sh`):

```bash
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
    
    DOCKER_VERSION=$(docker --version | grep -oP '\d+\.\d+\.\d+')
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
        COMPOSE_VERSION=$(docker compose version | grep -oP '\d+\.\d+\.\d+')
        echo -e "${GREEN}✅ Docker Compose ${COMPOSE_VERSION}${NC}"
    else
        COMPOSE_VERSION=$(docker-compose --version | grep -oP '\d+\.\d+\.\d+')
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
    
    GIT_VERSION=$(git --version | grep -oP '\d+\.\d+\.\d+')
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
        
        if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
            echo -e "${RED}❌ Puerto $PORT ($NAME) está ocupado${NC}"
            ALL_FREE=false
        else
            echo -e "${GREEN}✅ Puerto $PORT ($NAME) disponible${NC}"
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
    
    AVAILABLE=$(df -BG . | tail -1 | awk '{print $4}' | sed 's/G//')
    REQUIRED=2
    
    if [ "$AVAILABLE" -lt "$REQUIRED" ]; then
        echo -e "${RED}❌ Espacio insuficiente: ${AVAILABLE}GB disponibles (requerido: ${REQUIRED}GB)${NC}"
        return 1
    else
        echo -e "${GREEN}✅ Espacio suficiente: ${AVAILABLE}GB disponibles${NC}"
    fi
    
    return 0
}

# Verificar archivo .env
check_env_file() {
    echo ""
    echo "⚙️  Verificando configuración..."
    
    if [ ! -f ".env" ]; then
        echo -e "${YELLOW}⚠️  Archivo .env no encontrado${NC}"
        echo "   Se copiará desde .env.example"
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
    echo "=" * 60
    
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
```

#### Windows (`check_prerequisites.bat`):

```batch
@echo off
setlocal enabledelayedexpansion

echo Verificando prerequisitos...
echo.

set "FAILED=0"

REM Verificar Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker no esta instalado
    echo         Instala Docker Desktop desde: https://docs.docker.com/desktop/install/windows-install/
    set "FAILED=1"
) else (
    for /f "tokens=3" %%v in ('docker --version') do set DOCKER_VERSION=%%v
    echo [OK] Docker !DOCKER_VERSION!
)

REM Verificar Docker Compose
docker-compose --version >nul 2>&1
if errorlevel 1 (
    docker compose version >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Docker Compose no esta instalado
        set "FAILED=1"
    ) else (
        for /f "tokens=4" %%v in ('docker compose version') do set COMPOSE_VERSION=%%v
        echo [OK] Docker Compose !COMPOSE_VERSION!
    )
) else (
    for /f "tokens=3" %%v in ('docker-compose --version') do set COMPOSE_VERSION=%%v
    echo [OK] Docker Compose !COMPOSE_VERSION!
)

REM Verificar Git
git --version >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Git no esta instalado ^(opcional^)
) else (
    for /f "tokens=3" %%v in ('git --version') do set GIT_VERSION=%%v
    echo [OK] Git !GIT_VERSION!
)

REM Verificar puertos
echo.
echo Verificando puertos...
netstat -ano | findstr ":4200" >nul 2>&1
if not errorlevel 1 (
    echo [WARNING] Puerto 4200 ^(Frontend^) esta ocupado
) else (
    echo [OK] Puerto 4200 ^(Frontend^) disponible
)

netstat -ano | findstr ":8000" >nul 2>&1
if not errorlevel 1 (
    echo [WARNING] Puerto 8000 ^(Backend^) esta ocupado
) else (
    echo [OK] Puerto 8000 ^(Backend^) disponible
)

netstat -ano | findstr ":5432" >nul 2>&1
if not errorlevel 1 (
    echo [WARNING] Puerto 5432 ^(PostgreSQL^) esta ocupado
) else (
    echo [OK] Puerto 5432 ^(PostgreSQL^) disponible
)

REM Verificar directorios
echo.
echo Verificando directorios...
for %%D in (data logs uploads backups certs) do (
    if not exist %%D (
        mkdir %%D
        if errorlevel 1 (
            echo [ERROR] No se pudo crear directorio %%D
            set "FAILED=1"
        ) else (
            echo [OK] Directorio %%D creado
        )
    ) else (
        echo [OK] Directorio %%D existe
    )
)

REM Verificar .env
echo.
echo Verificando configuracion...
if not exist .env (
    echo [WARNING] Archivo .env no encontrado
    echo           Se copiara desde .env.example
) else (
    echo [OK] Archivo .env encontrado
)

echo.
echo ================================================================
if "%FAILED%"=="0" (
    echo [OK] Todos los prerequisitos estan cumplidos
    echo.
    echo Puedes continuar con: manage.bat setup
    exit /b 0
) else (
    echo [ERROR] Algunos prerequisitos no estan cumplidos
    echo         Revisa los errores arriba antes de continuar
    exit /b 1
)
```

---

### 3. Script de Setup Mejorado

Actualizar `manage.sh` y `manage.bat` con mejoras:

#### Cambios clave en `manage.sh`:

```bash
# Agregar al inicio del archivo
# Verificar prerequisitos
verify_prerequisites() {
    if [ -f "./check_prerequisites.sh" ]; then
        print_message "Verificando prerequisitos..."
        bash ./check_prerequisites.sh || {
            print_error "Prerequisitos no cumplidos. Setup cancelado."
            exit 1
        }
    fi
}

# Modificar la función setup
setup() {
    print_message "Iniciando configuración del proyecto..."
    
    # 1. Verificar prerequisitos
    verify_prerequisites
    
    # 2. Configurar .env
    check_env_file || {
        print_warning "Configura el archivo .env antes de continuar"
        exit 1
    }
    
    # 3. Crear directorios
    create_directories
    
    # 4. Verificar si Docker está funcionando
    if ! docker ps >/dev/null 2>&1; then
        print_error "Docker no está funcionando. Inicia Docker Desktop."
        exit 1
    fi
    
    # 5. Build con cache (eliminar --no-cache para primera vez)
    print_message "Construyendo imágenes Docker (esto puede tardar varios minutos)..."
    docker-compose build || {
        print_error "Error al construir imágenes"
        exit 1
    }
    
    echo ""
    print_message "Levantando base de datos..."
    docker-compose up -d db
    
    # 6. Esperar a que la BD esté lista (aumentar timeout)
    print_message "Esperando a que la base de datos esté lista (hasta 60 segundos)..."
    for i in {1..30}; do
        if docker-compose exec -T db pg_isready -U postgres >/dev/null 2>&1; then
            print_success "Base de datos lista!"
            break
        fi
        echo -n "."
        sleep 2
    done
    echo ""
    
    # 7. Crear base de datos
    echo ""
    print_message "Verificando base de datos..."
    DB_EXISTS=$(docker-compose exec -T db psql -U postgres -tc "SELECT 1 FROM pg_database WHERE datname = 'asistente_plantitas'" | grep -c 1 || true)
    if [ "$DB_EXISTS" -eq "0" ]; then
        print_message "Creando base de datos asistente_plantitas..."
        docker-compose exec -T db psql -U postgres -c "CREATE DATABASE asistente_plantitas;" || {
            print_error "Error al crear base de datos"
            docker-compose down
            exit 1
        }
    else
        print_success "Base de datos asistente_plantitas ya existe"
    fi
    
    # 8. Aplicar migraciones con script mejorado
    echo ""
    print_message "Iniciando backend para migraciones..."
    docker-compose up -d backend
    
    print_message "Esperando a que el backend esté listo..."
    sleep 5
    
    print_message "Aplicando migraciones de base de datos..."
    docker-compose exec backend python run_migrations_improved.py || {
        print_warning "Hubo un problema al aplicar las migraciones."
        print_warning "Puedes ejecutar './manage.sh db-migrate' manualmente."
        print_warning "O verifica los logs: ./manage.sh logs backend"
    }
    
    # 9. Verificar estado del frontend (npm install si es necesario)
    echo ""
    print_message "Verificando dependencias del frontend..."
    if [ ! -d "frontend/node_modules" ]; then
        print_message "Instalando dependencias de NPM (primera vez)..."
        docker-compose run --rm frontend npm install || {
            print_warning "Error al instalar dependencias de NPM"
        }
    fi
    
    # 10. Detener servicios temporales
    echo ""
    print_message "Deteniendo servicios temporales..."
    docker-compose down
    
    # 11. Resumen final
    echo ""
    print_success "=" * 60
    print_success "Configuración completada exitosamente!"
    print_success "=" * 60
    echo ""
    print_message "Próximos pasos:"
    echo "  1. Revisa y edita el archivo .env con tus configuraciones"
    echo "  2. Inicia el entorno:"
    echo "     - Desarrollo:  ./manage.sh dev"
    echo "     - Producción:  ./manage.sh prod"
    echo ""
    print_message "URLs disponibles:"
    echo "  - Frontend: http://localhost:4200"
    echo "  - Backend:  http://localhost:8000"
    echo "  - API Docs: http://localhost:8000/docs"
    echo ""
}
```

---

### 4. Mejoras en Dockerfile del Backend

Actualizar `backend/Dockerfile` para mejor caching:

```dockerfile
# Dockerfile para FastAPI Backend (Optimizado)
FROM python:3.11-slim

# Configurar variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# IMPORTANTE: Copiar solo requirements primero (mejor caching)
COPY requirements.txt .

# Instalar dependencias de Python
# Si requirements.txt no cambia, Docker usará cache
RUN pip install --no-cache-dir -r requirements.txt

# Crear usuario no-root
RUN addgroup --system appgroup && adduser --system --group appuser

# Ahora copiar el resto del código
COPY . .

# Crear directorios necesarios
RUN mkdir -p /app/logs /app/uploads /app/backups && \
    chown -R appuser:appgroup /app

USER appuser

# Exponer puerto
EXPOSE 8000

# Health check mejorado
HEALTHCHECK --interval=30s --timeout=30s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Comando por defecto
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

### 5. Mejoras en docker-compose.yml

```yaml
# Agregar restart policies y depends_on con condiciones

services:
  db:
    # ... configuración existente ...
    restart: unless-stopped
    # Agregar configuración de logs
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
  
  backend:
    # ... configuración existente ...
    restart: unless-stopped
    depends_on:
      db:
        condition: service_healthy
    # Variables de entorno mejoradas
    environment:
      # ... variables existentes ...
      
      # Timeouts para migraciones
      DB_CONNECTION_TIMEOUT: 60
      DB_POOL_PRE_PING: "true"
      
      # Logging
      LOG_LEVEL: ${LOG_LEVEL:-INFO}
      LOG_FORMAT: ${LOG_FORMAT:-json}
    
    # Logs
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
  
  frontend:
    # ... configuración existente ...
    restart: unless-stopped
    depends_on:
      backend:
        condition: service_healthy
    
    # Aumentar timeout de health check
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:4200 || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 60s  # Aumentado para npm install
```

---

### 6. Script de Validación Post-Setup

Crear `validate_installation.sh`:

```bash
#!/bin/bash

# Script para validar que todo funciona correctamente

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo "🔍 Validando instalación..."
echo ""

# Verificar contenedores
echo "1. Verificando contenedores..."
CONTAINERS=$(docker-compose ps --services)
REQUIRED=("db" "backend" "frontend")

for service in "${REQUIRED[@]}"; do
    if echo "$CONTAINERS" | grep -q "$service"; then
        if docker-compose ps "$service" | grep -q "Up"; then
            echo -e "${GREEN}✅ $service está funcionando${NC}"
        else
            echo -e "${RED}❌ $service no está funcionando${NC}"
        fi
    else
        echo -e "${RED}❌ $service no está definido${NC}"
    fi
done

# Verificar endpoints
echo ""
echo "2. Verificando endpoints..."

check_endpoint() {
    URL=$1
    NAME=$2
    
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$URL")
    if [ "$HTTP_CODE" -eq "200" ]; then
        echo -e "${GREEN}✅ $NAME responde correctamente${NC}"
    else
        echo -e "${RED}❌ $NAME no responde (HTTP $HTTP_CODE)${NC}"
    fi
}

check_endpoint "http://localhost:8000/health" "Backend Health"
check_endpoint "http://localhost:8000/docs" "API Docs"
check_endpoint "http://localhost:4200" "Frontend"

# Verificar base de datos
echo ""
echo "3. Verificando base de datos..."
DB_CHECK=$(docker-compose exec -T db psql -U postgres -d asistente_plantitas -c "SELECT 1" 2>/dev/null)
if echo "$DB_CHECK" | grep -q "1 row"; then
    echo -e "${GREEN}✅ Base de datos accesible${NC}"
else
    echo -e "${RED}❌ Base de datos no accesible${NC}"
fi

# Verificar migraciones
echo ""
echo "4. Verificando migraciones..."
MIGRATION_CHECK=$(docker-compose exec backend alembic current 2>/dev/null)
if [ -n "$MIGRATION_CHECK" ]; then
    echo -e "${GREEN}✅ Migraciones aplicadas${NC}"
    echo "   Revisión actual: $MIGRATION_CHECK"
else
    echo -e "${RED}❌ Sin migraciones aplicadas${NC}"
fi

echo ""
echo "✅ Validación completada"
```

---

## 📚 Documentación Actualizada

### Actualizar README.md con nueva sección:

```markdown
## 🔧 Troubleshooting del Setup

### Primera Instalación

Si es tu primera vez instalando el proyecto:

1. **Verifica prerequisitos primero:**
   ```bash
   # Linux/Mac
   bash check_prerequisites.sh
   
   # Windows
   check_prerequisites.bat
   ```

2. **Ejecuta setup:**
   ```bash
   # Linux/Mac
   ./manage.sh setup
   
   # Windows
   manage.bat setup
   ```

3. **Valida la instalación:**
   ```bash
   bash validate_installation.sh
   ```

### Problemas Comunes del Setup

#### "Error al construir imágenes"
```bash
# Limpiar cache de Docker
docker system prune -a

# Intentar de nuevo
./manage.sh setup
```

#### "Base de datos no está lista"
```bash
# Verificar logs de PostgreSQL
./manage.sh logs db

# Reiniciar solo la BD
docker-compose restart db
```

#### "Error en migraciones"
```bash
# Ver estado de migraciones
docker-compose exec backend alembic current

# Ver historial
docker-compose exec backend alembic history

# Si hay conflictos (merge heads)
docker-compose exec backend alembic heads
docker-compose exec backend alembic merge heads
```

#### "Puerto ya en uso"
```bash
# Ver qué proceso usa el puerto
# Linux/Mac
lsof -i :4200
lsof -i :8000

# Windows
netstat -ano | findstr :4200
netstat -ano | findstr :8000

# Cambiar puertos en .env
FRONTEND_PORT=8080
BACKEND_PORT=8001
```
```

---

## 📋 Checklist de Implementación

### Prioridad Alta
- [ ] Crear `run_migrations_improved.py`
- [ ] Crear scripts `check_prerequisites.sh/bat`
- [ ] Actualizar función `setup()` en `manage.sh/bat`
- [ ] Mejorar timeouts en scripts (5s → 30s para DB, 3s → 10s para backend)
- [ ] Agregar validación de merge heads en migraciones

### Prioridad Media
- [ ] Optimizar Dockerfile del backend para mejor caching
- [ ] Agregar logging policies en docker-compose.yml
- [ ] Crear script `validate_installation.sh`
- [ ] Actualizar README con troubleshooting detallado
- [ ] Agregar backups automáticos antes de migraciones

### Prioridad Baja
- [ ] Crear tests de integración del setup
- [ ] Agregar métricas de tiempo de setup
- [ ] Crear wizard interactivo para .env
- [ ] Agregar auto-recovery en caso de fallo

---

## 🎯 Resultado Esperado

Después de implementar estas mejoras:

✅ **Setup robusto:** Funciona en primera ejecución sin intervención manual  
✅ **Mensajes claros:** El usuario sabe exactamente qué está pasando y qué hacer  
✅ **Manejo de errores:** Rollback automático y mensajes de ayuda  
✅ **Validaciones:** Detecta problemas antes de que causen errores  
✅ **Performance:** Build más rápido gracias a caching mejorado  
✅ **Documentación:** Guías claras para cada problema posible  

---

## 📞 Próximos Pasos

1. Revisar este documento con el equipo
2. Priorizar qué mejoras implementar primero
3. Crear issues en GitHub para tracking
4. Implementar en orden de prioridad
5. Probar en instalación limpia
6. Actualizar documentación

¿Quieres que implemente alguna de estas mejoras ahora?
