# Implementación T-023: UI Resultados Identificación con Múltiples Imágenes

## 📋 Información General

- **Tarea**: T-023  
- **Título**: Actualizar UI del frontend para resultados de identificación con múltiples imágenes  
- **Sprint**: Sprint 3  
- **Fecha**: Enero 2026  
- **Branch**: `feature/T-023-ui-resultados-identificacion-multiple`  
- **Branch base**: `feature/T-022-multiple-images-organ-param`  
- **Estado**: 🔄 En Progreso  

## 🎯 Objetivo

Actualizar la interfaz de usuario del frontend para mostrar resultados de identificación con múltiples imágenes (1-5 imágenes) con parámetros organ, consumiendo el nuevo endpoint `/api/identificar/multiple` implementado en T-022.

## ✅ Cambios Realizados

### 1. Actualización de Tipos TypeScript (`frontend/models/plant.types.ts`)

#### Nuevos Tipos Agregados:
```typescript
// Nueva interfaz para imágenes en respuesta (T-022/T-023)
export interface ImagenIdentificacionResponse {
  id: number;
  nombre_archivo: string;
  url_blob: string;
  organ?: string;
  tamano_bytes: number;
}

// Respuesta actualizada para múltiples imágenes (T-022)
export interface IdentificarResponse {
  id: number;
  usuario_id: number;
  imagenes: ImagenIdentificacionResponse[];  // ✨ Nuevo: Array de imágenes
  especie_id?: number;
  confianza: number;
  origen: string;
  resultados: PlantNetResponse;
  fecha_identificacion: string;
  proyecto_usado: string;
  cantidad_imagenes: number;  // ✨ Nuevo: Contador de imágenes
}

// Respuesta simplificada para retrocompatibilidad
export interface IdentificarResponseSimple {
  identificacion_id?: number;
  especie: PlantIdentificationSimplified;
  confianza: number;
  confianza_porcentaje: string;
  es_confiable: boolean;
  plantnet_response: PlantNetResponse;
  mejor_resultado: PlantIdentificationSimplified;
}
```

#### Órganos Actualizados:
```typescript
// Actualizado para incluir nuevos órganos de T-022
export type OrganType = 'leaf' | 'flower' | 'fruit' | 'bark' | 'habit' | 'other' | 'sin_especificar' | 'auto';

export const NOMBRES_ORGANOS: Record<OrganType, string> = {
  leaf: 'Hoja',
  flower: 'Flor',
  fruit: 'Fruto',
  bark: 'Corteza',
  habit: 'Hábito',     // ✨ Nuevo
  other: 'Otro',        // ✨ Nuevo
  sin_especificar: 'Sin especificar',  // ✨ Nuevo
  auto: 'Automático'
};
```

### 2. Componente UI Carousel (`frontend/components/ui/carousel.tsx`)

**Archivo**: Nuevo componente  
**Propósito**: Carousel de imágenes usando embla-carousel-react  
**Dependencia**: `embla-carousel-react@8.5.1` (requiere instalación)

**Características**:
- ✅ Navegación con flechas (izquierda/derecha)
- ✅ Navegación con teclado (ArrowLeft/ArrowRight)
- ✅ Soporte para orientación horizontal/vertical
- ✅ Loop infinito configurable
- ✅ Scroll automático programable
- ✅ API para control externo

**Componentes exportados**:
- `<Carousel>` - Contenedor principal
- `<CarouselContent>` - Wrapper de contenido
- `<CarouselItem>` - Item individual del carousel
- `<CarouselPrevious>` - Botón anterior
- `<CarouselNext>` - Botón siguiente
- `CarouselApi` - Tipo para API del carousel

### 3. Componente IdentificationResultCard (`frontend/components/identification-result-card.tsx`)

**Archivo**: Nuevo componente  
**Propósito**: Tarjeta de resultado de identificación con carousel de múltiples imágenes

**Props**:
```typescript
interface IdentificationResultCardProps {
  scientificName: string;
  commonName: string;
  genus: string;
  family: string;
  confidence: number;
  images: ImagenIdentificacionResponse[];  // ✨ Array de imágenes
  isCorrect?: boolean;
  onConfirm?: () => void;
}
```

**Características**:
- ✅ Carousel automático de imágenes (cambio cada 3 segundos)
- ✅ Badges de órgano en cada imagen
- ✅ Indicadores de navegación (dots)
- ✅ Información del archivo (nombre, tamaño)
- ✅ Badge de confianza
- ✅ Metadata científica (género, familia)
- ✅ Botón de confirmación con animaciones
- ✅ Diseño responsive
- ✅ Accesibilidad (aria-labels, keyboard navigation)

**Estructura Visual**:
```
┌─────────────────────────────────────────────┐
│ 🌿  85.5%  Spathiphyllum wallisii Regel    │
│                                             │
│ Nombre Común | Género  | Familia           │
│ Cuna Moisés  | Spath.  | Araceae          │
│                                             │
│ ┌───────────────────────────────────────┐  │
│ │  [Imagen con badge "Flor" arriba]    │  │
│ │                                       │  │
│ │  flor-rosa.jpg           245.7 KB    │  │
│ └───────────────────────────────────────┘  │
│           ○ ● ○ ○                          │
│                                             │
│ [ ✓ Confirmar esta planta ]                │
└─────────────────────────────────────────────┘
```

### 4. Servicio PlantService Actualizado (`frontend/lib/plant.service.ts`)

#### Nuevo Método: `identificarDesdeMultiplesImagenes()`

```typescript
async identificarDesdeMultiplesImagenes(
  archivos: File[],
  organos: OrganType[],
  guardarResultado: boolean = true,
  onProgress?: (progreso: number) => void
): Promise<IdentificarResponse>
```

**Validaciones**:
- ✅ Valida 1-5 archivos
- ✅ Valida que haya un órgano por archivo
- ✅ Reporta progreso de upload

**Endpoint**: `POST /api/identificar/multiple`

**Formato de envío**:
```typescript
FormData:
  - archivos: [File, File, ...]  // Multiple files
  - organos: "flower,leaf,fruit"  // Comma-separated
  - guardar_resultado: "true"
```

#### Método Actualizado: `identificarDesdeImagen()`

- ✅ Tipo de retorno actualizado a `IdentificarResponseSimple` para retrocompatibilidad
- ✅ Mantiene compatibilidad con código existente

#### Método Actualizado: `identificarDesdeArchivo()`

- ✅ Tipo de retorno actualizado a `IdentificarResponseSimple`
- ✅ Sin cambios funcionales

### 5. Página de Resultados Actualizada (`frontend/app/identificar/resultados/page.tsx`)

**Estado**: ⚠️ Parcialmente actualizado (hay errores de tipo pendientes)

**Imports Agregados**:
```typescript
import { IdentificationResultCard } from '@/components/identification-result-card';
import { IdentificarResponse, IdentificarResponseSimple } from '@/models/plant.types';
```

**Cambios Necesarios** (pendientes):
1. Actualizar tipo de estado `resultado` de `IdentificarResponse` (nuevo) vs `IdentificarResponseSimple` (antiguo)
2. Cambiar `resultado.plantnet_response.results` a `resultado.resultados.results`
3. Pasar array de imágenes al `IdentificationResultCard`
4. Actualizar renderizado para mostrar múltiples imágenes
5. Agregar lógica de confirmación de especies

## 📦 Dependencias Requeridas

### NPM Package Pendiente de Instalación

```bash
# Ejecutar en el contenedor de Docker
docker exec -it projecto-ia_frontend_dev npm install embla-carousel-react@8.5.1
```

**Versión**: `embla-carousel-react@8.5.1`  
**Uso**: Componente carousel para múltiples imágenes  
**Tamaño**: ~25KB minified  

## 🔧 Configuración

### Archivo `package.json` (Actualizado pendiente)

```json
{
  "dependencies": {
    ...existing dependencies...
    "embla-carousel-react": "8.5.1"
  }
}
```

## 📊 Estructura de Datos

### Flujo de Datos: Backend → Frontend

```
Backend Response (POST /api/identificar/multiple):
┌─────────────────────────────────────────────────┐
│ IdentificacionResponse                          │
├─────────────────────────────────────────────────┤
│ id: number                                      │
│ usuario_id: number                              │
│ imagenes: [                                     │
│   {                                             │
│     id: 1,                                      │
│     nombre_archivo: "flor.jpg",                 │
│     url_blob: "https://...blob..",              │
│     organ: "flower",                            │
│     tamano_bytes: 245678                        │
│   },                                            │
│   { ... más imágenes ... }                      │
│ ]                                               │
│ confianza: 85                                   │
│ resultados: PlantNetResponse {                  │
│   results: [PlantNetResult, ...]                │
│ }                                               │
│ cantidad_imagenes: 2                            │
└─────────────────────────────────────────────────┘
           ↓
Frontend IdentificationResultCard:
┌─────────────────────────────────────────────────┐
│ Props recibidos:                                │
├─────────────────────────────────────────────────┤
│ images: ImagenIdentificacionResponse[]          │
│ → Carousel muestra cada imagen                  │
│ → Badge de organ en cada una                    │
│ → Nombre y tamaño de archivo                    │
└─────────────────────────────────────────────────┘
```

## 🧪 Testing

### Estado Actual
- ⏳ Tests unitarios: Pendientes
- ⏳ Tests de integración: Pendientes
- ⏳ Tests E2E: Pendientes

### Tests Planificados

#### 1. `identification-result-card.test.tsx`
```typescript
describe('IdentificationResultCard', () => {
  it('renders single image correctly')
  it('renders multiple images with carousel')
  it('shows organ badges on images')
  it('displays confidence badge')
  it('shows scientific name and metadata')
  it('carousel auto-advances every 3 seconds')
  it('manual navigation with dots works')
  it('confirms species on button click')
})
```

#### 2. `identificar-resultados.test.tsx`
```typescript
describe('ResultadosPage', () => {
  it('loads identification results')
  it('displays multiple result cards')
  it('handles error states')
  it('navigates back to identify page')
  it('confirms species selection')
})
```

#### 3. `plant-service.test.ts`
```typescript
describe('PlantService.identificarDesdeMultiplesImagenes', () => {
  it('validates 1-5 images')
  it('validates organ count matches image count')
  it('sends correct FormData')
  it('reports upload progress')
  it('handles API errors')
})
```

## 🐛 Issues Conocidos

### 1. ⚠️ Dependencia embla-carousel-react no instalada

**Error**:
```
Cannot find module 'embla-carousel-react' or its corresponding type declarations.
```

**Solución**:
```bash
docker exec -it projecto-ia_frontend_dev npm install embla-carousel-react@8.5.1
```

### 2. ⚠️ Errores de tipo en `page.tsx`

**Errores**:
- `Property 'plantnet_response' does not exist on type 'IdentificarResponse'`
- Tipo incorrecto en `setResultado(respuesta)` (IdentificarResponseSimple vs IdentificarResponse)

**Causa**: Refactorización incompleta de tipos entre T-017 (original) y T-022/T-023 (actualizado)

**Solución pendiente**:
1. Decidir estrategia: usar `IdentificarResponse` (nuevo) o `IdentificarResponseSimple` (antiguo)
2. Actualizar toda la página consistentemente
3. Mapear `resultados` ↔ `plantnet_response` según la estrategia elegida

### 3. ⚠️ ESLint: Array index in keys

**Código problemático**:
```typescript
{images.map((_, index) => (
  <button key={index}>  {/* ❌ No usar index como key */}
```

**Solución aplicada**:
```typescript
{images.map((img) => (
  <button key={`indicator-${img.id}`}>  {/* ✅ Usar ID único */}
```

## 📝 Tareas Pendientes

### Alta Prioridad
1. ⏳ Instalar dependencia `embla-carousel-react`
2. ⏳ Corregir errores de tipo en `page.tsx`
3. ⏳ Implementar lógica de confirmación de especies
4. ⏳ Crear tests unitarios para componentes nuevos

### Media Prioridad
5. ⏳ Actualizar componente `ImageUpload` para múltiples imágenes
6. ⏳ Testing manual en Docker
7. ⏳ Documentar casos edge

### Baja Prioridad
8. ⏳ Optimización de rendimiento del carousel
9. ⏳ Agregar animaciones de transición
10. ⏳ Mejorar accesibilidad

## 🚀 Siguientes Pasos

### Paso 1: Resolver Dependencias
```bash
# En Docker
docker exec -it projecto-ia_frontend_dev npm install embla-carousel-react@8.5.1
```

### Paso 2: Corregir Tipos en `page.tsx`

Opción A: Usar tipos nuevos (Recomendado)
```typescript
const [resultado, setResultado] = useState<IdentificarResponse | null>(null);

// Actualizar acceso a datos:
resultado.resultados.results  // En lugar de resultado.plantnet_response.results
```

Opción B: Mantener tipos antiguos (Retrocompatibilidad)
```typescript
const [resultado, setResultado] = useState<IdentificarResponseSimple | null>(null);

// Mantener:
resultado.plantnet_response.results
```

### Paso 3: Integrar IdentificationResultCard

```typescript
{resultado.resultados.results.slice(0, 10).map((result, index) => (
  <IdentificationResultCard
    key={`result-${resultado.id}-${index}`}
    scientificName={result.species.scientificName}
    commonName={result.species.commonNames[0] || 'Sin nombre'}
    genus={result.species.genus?.scientificNameWithoutAuthor || ''}
    family={result.species.family?.scientificNameWithoutAuthor || ''}
    confidence={result.score * 100}
    images={resultado.imagenes}  // ✨ Pasar array de imágenes
    onConfirm={() => handleConfirmarEspecie(result)}
  />
))}
```

### Paso 4: Tests Unitarios

```bash
# Crear tests
touch frontend/__tests__/components/identification-result-card.test.tsx

# Ejecutar tests
docker exec -it projecto-ia_frontend_dev npm test
```

### Paso 5: Testing Manual

```bash
# Levantar contenedores
docker-compose -f docker-compose.dev.yml up -d

# Acceder a http://localhost:4200/identificar/resultados?identificacionId=1
```

## 📚 Referencias

### Documentación Relacionada
- [IMPLEMENTACION_T022.md](../backend/IMPLEMENTACION_T022.md) - Backend con múltiples imágenes
- [embla-carousel-react Docs](https://www.embla-carousel.com/get-started/react/)
- [shadcn/ui Carousel](https://ui.shadcn.com/docs/components/carousel)

### Endpoints API
- `POST /api/identificar/multiple` - Identificación con múltiples imágenes (T-022)
- `POST /api/identificar/desde-imagen` - Identificación con imagen existente
- `POST /api/identificar/desde-archivo` - Upload e identificación en un paso

### Archivos Modificados
- ✅ `frontend/models/plant.types.ts`
- ✅ `frontend/components/ui/carousel.tsx` (nuevo)
- ✅ `frontend/components/identification-result-card.tsx` (nuevo)
- ✅ `frontend/lib/plant.service.ts`
- ⚠️ `frontend/app/identificar/resultados/page.tsx` (parcial)
- ⏳ `frontend/package.json` (pendiente)

### Story Points Estimados
- **Completado**: 5 SP (Tipos + Componentes + Servicio)
- **Pendiente**: 3 SP (Tests + Correcciones + Documentation)
- **Total**: 8 SP

---

**Última actualización**: Enero 2026  
**Responsable**: Equipo Frontend  
**Estado**: 🔄 En Progreso (62.5% completado)
