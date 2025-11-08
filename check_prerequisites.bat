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

netstat -ano | findstr ":8080" >nul 2>&1
if not errorlevel 1 (
    echo [WARNING] Puerto 8080 ^(Adminer^) esta ocupado
) else (
    echo [OK] Puerto 8080 ^(Adminer^) disponible
)

REM Verificar directorios
echo.
echo Verificando directorios...
for %%D in (data logs uploads backups certs) do (
    if not exist %%D (
        mkdir %%D 2>nul
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
    echo           Se copiara desde .env.example durante el setup
) else (
    echo [OK] Archivo .env encontrado
    
    REM Verificar variables criticas
    findstr /B "POSTGRES_PASSWORD=" .env >nul 2>&1
    if errorlevel 1 (
        echo [WARNING] Variable POSTGRES_PASSWORD no encontrada en .env
    )
    
    findstr /B "SECRET_KEY=" .env >nul 2>&1
    if errorlevel 1 (
        echo [WARNING] Variable SECRET_KEY no encontrada en .env
    )
)

REM Verificar espacio en disco
echo.
echo Verificando espacio en disco...
for /f "tokens=3" %%a in ('dir /-c ^| findstr /C:"bytes free"') do set AVAILABLE=%%a
set AVAILABLE_GB=!AVAILABLE:~0,-9!
if !AVAILABLE_GB! LSS 2 (
    echo [WARNING] Espacio en disco bajo: !AVAILABLE_GB!GB disponibles
) else (
    echo [OK] Espacio suficiente en disco
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
