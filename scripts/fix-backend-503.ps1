# Script para Resolver el Problema del Backend 503
# El problema: Azure no encuentra startup.sh porque el PROJECT path no funciona correctamente
# Solución: Configurar el startup command directamente con la ruta absoluta

Write-Host "🔧 DIAGNÓSTICO Y SOLUCIÓN DEL BACKEND 503" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Gray
Write-Host ""

# ============================================================================
# PROBLEMA IDENTIFICADO
# ============================================================================
Write-Host "❌ PROBLEMA IDENTIFICADO:" -ForegroundColor Red
Write-Host "   1. Deployment falló: 'Error: Could not find the .NET Core project file'" -ForegroundColor Yellow
Write-Host "   2. Oryx build no está detectando correctamente la carpeta 'backend'" -ForegroundColor Yellow
Write-Host "   3. startup.sh no se encuentra: '/opt/startup/startup.sh: 26: startup.sh: not found'" -ForegroundColor Yellow
Write-Host "   4. Container termina con exit code 127 (command not found)" -ForegroundColor Yellow
Write-Host ""

Write-Host "🔍 CAUSA RAÍZ:" -ForegroundColor Yellow
Write-Host "   - El setting PROJECT='backend' no funciona con manual integration deployment" -ForegroundColor White
Write-Host "   - Los archivos están en el root del repo, no en la subcarpeta backend" -ForegroundColor White
Write-Host "   - Azure no puede encontrar requirements.txt ni startup.sh en el lugar correcto" -ForegroundColor White
Write-Host ""

# ============================================================================
# OPCIONES DE SOLUCIÓN
# ============================================================================
Write-Host "💡 OPCIONES DE SOLUCIÓN:" -ForegroundColor Cyan
Write-Host ""

Write-Host "OPCIÓN 1: Deploy Local (ZIP Deploy)" -ForegroundColor Green
Write-Host "   Ventajas: Control total, deploy inmediato" -ForegroundColor Gray
Write-Host "   Desventajas: No automático, requiere pasos manuales" -ForegroundColor Gray
Write-Host ""

Write-Host "OPCIÓN 2: GitHub Actions (Recomendado)" -ForegroundColor Green
Write-Host "   Ventajas: Automático, CI/CD completo, control de subcarpetas" -ForegroundColor Gray
Write-Host "   Desventajas: Requiere crear workflow" -ForegroundColor Gray
Write-Host ""

Write-Host "OPCIÓN 3: Cambiar estructura del repo" -ForegroundColor Green
Write-Host "   Ventajas: Funcionará con deployment manual" -ForegroundColor Gray
Write-Host "   Desventajas: Requiere mover archivos, afecta estructura" -ForegroundColor Gray
Write-Host ""

# ============================================================================
# SOLUCIÓN RECOMENDADA: OPCIÓN 1 (ZIP DEPLOY) - RÁPIDA
# ============================================================================
Write-Host "═" * 60 -ForegroundColor Cyan
Write-Host "IMPLEMENTANDO SOLUCIÓN 1: ZIP DEPLOY (MÁS RÁPIDA)" -ForegroundColor Cyan
Write-Host "═" * 60 -ForegroundColor Cyan
Write-Host ""

$backend_path = ".\backend"
$zip_name = "backend-deploy.zip"

Write-Host "📦 Paso 1: Crear archivo ZIP del backend..." -ForegroundColor Yellow

# Verificar que la carpeta backend existe
if (-not (Test-Path $backend_path)) {
    Write-Host "❌ ERROR: No se encontró la carpeta backend" -ForegroundColor Red
    exit 1
}

# Eliminar ZIP anterior si existe
if (Test-Path $zip_name) {
    Remove-Item $zip_name -Force
    Write-Host "   ✅ ZIP anterior eliminado" -ForegroundColor Gray
}

# Crear ZIP con PowerShell
Write-Host "   Comprimiendo $backend_path..." -ForegroundColor Gray
Compress-Archive -Path "$backend_path\*" -DestinationPath $zip_name -Force

if (Test-Path $zip_name) {
    $zip_size = (Get-Item $zip_name).Length / 1MB
    Write-Host "   ✅ ZIP creado: $zip_name ($([math]::Round($zip_size, 2)) MB)" -ForegroundColor Green
} else {
    Write-Host "   ❌ ERROR: No se pudo crear el ZIP" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "📤 Paso 2: Subir ZIP a Azure App Service..." -ForegroundColor Yellow

# Deploy usando Azure CLI
az webapp deployment source config-zip `
    --name plantitas-demo-backend `
    --resource-group rg-plantitas-demo-academica `
    --src $zip_name

Write-Host ""
Write-Host "⏰ Paso 3: Esperando que el deployment complete (60 segundos)..." -ForegroundColor Yellow
Start-Sleep -Seconds 60

Write-Host ""
Write-Host "🔄 Paso 4: Reiniciando la aplicación..." -ForegroundColor Yellow
az webapp restart --name plantitas-demo-backend --resource-group rg-plantitas-demo-academica

Write-Host ""
Write-Host "⏰ Esperando que la aplicación inicie (30 segundos)..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

Write-Host ""
Write-Host "🧪 Paso 5: Probando el backend..." -ForegroundColor Yellow

try {
    $response = Invoke-WebRequest -Uri "https://plantitas-demo-backend.azurewebsites.net/docs" -Method Get -TimeoutSec 60 -UseBasicParsing
    
    Write-Host ""
    Write-Host "✅ ¡BACKEND ESTÁ FUNCIONANDO!" -ForegroundColor Green
    Write-Host "   Status: $($response.StatusCode) $($response.StatusDescription)" -ForegroundColor Cyan
    Write-Host "   URL: https://plantitas-demo-backend.azurewebsites.net/docs" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "🎉 PROBLEMA RESUELTO" -ForegroundColor Green
    
} catch {
    Write-Host ""
    Write-Host "⚠️ BACKEND AÚN NO RESPONDE" -ForegroundColor Yellow
    Write-Host "   Status: $($_.Exception.Response.StatusCode)" -ForegroundColor Red
    Write-Host "   Mensaje: $($_.Exception.Message)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "📋 Siguiente paso: Ver logs" -ForegroundColor Yellow
    Write-Host "   az webapp log tail --name plantitas-demo-backend --resource-group rg-plantitas-demo-academica" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "═" * 60 -ForegroundColor Cyan
Write-Host "SCRIPT COMPLETADO" -ForegroundColor Cyan
Write-Host "═" * 60 -ForegroundColor Cyan
