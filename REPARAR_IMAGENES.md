# 🔧 Reparación de Imágenes de Plantas

## 🎯 Problema

Las plantas creadas **antes del fix** tienen `imagen_principal_id = NULL`, por lo que muestran el placeholder "Imagen no disponible" en lugar de las fotos que subiste.

## ✅ Solución

Se creó un endpoint de reparación que:
1. Busca tus plantas sin imagen principal
2. Encuentra las identificaciones asociadas
3. Asigna la primera imagen como principal
4. ¡Las imágenes aparecen automáticamente!

## 🚀 Cómo Usar

### Opción 1: Script Python (Más Fácil)

1. Abre el archivo `reparar_imagenes.py`
2. **Cambia las credenciales:**
   ```python
   EMAIL = "tu_email@ejemplo.com"  # Tu email real
   PASSWORD = "tu_contraseña"       # Tu contraseña real
   ```
3. Ejecuta:
   ```bash
   python reparar_imagenes.py
   ```
4. ¡Listo! Recarga el dashboard

### Opción 2: Llamada API Manual

1. Obtén tu token de autenticación (login)
2. Llama al endpoint:
   ```bash
   POST http://localhost:8000/api/plantas/reparar-imagenes
   Headers: Authorization: Bearer TU_TOKEN
   ```

### Opción 3: Desde el Frontend (Temporal)

Puedes agregar un botón temporal en el dashboard que llame al endpoint:

```typescript
// En cualquier componente del dashboard
const repararImagenes = async () => {
  try {
    const response = await axios.post('/api/plantas/reparar-imagenes');
    console.log('Reparación:', response.data);
    alert(`${response.data.plantas_reparadas} plantas reparadas!`);
    window.location.reload(); // Recargar para ver los cambios
  } catch (error) {
    console.error('Error:', error);
  }
};

// Botón temporal
<button onClick={repararImagenes}>
  🔧 Reparar Imágenes
</button>
```

## 📊 Respuesta del Endpoint

```json
{
  "plantas_procesadas": 1,
  "plantas_reparadas": 1,
  "detalles": [
    {
      "id": 18,
      "nombre": "Girasol",
      "imagen_principal_id": 89
    }
  ]
}
```

## 🔍 Qué Hace el Endpoint

```
Para cada planta sin imagen_principal_id:
  ├─ Busca identificaciones con la misma especie
  ├─ Para cada identificación:
  │   ├─ Busca imágenes por identificacion_id (múltiples)
  │   ├─ O usa imagen_id directamente (legacy)
  │   └─ Si encuentra: asigna la primera imagen
  └─ Guarda los cambios en DB
```

## ⚠️ Notas Importantes

- **Seguro:** Solo repara TUS plantas (usuario autenticado)
- **Idempotente:** Puedes ejecutarlo varias veces sin problemas
- **No destructivo:** Solo actualiza `imagen_principal_id`, no borra nada
- **Automático:** Encuentra las imágenes basándose en la especie

## 🎉 Resultado Esperado

**ANTES:**
```
[Imagen no disponible] ← Placeholder SVG
Girasol
```

**DESPUÉS:**
```
[Tu foto de girasol] ← Imagen real que subiste
Girasol
```

## 🐛 Troubleshooting

### "Plantas reparadas: 0"

Posibles causas:
1. La planta ya tiene `imagen_principal_id` (no necesita reparación)
2. No hay identificación con la misma `especie_id`
3. La identificación no tiene imágenes asociadas

**Solución:** Elimina la planta y créala de nuevo desde una identificación reciente.

### "Error al iniciar sesión"

- Verifica que las credenciales en `reparar_imagenes.py` sean correctas
- Asegúrate de que el backend esté corriendo (`docker-compose ps`)

### "Error 500"

- Revisa los logs del backend: `docker-compose logs backend`
- Puede haber un problema con la base de datos

## 📝 Para el Futuro

Este endpoint es **temporal** para reparar plantas existentes. Las plantas nuevas que se creen ya tendrán la imagen principal correctamente asignada gracias al fix en `agregar_desde_identificacion()`.

Considera:
- Agregar un botón "🔧 Reparar Imágenes" en el dashboard (temporal)
- O ejecutar el script una sola vez para reparar todo
- O simplemente eliminar y re-crear las plantas afectadas
