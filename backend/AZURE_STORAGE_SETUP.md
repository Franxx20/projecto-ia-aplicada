# 🔧 Guía de Configuración de Azure Blob Storage

Esta guía te ayudará a configurar Azure Blob Storage para que las imágenes de las plantas se guarden y se muestren correctamente.

## 📋 Prerrequisitos

- Una cuenta de Azure activa
- Un Storage Account creado en Azure

## 🚀 Pasos para Configurar

### 1️⃣ Crear o Acceder a tu Storage Account en Azure

1. Ve al [Azure Portal](https://portal.azure.com)
2. Busca "Storage accounts" en la barra de búsqueda
3. Si no tienes uno, créalo:
   - Click en **"+ Create"**
   - Selecciona tu suscripción y grupo de recursos
   - Nombre: `plantitasstorage` (o el que prefieras)
   - Region: Selecciona la más cercana
   - Performance: **Standard**
   - Redundancy: **LRS** (Locally-redundant storage) para desarrollo
   - Click en **"Review + Create"** → **"Create"**

### 2️⃣ Obtener las Credenciales

#### Opción A: Connection String (RECOMENDADO)

1. Ve a tu Storage Account
2. En el menú izquierdo, busca **"Security + networking"** → **"Access keys"**
3. Click en **"Show keys"**
4. Copia el **"Connection string"** de la key1 o key2
5. Se verá así:
   ```
   DefaultEndpointsProtocol=https;AccountName=plantitasstorage;AccountKey=ABC123...xyz==;EndpointSuffix=core.windows.net
   ```

#### Opción B: Account Name + Key (Alternativa)

1. Ve a tu Storage Account
2. En el menú izquierdo, busca **"Security + networking"** → **"Access keys"**
3. Copia:
   - **Storage account name**: Ejemplo: `plantitasstorage`
   - **Key**: La key1 o key2 (se ve como una cadena larga de caracteres)

### 3️⃣ Configurar las Variables de Entorno

Edita el archivo `backend/.env` y reemplaza los valores:

#### Si usas Connection String (Opción A):

```bash
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=TU_CUENTA_AQUI;AccountKey=TU_KEY_AQUI;EndpointSuffix=core.windows.net
AZURE_STORAGE_CONTAINER_NAME=plantitas-imagenes
AZURE_STORAGE_USE_EMULATOR=false
```

#### Si usas Account Name + Key (Opción B):

```bash
# Comenta o elimina la línea de Connection String
# AZURE_STORAGE_CONNECTION_STRING=...

# Y descomenta estas líneas:
AZURE_STORAGE_ACCOUNT_NAME=tu-storage-account-name
AZURE_STORAGE_ACCOUNT_KEY=tu-key-aqui
AZURE_STORAGE_CONTAINER_NAME=plantitas-imagenes
AZURE_STORAGE_USE_EMULATOR=false
```

### 4️⃣ Configurar CORS (Importante para el Frontend)

Para que el frontend pueda acceder a las imágenes:

1. Ve a tu Storage Account en Azure Portal
2. En el menú izquierdo, busca **"Settings"** → **"Resource sharing (CORS)"**
3. En la pestaña **"Blob service"**, agrega una nueva regla:
   - **Allowed origins**: `*` (para desarrollo) o `http://localhost:3000,http://localhost:4200`
   - **Allowed methods**: GET, HEAD, OPTIONS
   - **Allowed headers**: `*`
   - **Exposed headers**: `*`
   - **Max age**: 3600
4. Click en **"Save"**

### 5️⃣ Verificar la Configuración

Ejecuta el script de diagnóstico:

```bash
cd backend
python test_azure_public_access.py
```

Deberías ver:
```
✅ El container 'plantitas-imagenes' existe
✅ El container ya tiene acceso público configurado correctamente
✅ Encontrados X blobs
```

### 6️⃣ Reiniciar el Backend

#### Si usas Docker:
```bash
docker-compose restart backend
```

#### Si ejecutas localmente:
```bash
# Detén el servidor (Ctrl+C) y vuelve a ejecutar:
cd backend
python run.py
```

## 🧪 Probar que Funciona

1. Ve a tu aplicación frontend
2. Identifica una nueva planta subiendo una foto
3. Ve al dashboard
4. Deberías ver la foto de la planta correctamente

## 🔍 Troubleshooting

### ❌ Error: "No se proporcionó configuración válida para Azure Storage"
- Verifica que el archivo `.env` tenga las variables correctamente configuradas
- Asegúrate de reiniciar el backend después de modificar el `.env`

### ❌ Las imágenes no se ven (Error 404 o 403)
- Verifica que el container tenga acceso público:
  ```bash
  python test_azure_public_access.py
  ```
- Si el script dice que el acceso no es público, se actualizará automáticamente
- Reinicia el backend

### ❌ Error de CORS al cargar imágenes
- Configura CORS en tu Storage Account (ver paso 4)
- Asegúrate de incluir los orígenes correctos

### ❌ Error: "Connection string is invalid"
- Verifica que copiaste el connection string completo
- No debe tener espacios al principio o final
- Debe estar en UNA sola línea (sin saltos de línea)

## 🌱 Desarrollo Local con Azurite (Opcional)

Si prefieres no usar Azure en desarrollo, puedes usar Azurite:

1. Instala Azurite:
   ```bash
   npm install -g azurite
   ```

2. Ejecuta Azurite:
   ```bash
   azurite --silent
   ```

3. Configura el `.env`:
   ```bash
   AZURE_STORAGE_USE_EMULATOR=true
   AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;
   ```

## 📚 Referencias

- [Azure Blob Storage Docs](https://docs.microsoft.com/azure/storage/blobs/)
- [Azure Storage Access Keys](https://docs.microsoft.com/azure/storage/common/storage-account-keys-manage)
- [CORS Configuration](https://docs.microsoft.com/azure/storage/blobs/storage-cors-support)

---

💡 **Nota**: Mantén tus credenciales seguras y NUNCA las subas a Git. El archivo `.env` ya está en `.gitignore`.
