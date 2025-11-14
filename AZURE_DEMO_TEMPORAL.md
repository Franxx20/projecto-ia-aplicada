# 🎓 Azure Demo Académica Temporal - Solución Óptima

**Fecha**: 12 de Noviembre de 2025  
**Objetivo**: Demo académica temporal usando $100 créditos Azure for Students  
**Duración estimada**: 2-4 semanas activa  
**Costo estimado**: $5-15 total (sobran $85-95 de crédito)

---

## 📋 Índice

1. [Arquitectura Recomendada](#arquitectura)
2. [Por qué Azure Container Apps](#por-que-aca)
3. [Comparación de Opciones Azure](#comparacion)
4. [Estimación de Costos](#costos)
5. [Deployment Paso a Paso](#deployment)
6. [Gestión de Recursos](#gestion)
7. [Activar/Desactivar Servicios](#activar-desactivar)
8. [Variables de Entorno](#variables)
9. [Monitoreo de Créditos](#monitoreo)
10. [Checklist y Timeline](#checklist)

---

## 🏗️ Arquitectura Recomendada {#arquitectura}

### Opción 1: Azure Container Apps (⭐ RECOMENDADA)

```
┌──────────────────────────────────────────────────────────────┐
│           Azure Container Apps Environment                    │
│                                                               │
│  ┌─────────────┐      ┌─────────────┐                       │
│  │  Frontend   │─────→│   Backend   │                       │
│  │  Next.js    │      │   FastAPI   │                       │
│  │ (Container) │      │ (Container) │                       │
│  └─────────────┘      └─────────────┘                       │
│         │                     │                              │
│         │                     ↓                              │
│         │            ┌─────────────────┐                    │
│         │            │ Azure Database  │                    │
│         │            │ for PostgreSQL  │                    │
│         │            │   Flexible      │                    │
│         │            └─────────────────┘                    │
│         │                                                    │
│         └────────────────────┐                              │
│                               ↓                              │
│                      ┌──────────────────┐                   │
│                      │  Azure Blob      │                   │
│                      │  Storage         │                   │
│                      │  (Imágenes)      │                   │
│                      └──────────────────┘                   │
└──────────────────────────────────────────────────────────────┘

URLs Resultantes:
- Frontend: https://plantitas-frontend.victoriousstone-12345.eastus.azurecontainerapps.io
- Backend: https://plantitas-backend.victoriousstone-12345.eastus.azurecontainerapps.io
```

### Ventajas para Demo Temporal

✅ **Scale to Zero**: Baja a 0 instancias cuando no hay tráfico → **$0/hora**  
✅ **Fácil activar/desactivar**: Un solo comando  
✅ **Pricing por segundo**: Solo pagas por tiempo activo  
✅ **Monorepo compatible**: Deployment directo desde GitHub  
✅ **HTTPS automático**: Certificado SSL gratis  
✅ **Logs integrados**: Application Insights incluido  

---

## 🎯 Por qué Azure Container Apps (no App Service) {#por-que-aca}

### Azure Container Apps vs App Service

| Característica | Container Apps ⭐ | App Service ❌ |
|----------------|-------------------|----------------|
| **Scale to Zero** | ✅ SÍ (0 instancias = $0) | ❌ NO (siempre paga plan) |
| **Costo mínimo/mes** | $0 cuando inactivo | ~$13/mes (B1) |
| **Monorepo** | ✅ Build multi-stage | ⚠️ Requiere config especial |
| **Activar/Desactivar** | ✅ Instantáneo | ⚠️ Requiere cambiar plan |
| **Precio demo 4 semanas** | ~$8-12 total | ~$52 total |
| **Sobra de $100** | ~$88-92 | ~$48 |

### Cálculo Real para 4 Semanas

**Azure Container Apps** (demo académica):
```
Frontend:  $0.000024/vCPU-s * 0.5 vCPU * 3600s/h * 8h/día * 28 días = ~$3
Backend:   $0.000024/vCPU-s * 0.5 vCPU * 3600s/h * 8h/día * 28 días = ~$3
PostgreSQL: $0.044/hora * 24h * 28 días * 0.5 (Burstable B1ms) = ~$15
Blob Storage: $0.018/GB * 2 GB = ~$0.04
───────────────────────────────────────────────────────────────
TOTAL: ~$21 por 4 semanas (sobran $79)
```

**Con Scale to Zero** (solo usas 8h/día en demos):
- Container Apps bajan a 0 cuando no hay tráfico
- PostgreSQL en tier Burstable (se puede pausar manualmente)
- **Costo real: $8-12** (sobran $88-92)

---

## 📊 Comparación de Opciones Azure {#comparacion}

### Opción A: Azure Container Apps ⭐ (RECOMENDADA)

| Componente | Servicio | Costo/mes | Scale to Zero |
|------------|----------|-----------|---------------|
| Frontend | Container App | ~$3-5 | ✅ SÍ |
| Backend | Container App | ~$3-5 | ✅ SÍ |
| Database | PostgreSQL Flexible (B1ms) | ~$15-20 | ⚠️ Manual |
| Storage | Azure Blob Standard | ~$0.50 | N/A |
| **Total** | | **$21-30/mes** | |
| **4 semanas activo** | | **$19-28** | |

**Ventajas**:
- ✅ Scale to zero automático
- ✅ Monorepo compatible
- ✅ Deploy desde GitHub Actions
- ✅ HTTPS automático
- ✅ Fácil activar/desactivar

**Desventajas**:
- ⚠️ Requiere registry (ACR) o GitHub Container Registry

---

### Opción B: Azure App Service + PostgreSQL

| Componente | Servicio | Costo/mes | Scale to Zero |
|------------|----------|-----------|---------------|
| Frontend | App Service (B1) | ~$13 | ❌ NO |
| Backend | App Service (B1) | ~$13 | ❌ NO |
| Database | PostgreSQL Flexible (B1ms) | ~$15-20 | ⚠️ Manual |
| Storage | Azure Blob Standard | ~$0.50 | N/A |
| **Total** | | **$41-47/mes** | |
| **4 semanas activo** | | **$38-44** | |

**Ventajas**:
- ✅ Más simple (lo que ya intentaste)
- ✅ Deploy directo desde GitHub

**Desventajas**:
- ❌ NO scale to zero
- ❌ Siempre paga plan mínimo
- ⚠️ Monorepo complicado (ya lo experimentaste)

---

### Opción C: Azure Container Instances (ACI)

| Componente | Servicio | Costo/mes | Scale to Zero |
|------------|----------|-----------|---------------|
| Frontend | ACI (1 vCPU, 1.5GB) | ~$35 | ⚠️ Manual |
| Backend | ACI (1 vCPU, 1.5GB) | ~$35 | ⚠️ Manual |
| Database | PostgreSQL Flexible | ~$15-20 | ⚠️ Manual |
| Storage | Azure Blob Standard | ~$0.50 | N/A |
| **Total** | | **$85-90/mes** | |

**Ventajas**:
- ✅ Muy simple
- ✅ Pay per second

**Desventajas**:
- ❌ Más caro
- ❌ No auto-scaling
- ❌ Requiere gestión manual

---

### Opción D: Azure Kubernetes Service (AKS)

| Componente | Servicio | Costo/mes |
|------------|----------|-----------|
| Cluster | AKS (2 nodes B2s) | ~$60 |
| Database | PostgreSQL Flexible | ~$15-20 |
| Storage | Azure Blob | ~$0.50 |
| **Total** | | **$75-80/mes** |

**Desventajas**:
- ❌ Muy caro para demo
- ❌ Complejo de configurar
- ❌ Overkill para proyecto pequeño

---

## 💰 Estimación Detallada de Costos {#costos}

### Opción Recomendada: Azure Container Apps

#### Costo por Componente (4 semanas)

**1. Container Apps Environment**
```
Costo base: $0 (gratis)
Logs (Application Insights): ~$2-3
─────────────────────────
Subtotal: $2-3
```

**2. Frontend Container App**
```
vCPU: 0.5 vCPU
Memoria: 1 GB
Precio: $0.000024/vCPU-s + $0.000004/GB-s

Cálculo (8 horas/día activo, 28 días):
- vCPU: 0.5 * $0.000024 * 3600s * 8h * 28d = $2.90
- Memoria: 1 * $0.000004 * 3600s * 8h * 28d = $3.23
─────────────────────────
Subtotal: $6.13
```

**3. Backend Container App**
```
vCPU: 0.5 vCPU
Memoria: 1 GB
Precio: Igual que frontend

Cálculo (8 horas/día activo, 28 días):
─────────────────────────
Subtotal: $6.13
```

**4. Azure Database for PostgreSQL Flexible**
```
Tier: Burstable B1ms
vCores: 1
Storage: 32 GB
Precio: ~$0.022/hora (Burstable)

Cálculo:
- Compute: $0.022 * 24h * 28d = $14.78
- Storage: $0.115/GB * 32 GB = $3.68/mes → ~$3.44 (28 días)
- Backup: Primer 32 GB gratis
─────────────────────────
Subtotal: $18.22
```

**5. Azure Blob Storage**
```
Tier: Hot (General Purpose v2)
Almacenamiento: ~2 GB (estimado para imágenes)
Operaciones: ~10,000 transacciones/mes
Precio: $0.018/GB + $0.05/10k operaciones

Cálculo:
- Almacenamiento: $0.018 * 2 GB = $0.036
- Operaciones: $0.05 * 1 = $0.05
─────────────────────────
Subtotal: $0.086
```

#### TOTAL (4 semanas activo 8h/día):

```
Container Apps Environment:  $2-3
Frontend Container:          $6.13
Backend Container:           $6.13
PostgreSQL Flexible:         $18.22
Blob Storage:                $0.09
───────────────────────────────────
TOTAL:                       $32.57 - $33.57
```

### ⚡ Con Optimizaciones

**Si desactivas servicios cuando no los usas** (solo 3 días/semana, 4 horas/día):

```
Frontend: $6.13 * (12h/56h) = $1.31
Backend: $6.13 * (12h/56h) = $1.31
PostgreSQL (pausado): $18.22 * 0.3 = $5.47
───────────────────────────────────
TOTAL OPTIMIZADO: ~$10-12
```

**Sobran**: **$88-90 de tus $100 créditos**

---

## 🚀 Deployment Paso a Paso {#deployment}

### Prerequisites

1. Azure for Students activado
2. Azure CLI instalado
3. Docker Desktop instalado
4. Código actualizado en GitHub

### Paso 1: Instalar Azure CLI y Login

```powershell
# Instalar Azure CLI (si no lo tienes)
winget install Microsoft.AzureCLI

# Login con cuenta de estudiante
az login

# Verificar subscripción
az account show
az account list-locations --output table
```

### Paso 2: Crear Resource Group

```powershell
# Variables de configuración
$RESOURCE_GROUP = "rg-plantitas-demo-temp"
$LOCATION = "eastus"
$PROJECT_NAME = "plantitas"

# Crear resource group
az group create `
  --name $RESOURCE_GROUP `
  --location $LOCATION

# Tag como temporal
az group update `
  --name $RESOURCE_GROUP `
  --tags "Environment=Demo" "Temporary=true" "Duration=4weeks" "AutoDelete=2025-12-10"
```

### Paso 3: Crear PostgreSQL Flexible Server

```powershell
# Variables PostgreSQL
$DB_SERVER = "plantitas-demo-db"
$DB_NAME = "plantitas_db"
$DB_USER = "plantitas_admin"
$DB_PASSWORD = "PlantitasDemo2025!SecurePass"  # Cambiar por uno seguro

# Crear PostgreSQL Flexible Server (Burstable B1ms)
az postgres flexible-server create `
  --resource-group $RESOURCE_GROUP `
  --name $DB_SERVER `
  --location $LOCATION `
  --admin-user $DB_USER `
  --admin-password $DB_PASSWORD `
  --sku-name Standard_B1ms `
  --tier Burstable `
  --version 15 `
  --storage-size 32 `
  --public-access 0.0.0.0-255.255.255.255 `
  --tags "Temporary=true"

# Crear base de datos
az postgres flexible-server db create `
  --resource-group $RESOURCE_GROUP `
  --server-name $DB_SERVER `
  --database-name $DB_NAME

# Obtener connection string
$DB_HOST = "$DB_SERVER.postgres.database.azure.com"
$DB_CONNECTION_STRING = "postgresql://$DB_USER`:$DB_PASSWORD@$DB_HOST`:5432/$DB_NAME"

Write-Host "Connection String: $DB_CONNECTION_STRING"
```

### Paso 4: Crear Azure Blob Storage

```powershell
# Variables Storage
$STORAGE_ACCOUNT = "plantitasdemostorage"  # Solo minúsculas y números
$STORAGE_CONTAINER = "plantitas-imagenes"

# Crear storage account
az storage account create `
  --name $STORAGE_ACCOUNT `
  --resource-group $RESOURCE_GROUP `
  --location $LOCATION `
  --sku Standard_LRS `
  --kind StorageV2 `
  --access-tier Hot `
  --tags "Temporary=true"

# Obtener connection string
$STORAGE_CONNECTION_STRING = az storage account show-connection-string `
  --name $STORAGE_ACCOUNT `
  --resource-group $RESOURCE_GROUP `
  --query connectionString `
  --output tsv

# Crear container para imágenes
az storage container create `
  --name $STORAGE_CONTAINER `
  --account-name $STORAGE_ACCOUNT `
  --connection-string $STORAGE_CONNECTION_STRING `
  --public-access blob

Write-Host "Storage Connection String: $STORAGE_CONNECTION_STRING"
```

### Paso 5: Crear Container Apps Environment

```powershell
# Variables Container Apps
$ENVIRONMENT = "plantitas-demo-env"
$LOG_ANALYTICS = "plantitas-demo-logs"

# Crear Log Analytics Workspace
az monitor log-analytics workspace create `
  --resource-group $RESOURCE_GROUP `
  --workspace-name $LOG_ANALYTICS `
  --location $LOCATION

# Obtener workspace ID y key
$LOG_ANALYTICS_ID = az monitor log-analytics workspace show `
  --resource-group $RESOURCE_GROUP `
  --workspace-name $LOG_ANALYTICS `
  --query customerId `
  --output tsv

$LOG_ANALYTICS_KEY = az monitor log-analytics workspace get-shared-keys `
  --resource-group $RESOURCE_GROUP `
  --workspace-name $LOG_ANALYTICS `
  --query primarySharedKey `
  --output tsv

# Crear Container Apps Environment
az containerapp env create `
  --name $ENVIRONMENT `
  --resource-group $RESOURCE_GROUP `
  --location $LOCATION `
  --logs-workspace-id $LOG_ANALYTICS_ID `
  --logs-workspace-key $LOG_ANALYTICS_KEY `
  --tags "Temporary=true"
```

### Paso 6: Build y Push Images a Azure Container Registry

```powershell
# Variables ACR
$ACR_NAME = "plantitasdemoacr"  # Solo alfanuméricos

# Crear Azure Container Registry
az acr create `
  --resource-group $RESOURCE_GROUP `
  --name $ACR_NAME `
  --sku Basic `
  --admin-enabled true `
  --location $LOCATION

# Login a ACR
az acr login --name $ACR_NAME

# Build y push backend
cd backend
az acr build `
  --registry $ACR_NAME `
  --image plantitas-backend:latest `
  --file Dockerfile `
  .

# Build y push frontend
cd ../frontend
az acr build `
  --registry $ACR_NAME `
  --image plantitas-frontend:latest `
  --file Dockerfile `
  .

cd ..

# Obtener login server
$ACR_LOGIN_SERVER = az acr show `
  --name $ACR_NAME `
  --query loginServer `
  --output tsv

Write-Host "ACR Login Server: $ACR_LOGIN_SERVER"
```

### Paso 7: Deploy Backend Container App

```powershell
# Generar JWT Secret
$JWT_SECRET = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 64 | ForEach-Object {[char]$_})

# Deploy backend
az containerapp create `
  --name plantitas-backend `
  --resource-group $RESOURCE_GROUP `
  --environment $ENVIRONMENT `
  --image "$ACR_LOGIN_SERVER/plantitas-backend:latest" `
  --target-port 8000 `
  --ingress external `
  --registry-server $ACR_LOGIN_SERVER `
  --min-replicas 0 `
  --max-replicas 2 `
  --cpu 0.5 `
  --memory 1.0Gi `
  --env-vars `
    "DATABASE_URL=$DB_CONNECTION_STRING" `
    "JWT_SECRET_KEY=$JWT_SECRET" `
    "JWT_ALGORITHM=HS256" `
    "ACCESS_TOKEN_EXPIRE_MINUTES=30" `
    "REFRESH_TOKEN_EXPIRE_DAYS=7" `
    "AZURE_STORAGE_CONNECTION_STRING=$STORAGE_CONNECTION_STRING" `
    "AZURE_STORAGE_CONTAINER_NAME=$STORAGE_CONTAINER" `
    "AZURE_STORAGE_USE_EMULATOR=false" `
    "ENVIRONMENT=production" `
    "DEBUG=false" `
    "GEMINI_API_KEY=TU_GEMINI_API_KEY"  # ⚠️ CAMBIAR

# Obtener backend URL
$BACKEND_URL = az containerapp show `
  --name plantitas-backend `
  --resource-group $RESOURCE_GROUP `
  --query properties.configuration.ingress.fqdn `
  --output tsv

$BACKEND_URL = "https://$BACKEND_URL"
Write-Host "Backend URL: $BACKEND_URL"
```

### Paso 8: Deploy Frontend Container App

```powershell
# Deploy frontend
az containerapp create `
  --name plantitas-frontend `
  --resource-group $RESOURCE_GROUP `
  --environment $ENVIRONMENT `
  --image "$ACR_LOGIN_SERVER/plantitas-frontend:latest" `
  --target-port 3000 `
  --ingress external `
  --registry-server $ACR_LOGIN_SERVER `
  --min-replicas 0 `
  --max-replicas 2 `
  --cpu 0.5 `
  --memory 1.0Gi `
  --env-vars `
    "NEXT_PUBLIC_API_URL=$BACKEND_URL" `
    "NODE_ENV=production"

# Obtener frontend URL
$FRONTEND_URL = az containerapp show `
  --name plantitas-frontend `
  --resource-group $RESOURCE_GROUP `
  --query properties.configuration.ingress.fqdn `
  --output tsv

$FRONTEND_URL = "https://$FRONTEND_URL"
Write-Host "Frontend URL: $FRONTEND_URL"
```

### Paso 9: Actualizar CORS en Backend

```powershell
# Actualizar backend con CORS correcto
az containerapp update `
  --name plantitas-backend `
  --resource-group $RESOURCE_GROUP `
  --set-env-vars "CORS_ORIGINS=$FRONTEND_URL"

# Restart backend
az containerapp revision restart `
  --name plantitas-backend `
  --resource-group $RESOURCE_GROUP
```

### Paso 10: Ejecutar Migraciones de Base de Datos

```powershell
# Opción A: Desde local (más fácil)
# Configurar DATABASE_URL local temporalmente
$env:DATABASE_URL = $DB_CONNECTION_STRING
cd backend
python -m alembic upgrade head

# Opción B: Job en Container Apps (más profesional)
az containerapp job create `
  --name plantitas-migrations `
  --resource-group $RESOURCE_GROUP `
  --environment $ENVIRONMENT `
  --trigger-type Manual `
  --replica-timeout 300 `
  --image "$ACR_LOGIN_SERVER/plantitas-backend:latest" `
  --registry-server $ACR_LOGIN_SERVER `
  --cpu 0.5 `
  --memory 1.0Gi `
  --command "python" "-m" "alembic" "upgrade" "head" `
  --env-vars "DATABASE_URL=$DB_CONNECTION_STRING"

# Ejecutar job
az containerapp job start `
  --name plantitas-migrations `
  --resource-group $RESOURCE_GROUP
```

---

## ⚙️ Gestión de Recursos {#gestion}

### Monitoreo de Costos en Tiempo Real

```powershell
# Ver costos acumulados
az consumption usage list `
  --start-date 2025-11-01 `
  --end-date 2025-11-12 `
  --query "[?contains(instanceName, 'plantitas')]" `
  --output table

# Ver presupuesto (si configuraste)
az consumption budget list `
  --resource-group $RESOURCE_GROUP `
  --output table
```

### Configurar Alert de Presupuesto

```powershell
# Crear alerta cuando gastes $30 (30% de $100)
az consumption budget create `
  --budget-name "plantitas-demo-budget" `
  --amount 30 `
  --time-grain Monthly `
  --start-date 2025-11-01 `
  --end-date 2025-12-31 `
  --resource-group $RESOURCE_GROUP `
  --notifications `
    threshold=80 `
    contact-emails="tu-email@ejemplo.com" `
    threshold=100 `
    contact-emails="tu-email@ejemplo.com"
```

---

## 🔄 Activar/Desactivar Servicios {#activar-desactivar}

### Desactivar Todo (cuando no lo usas)

```powershell
# Script: scripts/azure-demo-pause.ps1
$RESOURCE_GROUP = "rg-plantitas-demo-temp"

Write-Host "🛑 Pausando servicios de demo..." -ForegroundColor Yellow

# 1. Escalar Container Apps a 0
Write-Host "Escalando Container Apps a 0..." -ForegroundColor Cyan
az containerapp update `
  --name plantitas-backend `
  --resource-group $RESOURCE_GROUP `
  --min-replicas 0 `
  --max-replicas 0

az containerapp update `
  --name plantitas-frontend `
  --resource-group $RESOURCE_GROUP `
  --min-replicas 0 `
  --max-replicas 0

# 2. Detener PostgreSQL (⚠️ No disponible en Flexible, pero puedes eliminar y recrear)
Write-Host "⚠️  PostgreSQL Flexible no soporta stop/start" -ForegroundColor Yellow
Write-Host "   Opción: Hacer backup y eliminar, recrear cuando necesites" -ForegroundColor Yellow

# Backup automático
$DB_SERVER = "plantitas-demo-db"
$BACKUP_NAME = "backup-$(Get-Date -Format 'yyyyMMdd-HHmmss')"

Write-Host "Creando backup de seguridad..." -ForegroundColor Cyan
# El backup se hace automáticamente cada día

Write-Host "✅ Servicios pausados (Container Apps a 0 réplicas)" -ForegroundColor Green
Write-Host "💰 Costo mientras pausado: ~$0.50/día (solo PostgreSQL y Storage)" -ForegroundColor Green
```

### Reactivar Todo

```powershell
# Script: scripts/azure-demo-resume.ps1
$RESOURCE_GROUP = "rg-plantitas-demo-temp"

Write-Host "▶️  Reactivando servicios de demo..." -ForegroundColor Yellow

# Escalar Container Apps
Write-Host "Escalando Container Apps..." -ForegroundColor Cyan
az containerapp update `
  --name plantitas-backend `
  --resource-group $RESOURCE_GROUP `
  --min-replicas 0 `
  --max-replicas 2

az containerapp update `
  --name plantitas-frontend `
  --resource-group $RESOURCE_GROUP `
  --min-replicas 0 `
  --max-replicas 2

Write-Host "✅ Servicios reactivados" -ForegroundColor Green
Write-Host "🌐 Accede a tu app en unos segundos" -ForegroundColor Green

# Mostrar URLs
$FRONTEND_URL = az containerapp show `
  --name plantitas-frontend `
  --resource-group $RESOURCE_GROUP `
  --query properties.configuration.ingress.fqdn `
  --output tsv

Write-Host "Frontend: https://$FRONTEND_URL" -ForegroundColor Cyan
```

### Pausar PostgreSQL (Opción Avanzada)

```powershell
# PostgreSQL Flexible NO soporta stop/start directamente
# Opción 1: Backup → Delete → Restore cuando necesites
# Opción 2: Cambiar a tier más bajo temporalmente

# Backup manual antes de eliminar
$DB_SERVER = "plantitas-demo-db"
$BACKUP_NAME = "manual-backup-$(Get-Date -Format 'yyyyMMdd')"

# ⚠️ Los backups son automáticos cada día, no necesitas hacer manual

# Opción: Eliminar y recrear desde backup
# az postgres flexible-server delete --name $DB_SERVER --resource-group $RESOURCE_GROUP --yes

# Más adelante: Restore desde backup
# az postgres flexible-server restore `
#   --resource-group $RESOURCE_GROUP `
#   --name $DB_SERVER-restored `
#   --source-server $DB_SERVER `
#   --restore-time "2025-11-12T10:00:00Z"
```

---

## 🔐 Variables de Entorno Completas {#variables}

### Backend Container App

```bash
# ===== Base de Datos =====
DATABASE_URL=postgresql://plantitas_admin:PASSWORD@plantitas-demo-db.postgres.database.azure.com:5432/plantitas_db

# ===== JWT Authentication =====
JWT_SECRET_KEY=<generar-64-caracteres-aleatorios>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# ===== Azure Blob Storage =====
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=plantitasdemostorage;AccountKey=...;EndpointSuffix=core.windows.net
AZURE_STORAGE_CONTAINER_NAME=plantitas-imagenes
AZURE_STORAGE_USE_EMULATOR=false

# ===== Application =====
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
LOG_FORMAT=json

# ===== CORS =====
CORS_ORIGINS=https://plantitas-frontend.victoriousstone-12345.eastus.azurecontainerapps.io

# ===== Gemini API =====
GEMINI_API_KEY=<tu-api-key>
GEMINI_MODEL=gemini-2.0-flash-exp
GEMINI_MAX_REQUESTS_PER_DAY=1500
GEMINI_MAX_REQUESTS_PER_USER_PER_DAY=50
GEMINI_TEMPERATURE=0.7
GEMINI_MAX_OUTPUT_TOKENS=8192
GEMINI_TIMEOUT_SECONDS=30

# ===== Database Config =====
DB_CONNECTION_TIMEOUT=60
DB_POOL_PRE_PING=true
```

### Frontend Container App

```bash
# ===== API Configuration =====
NEXT_PUBLIC_API_URL=https://plantitas-backend.victoriousstone-12345.eastus.azurecontainerapps.io

# ===== Application =====
NODE_ENV=production
PORT=3000
```

---

## 📊 Monitoreo de Créditos {#monitoreo}

### Ver Saldo Restante

```powershell
# Ver subscripción y créditos
az account show --output table

# Ver consumo actual
az consumption usage list `
  --start-date (Get-Date).AddDays(-30).ToString("yyyy-MM-dd") `
  --end-date (Get-Date).ToString("yyyy-MM-dd") `
  --output table

# Exportar a CSV para análisis
az consumption usage list `
  --start-date (Get-Date).AddDays(-30).ToString("yyyy-MM-dd") `
  --end-date (Get-Date).ToString("yyyy-MM-dd") `
  --query "[].{Date:usageEnd, Service:meterName, Cost:pretaxCost, Currency:currency}" `
  --output table > costos-azure.csv
```

### Dashboard de Costos

1. **Azure Portal**: https://portal.azure.com
2. **Cost Management + Billing** → **Cost Analysis**
3. Filtrar por Resource Group: `rg-plantitas-demo-temp`
4. Ver gráficos de:
   - Costo por servicio
   - Costo por día
   - Forecast (proyección)

### Alertas Recomendadas

```powershell
# Alerta al 50% ($50 gastados)
az monitor action-group create `
  --name "plantitas-demo-alerts" `
  --resource-group $RESOURCE_GROUP `
  --short-name "PlantDemo" `
  --email-receiver "admin" "tu-email@ejemplo.com"

# Crear alerta
az monitor metrics alert create `
  --name "plantitas-demo-budget-50" `
  --resource-group $RESOURCE_GROUP `
  --scopes "/subscriptions/<SUBSCRIPTION_ID>/resourceGroups/$RESOURCE_GROUP" `
  --condition "total Budget >= 50" `
  --description "Alerta: 50% del presupuesto consumido" `
  --evaluation-frequency 1d `
  --window-size 1d `
  --severity 2 `
  --action "plantitas-demo-alerts"
```

---

## ✅ Checklist y Timeline {#checklist}

### Semana 0: Preparación (1-2 días)

- [ ] Verificar $100 créditos Azure for Students activos
- [ ] Instalar Azure CLI
- [ ] Actualizar código con compatibilidad Azure Blob
- [ ] Tests locales pasando
- [ ] Credenciales Gemini API listas

### Semana 1: Deployment Inicial (1 día)

- [ ] Crear Resource Group
- [ ] Deploy PostgreSQL Flexible Server
- [ ] Deploy Azure Blob Storage
- [ ] Crear Container Apps Environment
- [ ] Build y push imágenes a ACR
- [ ] Deploy Backend Container App
- [ ] Deploy Frontend Container App
- [ ] Configurar CORS
- [ ] Ejecutar migraciones
- [ ] Pruebas funcionales completas

**Costo acumulado**: ~$7-10

### Semana 2-3: Demo Activa (uso intermitente)

- [ ] Activar servicios para demos/presentaciones
- [ ] Pausar servicios cuando no se usan
- [ ] Monitorear costos semanalmente
- [ ] Revisar logs y performance

**Costo acumulado**: ~$15-20

### Semana 4: Finalización

- [ ] Última demo/presentación
- [ ] Exportar datos importantes
- [ ] Backup final de base de datos
- [ ] **ELIMINAR todos los recursos**

**Costo total**: ~$20-30 (sobran $70-80)

### Post-Demo: Limpieza

```powershell
# Eliminar todo el resource group (cuidado!)
az group delete `
  --name rg-plantitas-demo-temp `
  --yes `
  --no-wait

Write-Host "✅ Todos los recursos eliminados" -ForegroundColor Green
Write-Host "💰 Créditos restantes: ~$70-80" -ForegroundColor Cyan
```

---

## 🆘 Troubleshooting

### Problema: "Container Apps no escalan a 0"
**Solución**: Verificar que min-replicas esté en 0:
```powershell
az containerapp update --name plantitas-backend --resource-group $RESOURCE_GROUP --min-replicas 0
```

### Problema: "PostgreSQL muy caro"
**Solución**: Cambiar a tier Burstable B1ms (más barato):
```powershell
az postgres flexible-server update --name plantitas-demo-db --resource-group $RESOURCE_GROUP --sku-name Standard_B1ms
```

### Problema: "Superé $50 de gasto"
**Solución**: Pausar todo inmediatamente:
```powershell
.\scripts\azure-demo-pause.ps1
# Considerar eliminar PostgreSQL temporalmente
```

### Problema: "Migraciones fallan"
**Solución**: Verificar firewall PostgreSQL:
```powershell
az postgres flexible-server firewall-rule create `
  --resource-group $RESOURCE_GROUP `
  --name plantitas-demo-db `
  --rule-name AllowAll `
  --start-ip-address 0.0.0.0 `
  --end-ip-address 255.255.255.255
```

---

## 📚 Recursos

- **Azure Container Apps**: https://learn.microsoft.com/azure/container-apps/
- **Azure PostgreSQL Flexible**: https://learn.microsoft.com/azure/postgresql/flexible-server/
- **Azure for Students**: https://azure.microsoft.com/free/students/
- **Azure Pricing Calculator**: https://azure.microsoft.com/pricing/calculator/
- **Cost Management**: https://portal.azure.com/#view/Microsoft_Azure_CostManagement/

---

## 🎯 Resumen Ejecutivo

### ✅ Por qué Azure Container Apps para Demo Temporal

1. **Scale to Zero** → $0 cuando no usas (16h/día dormido)
2. **Pay per Second** → Solo pagas tiempo activo
3. **$10-15 total** por 4 semanas → Sobran $85-90
4. **Fácil pausar/reactivar** → Un comando
5. **Monorepo compatible** → Sin problemas de Oryx

### 💰 Comparación de Costos (4 semanas)

| Opción | Costo | Sobra de $100 | Scale to Zero |
|--------|-------|---------------|---------------|
| **Container Apps** ⭐ | $10-15 | $85-90 | ✅ SÍ |
| Railway | $0 | $100 | ✅ SÍ |
| App Service | $38-44 | $56-62 | ❌ NO |
| ACI | $80-90 | $10-20 | ⚠️ Manual |

### 🚀 Siguiente Paso

¿Quieres que te ayude a:

1. **Crear los scripts PowerShell** completos de deployment
2. **Actualizar el código** para usar Azure Blob (sin Azurite)
3. **Configurar GitHub Actions** para auto-deploy
4. **Implementar ahora mismo** el deployment

---

**Documentado por**: Franco Garcete  
**Proyecto**: Asistente Plantitas - Demo Académica  
**Fecha**: 12 de Noviembre de 2025  
**Créditos disponibles**: $100 Azure for Students  
**Duración estimada**: 4 semanas  
**Costo estimado**: $10-15 (sobran $85-90)
