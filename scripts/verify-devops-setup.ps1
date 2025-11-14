# Script para verificar que todo está listo para subir a Azure DevOps

Write-Host "`n╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     VERIFICACIÓN PRE-AZURE DEVOPS                        ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

$allGood = $true

# 1. Verificar Azure CLI
Write-Host "1️⃣  Verificando Azure CLI..." -ForegroundColor Yellow
try {
    $azVersion = az --version 2>&1 | Select-Object -First 1
    Write-Host "   ✅ Azure CLI instalado: $azVersion" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Azure CLI NO instalado" -ForegroundColor Red
    Write-Host "      Instalar: https://aka.ms/installazurecliwindows" -ForegroundColor Gray
    $allGood = $false
}

# 2. Verificar extensión azure-devops
Write-Host "`n2️⃣  Verificando extensión azure-devops..." -ForegroundColor Yellow
try {
    $devopsExt = az extension show --name azure-devops 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ Extensión azure-devops instalada" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  Extensión NO instalada, instalando..." -ForegroundColor Yellow
        az extension add --name azure-devops
        Write-Host "   ✅ Extensión instalada" -ForegroundColor Green
    }
} catch {
    Write-Host "   ❌ No se pudo verificar/instalar extensión" -ForegroundColor Red
    $allGood = $false
}

# 3. Verificar archivos necesarios
Write-Host "`n3️⃣  Verificando archivos necesarios..." -ForegroundColor Yellow

$requiredFiles = @(
    "EPICA_DEPLOYMENT_AZURE_ESTUDIANTES.md",
    "scripts\create-epic-in-azuredevops.ps1",
    "scripts\deploy-academic-demo.ps1",
    "AZURE_DEVOPS_SETUP.md"
)

foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "   ✅ $file" -ForegroundColor Green
    } else {
        Write-Host "   ❌ $file NO encontrado" -ForegroundColor Red
        $allGood = $false
    }
}

# 4. Verificar que NO existan archivos viejos
Write-Host "`n4️⃣  Verificando que archivos innecesarios fueron eliminados..." -ForegroundColor Yellow

$deletedFiles = @(
    "DEPLOYMENT_GUIDE.md",
    "DEPLOYMENT_AZURE_ESTUDIANTES.md",
    "ESTRATEGIA_HIBRIDA_ACADEMIA.md",
    "scripts\deploy-to-azure.ps1",
    "scripts\deploy-to-azure.sh",
    "scripts\deploy-to-azure-free.ps1"
)

$foundOldFiles = $false
foreach ($file in $deletedFiles) {
    if (Test-Path $file) {
        Write-Host "   ⚠️  $file todavía existe (debería eliminarse)" -ForegroundColor Yellow
        $foundOldFiles = $true
    }
}

if (-not $foundOldFiles) {
    Write-Host "   ✅ Todos los archivos innecesarios eliminados" -ForegroundColor Green
}

# 5. Verificar configuración del script
Write-Host "`n5️⃣  Verificando configuración en script..." -ForegroundColor Yellow

$scriptContent = Get-Content "scripts\create-epic-in-azuredevops.ps1" -Raw
if ($scriptContent -match '\$ORGANIZATION_URL = "https://dev.azure.com/tu-organizacion"') {
    Write-Host "   ⚠️  ORGANIZATION_URL necesita configurarse" -ForegroundColor Yellow
    Write-Host "      Edita línea 12 del script" -ForegroundColor Gray
} else {
    Write-Host "   ✅ ORGANIZATION_URL configurado" -ForegroundColor Green
}

if ($scriptContent -match '\$PROJECT_NAME = "projecto-ia-aplicada"') {
    Write-Host "   ✅ PROJECT_NAME configurado (default)" -ForegroundColor Green
} else {
    Write-Host "   ✅ PROJECT_NAME personalizado" -ForegroundColor Green
}

# 6. Verificar conexión actual a Azure DevOps
Write-Host "`n6️⃣  Verificando conexión a Azure DevOps..." -ForegroundColor Yellow
try {
    $projects = az devops project list 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ Conectado a Azure DevOps" -ForegroundColor Green
        $projectsJson = $projects | ConvertFrom-Json
        Write-Host "      Proyectos disponibles: $($projectsJson.count)" -ForegroundColor Gray
    } else {
        Write-Host "   ⚠️  No conectado a Azure DevOps (necesitarás PAT)" -ForegroundColor Yellow
        Write-Host "      El script te pedirá conectarte" -ForegroundColor Gray
    }
} catch {
    Write-Host "   ⚠️  No conectado a Azure DevOps" -ForegroundColor Yellow
}

# Resumen final
Write-Host "`n╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                  RESUMEN DE VERIFICACIÓN                 ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

if ($allGood) {
    Write-Host "✅ TODO LISTO PARA SUBIR A AZURE DEVOPS" -ForegroundColor Green
    Write-Host "`n📝 Próximos pasos:" -ForegroundColor Cyan
    Write-Host "   1. Edita scripts/create-epic-in-azuredevops.ps1" -ForegroundColor White
    Write-Host "      - Configura ORGANIZATION_URL (línea 12)" -ForegroundColor Gray
    Write-Host "      - Verifica PROJECT_NAME (línea 13)" -ForegroundColor Gray
    Write-Host "`n   2. Ejecuta:" -ForegroundColor White
    Write-Host "      .\scripts\create-epic-in-azuredevops.ps1" -ForegroundColor Yellow
    Write-Host "`n   3. Prepara tu PAT de Azure DevOps:" -ForegroundColor White
    Write-Host "      https://dev.azure.com/{org}/_usersSettings/tokens" -ForegroundColor Gray
    Write-Host "      Scopes: Work Items (Read, Write, Manage)" -ForegroundColor Gray
} else {
    Write-Host "⚠️  HAY PROBLEMAS QUE RESOLVER" -ForegroundColor Yellow
    Write-Host "   Revisa los mensajes arriba y corrige los errores`n" -ForegroundColor Gray
}

Write-Host "`n📖 Ver guía completa: AZURE_DEVOPS_SETUP.md`n" -ForegroundColor Cyan
