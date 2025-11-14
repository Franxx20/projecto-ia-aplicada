# 🔐 Azure Environment Variables - Guía Completa

**Fecha**: 12 de Noviembre de 2025  
**Proyecto**: Asistente Plantitas - Demo Académica Azure  
**Deployment**: Azure Container Apps

---

## 📋 Índice

1. [Introducción](#introduccion)
2. [Variables por Servicio](#variables-por-servicio)
3. [Generación de Secrets](#generacion-secrets)
4. [Configuración en Azure](#configuracion-azure)
5. [Comandos Azure CLI](#comandos-cli)
6. [Validación](#validacion)
7. [Troubleshooting](#troubleshooting)

---

## 🎯 Introducción {#introduccion}

Este documento explica **todas las variables de entorno** necesarias para deployar el proyecto en Azure Container Apps.

### Arquitectura de Variables

```
┌─────────────────────────────────────────────────────────────┐
│                     Azure Portal                             │
│                                                              │
│  ┌──────────────┐           ┌──────────────┐               │
│  │   Backend    │◄─────────►│   Frontend   │               │
│  │ Container App│           │ Container App│               │
│  │              │           │              │               │
│  │ 15 vars      │           │ 3 vars       │               │
│  └──────────────┘           └──────────────┘               │
│         ▲                            │                      │
│         │                            │                      │
│         └────────────────────────────┘                      │
│                      │                                      │
│         ┌────────────▼──────────────┐                      │
│         │   Secrets Compartidos     │                      │
│         │   • DATABASE_URL          │                      │
│         │   • JWT_SECRET_KEY        │                      │
│         │   • GEMINI_API_KEY        │                      │
│         │   • STORAGE_CONNECTION    │                      │
│         └───────────────────────────┘                      │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 Variables por Servicio {#variables-por-servicio}

### 🔧 Backend Container App (15 variables)

#### 1. Database (PostgreSQL)

| Variable | Descripción | Ejemplo | Requerida |
|----------|-------------|---------|-----------|
| `DATABASE_URL` | Connection string completo de PostgreSQL | `postgresql://user:pass@host:5432/db` | ✅ Sí |
| `DB_CONNECTION_TIMEOUT` | Timeout de conexión en segundos | `60` | ⚠️ Opcional |
| `DB_POOL_PRE_PING` | Verificar conexión antes de usar | `true` | ⚠️ Opcional |

**Cómo obtener `DATABASE_URL`**:
```powershell
# Opción 1: Mostrar connection string template
az postgres flexible-server show-connection-string `
  --server-name plantitas-demo-db `
  --database-name plantitas_db

# Opción 2: Construir manualmente
$DB_USER = "plantitas_admin"
$DB_PASSWORD = "TuPassword123!"
$DB_HOST = "plantitas-demo-db.postgres.database.azure.com"
$DB_NAME = "plantitas_db"
$DATABASE_URL = "postgresql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:5432/${DB_NAME}?sslmode=require"
```

#### 2. Azure Blob Storage (4 variables)

| Variable | Descripción | Ejemplo | Requerida |
|----------|-------------|---------|-----------|
| `AZURE_STORAGE_CONNECTION_STRING` | Connection string de Storage Account | `DefaultEndpointsProtocol=https;AccountName=...` | ✅ Sí |
| `AZURE_STORAGE_CONTAINER_NAME` | Nombre del contenedor de blobs | `plantitas-imagenes` | ✅ Sí |
| `AZURE_STORAGE_USE_EMULATOR` | Usar emulador local (Azurite) | `false` (producción) | ✅ Sí |
| `AZURE_STORAGE_ACCOUNT_NAME` | Nombre de Storage Account | `plantitasdemostorage456` | ⚠️ Opcional* |
| `AZURE_STORAGE_ACCOUNT_KEY` | Key de Storage Account | `abc123...` | ⚠️ Opcional* |

*Solo si no usas `AZURE_STORAGE_CONNECTION_STRING`

**Cómo obtener connection string**:
```powershell
az storage account show-connection-string `
  --name plantitasdemostorage456 `
  --resource-group rg-plantitas-demo-temp `
  --query connectionString `
  --output tsv
```

#### 3. JWT Authentication (4 variables)

| Variable | Descripción | Ejemplo | Requerida |
|----------|-------------|---------|-----------|
| `JWT_SECRET_KEY` | Secret key para firmar tokens (64 chars) | `kJ8n2Hx9pLm4...` | ✅ Sí |
| `JWT_ALGORITHM` | Algoritmo de encriptación | `HS256` | ✅ Sí |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Expiración de access token (minutos) | `30` | ✅ Sí |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Expiración de refresh token (días) | `7` | ✅ Sí |

**Ver sección [Generación de Secrets](#generacion-secrets)**

#### 4. Application Settings (5 variables)

| Variable | Descripción | Valores permitidos | Requerida |
|----------|-------------|--------------------|-----------|
| `ENVIRONMENT` | Entorno de ejecución | `production`, `development`, `staging` | ✅ Sí |
| `DEBUG` | Modo debug (⚠️ false en prod) | `true`, `false` | ✅ Sí |
| `LOG_LEVEL` | Nivel de logging | `DEBUG`, `INFO`, `WARNING`, `ERROR` | ⚠️ Opcional |
| `LOG_FORMAT` | Formato de logs | `json`, `text` | ⚠️ Opcional |
| `MAX_TAMANO_ARCHIVO_MB` | Tamaño máximo de archivos (MB) | `10` | ⚠️ Opcional |

#### 5. CORS Configuration (1 variable)

| Variable | Descripción | Ejemplo | Requerida |
|----------|-------------|---------|-----------|
| `CORS_ORIGINS` | URLs permitidas (separadas por coma) | `https://frontend.azurecontainerapps.io` | ✅ Sí |

**⚠️ Importante**: Debes actualizar esta variable **después** de deployar el frontend con su URL real.

#### 6. Gemini API (6 variables)

| Variable | Descripción | Ejemplo | Requerida |
|----------|-------------|---------|-----------|
| `GEMINI_API_KEY` | API Key de Google Gemini | `AIzaSyABC123...` | ✅ Sí |
| `GEMINI_MODEL` | Modelo a usar | `gemini-2.0-flash-exp` | ✅ Sí |
| `GEMINI_MAX_REQUESTS_PER_DAY` | Límite de requests/día | `1500` | ⚠️ Opcional |
| `GEMINI_MAX_REQUESTS_PER_USER_PER_DAY` | Límite por usuario/día | `50` | ⚠️ Opcional |
| `GEMINI_TEMPERATURE` | Creatividad del modelo (0-1) | `0.7` | ⚠️ Opcional |
| `GEMINI_MAX_OUTPUT_TOKENS` | Tokens máximos de respuesta | `8192` | ⚠️ Opcional |
| `GEMINI_TIMEOUT_SECONDS` | Timeout de requests | `30` | ⚠️ Opcional |

**Obtener API Key**: https://aistudio.google.com/app/apikey

---

### 🎨 Frontend Container App (3 variables)

| Variable | Descripción | Ejemplo | Requerida |
|----------|-------------|---------|-----------|
| `NEXT_PUBLIC_API_URL` | URL del backend API | `https://plantitas-backend.azurecontainerapps.io` | ✅ Sí |
| `NODE_ENV` | Entorno de Node.js | `production` | ✅ Sí |
| `PORT` | Puerto de escucha | `3000` | ⚠️ Opcional* |

*Azure Container Apps asigna `PORT` automáticamente si no se especifica

**⚠️ Importante**: `NEXT_PUBLIC_API_URL` debe apuntar a la URL del backend **sin trailing slash**.

---

## 🔑 Generación de Secrets {#generacion-secrets}

### JWT Secret Key (64 caracteres)

#### Opción 1: Python
```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

#### Opción 2: PowerShell
```powershell
-join ((65..90) + (97..122) + (48..57) | Get-Random -Count 64 | ForEach-Object {[char]$_})
```

#### Opción 3: OpenSSL
```bash
openssl rand -base64 48
```

#### Opción 4: Online
- https://generate-secret.vercel.app/64
- https://passwordsgenerator.net/ (64 caracteres)

**Ejemplo de JWT Secret válido**:
```
kJ8n2Hx9pLm4vB7qR5tYu1wE3zD6aC0fG9jK8nM2pL5rT7yU1xW3zA6cF9hJ2mN5qR8tY
```

---

## ⚙️ Configuración en Azure {#configuracion-azure}

### Método 1: Azure CLI (Recomendado)

#### Configurar Backend

```powershell
# Variables de configuración
$RESOURCE_GROUP = "rg-plantitas-demo-temp"
$BACKEND_APP = "plantitas-backend"

# Database
$DATABASE_URL = "postgresql://user:pass@host:5432/db?sslmode=require"

# Storage
$STORAGE_CONNECTION_STRING = "DefaultEndpointsProtocol=https;AccountName=...;AccountKey=...;EndpointSuffix=core.windows.net"

# JWT
$JWT_SECRET = "<tu-jwt-secret-generado>"

# Gemini
$GEMINI_API_KEY = "<tu-gemini-api-key>"

# Configurar todas las variables
az containerapp update `
  --name $BACKEND_APP `
  --resource-group $RESOURCE_GROUP `
  --set-env-vars `
    "DATABASE_URL=$DATABASE_URL" `
    "JWT_SECRET_KEY=$JWT_SECRET" `
    "JWT_ALGORITHM=HS256" `
    "ACCESS_TOKEN_EXPIRE_MINUTES=30" `
    "REFRESH_TOKEN_EXPIRE_DAYS=7" `
    "AZURE_STORAGE_CONNECTION_STRING=$STORAGE_CONNECTION_STRING" `
    "AZURE_STORAGE_CONTAINER_NAME=plantitas-imagenes" `
    "AZURE_STORAGE_USE_EMULATOR=false" `
    "ENVIRONMENT=production" `
    "DEBUG=false" `
    "LOG_LEVEL=INFO" `
    "GEMINI_API_KEY=$GEMINI_API_KEY" `
    "GEMINI_MODEL=gemini-2.0-flash-exp" `
    "CORS_ORIGINS=<frontend-url>"
```

#### Configurar Frontend

```powershell
$FRONTEND_APP = "plantitas-frontend"
$BACKEND_URL = "https://plantitas-backend.victoriousstone-12345.eastus.azurecontainerapps.io"

az containerapp update `
  --name $FRONTEND_APP `
  --resource-group $RESOURCE_GROUP `
  --set-env-vars `
    "NEXT_PUBLIC_API_URL=$BACKEND_URL" `
    "NODE_ENV=production" `
    "PORT=3000"
```

### Método 2: Azure Portal (GUI)

1. **Ir al Azure Portal**: https://portal.azure.com
2. **Navegar a Container Apps**: Buscar "plantitas-backend"
3. **Settings** → **Environment variables**
4. **Add variable**: Agregar cada variable individualmente
5. **Save** y **Restart** la aplicación

---

## 🔍 Comandos Azure CLI {#comandos-cli}

### Listar Variables Actuales

```powershell
# Backend
az containerapp show `
  --name plantitas-backend `
  --resource-group rg-plantitas-demo-temp `
  --query properties.template.containers[0].env `
  --output table

# Frontend
az containerapp show `
  --name plantitas-frontend `
  --resource-group rg-plantitas-demo-temp `
  --query properties.template.containers[0].env `
  --output table
```

### Obtener URLs de Servicios

```powershell
# Backend URL
$BACKEND_URL = az containerapp show `
  --name plantitas-backend `
  --resource-group rg-plantitas-demo-temp `
  --query properties.configuration.ingress.fqdn `
  --output tsv

Write-Host "Backend: https://$BACKEND_URL"

# Frontend URL
$FRONTEND_URL = az containerapp show `
  --name plantitas-frontend `
  --resource-group rg-plantitas-demo-temp `
  --query properties.configuration.ingress.fqdn `
  --output tsv

Write-Host "Frontend: https://$FRONTEND_URL"
```

### Actualizar Variable Individual

```powershell
# Actualizar solo CORS_ORIGINS
az containerapp update `
  --name plantitas-backend `
  --resource-group rg-plantitas-demo-temp `
  --set-env-vars "CORS_ORIGINS=https://nuevo-frontend-url.azurecontainerapps.io"

# Reiniciar para aplicar cambios
az containerapp revision restart `
  --name plantitas-backend `
  --resource-group rg-plantitas-demo-temp
```

### Eliminar Variable

```powershell
az containerapp update `
  --name plantitas-backend `
  --resource-group rg-plantitas-demo-temp `
  --remove-env-vars "VARIABLE_NAME"
```

---

## ✅ Validación {#validacion}

### Script de Validación

Crear archivo `scripts/validate-env-azure.ps1`:

```powershell
# Validar configuración de Backend
Write-Host "Validando Backend..." -ForegroundColor Cyan

$backendEnv = az containerapp show `
  --name plantitas-backend `
  --resource-group rg-plantitas-demo-temp `
  --query properties.template.containers[0].env `
  --output json | ConvertFrom-Json

$requiredVars = @(
    "DATABASE_URL",
    "JWT_SECRET_KEY",
    "JWT_ALGORITHM",
    "AZURE_STORAGE_CONNECTION_STRING",
    "AZURE_STORAGE_CONTAINER_NAME",
    "GEMINI_API_KEY",
    "ENVIRONMENT",
    "DEBUG",
    "CORS_ORIGINS"
)

$missing = @()
foreach ($var in $requiredVars) {
    $found = $backendEnv | Where-Object { $_.name -eq $var }
    if (-not $found) {
        $missing += $var
    }
}

if ($missing.Count -eq 0) {
    Write-Host "✅ Backend: Todas las variables requeridas están configuradas" -ForegroundColor Green
} else {
    Write-Host "❌ Backend: Faltan variables: $($missing -join ', ')" -ForegroundColor Red
}

# Validar Frontend
Write-Host "`nValidando Frontend..." -ForegroundColor Cyan

$frontendEnv = az containerapp show `
  --name plantitas-frontend `
  --resource-group rg-plantitas-demo-temp `
  --query properties.template.containers[0].env `
  --output json | ConvertFrom-Json

$requiredFrontend = @("NEXT_PUBLIC_API_URL", "NODE_ENV")
$missingFrontend = @()

foreach ($var in $requiredFrontend) {
    $found = $frontendEnv | Where-Object { $_.name -eq $var }
    if (-not $found) {
        $missingFrontend += $var
    }
}

if ($missingFrontend.Count -eq 0) {
    Write-Host "✅ Frontend: Todas las variables requeridas están configuradas" -ForegroundColor Green
} else {
    Write-Host "❌ Frontend: Faltan variables: $($missingFrontend -join ', ')" -ForegroundColor Red
}
```

### Tests de Conectividad

```powershell
# Test backend health
$BACKEND_URL = "https://plantitas-backend.victoriousstone-12345.eastus.azurecontainerapps.io"
Invoke-RestMethod -Uri "$BACKEND_URL/health" -Method GET

# Test backend docs
Start-Process "$BACKEND_URL/docs"

# Test frontend
$FRONTEND_URL = "https://plantitas-frontend.victoriousstone-12345.eastus.azurecontainerapps.io"
Start-Process $FRONTEND_URL
```

---

## 🆘 Troubleshooting {#troubleshooting}

### Problema: "DatabaseConnectionError"

**Causa**: `DATABASE_URL` incorrecto o PostgreSQL no accesible.

**Solución**:
```powershell
# Verificar connection string
az postgres flexible-server show `
  --name plantitas-demo-db `
  --resource-group rg-plantitas-demo-temp

# Verificar firewall rules
az postgres flexible-server firewall-rule list `
  --name plantitas-demo-db `
  --resource-group rg-plantitas-demo-temp
```

### Problema: "CORS Error" en Frontend

**Causa**: `CORS_ORIGINS` no incluye la URL del frontend.

**Solución**:
```powershell
# Obtener URL exacta del frontend
$FRONTEND_URL = az containerapp show `
  --name plantitas-frontend `
  --resource-group rg-plantitas-demo-temp `
  --query properties.configuration.ingress.fqdn `
  --output tsv

# Actualizar CORS en backend
az containerapp update `
  --name plantitas-backend `
  --resource-group rg-plantitas-demo-temp `
  --set-env-vars "CORS_ORIGINS=https://$FRONTEND_URL"
```

### Problema: "Azure Storage BlobNotFound"

**Causa**: `AZURE_STORAGE_CONTAINER_NAME` no existe o `AZURE_STORAGE_CONNECTION_STRING` incorrecto.

**Solución**:
```powershell
# Verificar storage account
az storage account show `
  --name plantitasdemostorage456 `
  --resource-group rg-plantitas-demo-temp

# Listar containers
az storage container list `
  --account-name plantitasdemostorage456 `
  --output table

# Crear container si no existe
az storage container create `
  --name plantitas-imagenes `
  --account-name plantitasdemostorage456
```

### Problema: "Gemini API Error"

**Causa**: `GEMINI_API_KEY` inválida o expirada.

**Solución**:
1. Generar nueva API Key: https://aistudio.google.com/app/apikey
2. Actualizar en Azure:
```powershell
az containerapp update `
  --name plantitas-backend `
  --resource-group rg-plantitas-demo-temp `
  --set-env-vars "GEMINI_API_KEY=<nueva-key>"
```

### Problema: "JWT Decode Error"

**Causa**: `JWT_SECRET_KEY` no coincide entre deployments o es demasiado corto.

**Solución**:
```powershell
# Generar nuevo secret
$JWT_SECRET = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 64 | ForEach-Object {[char]$_})

# Actualizar
az containerapp update `
  --name plantitas-backend `
  --resource-group rg-plantitas-demo-temp `
  --set-env-vars "JWT_SECRET_KEY=$JWT_SECRET"
```

---

## 📚 Referencias

- **Azure Container Apps Environment Variables**: https://learn.microsoft.com/azure/container-apps/environment-variables
- **Azure PostgreSQL Connection Strings**: https://learn.microsoft.com/azure/postgresql/flexible-server/connect-python
- **Azure Blob Storage SDK**: https://learn.microsoft.com/azure/storage/blobs/storage-quickstart-blobs-python
- **Gemini API Documentation**: https://ai.google.dev/docs

---

## ✅ Checklist Final

Antes de deployar, verifica:

- [ ] `DATABASE_URL` configurado y testeado
- [ ] `AZURE_STORAGE_CONNECTION_STRING` configurado
- [ ] `JWT_SECRET_KEY` generado (64 caracteres)
- [ ] `GEMINI_API_KEY` obtenida y válida
- [ ] `CORS_ORIGINS` apunta a URL del frontend
- [ ] `NEXT_PUBLIC_API_URL` apunta a URL del backend
- [ ] `DEBUG=false` en producción
- [ ] `ENVIRONMENT=production`
- [ ] Todos los containers creados en Azure Blob
- [ ] Firewall rules de PostgreSQL configurados

---

**Documentado por**: Franco Garcete  
**Proyecto**: Asistente Plantitas - Demo Académica  
**Fecha**: 12 de Noviembre de 2025  
**Azure Container Apps**: Producción
