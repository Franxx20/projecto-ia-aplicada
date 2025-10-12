# 📦 Configuración de Azure Blob Storage para Asistente Plantitas

## 📋 Tabla de Contenidos
- [Introducción](#introducción)
- [Azurite - Emulador Local](#azurite---emulador-local)
- [Configuración para Desarrollo](#configuración-para-desarrollo)
- [Configuración para Producción](#configuración-para-producción)
- [Testing](#testing)
- [API de Imágenes](#api-de-imágenes)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Introducción

Este proyecto utiliza **Azure Blob Storage** para almacenar y gestionar las imágenes de las plantas. Para facilitar el desarrollo local sin costos de Azure, utilizamos **Azurite**, el emulador oficial de Azure Storage.

### ¿Por qué Azure Blob Storage?

- ✅ **Escalable**: Soporta desde KB hasta PB de datos
- ✅ **Seguro**: Encriptación en tránsito y en reposo
- ✅ **Económico**: Pago por uso real
- ✅ **CDN Ready**: Integración directa con Azure CDN
- ✅ **REST API**: Acceso desde cualquier plataforma

---

## 🐳 Azurite - Emulador Local

Azurite es el emulador oficial de Microsoft para Azure Storage. Proporciona una experiencia **100% compatible** con la API de Azure Storage, pero corriendo localmente en Docker.

### Características de Azurite

| Característica | Azurite | Azure Storage Real |
|---------------|---------|-------------------|
| API Compatibility | ✅ 100% | ✅ 100% |
| Blob Service | ✅ | ✅ |
| Queue Service | ✅ | ✅ |
| Table Service | ✅ | ✅ |
| Costo | 🆓 Gratis | 💰 Por uso |
| Latencia | ⚡ <1ms | 🌐 50-200ms |
| Datos Persistentes | ✅ Opcional | ✅ Siempre |

### Servicios Incluidos

Azurite expone tres servicios en puertos diferentes:

- **Puerto 10000**: Blob Service (almacenamiento de archivos)
- **Puerto 10001**: Queue Service (colas de mensajes)
- **Puerto 10002**: Table Service (almacenamiento NoSQL)

---

## ⚙️ Configuración para Desarrollo

### 1. Configuración en Docker Compose

El archivo `docker-compose.dev.yml` ya incluye la configuración de Azurite:

```yaml
services:
  azurite:
    image: mcr.microsoft.com/azure-storage/azurite:latest
    container_name: projecto-ia_azurite_dev
    ports:
      - "10000:10000"  # Blob service
      - "10001:10001"  # Queue service
      - "10002:10002"  # Table service
    volumes:
      - azurite_data:/data
    command: azurite --blobHost 0.0.0.0 --queueHost 0.0.0.0 --tableHost 0.0.0.0 --loose
    networks:
      - plantitas-network

volumes:
  azurite_data:
    driver: local
```

### 2. Variables de Entorno

En el servicio `backend` del `docker-compose.dev.yml`:

```yaml
environment:
  AZURE_STORAGE_CONNECTION_STRING: "DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint=http://azurite:10000/devstoreaccount1;"
  AZURE_STORAGE_CONTAINER_NAME: "plantitas-imagenes"
  AZURE_STORAGE_USE_EMULATOR: "true"
```

#### Desglose del Connection String

```
DefaultEndpointsProtocol=http          # Protocolo (http en local, https en prod)
AccountName=devstoreaccount1           # Cuenta por defecto de Azurite
AccountKey=Eby8vdM02xNOcqF...          # Key fija de Azurite (públicamente conocida)
BlobEndpoint=http://azurite:10000/...  # URL del servicio blob
```

> **⚠️ Importante**: Estas credenciales son **públicas** y solo para Azurite. NUNCA uses estas keys en producción.

### 3. Iniciar los Servicios

```bash
# Levantar todos los servicios incluyendo Azurite
docker-compose -f docker-compose.dev.yml up -d

# Verificar que Azurite esté corriendo
docker-compose -f docker-compose.dev.yml ps azurite
```

### 4. Verificar Conectividad

Ejecuta el script de prueba de conectividad:

```bash
docker-compose -f docker-compose.dev.yml exec backend python test_azure_storage.py
```

Deberías ver:

```
🔍 Probando conexión a Azure Blob Storage...
✅ Cliente de Blob Storage creado exitosamente

📦 1. Creando contenedor 'plantitas-imagenes'...
✅ Contenedor creado: plantitas-imagenes

📤 2. Subiendo archivo de prueba...
✅ Archivo subido: test-image.txt

📋 3. Listando archivos en el contenedor...
✅ Archivos encontrados: 1
   - test-image.txt

📥 4. Descargando archivo...
✅ Archivo descargado correctamente
✅ Contenido verificado: coincide con el original

🗑️  5. Eliminando archivo de prueba...
✅ Archivo eliminado correctamente

✅ TODAS LAS PRUEBAS PASARON EXITOSAMENTE
```

---

## 🚀 Configuración para Producción

### 1. Crear Storage Account en Azure

```bash
# Instalar Azure CLI si no lo tienes
# https://docs.microsoft.com/en-us/cli/azure/install-azure-cli

# Login en Azure
az login

# Crear Resource Group
az group create --name plantitas-rg --location eastus

# Crear Storage Account
az storage account create \
  --name plantitasstorage \
  --resource-group plantitas-rg \
  --location eastus \
  --sku Standard_LRS \
  --kind StorageV2

# Obtener Connection String
az storage account show-connection-string \
  --name plantitasstorage \
  --resource-group plantitas-rg \
  --output tsv
```

### 2. Crear Contenedor

```bash
# Crear contenedor para imágenes
az storage container create \
  --name plantitas-imagenes \
  --account-name plantitasstorage \
  --public-access off
```

### 3. Configurar Variables de Entorno en Producción

Actualiza tus variables de entorno (`.env` o configuración de deployment):

```bash
AZURE_STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=plantitasstorage;AccountKey=TU_ACCOUNT_KEY_AQUI;EndpointSuffix=core.windows.net"
AZURE_STORAGE_CONTAINER_NAME="plantitas-imagenes"
AZURE_STORAGE_USE_EMULATOR="false"
```

> **🔒 Seguridad**: 
> - NUNCA commiteés el connection string de producción al repositorio
> - Usa Azure Key Vault o variables de entorno seguras
> - Considera usar Managed Identity en Azure App Service

### 4. Configurar CORS (si accedes desde navegador)

```bash
az storage cors add \
  --services b \
  --methods GET POST PUT DELETE \
  --origins "https://tudominio.com" \
  --allowed-headers "*" \
  --exposed-headers "*" \
  --max-age 3600 \
  --account-name plantitasstorage
```

---

## 🧪 Testing

### Script de Prueba de Conectividad

**Ubicación**: `backend/test_azure_storage.py`

Este script verifica que:
1. ✅ La conexión a Azure Storage funciona
2. ✅ Se puede crear un contenedor
3. ✅ Se pueden subir archivos
4. ✅ Se pueden listar archivos
5. ✅ Se pueden descargar archivos
6. ✅ Se pueden eliminar archivos

**Ejecución**:
```bash
docker-compose -f docker-compose.dev.yml exec backend python test_azure_storage.py
```

### Script de Prueba de API Completa

**Ubicación**: `backend/test_api_imagenes.py`

Este script prueba el flujo completo de la API:
1. ✅ Registro de usuario
2. ✅ Login y obtención de JWT
3. ✅ Subida de imagen
4. ✅ Listado de imágenes
5. ✅ Obtención de imagen específica
6. ✅ Actualización de descripción
7. ✅ Eliminación de imagen (soft delete)
8. ✅ Verificación de eliminación

**Ejecución**:
```bash
docker-compose -f docker-compose.dev.yml exec backend python test_api_imagenes.py
```

### Tests Unitarios

Para ejecutar los tests unitarios del servicio de imágenes:

```bash
# Todos los tests
docker-compose -f docker-compose.dev.yml exec backend pytest

# Solo tests de imágenes
docker-compose -f docker-compose.dev.yml exec backend pytest tests/test_t004*

# Con cobertura
docker-compose -f docker-compose.dev.yml exec backend pytest --cov=app.services.imagen_service
```

---

## 📡 API de Imágenes

### Endpoints Disponibles

#### 1. Subir Imagen

```http
POST /api/v1/imagenes/subir
Authorization: Bearer {jwt_token}
Content-Type: multipart/form-data

Body:
- archivo: File (required)
- descripcion: string (optional)
```

**Respuesta exitosa (201)**:
```json
{
  "id": 1,
  "usuario_id": 5,
  "nombre_archivo": "mi_planta.jpg",
  "nombre_blob": "uuid-generado.jpg",
  "url_blob": "http://azurite:10000/devstoreaccount1/plantitas-imagenes/uuid.jpg",
  "content_type": "image/jpeg",
  "tamano_bytes": 245678,
  "descripcion": "Mi planta favorita",
  "created_at": "2025-10-12T15:30:00",
  "is_deleted": false
}
```

#### 2. Listar Imágenes del Usuario

```http
GET /api/v1/imagenes/
Authorization: Bearer {jwt_token}
```

**Query Parameters**:
- `skip`: int (default: 0) - Paginación
- `limit`: int (default: 10) - Límite de resultados

**Respuesta exitosa (200)**:
```json
[
  {
    "id": 1,
    "nombre_archivo": "planta1.jpg",
    "url_blob": "http://...",
    "tamano_bytes": 245678,
    "created_at": "2025-10-12T15:30:00"
  },
  // ...más imágenes
]
```

#### 3. Obtener Imagen Específica

```http
GET /api/v1/imagenes/{imagen_id}
Authorization: Bearer {jwt_token}
```

**Respuesta exitosa (200)**: Objeto completo de la imagen

#### 4. Actualizar Descripción

```http
PUT /api/v1/imagenes/{imagen_id}
Authorization: Bearer {jwt_token}
Content-Type: application/json

{
  "descripcion": "Nueva descripción"
}
```

#### 5. Eliminar Imagen

```http
DELETE /api/v1/imagenes/{imagen_id}
Authorization: Bearer {jwt_token}
```

**Respuesta exitosa (200)**:
```json
{
  "mensaje": "Imagen eliminada exitosamente"
}
```

> **📝 Nota**: La eliminación es **soft delete**. La imagen se marca como `is_deleted=true` pero no se elimina físicamente de Azure Storage.

### Validaciones

- ✅ **Tipos de archivo permitidos**: JPG, JPEG, PNG, GIF, WEBP
- ✅ **Tamaño máximo**: 10 MB
- ✅ **Autenticación**: JWT requerido en todos los endpoints
- ✅ **Autorización**: Solo el propietario puede ver/modificar/eliminar sus imágenes

---

## 🔧 Troubleshooting

### Problema: "Connection refused" al conectar a Azurite

**Causa**: Azurite no está corriendo o hay problemas de red

**Solución**:
```bash
# Verificar que Azurite esté corriendo
docker-compose -f docker-compose.dev.yml ps azurite

# Si no está corriendo, iniciarlo
docker-compose -f docker-compose.dev.yml up -d azurite

# Ver logs de Azurite
docker-compose -f docker-compose.dev.yml logs azurite
```

### Problema: "column nombre_archivo does not exist"

**Causa**: La tabla `imagenes` no está sincronizada con el modelo actual

**Solución**:
```bash
# Eliminar y recrear la tabla (SOLO EN DESARROLLO)
docker-compose -f docker-compose.dev.yml exec db psql -U postgres -d proyecto_ia_db -c "DROP TABLE IF EXISTS imagenes CASCADE;"

# Aplicar migraciones
docker-compose -f docker-compose.dev.yml exec backend alembic upgrade head
```

### Problema: "ContentSettings object has no attribute..."

**Causa**: Bug ya corregido en `imagen_service.py`

**Solución**: Asegúrate de tener la última versión del código donde `ContentSettings` se importa correctamente:

```python
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, ContentSettings
```

### Problema: Connection string no funciona en producción

**Verificaciones**:
1. ✅ ¿El connection string tiene `https` en lugar de `http`?
2. ✅ ¿La Account Key es correcta?
3. ✅ ¿El Storage Account existe y está activo?
4. ✅ ¿El firewall de Azure permite tu IP?

```bash
# Verificar que el storage account existe
az storage account show --name plantitasstorage --resource-group plantitas-rg

# Verificar conectividad de red
curl https://plantitasstorage.blob.core.windows.net/
```

### Problema: "403 Forbidden" al acceder a blobs

**Causa**: Permisos incorrectos o firma SAS expirada

**Solución**:
```bash
# Verificar nivel de acceso del contenedor
az storage container show-permission \
  --name plantitas-imagenes \
  --account-name plantitasstorage

# Configurar acceso privado (recomendado)
az storage container set-permission \
  --name plantitas-imagenes \
  --account-name plantitasstorage \
  --public-access off
```

---

## 📊 Monitoreo y Logs

### Logs de Azurite (Desarrollo)

```bash
# Ver logs en tiempo real
docker-compose -f docker-compose.dev.yml logs -f azurite

# Ver últimas 100 líneas
docker-compose -f docker-compose.dev.yml logs --tail=100 azurite
```

### Logs de Azure Storage (Producción)

En Azure Portal:
1. Navega a tu Storage Account
2. Sección "Monitoring" → "Logs"
3. Ejecuta queries de Azure Monitor Logs

### Métricas Importantes

- **Transacciones**: Número de requests a Storage
- **Latencia**: Tiempo de respuesta E2E
- **Disponibilidad**: Uptime del servicio
- **Capacidad**: Espacio usado vs disponible

---

## 🔐 Mejores Prácticas de Seguridad

### 1. Connection Strings

- ❌ **NO** guardes connection strings en el código
- ✅ **SÍ** usa variables de entorno
- ✅ **SÍ** usa Azure Key Vault en producción
- ✅ **SÍ** rota las access keys periódicamente

### 2. Acceso a Blobs

- ✅ **Privado por defecto**: No hagas contenedores públicos
- ✅ **SAS Tokens**: Usa tokens temporales para acceso limitado
- ✅ **Managed Identity**: Usa identidades administradas en Azure
- ✅ **CORS**: Configura solo dominios autorizados

### 3. Datos Sensibles

- ✅ **Encriptación**: Activa encriptación en reposo
- ✅ **HTTPS**: Solo protocolo seguro en producción
- ✅ **Firewall**: Restringe IPs que pueden acceder
- ✅ **Auditoría**: Activa logging de accesos

---

## 📚 Referencias

- [Documentación oficial de Azure Blob Storage](https://docs.microsoft.com/en-us/azure/storage/blobs/)
- [Documentación de Azurite](https://github.com/Azure/Azurite)
- [Python SDK para Azure Storage](https://docs.microsoft.com/en-us/python/api/overview/azure/storage-blob-readme)
- [Mejores prácticas de seguridad](https://docs.microsoft.com/en-us/azure/storage/blobs/security-recommendations)

---

## 💬 Soporte

Si encuentras algún problema o tienes preguntas:

1. Revisa la sección de [Troubleshooting](#troubleshooting)
2. Revisa los logs: `docker-compose logs backend azurite`
3. Ejecuta los scripts de prueba para diagnosticar
4. Contacta al equipo de desarrollo

---

**Última actualización**: Octubre 2025  
**Versión**: 1.0.0  
**Mantenedores**: Equipo Backend - Proyecto Asistente Plantitas
