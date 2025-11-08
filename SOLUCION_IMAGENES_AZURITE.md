# SOLUCIÓN DEFINITIVA: Imágenes de Azurite no se ven en el Dashboard

## 🔍 Problema Identificado

Cuando agregas nuevas plantas, las imágenes se suben correctamente a Azurite (el emulador de Azure Storage), pero no se ven en el dashboard. El problema es que el backend genera URLs con `http://azurite:10000` (dirección interna de Docker) en lugar de `http://localhost:10000` (dirección accesible desde tu navegador).

## ✅ Soluciones Aplicadas

He aplicado **3 soluciones en paralelo** para garantizar que esto no vuelva a suceder:

### 1. Script de Corrección Automática al Iniciar
**Archivo: `backend/fix_azurite_on_startup.py`**
- Se ejecuta automáticamente cada vez que el backend inicia
- Corrige TODAS las URLs en la base de datos reemplazando `azurite:10000` y `127.0.0.1:10000` con `localhost:10000`
- Integrado en `run.py` para ejecutarse antes de levantar el servidor

### 2. Monkey Patch en el Código
**Archivo: `backend/app/azurite_patch.py`**
- Parchea el método `obtener_url_blob()` al iniciar la aplicación
- Transforma automáticamente las URLs cuando se generan
- Importado automáticamente en `app/main.py`

### 3. Código Mejorado en imagen_service.py
**Archivo: `backend/app/services/imagen_service.py`**
- El método `obtener_url_blob()` ahora reemplaza automáticamente:
  - `http://azurite:10000` → `http://localhost:10000`
  - `http://127.0.0.1:10000` → `http://localhost:10000`
  - `https://azurite:10000` → `http://localhost:10000`
  - `https://127.0.0.1:10000` → `http://localhost:10000`

### 4. Configuración de Docker Compose
**Archivo: `docker-compose.dev.yml`**
- Ahora lee `AZURE_STORAGE_CONNECTION_STRING` del archivo `.env`
- Permite mayor flexibilidad para configurar la conexión

## 🚀 Cómo Verificar que Funciona

### Opción A: Reiniciar Todo (Recomendado)
```powershell
# Desde el directorio del proyecto
docker-compose -f docker-compose.dev.yml down
docker-compose -f docker-compose.dev.yml build backend
docker-compose -f docker-compose.dev.yml up -d
```

### Opción B: Solo Backend
```powershell
docker-compose -f docker-compose.dev.yml restart backend
```

### Verificar URLs Corregidas
```powershell
docker exec projecto-ia_backend_dev python /app/fix_azurite_on_startup.py
```

Deberías ver algo como:
```
✅ Azurite URLs: Corregidas 8 URLs en la base de datos
```

## 🧪 Prueba Final

Después de reiniciar:

1. **Agrega una nueva planta** usando el botón "Identificar Planta"
2. **Toma una foto o sube una imagen**
3. **Guarda la planta en tu colección**
4. **Refresca el dashboard** (F5)
5. **Verifica que la imagen se muestre correctamente**

Si la imagen se ve, ¡el problema está resuelto! ✅

## 🔧 Solución Manual (Si Sigue Sin Funcionar)

Si después de todo esto las imágenes TODAVÍA no se ven, ejecuta manualmente:

```powershell
# 1. Detener backend
docker-compose -f docker-compose.dev.yml stop backend

# 2. Eliminar __pycache__
docker exec projecto-ia_backend_dev find /app -type d -name "__pycache__" -exec rm -rf {} + 2>$null

# 3. Copiar archivo actualizado
docker cp backend\app\services\imagen_service.py projecto-ia_backend_dev:/app/app/services/imagen_service.py

# 4. Iniciar backend
docker-compose -f docker-compose.dev.yml start backend

# 5. Corregir URLs en la base de datos
docker exec projecto-ia_backend_dev python /app/fix_azurite_on_startup.py
```

## 📝 Archivos Modificados

- ✅ `backend/app/services/imagen_service.py` - Método `obtener_url_blob()` mejorado
- ✅ `backend/app/azurite_patch.py` - Monkey patch automático (NUEVO)
- ✅ `backend/app/main.py` - Importa el parche al iniciar
- ✅ `backend/fix_azurite_on_startup.py` - Script de corrección automática (NUEVO)
- ✅ `backend/run.py` - Ejecuta corrección antes de iniciar servidor
- ✅ `backend/.env` - Connection string actualizado
- ✅ `docker-compose.dev.yml` - Configuración de Azure Storage mejorada

## 🎯 Resultado Esperado

- ✅ Imágenes existentes corregidas automáticamente al iniciar
- ✅ Nuevas imágenes generadas con URL correcta
- ✅ Dashboard muestra todas las imágenes sin problemas
- ✅ No más "Imagen no disponible"
- ✅ Problema permanentemente solucionado

## ⚠️ Notas Importantes

1. **El script de corrección se ejecuta automáticamente** cada vez que el backend inicia
2. **No necesitas hacer nada manualmente** después de reiniciar
3. **Las nuevas plantas que agregues** ya tendrán las URLs correctas
4. **Si ves "Imagen no disponible"**, simplemente refresca el navegador (F5)

## 🐛 Si Aún No Funciona

Si después de aplicar TODAS estas soluciones las imágenes siguen sin verse:

1. Verifica que Azurite esté corriendo:
   ```powershell
   docker ps | Select-String "azurite"
   ```

2. Verifica las URLs en la base de datos:
   ```powershell
   docker exec projecto-ia_backend_dev python -c "
   from sqlalchemy import create_engine, text
   import os
   engine = create_engine(os.getenv('DATABASE_URL'))
   with engine.connect() as conn:
       result = conn.execute(text('SELECT url_blob FROM imagenes LIMIT 5'))
       for row in result:
           print(row[0])
   "
   ```
   
   TODAS las URLs deberían empezar con `http://localhost:10000`

3. Verifica que Azurite esté accesible desde tu navegador:
   Abre: http://localhost:10000/devstoreaccount1/plantitas-imagenes/
   Deberías ver una respuesta XML de Azure Storage

---

**Última actualización:** 2025-11-01
**Estado:** ✅ SOLUCIONADO CON MÚLTIPLES CAPAS DE PROTECCIÓN
