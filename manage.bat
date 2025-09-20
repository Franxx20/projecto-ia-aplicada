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
if "%1"=="db-backup" goto db_backup
if "%1"=="db-restore" goto db_restore
if "%1"=="clean" goto clean
if "%1"=="build" goto build
if "%1"=="test" goto test
if "%1"=="help" goto help
goto help

:setup
echo [INFO] Iniciando configuración del proyecto...
echo [INFO] Construyendo imágenes Docker...
docker-compose build --no-cache
echo [INFO] Configuración completada!
echo [WARNING] Recuerda editar el archivo .env con tus configuraciones.
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
echo   setup           - Configuración inicial del proyecto
echo   dev             - Levantar entorno de desarrollo con hot reload
echo   prod            - Levantar entorno de producción
echo   stop            - Detener todos los servicios
echo   restart         - Reiniciar todos los servicios
echo   logs [servicio] - Ver logs (opcional: especificar servicio)
echo   shell [servicio]- Acceder al shell de un servicio
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
echo   manage.bat logs backend
echo   manage.bat shell backend
echo.

:end
endlocal