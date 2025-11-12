# ============================================================================
# Azure Container Apps - Reactivar Demo
# Proyecto: Asistente Plantitas
# ============================================================================

param(
    [string]$ResourceGroup = "rg-plantitas-demo-temp"
)

function Write-Step {
    param([string]$Message)
    Write-Host "`n==> $Message" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor Yellow
}

Write-Host @"
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║   ▶️  REACTIVAR SERVICIOS DE DEMO                             ║
║                                                                ║
║   Esto escalará los Container Apps y estarán disponibles      ║
║   en aproximadamente 30-60 segundos                           ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Cyan

# Verificar que el resource group existe
$rgExists = az group exists --name $ResourceGroup
if ($rgExists -ne "true") {
    Write-Host "❌ Resource Group '$ResourceGroup' no existe" -ForegroundColor Red
    exit 1
}

Write-Step "Reactivando Container Apps..."

# Escalar backend
Write-Host "   Reactivando backend..." -ForegroundColor Gray
az containerapp update `
    --name plantitas-backend `
    --resource-group $ResourceGroup `
    --min-replicas 0 `
    --max-replicas 2 2>$null

if ($LASTEXITCODE -eq 0) {
    Write-Success "Backend reactivado"
} else {
    Write-Warning "Backend no encontrado"
}

# Escalar frontend
Write-Host "   Reactivando frontend..." -ForegroundColor Gray
az containerapp update `
    --name plantitas-frontend `
    --resource-group $ResourceGroup `
    --min-replicas 0 `
    --max-replicas 2 2>$null

if ($LASTEXITCODE -eq 0) {
    Write-Success "Frontend reactivado"
} else {
    Write-Warning "Frontend no encontrado"
}

# Obtener URLs
Write-Step "Obteniendo URLs..."

$backendUrl = az containerapp show `
    --name plantitas-backend `
    --resource-group $ResourceGroup `
    --query properties.configuration.ingress.fqdn `
    --output tsv 2>$null

$frontendUrl = az containerapp show `
    --name plantitas-frontend `
    --resource-group $ResourceGroup `
    --query properties.configuration.ingress.fqdn `
    --output tsv 2>$null

if ($backendUrl) {
    $backendUrl = "https://$backendUrl"
}

if ($frontendUrl) {
    $frontendUrl = "https://$frontendUrl"
}

Write-Host @"

╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║   ✅ SERVICIOS REACTIVADOS                                    ║
║                                                                ║
║   ⏱️  Los servicios estarán disponibles en ~30-60 segundos    ║
║                                                                ║
║   🌐 URLs de tu aplicación:                                   ║
║                                                                ║
"@ -ForegroundColor Green

if ($frontendUrl) {
    Write-Host "║   Frontend: $frontendUrl" -ForegroundColor Green
}
if ($backendUrl) {
    Write-Host "║   Backend:  $backendUrl" -ForegroundColor Green
    Write-Host "║   API Docs: $backendUrl/docs" -ForegroundColor Green
}

Write-Host @"
║                                                                ║
║   💰 Costo activo: ~`$0.50-1.00/día (con tráfico moderado)     ║
║                                                                ║
║   Para pausar nuevamente:                                     ║
║   .\scripts\azure-demo-pause.ps1 -ResourceGroup $ResourceGroup
║                                                                ║
╚════════════════════════════════════════════════════════════════╝

"@ -ForegroundColor Green

Write-Host "⏳ Espera 30-60 segundos antes de acceder a la aplicación..." -ForegroundColor Yellow
