# Implementación de Carrusel Automático de Imágenes de Referencia

## 📋 Resumen

Se implementó un carrusel automático para mostrar las imágenes de referencia de PlantNet en la página de resultados de identificación, replicando la funcionalidad mostrada en el diseño de referencia.

## 🎯 Objetivo

Mejorar la experiencia de usuario al mostrar imágenes de referencia de las especies identificadas mediante un carrusel automático que permite:
- Rotación automática cada 3 segundos
- Navegación manual con botones
- Indicadores visuales de posición
- Vista ampliada en nueva pestaña

## 🔧 Cambios Implementados

### Backend

#### 1. `backend/app/services/identificacion_service.py`
```python
# Línea 73 - Identificación desde imagen única
respuesta = await PlantNetService.identificar_planta(
    imagenes=[(imagen.nombre_archivo, imagen_bytes)],
    organos=organos,
    include_related_images=True  # ✅ AGREGADO
)

# Línea 465 - Identificación desde múltiples imágenes
respuesta = await PlantNetService.identificar_planta(
    imagenes=imagenes_para_plantnet,
    organos=organos_para_plantnet,
    include_related_images=True  # ✅ AGREGADO
)
```

**Propósito:** Habilitar la obtención de imágenes de referencia desde la API de PlantNet.

### Frontend

#### 2. `frontend/models/plant.types.ts`

**Nueva interfaz:**
```typescript
export interface RelatedImage {
  organ: string;
  url: {
    o: string;  // URL original
    m: string;  // URL tamaño medio
    s: string;  // URL tamaño pequeño
  };
  citation?: string;
  license?: string;
}
```

**Actualización de PlantNetResult:**
```typescript
export interface PlantNetResult {
  score: number;
  species: PlantSpecies;
  gbif?: { id?: string };
  powo?: { id?: string };
  images?: RelatedImage[];  // ✅ AGREGADO
}
```

#### 3. `frontend/app/identificar/resultados/page.tsx`

**Nuevo componente CarruselImagenes:**

```typescript
function CarruselImagenes({ imagenes, especieNombre }: CarruselImagenesProps) {
  const [indiceActual, setIndiceActual] = useState(0);
  
  // Auto-avanzar cada 3 segundos
  useEffect(() => {
    if (imagenes.length <= 1) return;
    
    const intervalo = setInterval(() => {
      setIndiceActual((prev) => (prev + 1) % imagenes.length);
    }, 3000);
    
    return () => clearInterval(intervalo);
  }, [imagenes.length]);
  
  // ... resto del componente
}
```

**Características del carrusel:**
- ✅ Rotación automática cada 3 segundos
- ✅ Botones de navegación (anterior/siguiente) - aparecen en hover
- ✅ Indicadores de posición (dots) - clickeables
- ✅ Contador de imágenes (X/Y)
- ✅ Badge del tipo de órgano (leaf, flower, fruit, bark)
- ✅ Botón para ver imagen en tamaño completo (nueva pestaña)
- ✅ Diseño responsive con aspect-ratio 16:9
- ✅ Transiciones suaves

**Integración en resultados:**
```tsx
{result.images && result.images.length > 0 && (
  <CarruselImagenes 
    imagenes={result.images} 
    especieNombre={result.species.scientificName}
  />
)}
```

## 🎨 Características de UI/UX

### Diseño Visual
- **Aspecto:** 16:9 (aspect-video)
- **Bordes:** Redondeados con border-radius
- **Fondo:** Gris claro (#f3f4f6) para contraste
- **Imagen:** object-contain para mantener proporciones

### Interactividad
1. **Navegación Manual:**
   - Botones flotantes izquierda/derecha
   - Aparecen solo en hover
   - Fondo semi-transparente negro
   - Íconos de lucide-react (ChevronLeft/Right)

2. **Indicadores de Posición:**
   - Dots en la parte inferior
   - Activo: ancho 24px (w-6), color primario
   - Inactivo: ancho 6px (w-1.5), color gris
   - Clickeables para navegación directa

3. **Contador:**
   - Formato: "(X/Y)" donde X es índice actual, Y es total
   - Ubicación: Título de la sección

4. **Badge de Órgano:**
   - Posición: Inferior izquierda
   - Fondo: Negro semi-transparente
   - Texto: Capitalizado (Leaf, Flower, Fruit, Bark)

5. **Vista Completa:**
   - Botón con ícono ExternalLink
   - Aparece solo en hover
   - Abre imagen original en nueva pestaña

### Accesibilidad
- ✅ Atributos `aria-label` en todos los botones
- ✅ Roles semánticos correctos
- ✅ Navegación por teclado funcional
- ✅ Alt text descriptivo en imágenes

## 📊 Flujo de Datos

```
Usuario sube imagen
    ↓
Backend llama PlantNet API con include_related_images=True
    ↓
PlantNet retorna resultados con array de imágenes por especie
    ↓
Backend guarda respuesta completa en metadatos_ia (JSON)
    ↓
Frontend recibe resultados
    ↓
CarruselImagenes renderiza imágenes con auto-rotación
    ↓
Usuario puede navegar manualmente o ver imagen completa
```

## 🔍 Estructura de Datos

### Respuesta de PlantNet (con include-related-images=true)
```json
{
  "results": [
    {
      "score": 0.98,
      "species": { ... },
      "images": [
        {
          "organ": "flower",
          "url": {
            "o": "https://...",  // Original
            "m": "https://...",  // Medium
            "s": "https://..."   // Small
          },
          "citation": "...",
          "license": "..."
        }
      ]
    }
  ]
}
```

## 🧪 Testing Manual

### Escenarios de Prueba

1. **Con 1 imagen:**
   - ✅ No mostrar botones de navegación
   - ✅ No mostrar indicadores
   - ✅ Mostrar contador (1/1)

2. **Con múltiples imágenes:**
   - ✅ Auto-rotación cada 3 segundos
   - ✅ Botones visibles en hover
   - ✅ Indicadores interactivos
   - ✅ Navegación circular (último → primero)

3. **Sin imágenes:**
   - ✅ Componente no se renderiza
   - ✅ No hay error en consola

### Comandos para Testing

```bash
# Reiniciar backend con cambios
docker-compose -f docker-compose.dev.yml restart backend

# Verificar logs del backend
docker-compose -f docker-compose.dev.yml logs -f backend

# Verificar frontend compile sin errores
cd frontend
npm run build
```

## 📝 Notas Técnicas

### Performance
- **Intervalo de rotación:** 3000ms (3 segundos)
- **Cleanup:** useEffect limpia el intervalo al desmontar
- **Imágenes:** Se usa tamaño medio (url.m) para balance entre calidad/velocidad
- **Lazy loading:** React renderiza solo la imagen actual

### Compatibilidad
- ✅ Chrome/Edge (Chromium)
- ✅ Firefox
- ✅ Safari
- ✅ Navegadores móviles

### Dependencias Agregadas
```typescript
import { ChevronLeft, ChevronRight } from 'lucide-react';
```

## 🚀 Próximos Pasos

### Mejoras Opcionales
- [ ] Agregar transiciones con framer-motion para animaciones más suaves
- [ ] Implementar swipe gestures para móviles
- [ ] Agregar zoom in-page en lugar de abrir nueva pestaña
- [ ] Mostrar información de licencia/atribución de imágenes
- [ ] Cache de imágenes para mejorar performance

### Testing Automatizado
- [ ] Crear tests unitarios para CarruselImagenes
- [ ] Verificar auto-rotación con jest fake timers
- [ ] Test de navegación manual
- [ ] Test de indicadores clickeables

## 📚 Referencias

- [PlantNet API Docs - Related Images](https://my.plantnet.org/doc/api/identify)
- [React useEffect Hook](https://react.dev/reference/react/useEffect)
- [Lucide React Icons](https://lucide.dev/)
- [Tailwind CSS Aspect Ratio](https://tailwindcss.com/docs/aspect-ratio)

## ✅ Checklist de Implementación

- [x] Backend: Agregar `include_related_images=True` en llamadas a PlantNet
- [x] Frontend: Definir interfaz `RelatedImage`
- [x] Frontend: Actualizar `PlantNetResult` con campo `images`
- [x] Frontend: Crear componente `CarruselImagenes`
- [x] Frontend: Implementar auto-rotación con useEffect
- [x] Frontend: Agregar botones de navegación
- [x] Frontend: Agregar indicadores de posición
- [x] Frontend: Integrar en página de resultados
- [x] Testing: Verificar funcionamiento manual
- [x] Lint: Corregir errores de TypeScript/ESLint
- [x] Documentación: Crear este archivo

---

**Fecha de implementación:** Octubre 20, 2025  
**Sprint:** Sprint 3  
**Tarea relacionada:** T-023 - UI Resultados Identificación Múltiple
