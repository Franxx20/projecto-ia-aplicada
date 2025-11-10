# 🚀 Estado del Deployment - Azure for Students

**Fecha**: 2025-11-10  
**Región**: Chile Central  
**Suscripción**: Azure for Students (Universidad Nacional de La Matanza)

## ✅ Recursos Creados Exitosamente

### 1. **Resource Group**
- **Nombre**: `rg-plantitas-demo-academica`
- **Ubicación**: Chile Central
- **Estado**: ✅ Creado
- **Tags**: Proyecto="Plantitas", Tipo="Demo_Academica", Universidad="UNLAM", Temporal="Si"

### 2. **Storage Account**
- **Nombre**: `plantitasdemostorage`
- **SKU**: Standard_LRS
- **Tier**: Hot
- **Estado**: ✅ Succeeded
- **Container**: `plantitas-imagenes` (creado)

### 3. **App Service Plan**
- **Nombre**: `plantitas-demo-plan`
- **Tier**: Free (F1) - Linux
- **Estado**: ✅ Ready
- **Costo**: $0/mes (FREE tier)

### 4. **Backend Web App**
- **Nombre**: `plantitas-demo-backend`
- **Runtime**: Python 3.11
- **URL**: https://plantitas-demo-backend.azurewebsites.net
- **Estado**: ✅ Running
- **Startup File**: startup.sh

### 5. **Frontend Web App**
- **Nombre**: `plantitas-frontend-app`
- **Runtime**: Node.js 20 LTS
- **URL**: https://plantitas-frontend-app.azurewebsites.net
- **Estado**: ✅ Running

### 6. **MySQL Flexible Server**
- **Nombre**: `plantitas-mysql-server`
- **SKU**: Standard_B1ms (Burstable)
- **Storage**: 20 GB
- **Version**: 8.0.21
- **Estado**: 🔄 En creación (~10-15 min)
- **Admin User**: plantitasadmin
- **Password**: Guardado en `db_password_demo.txt`

---

## 📋 Tareas Pendientes

### 🔄 En Progreso:
1. Esperar finalización de MySQL Server (10-15 minutos)

### ⏳ Por Hacer:
1. Crear database `plantitas_db` en MySQL
2. Configurar variables de entorno en Backend:
   - DATABASE_URL
   - JWT_SECRET_KEY
   - AZURE_STORAGE_CONNECTION_STRING
   - CORS_ORIGINS
3. Configurar variables de entorno en Frontend:
   - NEXT_PUBLIC_API_URL
4. Configurar CORS en Blob Storage
5. Configurar firewall rules en MySQL

---

## 🔧 Comandos para Completar Deployment

### 1. Verificar Estado de MySQL
```powershell
az mysql flexible-server show --name plantitas-mysql-server --resource-group rg-plantitas-demo-academica
```

### 2. Crear Database
```powershell
az mysql flexible-server db create `
  --resource-group rg-plantitas-demo-academica `
  --server-name plantitas-mysql-server `
  --database-name plantitas_db
```

### 3. Configurar Backend Variables
```powershell
# Obtener connection string de Storage
$STORAGE_CONN = az storage account show-connection-string `
  --name plantitasdemostorage `
  --resource-group rg-plantitas-demo-academica `
  --output tsv

# Generar JWT Secret
$JWT_SECRET = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 64 | ForEach-Object {[char]$_})

# Obtener DB Password
$DB_PASSWORD = (Get-Content "db_password_demo.txt").Split(": ")[1]

# Database URL
$DATABASE_URL = "mysql+pymysql://plantitasadmin:${DB_PASSWORD}@plantitas-mysql-server.mysql.database.azure.com:3306/plantitas_db?ssl_ca=/etc/ssl/certs/ca-certificates.crt"

# Configurar Backend
az webapp config appsettings set `
  --name plantitas-demo-backend `
  --resource-group rg-plantitas-demo-academica `
  --settings `
    DATABASE_URL="$DATABASE_URL" `
    JWT_SECRET_KEY="$JWT_SECRET" `
    AZURE_STORAGE_CONNECTION_STRING="$STORAGE_CONN" `
    AZURE_STORAGE_CONTAINER_NAME="plantitas-imagenes" `
    AZURE_STORAGE_USE_EMULATOR="false" `
    ENVIRONMENT="production" `
    DEBUG="false" `
    CORS_ORIGINS="https://plantitas-frontend-app.azurewebsites.net"

# Configurar startup file
az webapp config set `
  --name plantitas-demo-backend `
  --resource-group rg-plantitas-demo-academica `
  --startup-file "startup.sh"
```

### 4. Configurar Frontend Variables
```powershell
az webapp config appsettings set `
  --name plantitas-frontend-app `
  --resource-group rg-plantitas-demo-academica `
  --settings `
    NEXT_PUBLIC_API_URL="https://plantitas-demo-backend.azurewebsites.net" `
    NODE_ENV="production"
```

### 5. Configurar CORS en Blob Storage
```powershell
az storage cors add `
  --services b `
  --methods GET POST PUT DELETE `
  --origins "https://plantitas-frontend-app.azurewebsites.net" `
  --allowed-headers "*" `
  --exposed-headers "*" `
  --max-age 3600 `
  --account-name plantitasdemostorage
```

---

## 💰 Costos Estimados

| Recurso | Tier | Costo |
|---------|------|-------|
| App Service Plan | F1 (Free) | **$0/mes** |
| MySQL Flexible Server | Standard_B1ms | **750 hrs/mes gratis** |
| Storage Account | Standard LRS | **5 GB gratis** |
| **TOTAL** | | **$0/mes** ✅ |

---

## 🌎 URLs del Proyecto

- **Frontend**: https://plantitas-frontend-app.azurewebsites.net
- **Backend**: https://plantitas-demo-backend.azurewebsites.net
- **Backend API Docs**: https://plantitas-demo-backend.azurewebsites.net/docs

---

## 📝 Notas Importantes

1. **Región Chile Central**: Es la única región permitida por la política de tu suscripción Azure for Students
2. **Password MySQL**: Guardado en `db_password_demo.txt` - **¡NO COMPARTIR!**
3. **Providers Registrados**: Microsoft.Storage, Microsoft.DBforMySQL, Microsoft.Web
4. **Tier FREE**: Todos los recursos están en tier gratuito, no consumirás créditos
5. **Apagar después**: Ver `INSTRUCCIONES_APAGAR_DEMO.md` para apagar recursos post-presentación

---

## 🐛 Problemas Resueltos Durante Deployment

1. ✅ **Región eastus bloqueada**: Cambiado a Chile Central
2. ✅ **Providers no registrados**: Registrados automáticamente
3. ✅ **Runtime Node.js 18**: Actualizado a Node.js 20 LTS
4. ✅ **Nombre frontend conflicto**: Cambiado a `plantitas-frontend-app`

---

**Última actualización**: 2025-11-10 02:23 UTC  
**Responsable**: Franco Garcete (fgarcete@alumno.unlam.edu.ar)
