@echo off
REM ============================================
REM SCRIPT DE GESTIÓN DEL PROYECTO DOCKER (WINDOWS)
REM ============================================

setlocal enabledelayedexpansion

REM Verificar si .env existe
if not exist .env (
    echo [WARNING] Archivo .env no encontrado. Copiando desde .env.example...
    copy .env.example .env > nul
    echo [WARNING] Por favor, edita el archivo .env con tus configuraciones específicas.
)

REM Crear directorios necesarios
if not exist data\postgres mkdir data\postgres
if not exist data\redis mkdir data\redis
if not exist logs mkdir logs
if not exist uploads mkdir uploads
if not exist backups mkdir backups
if not exist certs mkdir certs

REM Función principal
if "%1"=="" goto help
if "%1"=="setup" goto setup
if "%1"=="dev" goto dev
if "%1"=="prod" goto prod
if "%1"=="stop" goto stop
if "%1"=="restart" goto restart
if "%1"=="logs" goto logs
if "%1"=="shell" goto shell
if "%1"=="db-migrate" goto db_migrate
if "%1"=="db-backup" goto db_backup
if "%1"=="db-restore" goto db_restore
if "%1"=="clean" goto clean
if "%1"=="build" goto build
if "%1"=="test" goto test
if "%1"=="help" goto help
goto help

:setup
echo [INFO] Iniciando configuración del proyecto...
echo.
REM 1. Verificar prerequisitos
if exist check_prerequisites.bat (
    echo [INFO] Verificando prerequisitos...
    call check_prerequisites.bat
    if errorlevel 1 (
        echo [ERROR] Prerequisitos no cumplidos. Setup cancelado.
        goto end
    )
)
echo.
REM 2. Verificar Docker funcionando
docker ps >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker no esta funcionando. Inicia Docker Desktop.
    goto end
)
echo.
REM 3. Build con cache (sin --no-cache para mejor performance)
echo [INFO] Construyendo imágenes Docker (esto puede tardar varios minutos)...
docker-compose build
if errorlevel 1 (
    echo [ERROR] Error al construir imágenes
    goto end
)
echo.
echo [INFO] Levantando base de datos...
docker-compose up -d db
REM 4. Esperar a que la BD esté lista (60 segundos máximo)
echo [INFO] Esperando a que la base de datos esté lista (hasta 60 segundos)...
set /a counter=0
:wait_db_loop
docker-compose exec -T db pg_isready -U postgres >nul 2>&1
if not errorlevel 1 (
    echo [INFO] Base de datos lista!
    goto db_ready
)
set /a counter+=1
if %counter% GEQ 30 (
    echo [WARNING] Timeout esperando la base de datos
    goto db_ready
)
echo|set /p=.
timeout /t 2 /nobreak > nul
goto wait_db_loop
:db_ready
echo.
echo.
REM 5. Crear base de datos
echo [INFO] Verificando base de datos...
docker-compose exec -T db psql -U postgres -tc "SELECT 1 FROM pg_database WHERE datname = 'proyecto_ia_db'" | findstr /C:"1" > nul
if errorlevel 1 (
    echo [INFO] Creando base de datos proyecto_ia_db...
    docker-compose exec -T db psql -U postgres -c "CREATE DATABASE proyecto_ia_db;" 2>nul
    REM Verificar si la base de datos existe después del intento de creación
    docker-compose exec -T db psql -U postgres -tc "SELECT 1 FROM pg_database WHERE datname = 'proyecto_ia_db'" | findstr /C:"1" > nul
    if errorlevel 1 (
        echo [ERROR] Error al crear base de datos
        docker-compose down
        goto end
    )
    echo [INFO] Base de datos proyecto_ia_db creada exitosamente
) else (
    echo [INFO] Base de datos proyecto_ia_db ya existe
)
echo.
REM 6. Aplicar migraciones con script mejorado
echo [INFO] Iniciando backend para migraciones...
docker-compose up -d backend
echo [INFO] Esperando a que el backend esté listo...
timeout /t 10 /nobreak > nul
echo.
echo [INFO] Aplicando migraciones de base de datos...
docker-compose exec backend test -f run_migrations_improved.py >nul 2>&1
if not errorlevel 1 (
    docker-compose exec backend python run_migrations_improved.py
) else (
    docker-compose exec backend python run_migrations.py
)
if errorlevel 1 (
    echo [WARNING] Hubo un problema al aplicar las migraciones.
    echo [WARNING] Puedes ejecutar 'manage.bat db-migrate' manualmente.
    echo [WARNING] O verifica los logs: manage.bat logs backend
)
echo.
REM 7. Verificar dependencias frontend (opcional - solo en desarrollo local)
echo [INFO] Verificando dependencias del frontend...
if not exist frontend\node_modules (
    echo [INFO] node_modules no encontrado. Instalando dependencias...
    echo [INFO] Nota: Esto requiere Node.js instalado localmente o usar docker-compose.dev.yml
    where npm >nul 2>&1
    if not errorlevel 1 (
        cd frontend
        call npm install
        cd ..
    ) else (
        echo [WARNING] NPM no encontrado. Las dependencias se instalarán al usar 'manage.bat dev'
    )
) else (
    echo [INFO] Dependencias del frontend ya instaladas
)
echo.
REM 8. Detener servicios temporales
echo [INFO] Deteniendo servicios temporales...
docker-compose down
echo.
REM 9. Resumen final
echo ================================================================
echo [INFO] Configuración completada exitosamente!
echo ================================================================
echo.
echo [INFO] Próximos pasos:
echo   1. Revisa y edita el archivo .env con tus configuraciones
echo   2. Inicia el entorno:
echo      - Desarrollo:  manage.bat dev
echo      - Producción:  manage.bat prod
echo.
echo [INFO] URLs disponibles:
echo   - Frontend: http://localhost:4200
echo   - Backend:  http://localhost:8000
echo   - API Docs: http://localhost:8000/docs
echo.
goto end

:db_migrate
echo [INFO] Aplicando migraciones de base de datos...
docker-compose up -d db backend
echo [INFO] Esperando a que los servicios estén listos...
timeout /t 10 /nobreak > nul
echo.
REM Usar script mejorado si existe, sino usar el original
docker-compose exec backend test -f run_migrations_improved.py >nul 2>&1
if not errorlevel 1 (
    echo [INFO] Usando script mejorado de migraciones...
    docker-compose exec backend python run_migrations_improved.py
) else (
    docker-compose exec backend python run_migrations.py
)
if errorlevel 1 (
    echo [ERROR] Error al aplicar las migraciones
    goto end
)
echo [INFO] Migraciones aplicadas correctamente
goto end

:dev
echo [INFO] Levantando entorno de desarrollo...
docker-compose -f docker-compose.dev.yml up --build
goto end

:prod
echo [INFO] Levantando entorno de producción...
docker-compose up -d --build
echo [INFO] Servicios levantados. Revisa las URLs en tu archivo .env
goto end

:stop
echo [INFO] Deteniendo servicios...
docker-compose down
docker-compose -f docker-compose.dev.yml down 2>nul
goto end

:restart
echo [INFO] Reiniciando servicios...
call :stop
timeout /t 2 /nobreak > nul
call :prod
goto end

:logs
if "%2"=="" (
    docker-compose logs -f
) else (
    docker-compose logs -f %2
)
goto end

:shell
if "%2"=="" (
    echo [ERROR] Especifica el servicio: backend, frontend, db
    goto end
)

if "%2"=="backend" (
    docker-compose exec backend bash
) else if "%2"=="frontend" (
    docker-compose exec frontend sh
) else if "%2"=="db" (
    docker-compose exec db psql -U postgres -d proyecto_ia_db
) else (
    docker-compose exec %2 sh
)
goto end

:db_backup
echo [INFO] Creando backup de la base de datos...
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c%%a%%b)
for /f "tokens=1-2 delims=/:" %%a in ('time /t') do (set mytime=%%a%%b)
set timestamp=%mydate%_%mytime%
docker-compose exec db pg_dump -U postgres proyecto_ia_db > "./backups/backup_%timestamp%.sql"
echo [INFO] Backup creado: ./backups/backup_%timestamp%.sql
goto end

:db_restore
if "%2"=="" (
    echo [ERROR] Especifica el archivo de backup: manage.bat db-restore backup_file.sql
    goto end
)
echo [WARNING] Esto sobrescribirá la base de datos actual. ¿Continuar? (s/N)
set /p response=
if /i "!response!"=="s" (
    echo [INFO] Restaurando base de datos...
    docker-compose exec -T db psql -U postgres -d proyecto_ia_db < %2
    echo [INFO] Base de datos restaurada
) else (
    echo [INFO] Operación cancelada
)
goto end

:clean
echo [WARNING] Esto eliminará TODOS los contenedores, imágenes y volúmenes del proyecto. ¿Continuar? (s/N)
set /p response=
if /i "!response!"=="s" (
    echo [INFO] Limpiando Docker...
    docker-compose down -v --rmi all --remove-orphans
    docker system prune -f
    echo [INFO] Limpieza completada
) else (
    echo [INFO] Operación cancelada
)
goto end

:build
echo [INFO] Reconstruyendo todas las imágenes...
docker-compose build --no-cache
echo [INFO] Rebuild completado
goto end

:test
echo [INFO] Ejecutando tests...
echo [INFO] Ejecutando tests del backend...
docker-compose exec backend python -m pytest tests/ -v
echo [INFO] Ejecutando tests del frontend...
docker-compose exec frontend npm test -- --watch=false --browsers=ChromeHeadless
goto end

:help
echo.
echo Uso: manage.bat [COMANDO]
echo.
echo Comandos disponibles:
echo   setup           - Configuración inicial del proyecto (incluye migraciones)
echo   dev             - Levantar entorno de desarrollo con hot reload
echo   prod            - Levantar entorno de producción
echo   stop            - Detener todos los servicios
echo   restart         - Reiniciar todos los servicios
echo   logs [servicio] - Ver logs (opcional: especificar servicio)
echo   shell [servicio]- Acceder al shell de un servicio
echo   db-migrate      - Aplicar migraciones de base de datos
echo   db-backup       - Crear backup de la base de datos
echo   db-restore      - Restaurar backup de la base de datos
echo   clean           - Limpiar contenedores, imágenes y volúmenes
echo   build           - Rebuild de todas las imágenes
echo   test            - Ejecutar tests
echo   help            - Mostrar esta ayuda
echo.
echo Ejemplos:
echo   manage.bat setup
echo   manage.bat dev
echo   manage.bat db-migrate
echo   manage.bat logs backend
echo   manage.bat shell backend
echo.

:end
endlocal