# ============================================================================
# Azure Container Apps - Pausar Demo
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
║   🛑 PAUSAR SERVICIOS DE DEMO                                 ║
║                                                                ║
║   Esto escalará los Container Apps a 0 réplicas               ║
║   Costo mientras pausado: ~`$0.50/día (solo DB + Storage)     ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Yellow

# Verificar que el resource group existe
$rgExists = az group exists --name $ResourceGroup
if ($rgExists -ne "true") {
    Write-Host "❌ Resource Group '$ResourceGroup' no existe" -ForegroundColor Red
    exit 1
}

Write-Step "Pausando Container Apps..."

# Escalar backend a 0
Write-Host "   Pausando backend..." -ForegroundColor Gray
az containerapp update `
    --name plantitas-backend `
    --resource-group $ResourceGroup `
    --min-replicas 0 `
    --max-replicas 0 2>$null

if ($LASTEXITCODE -eq 0) {
    Write-Success "Backend pausado"
} else {
    Write-Warning "Backend no encontrado o ya está pausado"
}

# Escalar frontend a 0
Write-Host "   Pausando frontend..." -ForegroundColor Gray
az containerapp update `
    --name plantitas-frontend `
    --resource-group $ResourceGroup `
    --min-replicas 0 `
    --max-replicas 0 2>$null

if ($LASTEXITCODE -eq 0) {
    Write-Success "Frontend pausado"
} else {
    Write-Warning "Frontend no encontrado o ya está pausado"
}

Write-Host @"

╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║   ✅ SERVICIOS PAUSADOS                                       ║
║                                                                ║
║   💰 Costo actual: ~`$0.50/día                                 ║
║                                                                ║
║   Container Apps: 0 réplicas (sin costo)                      ║
║   PostgreSQL: Activo (~`$0.44/día)                             ║
║   Storage: Activo (~`$0.06/día)                                ║
║                                                                ║
║   Para reactivar:                                             ║
║   .\scripts\azure-demo-resume.ps1 -ResourceGroup $ResourceGroup
║                                                                ║
╚════════════════════════════════════════════════════════════════╝

"@ -ForegroundColor Green
