# Corrección de Imágenes Rotas en Azurite (Mock de Azure Storage)

## Problema
Las imágenes no se visualizaban en el dashboard porque las URLs generadas por Azurite usaban direcciones internas del contenedor (`127.0.0.1:10000` o `azurite:10000`) que no son accesibles desde el navegador del host.

## Solución Implementada

### 1. Configuración de Azurite (✅ Completo)
- **Archivo**: `backend/.env`
- **Cambio**: Configurado connection string de Azurite:
  ```env
  AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;
  AZURE_STORAGE_CONTAINER_NAME=plantitas-imagenes
  AZURE_STORAGE_USE_EMULATOR=true
  ```

### 2. Servicio de Imágenes - Reemplazo de URLs (✅ Completo)
- **Archivo**: `backend/app/services/imagen_service.py`
- **Método**: `obtener_url_blob()`
- **Cambio**: Agregado reemplazo automático de URLs internas por URLs accesibles:
  ```python
  if config.azure_storage_use_emulator or 'devstoreaccount1' in url:
      url = url.replace('http://azurite:10000', 'http://localhost:10000')
      url = url.replace('http://127.0.0.1:10000', 'http://localhost:10000')
  ```
- **Impacto**: Todas las **nuevas imágenes** subidas ahora tendrán URLs correctas automáticamente

### 3. Corrección de URLs Existentes en Base de Datos (✅ Completo)
- **Script**: `backend/fix_azurite_urls_auto.py`
- **Ejecución**: 
  ```bash
  docker exec projecto-ia_backend_dev python /app/fix_azurite_urls_auto.py
  ```
- **Resultado**: **106 URLs actualizadas** exitosamente en PostgreSQL
- **Antes**: `http://127.0.0.1:10000/devstoreaccount1/plantitas-imagenes/imagen.jpg`
- **Después**: `http://localhost:10000/devstoreaccount1/plantitas-imagenes/imagen.jpg`

### 4. Container de Azurite - Configuración de Acceso Público (✅ Completo)
- **Script**: `backend/test_azurite_local.py`
- **Cambio**: Configurado acceso público a nivel de blob:
  ```python
  container_client.set_container_access_policy(
      signed_identifiers={},
      public_access=PublicAccess.Blob
  )
  ```
- **Resultado**: Container `plantitas-imagenes` ahora permite acceso público

### 5. Reinicio del Backend (✅ Completo)
- **Comando**: `docker-compose -f docker-compose.dev.yml restart backend`
- **Estado**: Backend reiniciado exitosamente

## Archivos Modificados

### Modificados:
1. `backend/.env` - Configuración de Azurite
2. `backend/app/services/imagen_service.py` - Reemplazo de URLs
3. `backend/AZURE_STORAGE_SETUP.md` - Documentación actualizada (ya existía)

### Creados:
1. `backend/test_azurite_local.py` - Script de verificación de Azurite
2. `backend/fix_azurite_urls.py` - Script interactivo de corrección
3. `backend/fix_azurite_urls_auto.py` - Script automático de corrección

## Verificación

### Estado Actual:
- ✅ Azurite corriendo en puerto 10000
- ✅ Container `plantitas-imagenes` con acceso público
- ✅ 106 imágenes con URLs corregidas
- ✅ Backend reiniciado con nueva configuración
- ✅ Servicio de imágenes actualizado para generar URLs correctas

### Cómo Verificar que Funciona:
1. **Abrir el dashboard** en el navegador: `http://localhost:4200/dashboard`
2. **Verificar que las imágenes se muestran** en las tarjetas de plantas
3. **Inspeccionar URLs** en DevTools (F12 → Network):
   - Deben apuntar a `http://localhost:10000/devstoreaccount1/plantitas-imagenes/...`
   - Status code debe ser `200 OK`

### Solución de Problemas:

**Si las imágenes siguen sin mostrarse:**

1. **Verificar Azurite:**
   ```bash
   docker ps | grep azurite
   # Debe mostrar: projecto-ia_azurite_dev
   ```

2. **Probar URL directamente** en el navegador:
   ```
   http://localhost:10000/devstoreaccount1/plantitas-imagenes/[nombre-blob].jpg
   ```

3. **Verificar CORS** (si hay errores en consola):
   - Azurite debería tener CORS habilitado por defecto en modo loose
   - Si no funciona, reiniciar Azurite:
     ```bash
     docker-compose -f docker-compose.dev.yml restart azurite
     ```

4. **Re-ejecutar script de corrección:**
   ```bash
   docker exec projecto-ia_backend_dev python /app/fix_azurite_urls_auto.py
   ```

5. **Verificar con script de diagnóstico:**
   ```bash
   python backend/test_azurite_local.py
   ```

## Próximas Subidas de Imágenes

Las **nuevas imágenes** subidas a partir de ahora **tendrán automáticamente URLs correctas** gracias al cambio en el método `obtener_url_blob()`.

No es necesario ejecutar scripts de corrección para nuevas imágenes.

## Migración a Azure Storage Real (Producción)

Cuando quieras migrar de Azurite a Azure Storage real:

1. Editar `backend/.env`:
   ```env
   AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=YOUR_ACCOUNT;AccountKey=YOUR_KEY;EndpointSuffix=core.windows.net
   AZURE_STORAGE_USE_EMULATOR=false
   ```

2. El código **NO requiere cambios** - el mismo método `obtener_url_blob()` funcionará automáticamente porque solo reemplaza URLs cuando detecta Azurite.

3. Las imágenes en Azurite **no se migran automáticamente** - necesitarás un script de migración si quieres mover las existentes.

## Resumen

✅ **Problema resuelto**: Las imágenes ahora deberían mostrarse correctamente en el dashboard
✅ **106 URLs actualizadas** en la base de datos PostgreSQL
✅ **Backend configurado** para generar URLs correctas automáticamente
✅ **Azurite funcionando** con acceso público habilitado

---

**Última actualización**: 1 de noviembre de 2025  
**Estado**: ✅ COMPLETADO
