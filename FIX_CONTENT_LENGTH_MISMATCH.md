# Fix: ERR_CONTENT_LENGTH_MISMATCH en /api/identificar/multiple

## Problema

El endpoint `/api/identificar/multiple` estaba generando el error:
```
POST http://localhost:8000/api/identificar/multiple net::ERR_CONTENT_LENGTH_MISMATCH 201 (Created)
```

Este error ocurría cuando el frontend intentaba identificar plantas con múltiples imágenes.

## Causa Raíz

En `backend/app/api/identificacion.py`, el endpoint estaba:

1. **Serializando JSON manualmente** con `json.dumps()`
2. **Calculando Content-Length manualmente** 
3. **Creando un objeto Response() personalizado**

```python
# ❌ CÓDIGO PROBLEMÁTICO (ANTES)
json_str = json.dumps(resultado, ensure_ascii=False, default=str)
json_bytes = json_str.encode('utf-8')

return Response(
    content=json_bytes,
    status_code=status.HTTP_201_CREATED,
    media_type="application/json",
    headers={"Content-Length": str(len(json_bytes))}
)
```

Esto causaba un conflicto porque:
- Los middlewares de FastAPI intentaban procesar la respuesta después
- El `Content-Length` se recalculaba incorrectamente
- Había discrepancia entre el tamaño real del contenido y el header

## Solución

**Dejar que FastAPI maneje la serialización JSON automáticamente:**

```python
# ✅ CÓDIGO CORREGIDO (DESPUÉS)
resultado = await IdentificacionService.identificar_desde_multiples_imagenes(
    db=db,
    imagenes=imagenes_con_organos,
    usuario_id=current_user.id,
    guardar_resultado=guardar_resultado
)

# Retornar directamente el dict - FastAPI maneja la serialización JSON
# y calcula el Content-Length correctamente
return resultado
```

### Cambios Realizados

1. **Eliminado**: Manual JSON serialization con `json.dumps()`
2. **Eliminado**: Creación manual de `Response()` object
3. **Eliminado**: Header `Content-Length` manual
4. **Eliminadas**: Imports no utilizados (`json`, `Response`)
5. **Agregado**: Comentario explicativo sobre el comportamiento de FastAPI

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

- ✅ `backend/app/api/identificacion.py` - Endpoint `/multiple` simplificado
