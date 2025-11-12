# ============================================================================
# Validar Configuración de Variables de Entorno en Azure
# Proyecto: Asistente Plantitas
# ============================================================================

param(
    [string]$ResourceGroup = "rg-plantitas-demo-temp"
)

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Error {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ️  $Message" -ForegroundColor Cyan
}

Write-Host @"
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║   🔍 VALIDACIÓN DE CONFIGURACIÓN AZURE                        ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Cyan

# Verificar que el resource group existe
$rgExists = az group exists --name $ResourceGroup
if ($rgExists -ne "true") {
    Write-Error "Resource Group '$ResourceGroup' no existe"
    exit 1
}

# ============================================================================
# VALIDAR BACKEND
# ============================================================================

Write-Info "`n1. Validando Backend Container App..."

$backendEnv = az containerapp show `
    --name plantitas-backend `
    --resource-group $ResourceGroup `
    --query properties.template.containers[0].env `
    --output json 2>$null

if (-not $backendEnv) {
    Write-Error "No se pudo obtener configuración del backend"
    exit 1
}

$backendEnv = $backendEnv | ConvertFrom-Json

# Variables requeridas
$requiredBackendVars = @{
    "DATABASE_URL" = "Connection string de PostgreSQL"
    "JWT_SECRET_KEY" = "Secret key para JWT"
    "JWT_ALGORITHM" = "Algoritmo JWT (debe ser HS256)"
    "AZURE_STORAGE_CONNECTION_STRING" = "Connection string de Azure Storage"
    "AZURE_STORAGE_CONTAINER_NAME" = "Nombre del contenedor de blobs"
    "AZURE_STORAGE_USE_EMULATOR" = "Debe ser 'false' en producción"
    "GEMINI_API_KEY" = "API Key de Google Gemini"
    "ENVIRONMENT" = "Debe ser 'production'"
    "DEBUG" = "Debe ser 'false' en producción"
    "CORS_ORIGINS" = "URL del frontend"
}

$missingBackend = @()
$wrongValuesBackend = @()

foreach ($varName in $requiredBackendVars.Keys) {
    $found = $backendEnv | Where-Object { $_.name -eq $varName }
    
    if (-not $found) {
        $missingBackend += "$varName - $($requiredBackendVars[$varName])"
    } else {
        # Validaciones específicas
        switch ($varName) {
            "DEBUG" {
                if ($found.value -ne "false") {
                    $wrongValuesBackend += "DEBUG debe ser 'false' en producción (actual: $($found.value))"
                }
            }
            "ENVIRONMENT" {
                if ($found.value -ne "production") {
                    $wrongValuesBackend += "ENVIRONMENT debe ser 'production' (actual: $($found.value))"
                }
            }
            "AZURE_STORAGE_USE_EMULATOR" {
                if ($found.value -ne "false") {
                    $wrongValuesBackend += "AZURE_STORAGE_USE_EMULATOR debe ser 'false' (actual: $($found.value))"
                }
            }
            "JWT_ALGORITHM" {
                if ($found.value -ne "HS256") {
                    $wrongValuesBackend += "JWT_ALGORITHM debe ser 'HS256' (actual: $($found.value))"
                }
            }
        }
    }
}

if ($missingBackend.Count -eq 0 -and $wrongValuesBackend.Count -eq 0) {
    Write-Success "Backend: Configuración correcta ✨"
} else {
    if ($missingBackend.Count -gt 0) {
        Write-Error "Backend: Variables faltantes:"
        foreach ($var in $missingBackend) {
            Write-Host "   • $var" -ForegroundColor Red
        }
    }
    if ($wrongValuesBackend.Count -gt 0) {
        Write-Error "Backend: Valores incorrectos:"
        foreach ($issue in $wrongValuesBackend) {
            Write-Host "   • $issue" -ForegroundColor Red
        }
    }
}

# ============================================================================
# VALIDAR FRONTEND
# ============================================================================

Write-Info "`n2. Validando Frontend Container App..."

$frontendEnv = az containerapp show `
    --name plantitas-frontend `
    --resource-group $ResourceGroup `
    --query properties.template.containers[0].env `
    --output json 2>$null

if (-not $frontendEnv) {
    Write-Error "No se pudo obtener configuración del frontend"
    exit 1
}

$frontendEnv = $frontendEnv | ConvertFrom-Json

# Variables requeridas
$requiredFrontendVars = @{
    "NEXT_PUBLIC_API_URL" = "URL del backend API"
    "NODE_ENV" = "Debe ser 'production'"
}

$missingFrontend = @()
$wrongValuesFrontend = @()

foreach ($varName in $requiredFrontendVars.Keys) {
    $found = $frontendEnv | Where-Object { $_.name -eq $varName }
    
    if (-not $found) {
        $missingFrontend += "$varName - $($requiredFrontendVars[$varName])"
    } else {
        if ($varName -eq "NODE_ENV" -and $found.value -ne "production") {
            $wrongValuesFrontend += "NODE_ENV debe ser 'production' (actual: $($found.value))"
        }
    }
}

if ($missingFrontend.Count -eq 0 -and $wrongValuesFrontend.Count -eq 0) {
    Write-Success "Frontend: Configuración correcta ✨"
} else {
    if ($missingFrontend.Count -gt 0) {
        Write-Error "Frontend: Variables faltantes:"
        foreach ($var in $missingFrontend) {
            Write-Host "   • $var" -ForegroundColor Red
        }
    }
    if ($wrongValuesFrontend.Count -gt 0) {
        Write-Error "Frontend: Valores incorrectos:"
        foreach ($issue in $wrongValuesFrontend) {
            Write-Host "   • $issue" -ForegroundColor Red
        }
    }
}

# ============================================================================
# OBTENER URLs
# ============================================================================

Write-Info "`n3. Obteniendo URLs de servicios..."

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
    Write-Success "Backend URL: $backendUrl"
} else {
    Write-Error "No se pudo obtener URL del backend"
}

if ($frontendUrl) {
    $frontendUrl = "https://$frontendUrl"
    Write-Success "Frontend URL: $frontendUrl"
} else {
    Write-Error "No se pudo obtener URL del frontend"
}

# ============================================================================
# VALIDAR CORS CROSS-CHECK
# ============================================================================

Write-Info "`n4. Validando CORS configuration..."

$corsOrigins = ($backendEnv | Where-Object { $_.name -eq "CORS_ORIGINS" }).value
$apiUrl = ($frontendEnv | Where-Object { $_.name -eq "NEXT_PUBLIC_API_URL" }).value

if ($corsOrigins -and $frontendUrl) {
    if ($corsOrigins -match [regex]::Escape($frontendUrl.Replace("https://", ""))) {
        Write-Success "CORS configurado correctamente para el frontend"
    } else {
        Write-Error "CORS_ORIGINS ($corsOrigins) no incluye la URL del frontend ($frontendUrl)"
        Write-Host "   Ejecuta: az containerapp update --name plantitas-backend --resource-group $ResourceGroup --set-env-vars `"CORS_ORIGINS=$frontendUrl`"" -ForegroundColor Yellow
    }
}

if ($apiUrl -and $backendUrl) {
    if ($apiUrl -eq $backendUrl) {
        Write-Success "NEXT_PUBLIC_API_URL apunta correctamente al backend"
    } else {
        Write-Error "NEXT_PUBLIC_API_URL ($apiUrl) no coincide con backend URL ($backendUrl)"
        Write-Host "   Ejecuta: az containerapp update --name plantitas-frontend --resource-group $ResourceGroup --set-env-vars `"NEXT_PUBLIC_API_URL=$backendUrl`"" -ForegroundColor Yellow
    }
}

# ============================================================================
# TESTS DE CONECTIVIDAD
# ============================================================================

Write-Info "`n5. Tests de conectividad..."

if ($backendUrl) {
    try {
        $healthResponse = Invoke-RestMethod -Uri "$backendUrl/health" -Method GET -TimeoutSec 10 -ErrorAction Stop
        Write-Success "Backend /health responde correctamente"
    } catch {
        Write-Error "Backend /health no responde: $($_.Exception.Message)"
    }
}

# ============================================================================
# RESUMEN
# ============================================================================

Write-Host @"

╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║   📊 RESUMEN DE VALIDACIÓN                                    ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝

"@ -ForegroundColor Cyan

$totalIssues = $missingBackend.Count + $wrongValuesBackend.Count + $missingFrontend.Count + $wrongValuesFrontend.Count

if ($totalIssues -eq 0) {
    Write-Success "✅ Todo está configurado correctamente"
    Write-Host "`n🚀 Tu aplicación está lista para usar:" -ForegroundColor Green
    Write-Host "   Frontend: $frontendUrl" -ForegroundColor Cyan
    Write-Host "   Backend API: $backendUrl" -ForegroundColor Cyan
    Write-Host "   API Docs: $backendUrl/docs" -ForegroundColor Cyan
} else {
    Write-Error "❌ Se encontraron $totalIssues problemas de configuración"
    Write-Host "`nRevisa los errores arriba y corrige las variables mencionadas." -ForegroundColor Yellow
    Write-Host "Consulta: AZURE_ENVIRONMENT_VARIABLES.md para más detalles" -ForegroundColor Yellow
}

Write-Host "`nPresiona cualquier tecla para continuar..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
