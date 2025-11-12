# ============================================================================
# Azure Container Apps - Limpieza Completa
# Proyecto: Asistente Plantitas
# ============================================================================

param(
    [string]$ResourceGroup = "rg-plantitas-demo-temp",
    [switch]$Force
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

function Write-Error {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

Write-Host @"
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║   🗑️  ELIMINACIÓN COMPLETA DE RECURSOS                        ║
║                                                                ║
║   ⚠️  ADVERTENCIA: Esta acción NO SE PUEDE DESHACER            ║
║                                                                ║
║   Se eliminarán TODOS los recursos en:                        ║
║   Resource Group: $ResourceGroup
║                                                                ║
║   Recursos a eliminar:                                        ║
║   • PostgreSQL Flexible Server + Base de datos               ║
║   • Azure Blob Storage + Imágenes                             ║
║   • Container Apps (Backend + Frontend)                       ║
║   • Container Apps Environment                                ║
║   • Azure Container Registry + Imágenes Docker                ║
║   • Log Analytics Workspace                                   ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Red

# Verificar que el resource group existe
$rgExists = az group exists --name $ResourceGroup
if ($rgExists -ne "true") {
    Write-Error "Resource Group '$ResourceGroup' no existe"
    exit 1
}

# Mostrar recursos actuales
Write-Step "Recursos actuales en el Resource Group:"

$resources = az resource list --resource-group $ResourceGroup --query "[].{Name:name, Type:type, Location:location}" --output table

Write-Host $resources -ForegroundColor Gray

# Calcular costo estimado ahorrado
Write-Host "`n💰 Créditos que dejarás de consumir: ~`$0.50-1.00/día" -ForegroundColor Cyan

# Confirmación
if (-not $Force) {
    Write-Host "`n⚠️  ¿Estás COMPLETAMENTE SEGURO de eliminar todos estos recursos?" -ForegroundColor Yellow
    Write-Host "   Esta acción NO SE PUEDE DESHACER." -ForegroundColor Yellow
    Write-Host "   Se perderán todos los datos, imágenes y configuraciones." -ForegroundColor Yellow
    
    $confirm1 = Read-Host "`n   Escribe 'DELETE' para confirmar"
    
    if ($confirm1 -ne "DELETE") {
        Write-Warning "Eliminación cancelada"
        exit 0
    }
    
    Write-Host "`n   Segunda confirmación requerida." -ForegroundColor Yellow
    $confirm2 = Read-Host "   Escribe el nombre del Resource Group: $ResourceGroup"
    
    if ($confirm2 -ne $ResourceGroup) {
        Write-Warning "Eliminación cancelada - nombre incorrecto"
        exit 0
    }
}

# Crear backup de configuración antes de eliminar
Write-Step "Creando backup de configuración..."

$configFile = Join-Path $PSScriptRoot "..\azure-deployment-config.json"
if (Test-Path $configFile) {
    $backupFile = Join-Path $PSScriptRoot "..\azure-deployment-config-backup-$(Get-Date -Format 'yyyyMMdd-HHmmss').json"
    Copy-Item $configFile $backupFile
    Write-Success "Backup guardado: $backupFile"
}

# Listar recursos para registro
$resourcesList = az resource list --resource-group $ResourceGroup --query "[].{Name:name, Type:type}" | ConvertFrom-Json

$deletionLog = @{
    deletionDate = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    resourceGroup = $ResourceGroup
    resources = $resourcesList
}

$logFile = Join-Path $PSScriptRoot "..\azure-deletion-log-$(Get-Date -Format 'yyyyMMdd-HHmmss').json"
$deletionLog | ConvertTo-Json -Depth 10 | Out-File $logFile -Encoding UTF8

Write-Success "Log de eliminación guardado: $logFile"

# Eliminación
Write-Step "Eliminando Resource Group..."
Write-Host "   ⏱️  Esto puede tomar 5-10 minutos..." -ForegroundColor Gray

az group delete `
    --name $ResourceGroup `
    --yes `
    --no-wait

Write-Success "Eliminación iniciada en segundo plano"

Write-Host @"

╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║   ✅ ELIMINACIÓN INICIADA                                     ║
║                                                                ║
║   El Resource Group '$ResourceGroup' se está eliminando       ║
║   en segundo plano. Esto puede tomar 5-10 minutos.           ║
║                                                                ║
║   📋 Logs guardados en:                                       ║
║   $logFile
║                                                                ║
║   💰 Créditos Azure ahorrados: ~`$0.50-1.00/día               ║
║                                                                ║
║   Para verificar el estado:                                   ║
║   az group show --name $ResourceGroup
║                                                                ║
║   Cuando termine, verás un error:                             ║
║   "ResourceGroupNotFound"                                     ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝

"@ -ForegroundColor Green

Write-Host "Presiona cualquier tecla para continuar..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
