# 🚀 ÉPICA: Deployment a Azure para Estudiantes

**ID**: EPIC-DEPLOY-001  
**Proyecto**: Asistente Plantitas  
**Estrategia**: App Service (SIN Docker) - Opción GRATUITA  
**Fecha Creación**: 9 de Noviembre 2025  
**Estudiante**: Universidad Nacional de La Matanza  
**Costo Estimado**: $0/mes (servicios gratuitos)  

---

## 📋 Resumen Ejecutivo

Esta épica implementa el deployment de la aplicación "Asistente Plantitas" a **Azure for Students** usando la estrategia **más simple y económica**, evitando Docker y maximizando el uso de servicios gratuitos permanentes.

### ✅ Objetivos de la Épica

1. **Simplicidad Máxima**: Deployment sin Docker, directo desde código fuente
2. **Costo $0**: Usar solo servicios con tier gratuito permanente
3. **Controles de Gasto**: Alertas automáticas para proteger los $100 USD de créditos
4. **Demo Temporal**: Arquitectura diseñada para apagar fácilmente después de la presentación
5. **Mínima Fricción**: Automatización máxima con scripts PowerShell

### 🎯 Criterios de Éxito

- [ ] Aplicación accesible públicamente con HTTPS
- [ ] Backend y Frontend funcionando correctamente
- [ ] Base de datos MySQL con datos migrados
- [ ] Imágenes en Azure Blob Storage (migración desde Azurite)
- [ ] Autenticación JWT funcionando
- [ ] CORS configurado correctamente
- [ ] Alertas de presupuesto configuradas
- [ ] Documentación para apagar servicios post-demo
- [ ] Costo real: $0/mes

---

## 🏗️ Arquitectura de Deployment

```
┌─────────────────────────────────────────────────────────────┐
│                    AZURE FOR STUDENTS                       │
│                   (Servicios GRATUITOS)                     │
└─────────────────────────────────────────────────────────────┘
                            │
            ┌───────────────┴───────────────┐
            │                               │
    ┌───────▼────────┐            ┌────────▼────────┐
    │   App Service  │            │  App Service    │
    │    Frontend    │            │    Backend      │
    │   (Node 18)    │◄───────────┤  (Python 3.11)  │
    │   FREE F1      │   HTTPS    │   FREE F1       │
    └────────────────┘            └─────────┬───────┘
         │                                  │
         │ HTTPS                            │
         │                         ┌────────▼────────┐
    ┌────▼─────┐                   │  MySQL Flexible │
    │  Users   │                   │     Server      │
    │ Browser  │                   │ 750 hrs/mes FREE│
    └──────────┘                   └─────────┬───────┘
                                             │
                                   ┌─────────▼────────┐
                                   │  Blob Storage    │
                                   │  (Imágenes)      │
                                   │   5 GB FREE      │
                                   └──────────────────┘
```

### 🔧 Stack Técnico

| Componente | Tecnología | Tier Azure | Costo/mes |
|------------|-----------|------------|-----------|
| Frontend | Next.js 14 | App Service F1 | **$0** |
| Backend | FastAPI (Python 3.11) | App Service F1 | **$0** |
| Base de Datos | MySQL 8.0 | Flexible Server Burstable B1ms | **$0** (750 hrs) |
| Storage | Azure Blob Storage | LRS Standard | **$0** (5 GB) |
| CI/CD | GitHub Actions | - | **$0** |
| **TOTAL** | | | **$0/mes** |

---

## 📦 Historias de Usuario (Tareas)

### **FASE 1: Preparación del Código** 🛠️

---

#### **T-DEPLOY-001: Crear archivo startup.sh para Backend**

**Prioridad**: Alta  
**Estimación**: 15 minutos  
**Tipo**: Configuración  

**Descripción**:  
Crear script de arranque para App Service que ejecute migraciones de base de datos y lance Gunicorn con Uvicorn workers.

**Criterios de Aceptación**:
- [ ] Archivo `backend/startup.sh` creado
- [ ] Script ejecuta migraciones de Alembic
- [ ] Script inicia Gunicorn con configuración correcta
- [ ] Configuración para 1 worker (límite de F1)
- [ ] Logs informativos de arranque

**Archivos a Crear**:
```bash
backend/startup.sh
```

**Contenido del Script**:
```bash
#!/bin/bash
set -e

echo "🚀 Iniciando Asistente Plantitas Backend..."
echo "📍 Ubicación: Azure App Service"
echo "⏰ $(date)"

# Verificar variables de entorno críticas
echo "🔍 Verificando configuración..."
if [ -z "$DATABASE_URL" ]; then
    echo "❌ ERROR: DATABASE_URL no configurado"
    exit 1
fi

# Ejecutar migraciones de Alembic
echo "📦 Ejecutando migraciones de base de datos..."
cd /home/site/wwwroot
alembic upgrade head

if [ $? -eq 0 ]; then
    echo "✅ Migraciones ejecutadas exitosamente"
else
    echo "⚠️  Advertencia: Migraciones fallaron, continuando..."
fi

# Iniciar Gunicorn con Uvicorn workers
echo "🌟 Iniciando servidor Gunicorn + Uvicorn..."
exec gunicorn app.main:app \
    --worker-class uvicorn.workers.UvicornWorker \
    --workers 1 \
    --bind 0.0.0.0:8000 \
    --timeout 120 \
    --access-logfile '-' \
    --error-logfile '-' \
    --log-level info
```

**Comandos**:
```powershell
# Crear archivo con permisos de ejecución
New-Item -Path "backend/startup.sh" -ItemType File -Force
# Copiar contenido
# Commit
git add backend/startup.sh
git commit -m "feat: agregar startup.sh para Azure App Service"
```

---

#### **T-DEPLOY-002: Actualizar requirements.txt con dependencias de producción**

**Prioridad**: Alta  
**Estimación**: 10 minutos  
**Tipo**: Configuración  

**Descripción**:  
Agregar Gunicorn para servidor WSGI y PyMySQL para conexión a MySQL en Azure.

**Criterios de Aceptación**:
- [ ] `gunicorn==21.2.0` agregado
- [ ] `pymysql==1.1.0` agregado  
- [ ] `cryptography>=41.0.0` agregado (requerido por pymysql)
- [ ] Dependencias instalables sin errores

**Archivo a Modificar**:
```
backend/requirements.txt
```

**Líneas a Agregar** (al final del archivo):
```python
# Servidor de producción para Azure App Service
gunicorn==21.2.0

# MySQL connector para Azure Database for MySQL
pymysql==1.1.0
cryptography>=41.0.0
```

**Comandos**:
```powershell
# Agregar líneas al requirements.txt
git add backend/requirements.txt
git commit -m "feat: agregar gunicorn y pymysql para Azure deployment"
```

---

#### **T-DEPLOY-003: Configurar Next.js para Azure App Service**

**Prioridad**: Alta  
**Estimación**: 15 minutos  
**Tipo**: Configuración  

**Descripción**:  
Ajustar configuración de Next.js para deployment sin Docker en App Service.

**Criterios de Aceptación**:
- [ ] `output: 'standalone'` ya está configurado ✅
- [ ] Variables de entorno públicas configuradas
- [ ] Build scripts verificados
- [ ] Puerto configurado (4200 o default de App Service)

**Archivo a Verificar**:
```
frontend/next.config.mjs
```

**Verificación** (ya está correcto):
- ✅ `output: 'standalone'` configurado
- ✅ Variables de entorno definidas
- ✅ Rewrites para API configurados

**Acción Requerida**: 
```powershell
# Solo verificar que el archivo esté correcto
# NO requiere cambios - ya está optimizado para deployment
cat frontend/next.config.mjs
```

---

#### **T-DEPLOY-004: Crear archivo .deployment para App Service**

**Prioridad**: Media  
**Estimación**: 5 minutos  
**Tipo**: Configuración  

**Descripción**:  
Crear archivo de configuración para indicar a App Service cómo deployar el proyecto.

**Criterios de Aceptación**:
- [ ] Archivo `.deployment` creado en raíz
- [ ] Configuración apunta a proyecto correcto

**Archivo a Crear**:
```
.deployment
```

**Contenido**:
```ini
[config]
SCM_DO_BUILD_DURING_DEPLOYMENT=true
```

**Comandos**:
```powershell
# Crear archivo
New-Item -Path ".deployment" -ItemType File -Force
# Agregar contenido
git add .deployment
git commit -m "feat: agregar configuración de deployment para Azure"
```

---

#### **T-DEPLOY-005: Crear archivo .env.production de ejemplo**

**Prioridad**: Media  
**Estimación**: 10 minutos  
**Tipo**: Documentación  

**Descripción**:  
Crear archivo de ejemplo con todas las variables de entorno necesarias para producción.

**Criterios de Aceptación**:
- [ ] Archivo `.env.production.example` creado
- [ ] Todas las variables documentadas
- [ ] Placeholders para valores sensibles
- [ ] Comentarios explicativos

**Archivo a Crear**:
```
.env.production.example
```

**Contenido**:
```bash
# =============================================================================
# CONFIGURACIÓN DE PRODUCCIÓN - AZURE APP SERVICE
# =============================================================================

# ==================== Base de Datos ====================
DATABASE_URL=mysql+pymysql://usuario:password@servidor.mysql.database.azure.com:3306/plantitas_db?ssl_ca=/etc/ssl/certs/ca-certificates.crt

# ==================== Seguridad ====================
JWT_SECRET_KEY=CAMBIAR_POR_SECRET_ALEATORIO_64_CARACTERES
JWT_ALGORITHM=HS256
JWT_EXPIRACION_MINUTOS=30
JWT_REFRESH_EXPIRACION_DIAS=7

# ==================== Azure Blob Storage ====================
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=...
AZURE_STORAGE_CONTAINER_NAME=plantitas-imagenes
AZURE_STORAGE_USE_EMULATOR=false

# ==================== CORS ====================
ORIGENES_CORS=["https://plantitas-demo-frontend.azurewebsites.net"]
CORS_ALLOW_CREDENTIALS=true

# ==================== Entorno ====================
ENTORNO=produccion
DEBUG=false
NIVEL_LOG=INFO

# ==================== Frontend ====================
NEXT_PUBLIC_API_URL=https://plantitas-demo-backend.azurewebsites.net
NODE_ENV=production

# ==================== APIs Externas ====================
GEMINI_API_KEY=tu_api_key_aqui
GEMINI_MODEL=gemini-1.5-flash
```

**Comandos**:
```powershell
git add .env.production.example
git commit -m "docs: agregar ejemplo de configuración de producción"
```

---

### **FASE 2: Infraestructura Azure** ☁️

---

#### **T-DEPLOY-006: Verificar cuenta Azure for Students**

**Prioridad**: Alta  
**Estimación**: 5 minutos  
**Tipo**: Validación  

**Descripción**:  
Verificar que la cuenta de Azure for Students está activa y tiene créditos disponibles.

**Criterios de Aceptación**:
- [ ] Azure CLI instalado
- [ ] Autenticación exitosa
- [ ] Suscripción "Azure for Students" verificada
- [ ] Créditos disponibles confirmados

**Comandos**:
```powershell
# Verificar Azure CLI instalado
az --version

# Login a Azure
az login

# Verificar suscripción
az account show --output table

# Verificar créditos (aproximado)
az consumption usage list --output table
```

**Validación Esperada**:
```
Name                    State    IsDefault
----------------------  -------  -----------
Azure for Students      Enabled  True
```

---

#### **T-DEPLOY-007: Ejecutar script de deployment automatizado**

**Prioridad**: Alta  
**Estimación**: 30-45 minutos  
**Tipo**: Deployment  

**Descripción**:  
Ejecutar el script `deploy-academic-demo.ps1` que crea automáticamente todos los recursos de Azure necesarios.

**Criterios de Aceptación**:
- [ ] Resource Group creado
- [ ] Storage Account creado (5 GB gratis)
- [ ] MySQL Database creado (750 hrs/mes gratis)
- [ ] App Service Plan F1 creado (gratis)
- [ ] Backend App Service creado
- [ ] Frontend App Service creado
- [ ] Variables de entorno configuradas
- [ ] Alertas de presupuesto configuradas

**Script a Ejecutar**:
```powershell
# Actualizar email en el script primero (línea 22)
# Luego ejecutar:
.\scripts\deploy-academic-demo.ps1
```

**Duración Esperada**: 25-35 minutos

**Recursos Creados**:
| Recurso | Nombre | Tipo | Costo |
|---------|--------|------|-------|
| Resource Group | rg-plantitas-demo-academica | - | $0 |
| Storage Account | plantitasdemostorage | Standard LRS | $0 (5GB) |
| MySQL Server | plantitas-demo-mysql | Flexible B1ms | $0 (750hrs) |
| App Service Plan | plantitas-demo-plan | F1 Free | $0 |
| Backend App | plantitas-demo-backend | Python 3.11 | $0 |
| Frontend App | plantitas-demo-frontend | Node 18 | $0 |

---

#### **T-DEPLOY-008: Configurar CORS en Azure Blob Storage**

**Prioridad**: Alta  
**Estimación**: 10 minutos  
**Tipo**: Configuración  

**Descripción**:  
Configurar políticas CORS en Azure Blob Storage para permitir subida de imágenes desde el frontend.

**Criterios de Aceptación**:
- [ ] Regla CORS creada para frontend
- [ ] Métodos PUT, POST, GET permitidos
- [ ] Headers necesarios configurados
- [ ] Max age configurado

**Comandos**:
```powershell
# Variables
$STORAGE_ACCOUNT = "plantitasdemostorage"
$FRONTEND_URL = "https://plantitas-demo-frontend.azurewebsites.net"

# Configurar CORS
az storage cors add `
    --account-name $STORAGE_ACCOUNT `
    --services b `
    --methods GET POST PUT OPTIONS `
    --origins $FRONTEND_URL `
    --allowed-headers '*' `
    --exposed-headers '*' `
    --max-age 3600
```

**Validación**:
```powershell
# Verificar CORS configurado
az storage cors list --account-name $STORAGE_ACCOUNT --services b
```

---

#### **T-DEPLOY-009: Configurar conexión segura MySQL**

**Prioridad**: Alta  
**Estimación**: 15 minutos  
**Tipo**: Configuración  

**Descripción**:  
Configurar firewall de MySQL para permitir conexiones desde App Services y verificar SSL.

**Criterios de Aceptación**:
- [ ] Regla de firewall para Azure Services habilitada
- [ ] SSL obligatorio configurado
- [ ] Conexión desde App Service verificada
- [ ] Database creada

**Comandos**:
```powershell
$RESOURCE_GROUP = "rg-plantitas-demo-academica"
$DB_SERVER = "plantitas-demo-mysql"

# Permitir acceso desde Azure Services
az mysql flexible-server firewall-rule create `
    --resource-group $RESOURCE_GROUP `
    --name $DB_SERVER `
    --rule-name AllowAzureServices `
    --start-ip-address 0.0.0.0 `
    --end-ip-address 0.0.0.0

# Verificar SSL está habilitado
az mysql flexible-server show `
    --resource-group $RESOURCE_GROUP `
    --name $DB_SERVER `
    --query sslEnforcement
```

---

### **FASE 3: Deployment de Aplicaciones** 🚢

---

#### **T-DEPLOY-010: Preparar repositorio para GitHub Actions**

**Prioridad**: Alta  
**Estimación**: 20 minutos  
**Tipo**: CI/CD  

**Descripción**:  
Configurar GitHub Actions para deployment automático a Azure App Services.

**Criterios de Aceptación**:
- [ ] Workflow YAML creado
- [ ] Secrets de GitHub configurados
- [ ] Deploy profile descargado de Azure
- [ ] Trigger en push a main configurado

**Archivo a Crear**:
```
.github/workflows/azure-deploy-free.yml
```

**Contenido**:
```yaml
name: Deploy a Azure App Service (FREE)

on:
  push:
    branches: [ main ]
  workflow_dispatch:

env:
  AZURE_BACKEND_APP_NAME: plantitas-demo-backend
  AZURE_FRONTEND_APP_NAME: plantitas-demo-frontend

jobs:
  # ==================== Backend Deployment ====================
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - name: 📥 Checkout código
        uses: actions/checkout@v4

      - name: 🐍 Setup Python 3.11
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: 📦 Instalar dependencias
        run: |
          cd backend
          pip install --upgrade pip
          pip install -r requirements.txt

      - name: 🧪 Ejecutar tests
        run: |
          cd backend
          pytest tests/ -v

      - name: 🚀 Deploy a Azure App Service
        uses: azure/webapps-deploy@v2
        with:
          app-name: ${{ env.AZURE_BACKEND_APP_NAME }}
          publish-profile: ${{ secrets.AZURE_BACKEND_PUBLISH_PROFILE }}
          package: ./backend

  # ==================== Frontend Deployment ====================
  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
      - name: 📥 Checkout código
        uses: actions/checkout@v4

      - name: 📦 Setup Node.js 18
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json

      - name: 📦 Instalar dependencias
        run: |
          cd frontend
          npm ci

      - name: 🏗️ Build de producción
        run: |
          cd frontend
          npm run build
        env:
          NEXT_PUBLIC_API_URL: https://${{ env.AZURE_BACKEND_APP_NAME }}.azurewebsites.net

      - name: 🚀 Deploy a Azure App Service
        uses: azure/webapps-deploy@v2
        with:
          app-name: ${{ env.AZURE_FRONTEND_APP_NAME }}
          publish-profile: ${{ secrets.AZURE_FRONTEND_PUBLISH_PROFILE }}
          package: ./frontend
```

**Comandos para Secrets**:
```powershell
# Descargar publish profiles
az webapp deployment list-publishing-profiles `
    --name plantitas-demo-backend `
    --resource-group rg-plantitas-demo-academica `
    --xml > backend-profile.xml

az webapp deployment list-publishing-profiles `
    --name plantitas-demo-frontend `
    --resource-group rg-plantitas-demo-academica `
    --xml > frontend-profile.xml

# Agregar a GitHub Secrets:
# AZURE_BACKEND_PUBLISH_PROFILE: contenido de backend-profile.xml
# AZURE_FRONTEND_PUBLISH_PROFILE: contenido de frontend-profile.xml
```

---

#### **T-DEPLOY-011: Deploy manual inicial del Backend**

**Prioridad**: Alta  
**Estimación**: 20 minutos  
**Tipo**: Deployment  

**Descripción**:  
Realizar el primer deployment manual del backend para verificar configuración.

**Criterios de Aceptación**:
- [ ] Código comprimido y subido
- [ ] startup.sh ejecutándose
- [ ] Migraciones aplicadas
- [ ] Endpoint /health responde correctamente
- [ ] Logs sin errores críticos

**Comandos**:
```powershell
$RESOURCE_GROUP = "rg-plantitas-demo-academica"
$BACKEND_APP = "plantitas-demo-backend"

# Comprimir código del backend
cd backend
Compress-Archive -Path * -DestinationPath ../backend-deploy.zip -Force
cd ..

# Deploy con Azure CLI
az webapp deploy `
    --resource-group $RESOURCE_GROUP `
    --name $BACKEND_APP `
    --src-path backend-deploy.zip `
    --type zip

# Esperar 30 segundos para arranque
Start-Sleep -Seconds 30

# Verificar health check
curl https://plantitas-demo-backend.azurewebsites.net/health

# Ver logs en tiempo real
az webapp log tail `
    --name $BACKEND_APP `
    --resource-group $RESOURCE_GROUP
```

**Respuesta Esperada**:
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "database": "connected"
}
```

---

#### **T-DEPLOY-012: Deploy manual inicial del Frontend**

**Prioridad**: Alta  
**Estimación**: 20 minutos  
**Tipo**: Deployment  

**Descripción**:  
Realizar el primer deployment manual del frontend.

**Criterios de Aceptación**:
- [ ] Build de Next.js exitoso
- [ ] Código comprimido y subido
- [ ] Variables de entorno configuradas
- [ ] Página principal carga correctamente
- [ ] Conexión con backend funcional

**Comandos**:
```powershell
$RESOURCE_GROUP = "rg-plantitas-demo-academica"
$FRONTEND_APP = "plantitas-demo-frontend"
$BACKEND_URL = "https://plantitas-demo-backend.azurewebsites.net"

# Build del frontend
cd frontend
npm install
$env:NEXT_PUBLIC_API_URL = $BACKEND_URL
npm run build

# Comprimir el build
cd .next/standalone
Compress-Archive -Path * -DestinationPath ../../frontend-deploy.zip -Force
cd ../..

# Deploy
az webapp deploy `
    --resource-group $RESOURCE_GROUP `
    --name $FRONTEND_APP `
    --src-path frontend-deploy.zip `
    --type zip

# Esperar y verificar
Start-Sleep -Seconds 30
Start-Process "https://plantitas-demo-frontend.azurewebsites.net"
```

---

#### **T-DEPLOY-013: Migrar datos desde SQLite/PostgreSQL local a MySQL Azure**

**Prioridad**: Media  
**Estimación**: 30 minutos  
**Tipo**: Migración  

**Descripción**:  
Migrar datos existentes de la base de datos local a MySQL en Azure.

**Criterios de Aceptación**:
- [ ] Backup de base de datos local creado
- [ ] Datos exportados en formato compatible
- [ ] Datos importados en MySQL Azure
- [ ] Integridad de datos verificada
- [ ] Usuarios de prueba funcionando

**Comandos**:
```powershell
# 1. Exportar datos locales
cd backend

# Si usas SQLite (default en desarrollo)
python -c "
from app.db.session import SessionLocal
from app.db.models import Usuario
import json

db = SessionLocal()
usuarios = db.query(Usuario).all()
data = [{
    'email': u.email,
    'hashed_password': u.hashed_password,
    'nombre': u.nombre
} for u in usuarios]

with open('usuarios_backup.json', 'w') as f:
    json.dump(data, f, indent=2)

db.close()
print(f'✅ {len(usuarios)} usuarios exportados')
"

# 2. Importar a MySQL Azure (desde el backend en Azure)
# Crear script de importación
```

**Script de Importación** (`backend/import_data_azure.py`):
```python
"""Script para importar datos a MySQL Azure"""
import json
from app.db.session import SessionLocal
from app.db.models import Usuario

def importar_usuarios():
    db = SessionLocal()
    try:
        with open('usuarios_backup.json', 'r') as f:
            usuarios_data = json.load(f)
        
        for user_data in usuarios_data:
            usuario = Usuario(**user_data)
            db.add(usuario)
        
        db.commit()
        print(f'✅ {len(usuarios_data)} usuarios importados')
    except Exception as e:
        print(f'❌ Error: {e}')
        db.rollback()
    finally:
        db.close()

if __name__ == '__main__':
    importar_usuarios()
```

---

#### **T-DEPLOY-014: Migrar imágenes desde Azurite a Azure Blob Storage**

**Prioridad**: Media  
**Estimación**: 20 minutos  
**Tipo**: Migración  

**Descripción**:  
Migrar imágenes almacenadas localmente en Azurite al Azure Blob Storage real.

**Criterios de Aceptación**:
- [ ] Script de migración creado
- [ ] Imágenes copiadas a Azure Blob Storage
- [ ] URLs actualizadas en base de datos
- [ ] Imágenes accesibles desde frontend

**Comandos**:
```powershell
# Script de migración
$STORAGE_ACCOUNT = "plantitasdemostorage"
$CONTAINER = "plantitas-imagenes"
$LOCAL_AZURITE_PATH = ".\data\__blobstorage__\plantitas-imagenes"

# Obtener connection string
$CONN_STRING = az storage account show-connection-string `
    --name $STORAGE_ACCOUNT `
    --resource-group rg-plantitas-demo-academica `
    --output tsv

# Subir todas las imágenes locales
Get-ChildItem -Path $LOCAL_AZURITE_PATH -File | ForEach-Object {
    Write-Host "📤 Subiendo: $($_.Name)"
    
    az storage blob upload `
        --account-name $STORAGE_ACCOUNT `
        --container-name $CONTAINER `
        --name $_.Name `
        --file $_.FullName `
        --connection-string $CONN_STRING
}

Write-Host "✅ Migración de imágenes completada"
```

**Verificación**:
```powershell
# Listar blobs migrados
az storage blob list `
    --account-name $STORAGE_ACCOUNT `
    --container-name $CONTAINER `
    --output table
```

---

### **FASE 4: Verificación y Pruebas** ✅

---

#### **T-DEPLOY-015: Verificar endpoints del Backend**

**Prioridad**: Alta  
**Estimación**: 20 minutos  
**Tipo**: Testing  

**Descripción**:  
Verificar que todos los endpoints críticos del backend funcionan correctamente en Azure.

**Criterios de Aceptación**:
- [ ] /health responde correctamente
- [ ] /api/auth/register funciona
- [ ] /api/auth/login funciona
- [ ] /api/imagenes/upload funciona
- [ ] CORS configurado correctamente
- [ ] Sin errores en logs

**Script de Pruebas** (`test-azure-backend.ps1`):
```powershell
$BACKEND_URL = "https://plantitas-demo-backend.azurewebsites.net"

Write-Host "🧪 Probando Backend en Azure...`n" -ForegroundColor Cyan

# 1. Health Check
Write-Host "1️⃣ Health Check..." -ForegroundColor Yellow
$health = Invoke-RestMethod -Uri "$BACKEND_URL/health" -Method Get
Write-Host "   Status: $($health.status)" -ForegroundColor Green

# 2. Register
Write-Host "`n2️⃣ Register..." -ForegroundColor Yellow
$registerBody = @{
    email = "test-azure@unlam.edu.ar"
    password = "TestAzure123!"
    nombre = "Usuario Azure Test"
} | ConvertTo-Json

try {
    $register = Invoke-RestMethod `
        -Uri "$BACKEND_URL/api/auth/register" `
        -Method Post `
        -Body $registerBody `
        -ContentType "application/json"
    Write-Host "   ✅ Usuario registrado" -ForegroundColor Green
} catch {
    Write-Host "   ⚠️  Usuario ya existe (OK)" -ForegroundColor Yellow
}

# 3. Login
Write-Host "`n3️⃣ Login..." -ForegroundColor Yellow
$loginBody = @{
    username = "test-azure@unlam.edu.ar"
    password = "TestAzure123!"
} | ConvertTo-Json

$login = Invoke-RestMethod `
    -Uri "$BACKEND_URL/api/auth/login" `
    -Method Post `
    -Body $loginBody `
    -ContentType "application/json"

Write-Host "   ✅ Token obtenido" -ForegroundColor Green
$TOKEN = $login.access_token

# 4. Protected Endpoint
Write-Host "`n4️⃣ Endpoint Protegido..." -ForegroundColor Yellow
$headers = @{
    "Authorization" = "Bearer $TOKEN"
}

$me = Invoke-RestMethod `
    -Uri "$BACKEND_URL/api/auth/me" `
    -Method Get `
    -Headers $headers

Write-Host "   ✅ Usuario: $($me.email)" -ForegroundColor Green

Write-Host "`n✅ TODAS LAS PRUEBAS PASARON" -ForegroundColor Green
```

**Ejecutar**:
```powershell
.\test-azure-backend.ps1
```

---

#### **T-DEPLOY-016: Verificar funcionamiento del Frontend**

**Prioridad**: Alta  
**Estimación**: 15 minutos  
**Tipo**: Testing  

**Descripción**:  
Verificar que el frontend carga correctamente y puede comunicarse con el backend.

**Criterios de Aceptación**:
- [ ] Página principal carga sin errores
- [ ] Login funciona
- [ ] Dashboard carga después de login
- [ ] Subida de imágenes funciona
- [ ] Sin errores de CORS en consola
- [ ] Estilos Tailwind se aplican correctamente

**Checklist Manual**:
```
□ 1. Abrir https://plantitas-demo-frontend.azurewebsites.net
□ 2. Verificar que la página principal carga
□ 3. Click en "Iniciar Sesión"
□ 4. Registrar nuevo usuario
□ 5. Login con usuario registrado
□ 6. Verificar redirección a /dashboard
□ 7. Navegar a "Identificar Planta"
□ 8. Subir imagen de prueba
□ 9. Verificar que la imagen se sube correctamente
□ 10. Abrir DevTools → Console (verificar sin errores)
□ 11. Abrir DevTools → Network (verificar llamadas al backend)
```

**Comandos**:
```powershell
# Abrir frontend en navegador
Start-Process "https://plantitas-demo-frontend.azurewebsites.net"

# Ver logs en tiempo real
az webapp log tail `
    --name plantitas-demo-frontend `
    --resource-group rg-plantitas-demo-academica
```

---

#### **T-DEPLOY-017: Prueba end-to-end completa**

**Prioridad**: Alta  
**Estimación**: 30 minutos  
**Tipo**: Testing  

**Descripción**:  
Realizar flujo completo de usuario desde registro hasta identificación de planta.

**Criterios de Aceptación**:
- [ ] Registro de usuario exitoso
- [ ] Login exitoso
- [ ] Subida de imagen funciona
- [ ] Identificación de planta funciona (si Gemini API configurado)
- [ ] Datos persisten en MySQL
- [ ] Imágenes persisten en Blob Storage

**Flujo de Prueba**:
```
1. Registro
   └─> POST /api/auth/register
   └─> Verificar usuario en MySQL

2. Login
   └─> POST /api/auth/login
   └─> Obtener JWT token
   └─> Verificar token válido

3. Subir Imagen
   └─> POST /api/imagenes/upload
   └─> Verificar imagen en Blob Storage
   └─> Verificar metadata en MySQL

4. Identificar Planta (si API configurada)
   └─> POST /api/identificacion/identificar
   └─> Verificar respuesta de Gemini
   └─> Verificar resultados guardados

5. Ver Perfil
   └─> GET /api/usuarios/me
   └─> Verificar datos correctos
```

---

### **FASE 5: Controles de Gasto y Monitoreo** 💰

---

#### **T-DEPLOY-018: Configurar alertas de presupuesto**

**Prioridad**: Alta  
**Estimación**: 15 minutos  
**Tipo**: Monitoreo  

**Descripción**:  
Configurar alertas automáticas de presupuesto para proteger los $100 USD de créditos.

**Criterios de Aceptación**:
- [ ] Alerta configurada en $5 USD
- [ ] Alerta configurada en $10 USD
- [ ] Email de notificación configurado
- [ ] Alertas visibles en Azure Portal

**Comandos**:
```powershell
$EMAIL = "tu-email@unlam.edu.ar"  # CAMBIAR
$SUBSCRIPTION_ID = (az account show --query id -o tsv)

# Alerta a $5 USD
az consumption budget create `
    --budget-name "alerta-academica-5usd" `
    --amount 5 `
    --category Cost `
    --time-grain Monthly `
    --time-period start-date="2025-11-01" `
    --resource-group rg-plantitas-demo-academica

# Alerta a $10 USD
az consumption budget create `
    --budget-name "alerta-academica-10usd" `
    --amount 10 `
    --category Cost `
    --time-grain Monthly `
    --time-period start-date="2025-11-01" `
    --resource-group rg-plantitas-demo-academica

Write-Host "✅ Alertas de presupuesto configuradas" -ForegroundColor Green
Write-Host "📧 Recibirás emails en: $EMAIL" -ForegroundColor Cyan
```

**Verificar en Portal**:
```
1. Ir a Azure Portal → Cost Management
2. Click en "Budgets"
3. Verificar alertas creadas
4. Configurar email notifications manualmente si es necesario
```

---

#### **T-DEPLOY-019: Configurar Application Insights (Opcional)**

**Prioridad**: Baja  
**Estimación**: 20 minutos  
**Tipo**: Monitoreo  

**Descripción**:  
Configurar Application Insights para monitoreo avanzado de logs y performance (tiene tier gratuito).

**Criterios de Aceptación**:
- [ ] Application Insights creado
- [ ] Conectado al Backend App Service
- [ ] Conectado al Frontend App Service
- [ ] Dashboard de métricas visible
- [ ] Dentro del tier gratuito (5 GB/mes)

**Comandos**:
```powershell
$RESOURCE_GROUP = "rg-plantitas-demo-academica"
$APP_INSIGHTS = "plantitas-insights"

# Crear Application Insights
az monitor app-insights component create `
    --app $APP_INSIGHTS `
    --location eastus `
    --resource-group $RESOURCE_GROUP `
    --application-type web `
    --kind web

# Obtener instrumentation key
$INSTRUMENTATION_KEY = az monitor app-insights component show `
    --app $APP_INSIGHTS `
    --resource-group $RESOURCE_GROUP `
    --query instrumentationKey `
    --output tsv

# Configurar en Backend
az webapp config appsettings set `
    --name plantitas-demo-backend `
    --resource-group $RESOURCE_GROUP `
    --settings APPLICATIONINSIGHTS_CONNECTION_STRING="InstrumentationKey=$INSTRUMENTATION_KEY"

# Configurar en Frontend
az webapp config appsettings set `
    --name plantitas-demo-frontend `
    --resource-group $RESOURCE_GROUP `
    --settings APPLICATIONINSIGHTS_CONNECTION_STRING="InstrumentationKey=$INSTRUMENTATION_KEY"

Write-Host "✅ Application Insights configurado" -ForegroundColor Green
```

---

#### **T-DEPLOY-020: Crear script de monitoreo de costos**

**Prioridad**: Media  
**Estimación**: 15 minutos  
**Tipo**: Automatización  

**Descripción**:  
Crear script para verificar costos acumulados de forma fácil.

**Criterios de Aceptación**:
- [ ] Script PowerShell creado
- [ ] Muestra costos del mes actual
- [ ] Muestra costos por recurso
- [ ] Muestra créditos restantes (estimado)

**Archivo a Crear**:
```
scripts/check-azure-costs.ps1
```

**Contenido**:
```powershell
# Script para verificar costos de Azure

$RESOURCE_GROUP = "rg-plantitas-demo-academica"

Write-Host "`n╔═══════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║    MONITOREO DE COSTOS - AZURE STUDENTS      ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# Fecha actual
$fechaInicio = (Get-Date).AddDays(-30).ToString("yyyy-MM-dd")
$fechaFin = (Get-Date).ToString("yyyy-MM-dd")

Write-Host "📅 Período: $fechaInicio a $fechaFin`n" -ForegroundColor Gray

# Obtener costos
Write-Host "💰 Consultando costos..." -ForegroundColor Yellow

$costos = az consumption usage list `
    --start-date $fechaInicio `
    --end-date $fechaFin `
    --query "[?contains(instanceName, 'plantitas')].{Recurso:instanceName, Costo:pretaxCost}" `
    --output json | ConvertFrom-Json

if ($costos) {
    Write-Host "`n📊 Costos por recurso:" -ForegroundColor Green
    $costos | Format-Table -AutoSize
    
    $costoTotal = ($costos | Measure-Object -Property Costo -Sum).Sum
    Write-Host "`n💵 COSTO TOTAL DEL MES: `$$([math]::Round($costoTotal, 2))" -ForegroundColor Cyan
} else {
    Write-Host "✅ No hay costos registrados - Todo en tier GRATUITO" -ForegroundColor Green
    $costoTotal = 0
}

# Calcular créditos restantes
$creditosIniciales = 100
$creditosRestantes = $creditosIniciales - $costoTotal

Write-Host "`n💳 CRÉDITOS RESTANTES: `$$([math]::Round($creditosRestantes, 2)) USD" -ForegroundColor Green
Write-Host "   (de `$$creditosIniciales USD iniciales)`n" -ForegroundColor Gray

# Alertas
if ($costoTotal -gt 10) {
    Write-Host "⚠️  ADVERTENCIA: Has consumido más de `$10 USD" -ForegroundColor Red
} elseif ($costoTotal -gt 5) {
    Write-Host "⚠️  ATENCIÓN: Has consumido más de `$5 USD" -ForegroundColor Yellow
} else {
    Write-Host "✅ Consumo dentro de lo esperado" -ForegroundColor Green
}

Write-Host "`n"
```

**Uso**:
```powershell
# Ejecutar script
.\scripts\check-azure-costs.ps1

# Ejecutar semanalmente durante la demo
```

---

### **FASE 6: Documentación y Cierre** 📚

---

#### **T-DEPLOY-021: Documentar URLs y credenciales**

**Prioridad**: Alta  
**Estimación**: 15 minutos  
**Tipo**: Documentación  

**Descripción**:  
Crear documento con todas las URLs, credenciales y datos importantes del deployment.

**Criterios de Aceptación**:
- [ ] Documento DEPLOYMENT_INFO.md creado
- [ ] URLs de frontend y backend documentadas
- [ ] Credenciales de MySQL guardadas de forma segura
- [ ] Connection strings documentados
- [ ] Comandos útiles incluidos

**Archivo a Crear**:
```
DEPLOYMENT_INFO.md
```

**Contenido**:
```markdown
# 📋 Información de Deployment - Asistente Plantitas

**Fecha de Deployment**: 9 de Noviembre 2025  
**Estudiante**: Universidad Nacional de La Matanza  
**Azure Subscription**: Azure for Students  

---

## 🌐 URLs de la Aplicación

| Componente | URL | Estado |
|------------|-----|--------|
| **Frontend** | https://plantitas-demo-frontend.azurewebsites.net | ✅ Activo |
| **Backend** | https://plantitas-demo-backend.azurewebsites.net | ✅ Activo |
| **Health Check** | https://plantitas-demo-backend.azurewebsites.net/health | ✅ |
| **API Docs** | https://plantitas-demo-backend.azurewebsites.net/docs | ✅ |

---

## 🔐 Credenciales (CONFIDENCIAL)

### MySQL Database
- **Server**: plantitas-demo-mysql.mysql.database.azure.com
- **Database**: plantitas_db
- **Usuario**: plantitasadmin
- **Password**: Ver archivo `db_password_demo.txt`
- **Connection String**:
  ```
  mysql+pymysql://plantitasadmin:PASSWORD@plantitas-demo-mysql.mysql.database.azure.com:3306/plantitas_db?ssl_ca=/etc/ssl/certs/ca-certificates.crt
  ```

### Azure Storage
- **Account**: plantitasdemostorage
- **Container**: plantitas-imagenes
- **Connection String**: Ver Azure Portal → Storage Account → Access Keys

---

## 🛠️ Comandos Útiles

### Ver logs en tiempo real
```powershell
# Backend
az webapp log tail --name plantitas-demo-backend --resource-group rg-plantitas-demo-academica

# Frontend
az webapp log tail --name plantitas-demo-frontend --resource-group rg-plantitas-demo-academica
```

### Reiniciar servicios
```powershell
# Backend
az webapp restart --name plantitas-demo-backend --resource-group rg-plantitas-demo-academica

# Frontend
az webapp restart --name plantitas-demo-frontend --resource-group rg-plantitas-demo-academica
```

### Apagar servicios (post-demo)
```powershell
# Apagar todo
az webapp stop --name plantitas-demo-backend --resource-group rg-plantitas-demo-academica
az webapp stop --name plantitas-demo-frontend --resource-group rg-plantitas-demo-academica
az mysql flexible-server stop --name plantitas-demo-mysql --resource-group rg-plantitas-demo-academica
```

### Ver costos
```powershell
.\scripts\check-azure-costs.ps1
```

---

## 📊 Recursos de Azure

| Recurso | Tipo | Tier | Costo/mes |
|---------|------|------|-----------|
| rg-plantitas-demo-academica | Resource Group | - | $0 |
| plantitas-demo-plan | App Service Plan | F1 Free | $0 |
| plantitas-demo-backend | App Service | Python 3.11 | $0 |
| plantitas-demo-frontend | App Service | Node 18 | $0 |
| plantitas-demo-mysql | MySQL Flexible | B1ms | $0 (750 hrs) |
| plantitasdemostorage | Storage Account | LRS | $0 (5 GB) |
| **TOTAL** | | | **$0/mes** |

---

## ⚠️ IMPORTANTE

1. **Apagar servicios después de la demo** para evitar consumir las 750 horas gratis de MySQL
2. **Monitorear costos semanalmente** con el script `check-azure-costs.ps1`
3. **No compartir** este documento públicamente (contiene info sensible)
4. **Backup** de `db_password_demo.txt` en lugar seguro

---

## 📞 Soporte

- **Azure Portal**: https://portal.azure.com
- **Documentación**: Ver `ESTRATEGIA_HIBRIDA_ACADEMIA.md`
- **Apagar servicios**: Ver `INSTRUCCIONES_APAGAR_DEMO.md`
```

---

#### **T-DEPLOY-022: Crear guía de troubleshooting**

**Prioridad**: Media  
**Estimación**: 20 minutos  
**Tipo**: Documentación  

**Descripción**:  
Documentar problemas comunes y sus soluciones.

**Criterios de Aceptación**:
- [ ] Documento TROUBLESHOOTING.md creado
- [ ] Al menos 10 problemas comunes documentados
- [ ] Soluciones paso a paso incluidas
- [ ] Comandos de diagnóstico incluidos

**Archivo a Crear**:
```
TROUBLESHOOTING_AZURE.md
```

**Contenido**: (Ver siguiente comentario por límite de caracteres)

---

#### **T-DEPLOY-023: Preparar presentación para la demo**

**Prioridad**: Media  
**Estimación**: 30 minutos  
**Tipo**: Documentación  

**Descripción**:  
Crear slide deck o documento para presentar el proyecto deployado.

**Criterios de Aceptación**:
- [ ] Presentación PowerPoint o PDF creada
- [ ] Arquitectura explicada
- [ ] Demo flow definido
- [ ] Screenshots de la aplicación incluidos
- [ ] Costos y servicios documentados

**Secciones de la Presentación**:
```
1. Introducción
   - Qué es Asistente Plantitas
   - Problema que resuelve

2. Stack Tecnológico
   - Frontend: Next.js + React + TypeScript
   - Backend: FastAPI + Python
   - Database: MySQL
   - Storage: Azure Blob Storage

3. Arquitectura en Azure
   - Diagrama de componentes
   - Servicios utilizados
   - Costo: $0/mes

4. Demo en Vivo
   - Registro de usuario
   - Login
   - Subir imagen de planta
   - Ver identificación

5. Deployment y DevOps
   - GitHub Actions CI/CD
   - Controles de gasto
   - Monitoreo

6. Conclusiones
   - Aprendizajes
   - Próximos pasos
```

---

#### **T-DEPLOY-024: Crear video demo de la aplicación**

**Prioridad**: Baja  
**Estimación**: 45 minutos  
**Tipo**: Documentación  

**Descripción**:  
Grabar video demo de 3-5 minutos mostrando la aplicación funcionando en Azure.

**Criterios de Aceptación**:
- [ ] Video de 3-5 minutos grabado
- [ ] Flujo completo demostrado
- [ ] Narración en español
- [ ] Calidad 1080p mínimo
- [ ] Subido a YouTube/Drive

**Script del Video**:
```
00:00-00:30 - Introducción
  - Presentación del proyecto
  - Stack tecnológico
  - Deployment en Azure

00:30-01:30 - Registro y Login
  - Abrir aplicación
  - Registrar nuevo usuario
  - Iniciar sesión

01:30-03:00 - Funcionalidades Principales
  - Dashboard
  - Subir imagen de planta
  - Ver identificación
  - Guardar como favorita

03:00-04:00 - Backend y Arquitectura
  - Mostrar Azure Portal
  - Explicar servicios utilizados
  - Mostrar costos ($0)

04:00-05:00 - Conclusión
  - Resumen de tecnologías
  - Costo total: $0/mes
  - Próximos pasos
```

---

### **FASE 7: Post-Demo** 🏁

---

#### **T-DEPLOY-025: Apagar servicios después de la presentación**

**Prioridad**: Alta (post-demo)  
**Estimación**: 5 minutos  
**Tipo**: Mantenimiento  

**Descripción**:  
Apagar todos los servicios para conservar las 750 horas gratuitas de MySQL y evitar cualquier costo.

**Criterios de Aceptación**:
- [ ] Backend App Service detenido
- [ ] Frontend App Service detenido
- [ ] MySQL Server detenido
- [ ] Confirmación de estado detenido
- [ ] Costo después de apagar: $0/día

**Comandos**:
```powershell
Write-Host "🛑 Apagando servicios de demo académica..." -ForegroundColor Yellow

# Apagar Backend
az webapp stop `
    --name plantitas-demo-backend `
    --resource-group rg-plantitas-demo-academica
Write-Host "✅ Backend detenido" -ForegroundColor Green

# Apagar Frontend
az webapp stop `
    --name plantitas-demo-frontend `
    --resource-group rg-plantitas-demo-academica
Write-Host "✅ Frontend detenido" -ForegroundColor Green

# Apagar MySQL
az mysql flexible-server stop `
    --name plantitas-demo-mysql `
    --resource-group rg-plantitas-demo-academica
Write-Host "✅ MySQL detenido" -ForegroundColor Green

Write-Host "`n✅ TODOS LOS SERVICIOS APAGADOS" -ForegroundColor Green
Write-Host "💰 Costo mientras está apagado: `$0/día" -ForegroundColor Cyan
Write-Host "💳 Tus `$100 USD están intactos" -ForegroundColor Cyan
```

---

#### **T-DEPLOY-026: (Opcional) Eliminar recursos permanentemente**

**Prioridad**: Baja (post-demo)  
**Estimación**: 5 minutos  
**Tipo**: Limpieza  

**Descripción**:  
Si ya no necesitas los recursos, eliminarlos permanentemente para liberar espacio.

**Criterios de Aceptación**:
- [ ] Backup de datos realizado
- [ ] Confirmación del usuario obtenida
- [ ] Resource Group eliminado
- [ ] Recursos ya no aparecen en Azure Portal

**Comandos**:
```powershell
Write-Host "⚠️  ADVERTENCIA: Esto eliminará PERMANENTEMENTE todos los recursos" -ForegroundColor Red
$confirm = Read-Host "¿Estás seguro? (escribir 'SI' para confirmar)"

if ($confirm -eq "SI") {
    Write-Host "`n🗑️  Eliminando Resource Group..." -ForegroundColor Yellow
    
    az group delete `
        --name rg-plantitas-demo-academica `
        --yes `
        --no-wait
    
    Write-Host "✅ Eliminación iniciada (puede tardar 5-10 minutos)" -ForegroundColor Green
    Write-Host "💰 Costo después de eliminar: `$0" -ForegroundColor Green
    Write-Host "💳 Tus `$100 USD siguen intactos" -ForegroundColor Cyan
} else {
    Write-Host "❌ Eliminación cancelada" -ForegroundColor Yellow
}
```

---

## 📊 Resumen de la Épica

### Estadísticas

| Métrica | Valor |
|---------|-------|
| **Total de Tareas** | 26 |
| **Fases** | 7 |
| **Estimación Total** | ~6-8 horas |
| **Costo del Deployment** | **$0/mes** |
| **Servicios Azure** | 6 |
| **Archivos a Crear** | 8 |
| **Archivos a Modificar** | 2 |

### Distribución por Fase

| Fase | Tareas | Tiempo Estimado |
|------|--------|-----------------|
| 1. Preparación del Código | 5 | 55 min |
| 2. Infraestructura Azure | 4 | 60-80 min |
| 3. Deployment de Aplicaciones | 5 | 120 min |
| 4. Verificación y Pruebas | 3 | 65 min |
| 5. Controles de Gasto | 3 | 50 min |
| 6. Documentación | 4 | 110 min |
| 7. Post-Demo | 2 | 10 min |
| **TOTAL** | **26** | **~6-8 horas** |

### Priorización

| Prioridad | Cantidad | Descripción |
|-----------|----------|-------------|
| **Alta** | 15 | Tareas críticas para el deployment |
| **Media** | 8 | Tareas importantes pero no bloqueantes |
| **Baja** | 3 | Tareas opcionales o post-demo |

---

## 🎯 Orden de Ejecución Recomendado

### Día 1: Preparación (1-2 horas)
1. T-DEPLOY-001: Crear startup.sh
2. T-DEPLOY-002: Actualizar requirements.txt
3. T-DEPLOY-003: Verificar Next.js config
4. T-DEPLOY-004: Crear .deployment
5. T-DEPLOY-005: Crear .env.production.example
6. **Commit y push** a GitHub

### Día 2: Deployment a Azure (2-3 horas)
7. T-DEPLOY-006: Verificar cuenta Azure
8. T-DEPLOY-007: Ejecutar script deployment (⏱️ 30-45 min)
9. T-DEPLOY-008: Configurar CORS en Blob Storage
10. T-DEPLOY-009: Configurar MySQL firewall
11. T-DEPLOY-010: Preparar GitHub Actions
12. **Break ☕**
13. T-DEPLOY-011: Deploy manual Backend
14. T-DEPLOY-012: Deploy manual Frontend

### Día 3: Migraciones y Testing (2-3 horas)
15. T-DEPLOY-013: Migrar datos a MySQL
16. T-DEPLOY-014: Migrar imágenes a Blob Storage
17. T-DEPLOY-015: Verificar endpoints Backend
18. T-DEPLOY-016: Verificar Frontend
19. T-DEPLOY-017: Prueba end-to-end completa
20. **Break ☕**
21. T-DEPLOY-018: Configurar alertas de presupuesto
22. T-DEPLOY-020: Crear script monitoreo costos

### Día 4: Documentación (1-2 horas)
23. T-DEPLOY-021: Documentar URLs y credenciales
24. T-DEPLOY-022: Crear guía troubleshooting
25. T-DEPLOY-023: Preparar presentación
26. (Opcional) T-DEPLOY-024: Grabar video demo

### Post-Presentación: Limpieza
27. T-DEPLOY-025: Apagar servicios
28. (Opcional) T-DEPLOY-026: Eliminar recursos

---

## ✅ Checklist Final

Antes de la presentación, verifica:

```
□ Frontend accesible públicamente
□ Backend accesible públicamente
□ Login funciona correctamente
□ Subida de imágenes funciona
□ Base de datos con datos de prueba
□ CORS configurado sin errores
□ Alertas de presupuesto activas
□ Costo actual: $0
□ Presentación preparada
□ Video demo grabado (opcional)
□ DEPLOYMENT_INFO.md actualizado
□ Instrucciones para apagar servicios documentadas
```

---

## 🆘 Soporte y Recursos

- **Azure Portal**: https://portal.azure.com
- **Azure Students**: https://azure.microsoft.com/es-es/free/students/
- **Documentación Azure App Service**: https://learn.microsoft.com/es-es/azure/app-service/
- **GitHub Actions Docs**: https://docs.github.com/es/actions
- **Stack Overflow**: Tag `azure-app-service`

---

## 📞 Contacto

**Proyecto**: Asistente Plantitas  
**Universidad**: Nacional de La Matanza  
**Fecha**: Noviembre 2025  

---

**¡Éxito con tu presentación! 🚀🌱**
