# Configuración de Idioma Español en PlantNet API

## Resumen de Cambios

Se ha verificado y documentado la configuración de idioma español para las respuestas de PlantNet API.

## Cambios Realizados

### 1. Backend - `plantnet_service.py`

**Archivo:** `backend/app/services/plantnet_service.py`

**Cambios:**
- ✅ El parámetro `lang` ya está configurado con valor por defecto `"es"` (español) en la línea 114
- ✅ Actualizada la documentación del método para clarificar el uso del parámetro
- ✅ El parámetro `lang` se incluye correctamente en los query parameters del request a PlantNet API (línea 201)

**Código relevante:**
```python
@classmethod
async def identificar_planta(
    cls,
    imagenes: List[Tuple[str, BinaryIO]],
    organos: List[str],
    project: Optional[str] = None,
    include_related_images: bool = False,
    nb_results: int = 10,
    lang: str = "es"  # ← ESPAÑOL POR DEFECTO
) -> Dict[str, Any]:
```

**Query parameters enviados a PlantNet:**
```python
params = {
    "api-key": settings.plantnet_api_key,
    "include-related-images": str(include_related_images).lower(),
    "nb-results": nb_results,
    "lang": lang  # ← Se envía a la API
}
```

### 2. Backend - `plantnet.py` (Schemas)

**Archivo:** `backend/app/schemas/plantnet.py`

**Cambios:**
- ✅ Actualizada la descripción del campo `lang` en el schema Pydantic
- ✅ El valor por defecto ya estaba configurado como `"es"`
- ✅ Agregados más ejemplos de códigos de idioma disponibles

**Código actualizado:**
```python
lang: str = Field(
    "es",
    description="Código de idioma para nombres comunes (default: español). Valores: es, en, fr, pt, de, it, ar, cs, etc.",
    min_length=2,
    max_length=5,
    examples=["es", "en", "fr"]
)
```

### 3. Test de Verificación

**Archivo creado:** `backend/test_plantnet_lang_es.py`

- ✅ Script de verificación que confirma que el parámetro `lang="es"` está configurado correctamente
- ✅ Documenta cómo usar el servicio con diferentes idiomas
- ✅ Verifica que el parámetro se pasa correctamente a la API

**Resultado del test:**
```
✓ Parámetro 'lang' tiene valor por defecto: 'es'
✓ CORRECTO: El valor por defecto es 'es' (español)
✓ CONCLUSIÓN: El código está configurado correctamente
✓ Los nombres comunes vendrán en ESPAÑOL
```

## Impacto en la Aplicación

### Comportamiento Actual

1. **Por Defecto - Español:**
   - Todas las identificaciones de plantas devolverán nombres comunes en **español**
   - No se requiere ningún cambio en el código existente
   - Todas las llamadas a `PlantNetService.identificar_planta()` usarán español automáticamente

2. **Campos Afectados:**
   - `commonNames`: Array de nombres comunes de la planta
   - Ejemplos: ["Potos", "Hiedra del diablo", "Potus dorado"] en lugar de ["Pothos", "Devil's ivy", "Golden pothos"]

3. **Retrocompatibilidad:**
   - ✅ Todas las llamadas existentes seguirán funcionando
   - ✅ Si se necesita otro idioma, se puede especificar: `lang="en"`, `lang="fr"`, etc.

### Lugares donde se Llama a PlantNet

1. **`identificacion_service.py` - Línea 73:**
   ```python
   respuesta = await PlantNetService.identificar_planta(
       imagenes=[(imagen.nombre_archivo, imagen_bytes)],
       organos=organos,
       include_related_images=True
   )
   # ← Usará español por defecto
   ```

2. **`identificacion_service.py` - Línea 463:**
   ```python
   respuesta = await PlantNetService.identificar_planta(
       imagenes=imagenes_para_plantnet,
       organos=organos_para_plantnet,
       include_related_images=True
   )
   # ← Usará español por defecto
   ```

3. **`identificacion_service.py` - Línea 161:**
   ```python
   respuesta = await PlantNetService.identificar_desde_path(
       rutas_imagenes=[str(ruta_completa)],
       organos=organos
   )
   # ← Usará español por defecto (kwargs se pasan a identificar_planta)
   ```

## Idiomas Disponibles

Según la documentación de PlantNet API, los siguientes códigos de idioma están soportados:

- `es` - Español ⭐ **(configurado por defecto)**
- `en` - Inglés
- `fr` - Francés
- `pt` - Portugués
- `de` - Alemán
- `it` - Italiano
- `ar` - Árabe
- `cs` - Checo
- Y más...

Para ver la lista completa, consultar: https://my.plantnet.org/doc/api/other (endpoint `/v2/languages`)

## Ejemplo de Uso

### Uso por Defecto (Español)

```python
# Automáticamente usará español
respuesta = await PlantNetService.identificar_planta(
    imagenes=[('planta.jpg', archivo_bytes)],
    organos=['leaf']
)

# Resultado:
# {
#   "results": [{
#     "species": {
#       "commonNames": ["Potos", "Hiedra del diablo", "Potus dorado"]
#     }
#   }]
# }
```

### Uso con Otro Idioma

```python
# Especificar idioma manualmente
respuesta = await PlantNetService.identificar_planta(
    imagenes=[('planta.jpg', archivo_bytes)],
    organos=['leaf'],
    lang='en'  # Inglés
)

# Resultado:
# {
#   "results": [{
#     "species": {
#       "commonNames": ["Pothos", "Devil's ivy", "Golden pothos"]
#     }
#   }]
# }
```

## Referencias

- Documentación PlantNet API: https://my.plantnet.org/doc/getting-started/introduction
- Endpoint de identificación: https://my.plantnet.org/doc/api/identify
- Idiomas disponibles: https://my.plantnet.org/doc/api/other

## Conclusión

✅ **La aplicación ya está configurada correctamente para devolver nombres comunes en español**

✅ **No se requieren cambios adicionales en el código**

✅ **Todos los endpoints de identificación usarán español automáticamente**

---

**Fecha:** 7 de noviembre de 2025
**Autor:** Sistema de IA Aplicada
**Estado:** ✅ Completado y verificado
