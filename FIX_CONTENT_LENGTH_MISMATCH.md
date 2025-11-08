# Fix: ERR_CONTENT_LENGTH_MISMATCH en /api/identificar/multiple

## Problema

El endpoint `/api/identificar/multiple` estaba generando el error:
```
POST http://localhost:8000/api/identificar/multiple net::ERR_CONTENT_LENGTH_MISMATCH 201 (Created)
RuntimeError: Response content longer than Content-Length
```

Este error ocurría cuando el frontend intentaba identificar plantas con múltiples imágenes.

## Causa Raíz REAL ⚠️

El problema NO estaba en el endpoint `/multiple`, sino en el **middleware de Azurite URL Replacement** en `backend/app/main.py`.

### El Middleware Problemático

El middleware `reemplazar_urls_azurite` estaba:

1. ✅ Leyendo el body de la respuesta JSON
2. ✅ Reemplazando URLs de `http://azurite:10000` → `http://localhost:10000`
3. ❌ **Creando una nueva Response con string en lugar de bytes**
4. ❌ **NO recalculando el Content-Length después de la modificación**

```python
# ❌ CÓDIGO PROBLEMÁTICO (ANTES)
return Response(
    content=content,  # ← STRING, no bytes!
    status_code=response.status_code,
    headers=dict(response.headers),  # ← Content-Length viejo!
    media_type=response.media_type
)
```

### ¿Por qué fallaba?

Cuando el contenido JSON tiene:
- **Caracteres UTF-8 multibyte** (ñ, á, é, etc.)
- **Caracteres especiales** en nombres científicos
- **Texto en español** de PlantNet

El `Content-Length` calculado en **caracteres** (string) es DIFERENTE al calculado en **bytes** (UTF-8).

**Ejemplo:**
- String "Potus" = 5 caracteres = 5 bytes
- String "Potos áureo" = 11 caracteres = 12 bytes (á = 2 bytes en UTF-8)

El middleware estaba usando el Content-Length original (antes del replace), pero el contenido modificado podría tener diferente longitud en bytes.

## Solución

**Corregir el middleware de Azurite para codificar correctamente a bytes y recalcular Content-Length:**

```python
# ✅ CÓDIGO CORREGIDO (DESPUÉS) - backend/app/main.py
# Reemplazar URLs de Azurite
content = content.replace('http://azurite:10000', 'http://localhost:10000')
content = content.replace('http://127.0.0.1:10000', 'http://localhost:10000')
content = content.replace('https://azurite:10000', 'http://localhost:10000')
content = content.replace('https://127.0.0.1:10000', 'http://localhost:10000')

# Codificar a bytes y calcular Content-Length correcto
content_bytes = content.encode('utf-8')

# Crear nueva respuesta con el contenido modificado
# IMPORTANTE: Usar bytes y actualizar Content-Length
headers = dict(response.headers)
headers['Content-Length'] = str(len(content_bytes))  # ← RECALCULAR!

return Response(
    content=content_bytes,  # ← BYTES, no string!
    status_code=response.status_code,
    headers=headers,
    media_type=response.media_type
)
```

### Cambios Realizados

1. **Modificado** `backend/app/main.py` - Middleware `reemplazar_urls_azurite`
2. **Agregado**: Codificación explícita a bytes con `.encode('utf-8')`
3. **Agregado**: Recálculo de `Content-Length` con `len(content_bytes)`
4. **Corregido**: Response ahora usa `content_bytes` en lugar de `content` string
5. **Documentado**: Comentarios explicando la importancia de bytes y Content-Length

## Por Qué Funciona Ahora

FastAPI internamente:
1. Serializa el diccionario a JSON usando `jsonable_encoder()`
2. Calcula el `Content-Length` **después** de procesar todos los middlewares
3. Asegura que el header coincida con el tamaño real del body
4. Maneja correctamente caracteres UTF-8 y objetos especiales

## Optimizaciones Previas Relacionadas

En commits anteriores ya se había optimizado `identificacion_service.py` para:
- ✅ Reducir el tamaño de `metadatos_ia` eliminando la respuesta completa de PlantNet
- ✅ Limitar `nombres_comunes` a solo 3 resultados
- ✅ Guardar solo metadata esencial

Estas optimizaciones ayudaron a reducir el payload, pero el error persistía debido al manejo manual de la respuesta.

## Testing

Para verificar el fix:

```bash
# 1. Verificar que el backend reinició correctamente
docker-compose ps backend

# 2. Probar el endpoint desde el frontend
# - Ir a la página de identificación
# - Subir 1-5 imágenes
# - Verificar que NO aparece ERR_CONTENT_LENGTH_MISMATCH
```

## Referencias

- **FastAPI Response Models**: https://fastapi.tiangolo.com/tutorial/response-model/
- **Custom Response**: https://fastapi.tiangolo.com/advanced/custom-response/
- **ERR_CONTENT_LENGTH_MISMATCH**: Ocurre cuando el Content-Length header no coincide con el tamaño real del body

## Archivos Modificados

- ✅ `backend/app/main.py` - Middleware `reemplazar_urls_azurite` corregido
- ✅ `backend/app/api/identificacion.py` - Endpoint `/multiple` simplificado (cambio previo innecesario pero inofensivo)
