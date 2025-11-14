# Script Final para Resolver Backend 503
# Estrategia: Deshabilitar Oryx build y usar deploy directo sin build

Write-Host "🔧 SOLUCIÓN FINAL: Deploy sin Build Automático" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Gray
Write-Host ""

Write-Host "📝 ESTRATEGIA:" -ForegroundColor Yellow
Write-Host "   1. Deshabilitar SCM_DO_BUILD_DURING_DEPLOYMENT" -ForegroundColor White
Write-Host "   2. Hacer deploy del código Python sin que Oryx intente detectar el proyecto" -ForegroundColor White
Write-Host "   3. Configurar startup command para instalar deps y ejecutar gunicorn" -ForegroundColor White
Write-Host ""

# ============================================================================
# Paso 1: Deshabilitar build automático
# ============================================================================
Write-Host "📋 Paso 1: Deshabilitar build automático de Oryx..." -ForegroundColor Yellow

az webapp config appsettings set `
    --name plantitas-demo-backend `
    --resource-group rg-plantitas-demo-academica `
    --settings SCM_DO_BUILD_DURING_DEPLOYMENT="false" ENABLE_ORYX_BUILD="false" `
    --output none

Write-Host "   ✅ Build automático deshabilitado" -ForegroundColor Green
Write-Host ""

# ============================================================================
# Paso 2: Configurar startup command completo
# ============================================================================
Write-Host "📋 Paso 2: Configurar startup command..." -ForegroundColor Yellow

$startup_cmd = @"
cd /home/site/wwwroot && python -m pip install --upgrade pip && pip install -r requirements.txt && python -m alembic upgrade head; gunicorn app.main:app --worker-class uvicorn.workers.UvicornWorker --workers 1 --bind 0.0.0.0:8000 --timeout 120 --access-logfile '-' --error-logfile '-' --log-level info
"@

az webapp config set `
    --name plantitas-demo-backend `
    --resource-group rg-plantitas-demo-academica `
    --startup-file "$startup_cmd" `
    --output none

Write-Host "   ✅ Startup command configurado" -ForegroundColor Green
Write-Host ""

# ============================================================================
# Paso 3: Deploy ZIP sin build
# ============================================================================
Write-Host "📋 Paso 3: Deploy del código..." -ForegroundColor Yellow

# Crear ZIP si no existe
if (-not (Test-Path "backend-deploy.zip")) {
    Write-Host "   Creando ZIP..." -ForegroundColor Gray
    Compress-Archive -Path ".\backend\*" -DestinationPath "backend-deploy.zip" -Force
}

az webapp deployment source config-zip `
    --name plantitas-demo-backend `
    --resource-group rg-plantitas-demo-academica `
    --src backend-deploy.zip

Write-Host "   ✅ Deploy completado" -ForegroundColor Green
Write-Host ""

# ============================================================================
# Paso 4: Reiniciar app
# ============================================================================
Write-Host "📋 Paso 4: Reiniciando aplicación..." -ForegroundColor Yellow
az webapp restart --name plantitas-demo-backend --resource-group rg-plantitas-demo-academica --output none
Write-Host "   ✅ Aplicación reiniciada" -ForegroundColor Green
Write-Host ""

# ============================================================================
# Paso 5: Esperar y probar
# ============================================================================
Write-Host "⏰ Esperando que la aplicación inicie (90 segundos)..." -ForegroundColor Yellow
Start-Sleep -Seconds 90

Write-Host ""
Write-Host "🧪 Probando el backend..." -ForegroundColor Yellow

try {
    $response = Invoke-WebRequest -Uri "https://plantitas-demo-backend.azurewebsites.net/docs" -Method Get -TimeoutSec 60 -UseBasicParsing
    
    Write-Host ""
    Write-Host "✅ ¡BACKEND FUNCIONANDO!" -ForegroundColor Green
    Write-Host "   Status: $($response.StatusCode)" -ForegroundColor Cyan
    Write-Host "   URL: https://plantitas-demo-backend.azurewebsites.net/docs" -ForegroundColor Cyan
    
} catch {
    Write-Host ""
    Write-Host "⚠️  Backend aún no responde" -ForegroundColor Yellow
    Write-Host "   $($_.Exception.Message)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "📋 Ver logs para diagnosticar:" -ForegroundColor Yellow
    Write-Host "   az webapp log tail --name plantitas-demo-backend --resource-group rg-plantitas-demo-academica" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "=" * 70 -ForegroundColor Gray
