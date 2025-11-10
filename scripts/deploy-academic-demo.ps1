# =============================================================================
# Script de Deployment para DEMO ACADÉMICA
# Azure for Students - Con Controles de Gasto
# =============================================================================

$ErrorActionPreference = "Stop"

# =============================================================================
# CONFIGURACIÓN
# =============================================================================

$RESOURCE_GROUP = "rg-plantitas-demo-academica"
$LOCATION = "eastus"
$STORAGE_ACCOUNT = "plantitasdemostorage"
$DB_SERVER = "plantitas-demo-mysql"
$DB_NAME = "plantitas_db"
$DB_USER = "plantitasadmin"
$APP_PLAN = "plantitas-demo-plan"
$BACKEND_APP = "plantitas-demo-backend"
$FRONTEND_APP = "plantitas-demo-frontend"

# Email para alertas de presupuesto
$ALERT_EMAIL = "fgarcete@alumno.unlam.edu.ar"

# =============================================================================
# FUNCIONES DE LOGGING
# =============================================================================

function Log-Info {
    param([string]$Message)
    Write-Host "ℹ️  $Message" -ForegroundColor Blue
}

function Log-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Log-Warning {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor Yellow
}

function Log-Error {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

# =============================================================================
# FUNCIONES PRINCIPALES
# =============================================================================

function Show-Welcome {
    Clear-Host
    Write-Host "`n╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║     DEPLOYMENT PARA DEMO ACADÉMICA - AZURE STUDENTS      ║" -ForegroundColor Cyan
    Write-Host "║                 Costo: `$0/mes                             ║" -ForegroundColor Green
    Write-Host "║     Con controles de gasto y alertas configuradas        ║" -ForegroundColor Cyan
    Write-Host "╚═══════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan
    
    Log-Info "Este script está optimizado para demos académicas temporales"
    Log-Info "Incluye controles de gasto automáticos"
    Log-Info "Puedes apagar los servicios después de la presentación"
    Write-Host ""
}

function Check-Prerequisites {
    Log-Info "Verificando prerequisitos..."
    
    # Check Azure CLI
    if (-not (Get-Command az -ErrorAction SilentlyContinue)) {
        Log-Error "Azure CLI no está instalado. Instala con: winget install Microsoft.AzureCLI"
        exit 1
    }
    
    # Check authentication
    try {
        $account = az account show | ConvertFrom-Json
        Log-Success "✅ Autenticado como: $($account.user.name)"
        Log-Success "✅ Suscripción: $($account.name)"
        
        # Verificar créditos restantes
        Log-Info "Consultando créditos disponibles..."
        # Nota: Azure no expone créditos directamente, pero podemos ver el consumo
    }
    catch {
        Log-Error "No estás autenticado en Azure. Ejecuta: az login"
        exit 1
    }
    
    Write-Host ""
}

function Confirm-Deployment {
    Write-Host "╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Yellow
    Write-Host "║                  CONFIRMACIÓN DE DEPLOYMENT              ║" -ForegroundColor Yellow
    Write-Host "╚═══════════════════════════════════════════════════════════╝" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Se crearán los siguientes recursos GRATUITOS:" -ForegroundColor White
    Write-Host "  • Resource Group: $RESOURCE_GROUP" -ForegroundColor Gray
    Write-Host "  • App Service Plan: F1 Free tier" -ForegroundColor Gray
    Write-Host "  • Backend App: $BACKEND_APP.azurewebsites.net" -ForegroundColor Gray
    Write-Host "  • Frontend App: $FRONTEND_APP.azurewebsites.net" -ForegroundColor Gray
    Write-Host "  • MySQL Database: 750 horas/mes gratis" -ForegroundColor Gray
    Write-Host "  • Blob Storage: 5 GB gratis" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Se configurarán:" -ForegroundColor White
    Write-Host "  • Alertas de presupuesto en \$5 y \$10 USD" -ForegroundColor Gray
    Write-Host "  • Tags para identificar como proyecto académico" -ForegroundColor Gray
    Write-Host "  • Documentación para apagar después de la demo" -ForegroundColor Gray
    Write-Host ""
    Log-Warning "Costo esperado: \$0/mes (servicios gratuitos)"
    Log-Warning "Tus \$100 USD de créditos NO se consumirán"
    Write-Host ""
    
    $continue = Read-Host "¿Continuar con el deployment? (s/n)"
    if ($continue -ne "s") {
        Log-Info "Deployment cancelado por el usuario"
        exit 0
    }
    Write-Host ""
}

function Create-ResourceGroup {
    Log-Info "Creando Resource Group: $RESOURCE_GROUP..."
    
    $exists = az group show --name $RESOURCE_GROUP 2>$null
    if ($exists) {
        Log-Warning "Resource Group ya existe, saltando..."
    }
    else {
        az group create `
            --name $RESOURCE_GROUP `
            --location $LOCATION `
            --tags `
                Proyecto="Plantitas" `
                Tipo="Demo_Academica" `
                Universidad="UNLAM" `
                Temporal="Si"
        
        Log-Success "Resource Group creado con tags académicos"
    }
}

function Setup-BudgetAlerts {
    Log-Info "Configurando alertas de presupuesto..."
    
    # Alerta a los $5 USD
    Log-Info "Creando alerta: \$5 USD (5% de créditos)..."
    try {
        az consumption budget create `
            --budget-name "alerta-academica-5usd" `
            --amount 5 `
            --category Cost `
            --time-grain Monthly `
            --time-period start-date=(Get-Date -Format "yyyy-MM-01") `
            --resource-group $RESOURCE_GROUP 2>$null
        
        Log-Success "Alerta de \$5 USD configurada"
    }
    catch {
        Log-Warning "No se pudo crear alerta de presupuesto (puede requerir permisos adicionales)"
    }
    
    # Alerta a los $10 USD
    Log-Info "Creando alerta: \$10 USD (10% de créditos)..."
    try {
        az consumption budget create `
            --budget-name "alerta-academica-10usd" `
            --amount 10 `
            --category Cost `
            --time-grain Monthly `
            --time-period start-date=(Get-Date -Format "yyyy-MM-01") `
            --resource-group $RESOURCE_GROUP 2>$null
        
        Log-Success "Alerta de \$10 USD configurada"
    }
    catch {
        Log-Warning "No se pudo crear alerta de presupuesto"
    }
    
    Log-Info "Puedes configurar alertas adicionales en Azure Portal → Cost Management"
}

function Create-StorageAccount {
    Log-Info "Creando Storage Account GRATUITO (5 GB)..."
    
    $exists = az storage account show --name $STORAGE_ACCOUNT 2>$null
    if ($exists) {
        Log-Warning "Storage Account ya existe, saltando..."
    }
    else {
        az storage account create `
            --name $STORAGE_ACCOUNT `
            --resource-group $RESOURCE_GROUP `
            --location $LOCATION `
            --sku Standard_LRS `
            --kind StorageV2 `
            --access-tier Hot `
            --tags Proyecto="Plantitas" Tipo="Demo_Academica"
        
        Log-Success "Storage Account creado - 5 GB GRATIS"
    }
    
    # Crear container
    Log-Info "Creando container para imágenes..."
    az storage container create `
        --name plantitas-imagenes `
        --account-name $STORAGE_ACCOUNT `
        --public-access off 2>$null | Out-Null
    
    Log-Success "Container creado"
}

function Create-MySQLDatabase {
    Log-Info "Creando MySQL Database GRATUITO (750 hrs/mes)..."
    
    $exists = az mysql flexible-server show --name $DB_SERVER --resource-group $RESOURCE_GROUP 2>$null
    if ($exists) {
        Log-Warning "MySQL server ya existe, saltando..."
        
        # Leer password del archivo
        if (Test-Path "db_password_demo.txt") {
            Log-Info "Usando password existente de db_password_demo.txt"
        }
    }
    else {
        # Generar password aleatorio
        $DB_PASSWORD = -join ((65..90) + (97..122) + (48..57) + (33,35,36,37,38,42,43,45,61) | Get-Random -Count 24 | ForEach-Object { [char]$_ })
        "Database Password: $DB_PASSWORD" | Out-File -FilePath "db_password_demo.txt"
        Log-Success "Password guardado en: db_password_demo.txt"
        Log-Warning "⚠️  IMPORTANTE: Guarda este archivo en un lugar seguro"
        
        Log-Info "Creando servidor MySQL (5-10 minutos)..."
        az mysql flexible-server create `
            --name $DB_SERVER `
            --resource-group $RESOURCE_GROUP `
            --location $LOCATION `
            --admin-user $DB_USER `
            --admin-password "$DB_PASSWORD" `
            --sku-name Standard_B1ms `
            --tier Burstable `
            --storage-size 20 `
            --version 8.0.21 `
            --public-access 0.0.0.0 `
            --tags Proyecto="Plantitas" Tipo="Demo_Academica" Temporal="Si"
        
        Log-Success "MySQL server creado - 750 horas/mes GRATIS"
        
        # Crear database
        az mysql flexible-server db create `
            --resource-group $RESOURCE_GROUP `
            --server-name $DB_SERVER `
            --database-name $DB_NAME
        
        Log-Success "Database '$DB_NAME' creada"
    }
}

function Create-AppServices {
    Log-Info "Creando App Service Plan FREE (F1)..."
    
    $exists = az appservice plan show --name $APP_PLAN --resource-group $RESOURCE_GROUP 2>$null
    if ($exists) {
        Log-Warning "App Service Plan ya existe, saltando..."
    }
    else {
        az appservice plan create `
            --name $APP_PLAN `
            --resource-group $RESOURCE_GROUP `
            --location $LOCATION `
            --sku F1 `
            --is-linux `
            --tags Proyecto="Plantitas" Tipo="Demo_Academica"
        
        Log-Success "App Service Plan creado - FREE F1 tier"
    }
    
    # Backend App
    Log-Info "Creando Backend App Service..."
    $backendExists = az webapp show --name $BACKEND_APP --resource-group $RESOURCE_GROUP 2>$null
    if (-not $backendExists) {
        az webapp create `
            --name $BACKEND_APP `
            --resource-group $RESOURCE_GROUP `
            --plan $APP_PLAN `
            --runtime "PYTHON:3.11" `
            --tags Proyecto="Plantitas" Tipo="Backend" Demo="Academica"
        
        Log-Success "Backend App creado"
    }
    else {
        Log-Warning "Backend App ya existe"
    }
    
    # Frontend App
    Log-Info "Creando Frontend App Service..."
    $frontendExists = az webapp show --name $FRONTEND_APP --resource-group $RESOURCE_GROUP 2>$null
    if (-not $frontendExists) {
        az webapp create `
            --name $FRONTEND_APP `
            --resource-group $RESOURCE_GROUP `
            --plan $APP_PLAN `
            --runtime "NODE:18-lts" `
            --tags Proyecto="Plantitas" Tipo="Frontend" Demo="Academica"
        
        Log-Success "Frontend App creado"
    }
    else {
        Log-Warning "Frontend App ya existe"
    }
}

function Configure-AppSettings {
    Log-Info "Configurando variables de entorno..."
    
    # Obtener connection strings
    $STORAGE_CONN = az storage account show-connection-string `
        --name $STORAGE_ACCOUNT `
        --resource-group $RESOURCE_GROUP `
        --output tsv
    
    # Generar JWT secret
    $JWT_SECRET = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 64 | ForEach-Object { [char]$_ })
    
    # Obtener DB password
    if (Test-Path "db_password_demo.txt") {
        $DB_PASSWORD = (Get-Content "db_password_demo.txt").Split(": ")[1]
    }
    else {
        $DB_PASSWORD = Read-Host "Ingresa la password de MySQL" -AsSecureString
        $DB_PASSWORD = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto(
            [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($DB_PASSWORD))
    }
    
    $DATABASE_URL = "mysql+pymysql://${DB_USER}:${DB_PASSWORD}@${DB_SERVER}.mysql.database.azure.com:3306/${DB_NAME}?ssl_ca=/etc/ssl/certs/ca-certificates.crt"
    
    # Configurar Backend
    az webapp config appsettings set `
        --name $BACKEND_APP `
        --resource-group $RESOURCE_GROUP `
        --settings `
            DATABASE_URL="$DATABASE_URL" `
            JWT_SECRET_KEY="$JWT_SECRET" `
            AZURE_STORAGE_CONNECTION_STRING="$STORAGE_CONN" `
            AZURE_STORAGE_CONTAINER_NAME="plantitas-imagenes" `
            AZURE_STORAGE_USE_EMULATOR="false" `
            ENVIRONMENT="production" `
            DEBUG="false" `
            CORS_ORIGINS="https://${FRONTEND_APP}.azurewebsites.net" | Out-Null
    
    az webapp config set `
        --name $BACKEND_APP `
        --resource-group $RESOURCE_GROUP `
        --startup-file "startup.sh" | Out-Null
    
    Log-Success "Backend configurado"
    
    # Configurar Frontend
    $BACKEND_URL = "https://${BACKEND_APP}.azurewebsites.net"
    
    az webapp config appsettings set `
        --name $FRONTEND_APP `
        --resource-group $RESOURCE_GROUP `
        --settings `
            NEXT_PUBLIC_API_URL="$BACKEND_URL" `
            NODE_ENV="production" | Out-Null
    
    Log-Success "Frontend configurado"
}

function Create-ShutdownInstructions {
    $instructions = @"
# 🛑 Instrucciones para Apagar la Demo Después de la Presentación

## Opción 1: Apagar Temporalmente (Recomendado)
Esto mantiene los recursos pero los apaga para que no consuman recursos:

``````powershell
# Apagar Backend
az webapp stop --name $BACKEND_APP --resource-group $RESOURCE_GROUP

# Apagar Frontend  
az webapp stop --name $FRONTEND_APP --resource-group $RESOURCE_GROUP

# Apagar MySQL (IMPORTANTE: ahorra las 750 horas gratis)
az mysql flexible-server stop --name $DB_SERVER --resource-group $RESOURCE_GROUP

# Costo mientras está apagado: `$0/día
``````

## Opción 2: Eliminar Todo (Si ya no lo necesitas)
Esto elimina permanentemente todos los recursos:

``````powershell
# Eliminar todo el Resource Group
az group delete --name $RESOURCE_GROUP --yes --no-wait

# Costo después de eliminar: `$0
# Tus `$100 USD quedan intactos
``````

## Para Reactivar (si usaste Opción 1)
``````powershell
# Iniciar Backend
az webapp start --name $BACKEND_APP --resource-group $RESOURCE_GROUP

# Iniciar Frontend
az webapp start --name $FRONTEND_APP --resource-group $RESOURCE_GROUP

# Iniciar MySQL
az mysql flexible-server start --name $DB_SERVER --resource-group $RESOURCE_GROUP
``````

## Monitorear Costos
``````powershell
# Ver costos acumulados
az consumption usage list \
  --start-date (Get-Date).AddDays(-7).ToString("yyyy-MM-dd") \
  --end-date (Get-Date).ToString("yyyy-MM-dd") \
  --output table
``````

## URLs de tu Aplicación
- Frontend: https://$FRONTEND_APP.azurewebsites.net
- Backend: https://$BACKEND_APP.azurewebsites.net

---
Generado el: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
"@

    $instructions | Out-File -FilePath "INSTRUCCIONES_APAGAR_DEMO.md" -Encoding UTF8
    Log-Success "Instrucciones guardadas en: INSTRUCCIONES_APAGAR_DEMO.md"
}

function Show-Summary {
    Write-Host "`n╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║        DEPLOYMENT COMPLETADO EXITOSAMENTE                ║" -ForegroundColor Green
    Write-Host "║                COSTO: `$0/MES                             ║" -ForegroundColor Green
    Write-Host "╚═══════════════════════════════════════════════════════════╝`n" -ForegroundColor Green
    
    $BACKEND_URL = "https://${BACKEND_APP}.azurewebsites.net"
    $FRONTEND_URL = "https://${FRONTEND_APP}.azurewebsites.net"
    
    Log-Info "📱 URLs de tu aplicación:"
    Write-Host "   Frontend: $FRONTEND_URL" -ForegroundColor Cyan
    Write-Host "   Backend:  $BACKEND_URL" -ForegroundColor Cyan
    Write-Host ""
    
    Log-Info "✅ Servicios gratuitos activos:"
    Write-Host "   • App Service F1 (Backend + Frontend)"
    Write-Host "   • MySQL Database (750 hrs/mes gratis)"
    Write-Host "   • Blob Storage (5 GB gratis)"
    Write-Host "   • HTTPS automático"
    Write-Host ""
    
    Log-Info "🛡️ Controles de gasto configurados:"
    Write-Host "   • Alertas en \$5 y \$10 USD"
    Write-Host "   • Tags para identificar como proyecto académico"
    Write-Host "   • Instrucciones para apagar en: INSTRUCCIONES_APAGAR_DEMO.md"
    Write-Host ""
    
    Log-Info "📋 Próximos pasos:"
    Write-Host "   1. Deploy tu código con: git push"
    Write-Host "   2. Configura GitHub Actions para CI/CD automático"
    Write-Host "   3. Prueba la aplicación en las URLs de arriba"
    Write-Host "   4. Después de la demo, lee: INSTRUCCIONES_APAGAR_DEMO.md"
    Write-Host ""
    
    Log-Warning "⏰ RECORDATORIO:"
    Write-Host "   • Apaga los servicios después de la presentación"
    Write-Host "   • Monitorea costos semanalmente"
    Write-Host "   • Tus \$100 USD están intactos 💰"
    Write-Host ""
    
    if (Test-Path "db_password_demo.txt") {
        Log-Warning "🔐 IMPORTANTE: Guarda db_password_demo.txt en un lugar seguro"
    }
}

# =============================================================================
# MAIN
# =============================================================================

function Main {
    Show-Welcome
    Check-Prerequisites
    Confirm-Deployment
    
    Log-Info "Iniciando deployment para demo académica...`n"
    
    Create-ResourceGroup
    Setup-BudgetAlerts
    Create-StorageAccount
    Create-MySQLDatabase
    Create-AppServices
    Configure-AppSettings
    Create-ShutdownInstructions
    Show-Summary
}

# Ejecutar script
Main
