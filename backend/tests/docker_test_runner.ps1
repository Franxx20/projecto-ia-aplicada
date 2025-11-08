# PowerShell script para ejecutar tests en Docker con PostgreSQL
# Uso: .\docker_test_runner.ps1 [coverage|health]

param(
    [string]$Mode = "normal"
)

# Colores
$GREEN = "Green"
$YELLOW = "Yellow"
$RED = "Red"

Write-Host "🧪 Ejecutando tests en Docker con PostgreSQL..." -ForegroundColor $YELLOW
Write-Host "================================================" -ForegroundColor $YELLOW

# Función de limpieza
function Cleanup {
    Write-Host "`n🧹 Limpiando contenedores de test..." -ForegroundColor $YELLOW
    docker-compose -f ..\..\docker-compose.test.yml down -v 2>$null
}

# Registrar limpieza al salir
trap { Cleanup }

# Verificar que docker-compose.test.yml existe
$composeFile = "..\..\docker-compose.test.yml"
if (-not (Test-Path $composeFile)) {
    Write-Host "❌ Error: docker-compose.test.yml no encontrado en: $composeFile" -ForegroundColor $RED
    Write-Host "Directorio actual: $(Get-Location)" -ForegroundColor $YELLOW
    exit 1
}

# Levantar servicios de test (PostgreSQL)
Write-Host "🐘 Levantando PostgreSQL de test..." -ForegroundColor $YELLOW
Set-Location ..\..
docker-compose -f docker-compose.test.yml up -d db_test

# Esperar a que PostgreSQL esté listo
Write-Host "⏳ Esperando a que PostgreSQL esté listo..." -ForegroundColor $YELLOW
Start-Sleep -Seconds 5

# Ejecutar migraciones
Write-Host "🔄 Ejecutando migraciones..." -ForegroundColor $YELLOW
docker-compose -f docker-compose.test.yml run --rm backend_test alembic upgrade head

# Ejecutar tests según modo
Write-Host "🧪 Ejecutando suite de tests..." -ForegroundColor $GREEN

switch ($Mode) {
    "coverage" {
        Write-Host "📊 Modo: Cobertura" -ForegroundColor $YELLOW
        docker-compose -f docker-compose.test.yml run --rm backend_test pytest tests/ `
            --cov=app `
            --cov-report=html `
            --cov-report=term-missing `
            -v
    }
    "health" {
        Write-Host "🏥 Modo: Solo tests de salud" -ForegroundColor $YELLOW
        docker-compose -f docker-compose.test.yml run --rm backend_test pytest tests/test_health_endpoints.py -v
    }
    default {
        Write-Host "⚡ Modo: Tests rápidos" -ForegroundColor $YELLOW
        docker-compose -f docker-compose.test.yml run --rm backend_test pytest tests/ -v
    }
}

$TEST_EXIT_CODE = $LASTEXITCODE

if ($TEST_EXIT_CODE -eq 0) {
    Write-Host "`n✅ Todos los tests pasaron exitosamente!" -ForegroundColor $GREEN
} else {
    Write-Host "`n❌ Algunos tests fallaron (código: $TEST_EXIT_CODE)" -ForegroundColor $RED
}

# Limpieza
Cleanup

exit $TEST_EXIT_CODE
