# ============================================================================
# Azure Container Apps - Deployment Completo
# Proyecto: Asistente Plantitas - Demo Académica
# ============================================================================

param(
    [string]$ResourceGroup = "rg-plantitas-demo-temp",
    [string]$Location = "eastus",
    [string]$ProjectName = "plantitas",
    [string]$DBPassword = "",
    [string]$GeminiApiKey = ""
)

# Colores para output
function Write-Step {
    param([string]$Message)
    Write-Host "`n==> $Message" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Error {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor Yellow
}

# ============================================================================
# VALIDACIONES PREVIAS
# ============================================================================

Write-Host @"
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║   🚀 AZURE CONTAINER APPS - DEPLOYMENT COMPLETO               ║
║                                                                ║
║   Proyecto: Asistente Plantitas                               ║
║   Tipo: Demo Académica Temporal                               ║
║   Duración estimada: 30-45 minutos                            ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Cyan

Write-Step "1. Validando prerequisitos..."

# Verificar Azure CLI
if (-not (Get-Command az -ErrorAction SilentlyContinue)) {
    Write-Error "Azure CLI no está instalado. Instala desde: https://aka.ms/installazurecli"
    exit 1
}

# Verificar login
$account = az account show 2>$null | ConvertFrom-Json
if (-not $account) {
    Write-Warning "No has iniciado sesión en Azure"
    Write-Host "Iniciando sesión..." -ForegroundColor Yellow
    az login
    $account = az account show | ConvertFrom-Json
}

Write-Success "Azure CLI configurado correctamente"
Write-Host "   Cuenta: $($account.user.name)" -ForegroundColor Gray
Write-Host "   Subscription: $($account.name)" -ForegroundColor Gray

# Solicitar contraseña DB si no se proporcionó
if ([string]::IsNullOrEmpty($DBPassword)) {
    Write-Host "`n⚠️  Necesitas una contraseña segura para PostgreSQL" -ForegroundColor Yellow
    Write-Host "   Requisitos: 8+ caracteres, mayúsculas, minúsculas, números, símbolos" -ForegroundColor Gray
    $DBPassword = Read-Host "Contraseña PostgreSQL" -AsSecureString
    $DBPassword = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto(
        [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($DBPassword)
    )
}

# Solicitar Gemini API Key si no se proporcionó
if ([string]::IsNullOrEmpty($GeminiApiKey)) {
    Write-Host "`n⚠️  Necesitas tu Gemini API Key" -ForegroundColor Yellow
    Write-Host "   Obtén una en: https://aistudio.google.com/app/apikey" -ForegroundColor Gray
    $GeminiApiKey = Read-Host "Gemini API Key"
}

# Confirmación final
Write-Host "`n╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Yellow
Write-Host "║  CONFIGURACIÓN DEL DEPLOYMENT                                  ║" -ForegroundColor Yellow
Write-Host "╠════════════════════════════════════════════════════════════════╣" -ForegroundColor Yellow
Write-Host "║  Resource Group: $ResourceGroup" -ForegroundColor Yellow
Write-Host "║  Location: $Location" -ForegroundColor Yellow
Write-Host "║  Project Name: $ProjectName" -ForegroundColor Yellow
Write-Host "║" -ForegroundColor Yellow
Write-Host "║  Servicios a crear:" -ForegroundColor Yellow
Write-Host "║    - PostgreSQL Flexible Server (Burstable B1ms)" -ForegroundColor Yellow
Write-Host "║    - Azure Blob Storage (Standard LRS)" -ForegroundColor Yellow
Write-Host "║    - Container Apps Environment" -ForegroundColor Yellow
Write-Host "║    - Azure Container Registry (Basic)" -ForegroundColor Yellow
Write-Host "║    - Backend Container App" -ForegroundColor Yellow
Write-Host "║    - Frontend Container App" -ForegroundColor Yellow
Write-Host "║" -ForegroundColor Yellow
Write-Host "║  Costo estimado: ~\$10-15 por 4 semanas" -ForegroundColor Yellow
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Yellow

$confirm = Read-Host "`n¿Continuar con el deployment? (s/n)"
if ($confirm -ne 's' -and $confirm -ne 'S') {
    Write-Warning "Deployment cancelado por el usuario"
    exit 0
}

# ============================================================================
# 2. CREAR RESOURCE GROUP
# ============================================================================

Write-Step "2. Creando Resource Group..."

$rgExists = az group exists --name $ResourceGroup
if ($rgExists -eq "true") {
    Write-Warning "Resource Group '$ResourceGroup' ya existe"
} else {
    az group create `
        --name $ResourceGroup `
        --location $Location `
        --tags "Environment=Demo" "Temporary=true" "Duration=4weeks" "Project=PlantitasDemo" | Out-Null
    
    Write-Success "Resource Group creado"
}

# ============================================================================
# 3. CREAR POSTGRESQL FLEXIBLE SERVER
# ============================================================================

Write-Step "3. Creando PostgreSQL Flexible Server..."
Write-Host "   ⏱️  Esto puede tomar 5-10 minutos..." -ForegroundColor Gray

$dbServer = "$ProjectName-demo-db"
$dbName = "plantitas_db"
$dbUser = "plantitas_admin"

# Verificar si ya existe
$dbExists = az postgres flexible-server show --name $dbServer --resource-group $ResourceGroup 2>$null
if ($dbExists) {
    Write-Warning "PostgreSQL Server '$dbServer' ya existe"
} else {
    az postgres flexible-server create `
        --resource-group $ResourceGroup `
        --name $dbServer `
        --location $Location `
        --admin-user $dbUser `
        --admin-password $DBPassword `
        --sku-name Standard_B1ms `
        --tier Burstable `
        --version 15 `
        --storage-size 32 `
        --public-access 0.0.0.0-255.255.255.255 `
        --tags "Temporary=true" `
        --yes | Out-Null
    
    Write-Success "PostgreSQL Server creado"
    
    # Crear base de datos
    Write-Host "   Creando base de datos '$dbName'..." -ForegroundColor Gray
    az postgres flexible-server db create `
        --resource-group $ResourceGroup `
        --server-name $dbServer `
        --database-name $dbName | Out-Null
    
    Write-Success "Base de datos creada"
}

# Obtener connection string
$dbHost = "$dbServer.postgres.database.azure.com"
$dbConnectionString = "postgresql://${dbUser}:${DBPassword}@${dbHost}:5432/${dbName}?sslmode=require"

Write-Success "PostgreSQL configurado"
Write-Host "   Host: $dbHost" -ForegroundColor Gray

# ============================================================================
# 4. CREAR AZURE BLOB STORAGE
# ============================================================================

Write-Step "4. Creando Azure Blob Storage..."

$storageAccount = "$ProjectName`demostorage$(Get-Random -Minimum 100 -Maximum 999)"
$storageContainer = "plantitas-imagenes"

# Verificar disponibilidad del nombre
$nameAvailable = az storage account check-name --name $storageAccount | ConvertFrom-Json
if (-not $nameAvailable.nameAvailable) {
    Write-Warning "Nombre de storage '$storageAccount' no disponible, generando nuevo..."
    $storageAccount = "$ProjectName`demostorage$(Get-Random -Minimum 1000 -Maximum 9999)"
}

az storage account create `
    --name $storageAccount `
    --resource-group $ResourceGroup `
    --location $Location `
    --sku Standard_LRS `
    --kind StorageV2 `
    --access-tier Hot `
    --tags "Temporary=true" | Out-Null

Write-Success "Storage Account creado: $storageAccount"

# Obtener connection string
$storageConnectionString = az storage account show-connection-string `
    --name $storageAccount `
    --resource-group $ResourceGroup `
    --query connectionString `
    --output tsv

# Crear container
az storage container create `
    --name $storageContainer `
    --account-name $storageAccount `
    --connection-string $storageConnectionString `
    --public-access blob | Out-Null

Write-Success "Blob Container creado: $storageContainer"

# ============================================================================
# 5. CREAR LOG ANALYTICS WORKSPACE
# ============================================================================

Write-Step "5. Creando Log Analytics Workspace..."

$logAnalytics = "$ProjectName-demo-logs"

az monitor log-analytics workspace create `
    --resource-group $ResourceGroup `
    --workspace-name $logAnalytics `
    --location $Location | Out-Null

$logAnalyticsId = az monitor log-analytics workspace show `
    --resource-group $ResourceGroup `
    --workspace-name $logAnalytics `
    --query customerId `
    --output tsv

$logAnalyticsKey = az monitor log-analytics workspace get-shared-keys `
    --resource-group $ResourceGroup `
    --workspace-name $logAnalytics `
    --query primarySharedKey `
    --output tsv

Write-Success "Log Analytics Workspace creado"

# ============================================================================
# 6. CREAR CONTAINER APPS ENVIRONMENT
# ============================================================================

Write-Step "6. Creando Container Apps Environment..."

$environment = "$ProjectName-demo-env"

az containerapp env create `
    --name $environment `
    --resource-group $ResourceGroup `
    --location $Location `
    --logs-workspace-id $logAnalyticsId `
    --logs-workspace-key $logAnalyticsKey `
    --tags "Temporary=true" | Out-Null

Write-Success "Container Apps Environment creado"

# ============================================================================
# 7. CREAR AZURE CONTAINER REGISTRY
# ============================================================================

Write-Step "7. Creando Azure Container Registry..."

$acrName = "$ProjectName`demoacr$(Get-Random -Minimum 100 -Maximum 999)"

# Verificar disponibilidad
$acrNameAvailable = az acr check-name --name $acrName | ConvertFrom-Json
if (-not $acrNameAvailable.nameAvailable) {
    Write-Warning "Nombre de ACR '$acrName' no disponible, generando nuevo..."
    $acrName = "$ProjectName`demoacr$(Get-Random -Minimum 1000 -Maximum 9999)"
}

az acr create `
    --resource-group $ResourceGroup `
    --name $acrName `
    --sku Basic `
    --admin-enabled true `
    --location $Location | Out-Null

Write-Success "Azure Container Registry creado: $acrName"

# Login a ACR
az acr login --name $acrName | Out-Null

$acrLoginServer = az acr show `
    --name $acrName `
    --query loginServer `
    --output tsv

Write-Host "   Login Server: $acrLoginServer" -ForegroundColor Gray

# ============================================================================
# 8. BUILD Y PUSH IMÁGENES
# ============================================================================

Write-Step "8. Building y pushing imágenes Docker..."
Write-Host "   ⏱️  Esto puede tomar 10-15 minutos..." -ForegroundColor Gray

# Backend
Write-Host "`n   📦 Building backend..." -ForegroundColor Cyan
$backendPath = Join-Path $PSScriptRoot "..\backend"
if (-not (Test-Path $backendPath)) {
    Write-Error "No se encontró el directorio backend en: $backendPath"
    exit 1
}

Push-Location $backendPath
az acr build `
    --registry $acrName `
    --image plantitas-backend:latest `
    --file Dockerfile `
    . | Out-Null
Pop-Location

Write-Success "Backend image pushed"

# Frontend
Write-Host "`n   📦 Building frontend..." -ForegroundColor Cyan
$frontendPath = Join-Path $PSScriptRoot "..\frontend"
if (-not (Test-Path $frontendPath)) {
    Write-Error "No se encontró el directorio frontend en: $frontendPath"
    exit 1
}

Push-Location $frontendPath
az acr build `
    --registry $acrName `
    --image plantitas-frontend:latest `
    --file Dockerfile `
    . | Out-Null
Pop-Location

Write-Success "Frontend image pushed"

# ============================================================================
# 9. GENERAR JWT SECRET
# ============================================================================

Write-Step "9. Generando JWT Secret..."

$jwtSecret = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 64 | ForEach-Object {[char]$_})

Write-Success "JWT Secret generado"

# ============================================================================
# 10. DEPLOY BACKEND CONTAINER APP
# ============================================================================

Write-Step "10. Deploying Backend Container App..."

az containerapp create `
    --name plantitas-backend `
    --resource-group $ResourceGroup `
    --environment $environment `
    --image "$acrLoginServer/plantitas-backend:latest" `
    --target-port 8000 `
    --ingress external `
    --registry-server $acrLoginServer `
    --min-replicas 0 `
    --max-replicas 2 `
    --cpu 0.5 `
    --memory 1.0Gi `
    --env-vars `
        "DATABASE_URL=$dbConnectionString" `
        "JWT_SECRET_KEY=$jwtSecret" `
        "JWT_ALGORITHM=HS256" `
        "ACCESS_TOKEN_EXPIRE_MINUTES=30" `
        "REFRESH_TOKEN_EXPIRE_DAYS=7" `
        "AZURE_STORAGE_CONNECTION_STRING=$storageConnectionString" `
        "AZURE_STORAGE_CONTAINER_NAME=$storageContainer" `
        "AZURE_STORAGE_USE_EMULATOR=false" `
        "ENVIRONMENT=production" `
        "DEBUG=false" `
        "LOG_LEVEL=INFO" `
        "GEMINI_API_KEY=$GeminiApiKey" `
        "GEMINI_MODEL=gemini-2.0-flash-exp" | Out-Null

$backendUrl = az containerapp show `
    --name plantitas-backend `
    --resource-group $ResourceGroup `
    --query properties.configuration.ingress.fqdn `
    --output tsv

$backendUrl = "https://$backendUrl"

Write-Success "Backend deployed"
Write-Host "   URL: $backendUrl" -ForegroundColor Gray

# ============================================================================
# 11. DEPLOY FRONTEND CONTAINER APP
# ============================================================================

Write-Step "11. Deploying Frontend Container App..."

az containerapp create `
    --name plantitas-frontend `
    --resource-group $ResourceGroup `
    --environment $environment `
    --image "$acrLoginServer/plantitas-frontend:latest" `
    --target-port 3000 `
    --ingress external `
    --registry-server $acrLoginServer `
    --min-replicas 0 `
    --max-replicas 2 `
    --cpu 0.5 `
    --memory 1.0Gi `
    --env-vars `
        "NEXT_PUBLIC_API_URL=$backendUrl" `
        "NODE_ENV=production" | Out-Null

$frontendUrl = az containerapp show `
    --name plantitas-frontend `
    --resource-group $ResourceGroup `
    --query properties.configuration.ingress.fqdn `
    --output tsv

$frontendUrl = "https://$frontendUrl"

Write-Success "Frontend deployed"
Write-Host "   URL: $frontendUrl" -ForegroundColor Gray

# ============================================================================
# 12. ACTUALIZAR CORS EN BACKEND
# ============================================================================

Write-Step "12. Actualizando CORS en Backend..."

az containerapp update `
    --name plantitas-backend `
    --resource-group $ResourceGroup `
    --set-env-vars "CORS_ORIGINS=$frontendUrl" | Out-Null

Write-Success "CORS actualizado"

# ============================================================================
# 13. EJECUTAR MIGRACIONES
# ============================================================================

Write-Step "13. Ejecutando migraciones de base de datos..."

# Ejecutar migraciones desde local
$env:DATABASE_URL = $dbConnectionString
Push-Location $backendPath

Write-Host "   Instalando dependencias..." -ForegroundColor Gray
pip install -q -r requirements.txt

Write-Host "   Ejecutando alembic upgrade head..." -ForegroundColor Gray
python -m alembic upgrade head

Pop-Location

Write-Success "Migraciones ejecutadas"

# ============================================================================
# 14. GUARDAR CONFIGURACIÓN
# ============================================================================

Write-Step "14. Guardando configuración..."

$configFile = Join-Path $PSScriptRoot "..\azure-deployment-config.json"

$config = @{
    deploymentDate = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    resourceGroup = $ResourceGroup
    location = $Location
    services = @{
        postgresql = @{
            server = $dbServer
            database = $dbName
            host = $dbHost
        }
        storage = @{
            account = $storageAccount
            container = $storageContainer
        }
        containerRegistry = @{
            name = $acrName
            loginServer = $acrLoginServer
        }
        backend = @{
            name = "plantitas-backend"
            url = $backendUrl
        }
        frontend = @{
            name = "plantitas-frontend"
            url = $frontendUrl
        }
    }
}

$config | ConvertTo-Json -Depth 10 | Out-File $configFile -Encoding UTF8

Write-Success "Configuración guardada en: $configFile"

# ============================================================================
# RESUMEN FINAL
# ============================================================================

Write-Host @"

╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║   ✅ DEPLOYMENT COMPLETADO EXITOSAMENTE                       ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝

🌐 URLs de tu aplicación:
   Frontend: $frontendUrl
   Backend:  $backendUrl
   API Docs: $backendUrl/docs

📊 Resource Group: $ResourceGroup

🔐 Credenciales guardadas en:
   $configFile

💰 Costo estimado: ~`$0.50/día (con scale to zero)

📚 Próximos pasos:

   1. Prueba tu aplicación en: $frontendUrl
   
   2. Para PAUSAR servicios cuando no los uses:
      .\scripts\azure-demo-pause.ps1 -ResourceGroup $ResourceGroup
   
   3. Para REACTIVAR servicios:
      .\scripts\azure-demo-resume.ps1 -ResourceGroup $ResourceGroup
   
   4. Para ELIMINAR todo al finalizar:
      .\scripts\azure-cleanup.ps1 -ResourceGroup $ResourceGroup

⚠️  IMPORTANTE: Recuerda pausar los servicios cuando no los uses para ahorrar créditos!

"@ -ForegroundColor Green

Write-Host "Presiona cualquier tecla para continuar..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
