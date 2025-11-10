# =============================================================================
# Script para crear ÉPICA de Deployment en Azure DevOps
# Proyecto: Asistente Plantitas
# =============================================================================

$ErrorActionPreference = "Stop"

# =============================================================================
# CONFIGURACIÓN
# =============================================================================

# IMPORTANTE: Configurar estas variables antes de ejecutar
$ORGANIZATION_URL = "https://dev.azure.com/ia-grupo-5"  # CAMBIAR
$PROJECT_NAME = "proyecto-plantitas"  # CAMBIAR si es diferente
$AREA_PATH = "$PROJECT_NAME"  # Ajustar si tienes área específica

# =============================================================================
# FUNCIONES
# =============================================================================

function Show-Welcome {
    Write-Host "`n╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║     CREAR ÉPICA DE DEPLOYMENT EN AZURE DEVOPS           ║" -ForegroundColor Cyan
    Write-Host "║              Asistente Plantitas                         ║" -ForegroundColor Cyan
    Write-Host "╚═══════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan
}

function Test-AzureDevOpsConnection {
    Write-Host "🔍 Verificando conexión a Azure DevOps..." -ForegroundColor Yellow
    
    try {
        $projects = az devops project list --output json 2>&1 | ConvertFrom-Json
        
        if ($projects.count -gt 0) {
            Write-Host "✅ Conectado a Azure DevOps" -ForegroundColor Green
            Write-Host "   Organización: $ORGANIZATION_URL" -ForegroundColor Gray
            Write-Host "   Proyectos disponibles: $($projects.count)`n" -ForegroundColor Gray
            return $true
        }
    }
    catch {
        Write-Host "❌ No conectado a Azure DevOps" -ForegroundColor Red
        return $false
    }
}

function Configure-AzureDevOps {
    Write-Host "`n📝 Configurando Azure DevOps CLI...`n" -ForegroundColor Yellow
    
    Write-Host "Para configurar Azure DevOps necesitas:" -ForegroundColor White
    Write-Host "1. Ir a: $ORGANIZATION_URL/_usersSettings/tokens" -ForegroundColor Gray
    Write-Host "2. Crear un nuevo Personal Access Token (PAT)" -ForegroundColor Gray
    Write-Host "3. Permisos necesarios: Work Items (Read, Write, Manage)" -ForegroundColor Gray
    Write-Host "4. Copiar el token generado`n" -ForegroundColor Gray
    
    $pat = Read-Host "Pega tu Personal Access Token (PAT)" -AsSecureString
    $patText = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto(
        [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($pat))
    
    # Configurar defaults
    Write-Host "`n🔧 Configurando defaults..." -ForegroundColor Yellow
    echo $patText | az devops login --organization $ORGANIZATION_URL
    
    az devops configure --defaults organization=$ORGANIZATION_URL project=$PROJECT_NAME
    
    Write-Host "✅ Azure DevOps configurado correctamente`n" -ForegroundColor Green
}

function Create-Epic {
    Write-Host "📋 Creando ÉPICA: Deployment a Azure para Estudiantes...`n" -ForegroundColor Yellow
    
    $epicDescription = @"
# 🚀 ÉPICA: Deployment a Azure para Estudiantes

**Estrategia**: App Service (SIN Docker) - Opción GRATUITA
**Costo Estimado**: `$0/mes (servicios gratuitos)
**Tiempo Estimado**: 6-8 horas distribuidas en 4 días

## Objetivos
1. Simplicidad Máxima: Deployment sin Docker
2. Costo `$0: Usar solo servicios con tier gratuito
3. Controles de Gasto: Alertas automáticas
4. Demo Temporal: Fácil de apagar después de presentación
5. Mínima Fricción: Automatización con scripts PowerShell

## Arquitectura
- Frontend: Next.js 14 en App Service F1 (FREE)
- Backend: FastAPI en App Service F1 (FREE)
- Database: MySQL Flexible Server (750 hrs/mes FREE)
- Storage: Azure Blob Storage (5 GB FREE)

## 7 Fases
- Fase 1: Preparación del Código (5 tareas)
- Fase 2: Infraestructura Azure (4 tareas)
- Fase 3: Deployment de Aplicaciones (5 tareas)
- Fase 4: Verificación y Pruebas (3 tareas)
- Fase 5: Controles de Gasto (3 tareas)
- Fase 6: Documentación (4 tareas)
- Fase 7: Post-Demo (2 tareas)

Ver documento completo: EPICA_DEPLOYMENT_AZURE_ESTUDIANTES.md
"@
    
    # Crear Epic
    $epic = az boards work-item create `
        --title "EPIC-DEPLOY-001: Deployment a Azure para Estudiantes" `
        --type "Epic" `
        --project $PROJECT_NAME `
        --area $AREA_PATH `
        --description $epicDescription `
        --output json | ConvertFrom-Json
    
    Write-Host "✅ Épica creada: #$($epic.id)" -ForegroundColor Green
    Write-Host "   URL: $($epic._links.html.href)`n" -ForegroundColor Cyan
    
    return $epic.id
}

function Create-Task {
    param(
        [string]$Title,
        [string]$Description,
        [string]$AcceptanceCriteria,
        [int]$EpicId,
        [int]$EstimateMinutes,
        [string]$Priority = "2",  # 1=High, 2=Medium, 3=Low
        [string]$Iteration = ""
    )
    
    $fullDescription = @"
$Description

## ✅ Criterios de Aceptación
$AcceptanceCriteria

## ⏱️ Estimación
$EstimateMinutes minutos

Ver detalles en: EPICA_DEPLOYMENT_AZURE_ESTUDIANTES.md
"@
    
    $task = az boards work-item create `
        --title $Title `
        --type "Task" `
        --project $PROJECT_NAME `
        --area $AREA_PATH `
        --description $fullDescription `
        --output json | ConvertFrom-Json
    
    # Vincular con Epic
    az boards work-item relation add `
        --id $task.id `
        --relation-type "Parent" `
        --target-id $EpicId `
        --project $PROJECT_NAME `
        --output none
    
    # Configurar prioridad
    az boards work-item update `
        --id $task.id `
        --project $PROJECT_NAME `
        --fields "Microsoft.VSTS.Common.Priority=$Priority" `
        --output none
    
    Write-Host "  ✅ Tarea creada: #$($task.id) - $Title" -ForegroundColor Green
    
    return $task.id
}

# =============================================================================
# DEFINICIÓN DE TAREAS
# =============================================================================

$tasks = @(
    # FASE 1: Preparación del Código
    @{
        Title = "T-DEPLOY-001: Crear archivo startup.sh para Backend"
        Description = "Crear script de arranque para App Service que ejecute migraciones y lance Gunicorn"
        AcceptanceCriteria = @"
- Archivo backend/startup.sh creado
- Script ejecuta migraciones de Alembic
- Script inicia Gunicorn con configuración correcta
- Configuración para 1 worker (límite F1)
- Logs informativos de arranque
"@
        EstimateMinutes = 15
        Priority = "1"
    },
    @{
        Title = "T-DEPLOY-002: Actualizar requirements.txt"
        Description = "Agregar Gunicorn y PyMySQL para producción en Azure"
        AcceptanceCriteria = @"
- gunicorn==21.2.0 agregado
- pymysql==1.1.0 agregado
- cryptography>=41.0.0 agregado
- Dependencias instalables sin errores
"@
        EstimateMinutes = 10
        Priority = "1"
    },
    @{
        Title = "T-DEPLOY-003: Configurar Next.js para Azure"
        Description = "Verificar configuración de Next.js para deployment sin Docker"
        AcceptanceCriteria = @"
- output: 'standalone' configurado
- Variables de entorno públicas configuradas
- Build scripts verificados
- Puerto configurado correctamente
"@
        EstimateMinutes = 15
        Priority = "1"
    },
    @{
        Title = "T-DEPLOY-004: Crear archivo .deployment"
        Description = "Crear configuración para indicar a App Service cómo deployar"
        AcceptanceCriteria = @"
- Archivo .deployment creado en raíz
- Configuración apunta a proyecto correcto
"@
        EstimateMinutes = 5
        Priority = "2"
    },
    @{
        Title = "T-DEPLOY-005: Crear .env.production.example"
        Description = "Crear archivo de ejemplo con variables de entorno para producción"
        AcceptanceCriteria = @"
- Archivo .env.production.example creado
- Todas las variables documentadas
- Placeholders para valores sensibles
- Comentarios explicativos
"@
        EstimateMinutes = 10
        Priority = "2"
    },
    
    # FASE 2: Infraestructura Azure
    @{
        Title = "T-DEPLOY-006: Verificar cuenta Azure for Students"
        Description = "Verificar cuenta activa y créditos disponibles"
        AcceptanceCriteria = @"
- Azure CLI instalado
- Autenticación exitosa
- Suscripción Azure for Students verificada
- Créditos disponibles confirmados
"@
        EstimateMinutes = 5
        Priority = "1"
    },
    @{
        Title = "T-DEPLOY-007: Ejecutar script de deployment"
        Description = "Ejecutar deploy-academic-demo.ps1 para crear recursos"
        AcceptanceCriteria = @"
- Resource Group creado
- Storage Account creado (5 GB gratis)
- MySQL Database creado (750 hrs/mes)
- App Service Plan F1 creado
- Backend y Frontend Apps creados
- Variables de entorno configuradas
- Alertas de presupuesto configuradas
"@
        EstimateMinutes = 45
        Priority = "1"
    },
    @{
        Title = "T-DEPLOY-008: Configurar CORS en Blob Storage"
        Description = "Configurar políticas CORS para permitir subida de imágenes"
        AcceptanceCriteria = @"
- Regla CORS creada para frontend
- Métodos PUT, POST, GET permitidos
- Headers necesarios configurados
- Max age configurado
"@
        EstimateMinutes = 10
        Priority = "1"
    },
    @{
        Title = "T-DEPLOY-009: Configurar conexión segura MySQL"
        Description = "Configurar firewall de MySQL y verificar SSL"
        AcceptanceCriteria = @"
- Regla de firewall para Azure Services habilitada
- SSL obligatorio configurado
- Conexión desde App Service verificada
- Database creada
"@
        EstimateMinutes = 15
        Priority = "1"
    },
    
    # FASE 3: Deployment de Aplicaciones
    @{
        Title = "T-DEPLOY-010: Preparar GitHub Actions"
        Description = "Configurar CI/CD con GitHub Actions para deployment automático"
        AcceptanceCriteria = @"
- Workflow YAML creado
- Secrets de GitHub configurados
- Deploy profile descargado
- Trigger en push a main configurado
"@
        EstimateMinutes = 20
        Priority = "1"
    },
    @{
        Title = "T-DEPLOY-011: Deploy manual inicial Backend"
        Description = "Realizar primer deployment manual del backend"
        AcceptanceCriteria = @"
- Código comprimido y subido
- startup.sh ejecutándose
- Migraciones aplicadas
- Endpoint /health responde
- Logs sin errores críticos
"@
        EstimateMinutes = 20
        Priority = "1"
    },
    @{
        Title = "T-DEPLOY-012: Deploy manual inicial Frontend"
        Description = "Realizar primer deployment manual del frontend"
        AcceptanceCriteria = @"
- Build de Next.js exitoso
- Código comprimido y subido
- Variables de entorno configuradas
- Página principal carga
- Conexión con backend funcional
"@
        EstimateMinutes = 20
        Priority = "1"
    },
    @{
        Title = "T-DEPLOY-013: Migrar datos a MySQL Azure"
        Description = "Migrar datos desde base local a MySQL en Azure"
        AcceptanceCriteria = @"
- Backup de BD local creado
- Datos exportados en formato compatible
- Datos importados en MySQL Azure
- Integridad de datos verificada
- Usuarios de prueba funcionando
"@
        EstimateMinutes = 30
        Priority = "2"
    },
    @{
        Title = "T-DEPLOY-014: Migrar imágenes a Blob Storage"
        Description = "Migrar imágenes desde Azurite a Azure Blob Storage"
        AcceptanceCriteria = @"
- Script de migración creado
- Imágenes copiadas a Azure
- URLs actualizadas en BD
- Imágenes accesibles desde frontend
"@
        EstimateMinutes = 20
        Priority = "2"
    },
    
    # FASE 4: Verificación y Pruebas
    @{
        Title = "T-DEPLOY-015: Verificar endpoints Backend"
        Description = "Verificar que todos los endpoints críticos funcionan"
        AcceptanceCriteria = @"
- /health responde correctamente
- /api/auth/register funciona
- /api/auth/login funciona
- /api/imagenes/upload funciona
- CORS configurado correctamente
- Sin errores en logs
"@
        EstimateMinutes = 20
        Priority = "1"
    },
    @{
        Title = "T-DEPLOY-016: Verificar funcionamiento Frontend"
        Description = "Verificar frontend y comunicación con backend"
        AcceptanceCriteria = @"
- Página principal carga sin errores
- Login funciona
- Dashboard carga después de login
- Subida de imágenes funciona
- Sin errores de CORS en consola
- Estilos Tailwind aplicados
"@
        EstimateMinutes = 15
        Priority = "1"
    },
    @{
        Title = "T-DEPLOY-017: Prueba end-to-end completa"
        Description = "Realizar flujo completo desde registro hasta identificación"
        AcceptanceCriteria = @"
- Registro de usuario exitoso
- Login exitoso
- Subida de imagen funciona
- Identificación funciona (si API configurada)
- Datos persisten en MySQL
- Imágenes persisten en Blob Storage
"@
        EstimateMinutes = 30
        Priority = "1"
    },
    
    # FASE 5: Controles de Gasto
    @{
        Title = "T-DEPLOY-018: Configurar alertas de presupuesto"
        Description = "Configurar alertas automáticas de presupuesto"
        AcceptanceCriteria = @"
- Alerta configurada en `$5 USD
- Alerta configurada en `$10 USD
- Email de notificación configurado
- Alertas visibles en Azure Portal
"@
        EstimateMinutes = 15
        Priority = "1"
    },
    @{
        Title = "T-DEPLOY-019: Configurar Application Insights"
        Description = "Configurar monitoreo avanzado (opcional, tier gratuito)"
        AcceptanceCriteria = @"
- Application Insights creado
- Conectado a Backend App Service
- Conectado a Frontend App Service
- Dashboard de métricas visible
- Dentro del tier gratuito (5 GB/mes)
"@
        EstimateMinutes = 20
        Priority = "3"
    },
    @{
        Title = "T-DEPLOY-020: Crear script monitoreo costos"
        Description = "Crear script para verificar costos acumulados"
        AcceptanceCriteria = @"
- Script PowerShell creado
- Muestra costos del mes actual
- Muestra costos por recurso
- Muestra créditos restantes (estimado)
"@
        EstimateMinutes = 15
        Priority = "2"
    },
    
    # FASE 6: Documentación
    @{
        Title = "T-DEPLOY-021: Documentar URLs y credenciales"
        Description = "Crear documento con URLs, credenciales y datos importantes"
        AcceptanceCriteria = @"
- Documento DEPLOYMENT_INFO.md creado
- URLs documentadas
- Credenciales guardadas de forma segura
- Connection strings documentados
- Comandos útiles incluidos
"@
        EstimateMinutes = 15
        Priority = "1"
    },
    @{
        Title = "T-DEPLOY-022: Crear guía troubleshooting"
        Description = "Documentar problemas comunes y soluciones"
        AcceptanceCriteria = @"
- Documento TROUBLESHOOTING.md creado
- Al menos 10 problemas documentados
- Soluciones paso a paso incluidas
- Comandos de diagnóstico incluidos
"@
        EstimateMinutes = 20
        Priority = "2"
    },
    @{
        Title = "T-DEPLOY-023: Preparar presentación demo"
        Description = "Crear slide deck para presentar el proyecto"
        AcceptanceCriteria = @"
- Presentación PowerPoint/PDF creada
- Arquitectura explicada
- Demo flow definido
- Screenshots incluidos
- Costos y servicios documentados
"@
        EstimateMinutes = 30
        Priority = "2"
    },
    @{
        Title = "T-DEPLOY-024: Crear video demo"
        Description = "Grabar video demo de 3-5 minutos (opcional)"
        AcceptanceCriteria = @"
- Video de 3-5 minutos grabado
- Flujo completo demostrado
- Narración en español
- Calidad 1080p mínimo
- Subido a YouTube/Drive
"@
        EstimateMinutes = 45
        Priority = "3"
    },
    
    # FASE 7: Post-Demo
    @{
        Title = "T-DEPLOY-025: Apagar servicios post-presentación"
        Description = "Apagar servicios para conservar créditos"
        AcceptanceCriteria = @"
- Backend App Service detenido
- Frontend App Service detenido
- MySQL Server detenido
- Confirmación de estado detenido
- Costo después: `$0/día
"@
        EstimateMinutes = 5
        Priority = "1"
    },
    @{
        Title = "T-DEPLOY-026: Eliminar recursos (opcional)"
        Description = "Eliminar permanentemente si ya no se necesitan"
        AcceptanceCriteria = @"
- Backup de datos realizado
- Confirmación del usuario obtenida
- Resource Group eliminado
- Recursos ya no aparecen en Portal
"@
        EstimateMinutes = 5
        Priority = "3"
    }
)

# =============================================================================
# MAIN
# =============================================================================

function Main {
    Show-Welcome
    
    # Verificar conexión
    if (-not (Test-AzureDevOpsConnection)) {
        Write-Host "⚠️  No estás conectado a Azure DevOps`n" -ForegroundColor Yellow
        
        $configure = Read-Host "¿Quieres configurar la conexión ahora? (s/n)"
        if ($configure -eq "s") {
            Configure-AzureDevOps
        }
        else {
            Write-Host "`n❌ No se puede continuar sin conexión a Azure DevOps" -ForegroundColor Red
            Write-Host "`nPara configurar manualmente:`n" -ForegroundColor Yellow
            Write-Host "1. Crea un PAT en: $ORGANIZATION_URL/_usersSettings/tokens" -ForegroundColor Gray
            Write-Host "2. Ejecuta: echo <TU_PAT> | az devops login --organization $ORGANIZATION_URL" -ForegroundColor Gray
            Write-Host "3. Ejecuta: az devops configure --defaults organization=$ORGANIZATION_URL project=$PROJECT_NAME`n" -ForegroundColor Gray
            exit 1
        }
    }
    
    # Crear Epic
    Write-Host "`n📝 Creando épica y tareas en Azure DevOps...`n" -ForegroundColor Cyan
    $epicId = Create-Epic
    
    # Crear tareas
    Write-Host "`n📋 Creando $($tasks.Count) tareas...`n" -ForegroundColor Yellow
    
    $createdTasks = @()
    foreach ($task in $tasks) {
        $taskId = Create-Task `
            -Title $task.Title `
            -Description $task.Description `
            -AcceptanceCriteria $task.AcceptanceCriteria `
            -EpicId $epicId `
            -EstimateMinutes $task.EstimateMinutes `
            -Priority $task.Priority
        
        $createdTasks += $taskId
        Start-Sleep -Milliseconds 500  # Evitar rate limiting
    }
    
    # Resumen
    Write-Host "`n╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║              ÉPICA CREADA EXITOSAMENTE                   ║" -ForegroundColor Green
    Write-Host "╚═══════════════════════════════════════════════════════════╝`n" -ForegroundColor Green
    
    Write-Host "📊 Resumen:" -ForegroundColor Cyan
    Write-Host "   • Épica: #$epicId" -ForegroundColor White
    Write-Host "   • Tareas creadas: $($createdTasks.Count)" -ForegroundColor White
    Write-Host "   • Tiempo total estimado: 6-8 horas" -ForegroundColor White
    Write-Host "   • Costo estimado: `$0/mes`n" -ForegroundColor White
    
    Write-Host "🔗 Ver en Azure DevOps:" -ForegroundColor Cyan
    Write-Host "   $ORGANIZATION_URL/$PROJECT_NAME/_workitems/edit/$epicId`n" -ForegroundColor Yellow
    
    Write-Host "✅ Ahora puedes gestionar las tareas desde Azure Boards" -ForegroundColor Green
    Write-Host "`n"
}

# Ejecutar script
Main
