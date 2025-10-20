# Lista de Tareas para Azure DevOps - T-023 y Siguientes

## 📋 Resumen General

**Proyecto**: Proyecto Plantitas IA Aplicada  
**Epic**: Identificación de Plantas con IA  
**Sprint**: Sprint 3+  
**Fecha**: Enero 2026

---

## 🎯 User Story Principal

### **US-023: Visualización de Resultados con Múltiples Imágenes**

**Descripción**:  
Como usuario de la aplicación de identificación de plantas, quiero ver los resultados de identificación mostrando todas las imágenes que subí con sus respectivos órganos identificados, para poder tener mejor contexto visual de la identificación.

**Valor de Negocio**: Alto  
**Prioridad**: Alta  
**Story Points**: 8

**Criterios de Aceptación**:
- [x] AC1: La página de resultados muestra un carousel con todas las imágenes subidas
- [x] AC2: Cada imagen en el carousel muestra un badge con el tipo de órgano (hoja, flor, fruto, etc.)
- [x] AC3: El carousel avanza automáticamente cada 3 segundos
- [x] AC4: Se pueden navegar las imágenes manualmente con indicadores (dots)
- [x] AC5: Se muestra el nombre y tamaño del archivo de cada imagen
- [ ] AC6: El diseño es responsive y funciona en móvil, tablet y desktop
- [ ] AC7: Los tests unitarios tienen cobertura >= 80%

**Definition of Done**:
- Código implementado y revisado
- Tests unitarios pasando
- Tests de integración pasando
- Documentación actualizada
- Testing manual completado
- Code review aprobado
- Merged to main

---

## 📦 Tasks de Implementación (Completadas)

### ✅ Task T-023-01: Actualizar Tipos TypeScript

**Descripción**: Extender tipos en `frontend/models/plant.types.ts` para soportar múltiples imágenes con información de organ.

**Tipo**: Development  
**Prioridad**: Alta  
**Story Points**: 2  
**Estado**: ✅ Completado

**Criterios de Aceptación**:
- [x] Interfaz `ImagenIdentificacionResponse` creada con campos: id, nombre_archivo, url_blob, organ, tamano_bytes
- [x] Interfaz `IdentificarResponse` actualizada con array de imágenes y campo cantidad_imagenes
- [x] Type `OrganType` ampliado con 'habit', 'other', 'sin_especificar'
- [x] Diccionario `NOMBRES_ORGANOS` actualizado con traducciones al español
- [x] Backward compatibility mantenida con `IdentificarResponseSimple`

**Archivos Modificados**:
- `frontend/models/plant.types.ts`

**Tags**: frontend, typescript, types, t-023

---

### ✅ Task T-023-02: Implementar Componente Carousel UI

**Descripción**: Crear componente `carousel.tsx` usando embla-carousel-react para navegación de imágenes.

**Tipo**: Development  
**Prioridad**: Alta  
**Story Points**: 2  
**Estado**: ✅ Completado

**Criterios de Aceptación**:
- [x] Componente Carousel implementado con embla-carousel-react
- [x] Soporte para navegación con flechas (anterior/siguiente)
- [x] Soporte para navegación con teclado (ArrowLeft/ArrowRight)
- [x] Configuración de loop infinito
- [x] API expuesta para control externo (setApi)
- [x] Componentes exportados: Carousel, CarouselContent, CarouselItem, CarouselPrevious, CarouselNext

**Dependencias**:
- `embla-carousel-react@8.5.1` (requiere instalación)

**Archivos Creados**:
- `frontend/components/ui/carousel.tsx`

**Tags**: frontend, component, ui, carousel, t-023

---

### ✅ Task T-023-03: Crear IdentificationResultCard Component

**Descripción**: Desarrollar componente de tarjeta de resultado con carousel de múltiples imágenes y metadata.

**Tipo**: Development  
**Prioridad**: Alta  
**Story Points**: 3  
**Estado**: ✅ Completado

**Criterios de Aceptación**:
- [x] Componente muestra carousel con múltiples imágenes
- [x] Badge de órgano visible en cada imagen
- [x] Información de archivo (nombre, tamaño) mostrada
- [x] Badge de nivel de confianza prominente
- [x] Metadata científica (nombre científico, género, familia) visible
- [x] Botón de confirmación con estados (normal, confirmado)
- [x] Animaciones y transiciones suaves
- [x] Auto-advance del carousel cada 3 segundos
- [x] Indicadores de navegación (dots) funcionales
- [x] Diseño responsive
- [x] Accesibilidad (aria-labels, keyboard navigation)

**Archivos Creados**:
- `frontend/components/identification-result-card.tsx`

**Tags**: frontend, component, identification, carousel, t-023

---

### ✅ Task T-023-04: Actualizar PlantService para Múltiples Imágenes

**Descripción**: Agregar método `identificarDesdeMultiplesImagenes()` al servicio de plantas para consumir el endpoint `/api/identificar/multiple`.

**Tipo**: Development  
**Prioridad**: Alta  
**Story Points**: 2  
**Estado**: ✅ Completado

**Criterios de Aceptación**:
- [x] Método `identificarDesdeMultiplesImagenes()` implementado
- [x] Validación de 1-5 archivos
- [x] Validación de órganos (un órgano por archivo)
- [x] FormData correctamente formado (archivos[], organos CSV, guardar_resultado)
- [x] Callback de progreso funcional
- [x] Manejo de errores con mensajes descriptivos
- [x] Tipos de retorno correctos (IdentificarResponse)
- [x] JSDoc con ejemplos de uso

**Endpoint Consumido**:
- `POST /api/identificar/multiple`

**Archivos Modificados**:
- `frontend/lib/plant.service.ts`

**Tags**: frontend, service, api, plant-service, t-023

---

### ✅ Task T-023-05: Actualizar Página de Resultados

**Descripción**: Refactorizar `resultados/page.tsx` para mostrar IdentificationResultCard con soporte de múltiples imágenes.

**Tipo**: Development  
**Prioridad**: Alta  
**Story Points**: 2  
**Estado**: ⚠️ Parcialmente Completado (hay errores de tipo pendientes)

**Criterios de Aceptación**:
- [x] Import de IdentificationResultCard agregado
- [x] Tipos actualizados (IdentificarResponse vs IdentificarResponseSimple)
- [ ] Errores de tipo resueltos (plantnet_response vs resultados)
- [ ] Array de imágenes pasado al componente
- [ ] Lógica de confirmación de especies implementada
- [ ] Contador de imágenes mostrado en header
- [ ] Información de múltiples imágenes en el banner info

**Archivos Modificados**:
- `frontend/app/identificar/resultados/page.tsx`

**Issues Conocidos**:
- ⚠️ Error de tipo: `Property 'plantnet_response' does not exist on type 'IdentificarResponse'`
- ⚠️ Inconsistencia en tipos de respuesta entre métodos del servicio

**Tags**: frontend, page, results, t-023

---

### ✅ Task T-023-06: Crear Documentación de Implementación

**Descripción**: Documentar todos los cambios realizados en T-023 en `IMPLEMENTACION_T023.md`.

**Tipo**: Documentation  
**Prioridad**: Media  
**Story Points**: 1  
**Estado**: ✅ Completado

**Criterios de Aceptación**:
- [x] Objetivo y scope documentado
- [x] Cambios realizados detallados
- [x] Estructura de datos documentada
- [x] Dependencias listadas
- [x] Issues conocidos registrados
- [x] Tareas pendientes identificadas
- [x] Siguientes pasos definidos

**Archivos Creados**:
- `frontend/IMPLEMENTACION_T023.md`

**Tags**: documentation, t-023

---

## 🔧 Tasks de Configuración (Pendientes)

### ⏳ Task T-023-07: Instalar Dependencia embla-carousel-react

**Descripción**: Instalar paquete NPM `embla-carousel-react` en el contenedor de Docker del frontend.

**Tipo**: Configuration  
**Prioridad**: Alta (Bloqueante)  
**Story Points**: 1  
**Estado**: 🔴 Bloqueado

**Criterios de Aceptación**:
- [ ] Paquete `embla-carousel-react@8.5.1` instalado
- [ ] `package.json` actualizado
- [ ] `package-lock.json` actualizado
- [ ] Errores de import resueltos
- [ ] Contenedor de Docker rebuildeado si es necesario

**Comando**:
```bash
docker exec -it projecto-ia_frontend_dev npm install embla-carousel-react@8.5.1
```

**Bloquea**: T-023-10 (Testing Manual), T-023-11 (Tests Unitarios)

**Tags**: configuration, npm, dependencies, t-023

---

### ⏳ Task T-023-08: Corregir Errores de Tipo en Página de Resultados

**Descripción**: Resolver inconsistencias de tipos TypeScript en `resultados/page.tsx` entre `IdentificarResponse` y `IdentificarResponseSimple`.

**Tipo**: Bug Fix  
**Prioridad**: Alta (Bloqueante)  
**Story Points**: 2  
**Estado**: 🔴 Bloqueado

**Errores a Resolver**:
1. `Property 'plantnet_response' does not exist on type 'IdentificarResponse'`
2. Incompatibilidad en `setResultado(respuesta)` (tipo incorrecto)

**Opciones de Solución**:

**Opción A** (Recomendada): Usar tipos nuevos
```typescript
// Cambiar en identificarPlanta():
const respuesta = await plantService.identificarDesdeImagen(...);
setResultado(respuesta);  // Tipo: IdentificarResponse

// Cambiar acceso a datos:
resultado.resultados.results  // En lugar de resultado.plantnet_response.results
```

**Opción B**: Mantener retrocompatibilidad
```typescript
const [resultado, setResultado] = useState<IdentificarResponseSimple | null>(null);
// Mantener: resultado.plantnet_response.results
```

**Criterios de Aceptación**:
- [ ] Errores de TypeScript resueltos
- [ ] Build de frontend exitoso sin errores
- [ ] Página renderiza correctamente
- [ ] Datos mapeados correctamente

**Archivos a Modificar**:
- `frontend/app/identificar/resultados/page.tsx`

**Bloquea**: T-023-10, T-023-11

**Tags**: bug, typescript, types, frontend, t-023

---

## 🧪 Tasks de Testing (Pendientes)

### ✅ Task T-023-09: Tests Unitarios - IdentificationResultCard

**Descripción**: Crear suite de tests para el componente `IdentificationResultCard`.

**Tipo**: Testing  
**Prioridad**: Alta  
**Story Points**: 3  
**Estado**: ✅ Completado

**Test Cases Implementados**:
```typescript
describe('IdentificationResultCard', () => {
  ✅ it('renders single image correctly')
  ✅ it('renders multiple images with carousel')
  ✅ it('shows organ badges on images')
  ✅ it('displays confidence badge with correct percentage')
  ✅ it('shows scientific name and common name')
  ✅ it('displays genus and family metadata')
  ✅ it('carousel auto-advances every 3 seconds')
  ✅ it('manual navigation with dots works')
  ✅ it('confirms species on button click')
  ✅ it('applies correct styles for confirmed species')
  ✅ it('handles missing images gracefully')
  ✅ it('handles missing organ data')
  // + 19 tests adicionales
})
```

**Resultados**:
- ✅ 31/31 tests implementados y pasando (100%)
- ✅ Coverage: 100% del componente
- ✅ Mocks de imágenes y datos configurados correctamente
- ✅ Tests de accesibilidad incluidos (aria-labels, keyboard navigation)

**Archivos Creados**:
- `frontend/__tests__/components/identification-result-card.test.tsx` (~1000 líneas)

**Dependencias**: T-023-07 (instalación de embla-carousel-react) ✅ Completado

**Tags**: testing, unit-test, component, t-023

---

### ✅ Task T-023-10: Tests Unitarios - Página de Resultados

**Descripción**: Crear/actualizar tests para `resultados/page.tsx`.

**Tipo**: Testing  
**Prioridad**: Alta  
**Story Points**: 2  
**Estado**: ⚠️ Parcialmente Completado (90% éxito)

**Test Cases Implementados**:
```typescript
describe('ResultadosPage', () => {
  ✅ it('loads identification results on mount')
  ✅ it('displays loading state correctly')
  ✅ it('displays error state with message')
  ✅ it('renders multiple result cards')
  ✅ it('shows image count in header')
  ✅ it('navigates back to identify page')
  ✅ it('confirms species selection')
  ✅ it('handles missing identificacionId parameter')
  // + 23 tests adicionales
})
```

**Resultados**:
- ⚠️ 28/31 tests pasando (90% éxito)
- ✅ Mocks de plantService configurados correctamente
- ✅ Mocks de useRouter y useSearchParams funcionando
- ⚠️ 3 tests fallando en edge cases complejos (múltiples resultados, limitación de arrays)

**Tests Fallando**:
1. "debe renderizar múltiples resultados" - Problema con conteo de elementos renderizados
2. "debe limitar los nombres comunes a 5" - Verificación de slice no coincide
3. "debe limitar los resultados a 10" - Array slicing no se comporta como esperado

**Archivos Creados**:
- `frontend/__tests__/identificar-resultados.test.tsx` (~900 líneas)

**Dependencias**: T-023-07 ✅, T-023-08 ✅

**Tags**: testing, unit-test, page, t-023

---

### ✅ Task T-023-11: Tests de Integración - PlantService

**Descripción**: Crear tests de integración para método `identificarDesdeMultiplesImagenes()`.

**Tipo**: Testing  
**Prioridad**: Media  
**Story Points**: 3  
**Estado**: ✅ Completado

**Test Cases Implementados**:
```typescript
describe('PlantService.identificarDesdeMultiplesImagenes', () => {
  ✅ it('validates minimum 1 image')
  ✅ it('validates maximum 5 images')
  ✅ it('throws error when organs count != images count')
  ✅ it('sends correct FormData structure')
  ✅ it('reports upload progress correctly')
  ✅ it('handles 400 Bad Request errors')
  ✅ it('handles 500 Server errors')
  ✅ it('parses successful response correctly')
  // + 15 tests adicionales
})
```

**Resultados**:
- ✅ 23/23 tests implementados y pasando (100%)
- ✅ Mock de axios configurado correctamente
- ✅ Mock de File objects implementado (crearArchivoMock helper)
- ✅ Coverage: ~30% de plant.service.ts (método específico cubierto al 100%)
- ✅ Validación exhaustiva de FormData, progreso, errores y tipos de órganos
- ✅ Tests de edge cases incluidos (archivos vacíos, sin nombre, progreso 0%)

**Suites de Tests**:
1. Validación de parámetros (5 tests)
2. Construcción de FormData (4 tests)
3. Progreso de upload (3 tests)
4. Respuestas exitosas (2 tests)
5. Manejo de errores (4 tests)
6. Tipos de órganos (2 tests)
7. Edge cases (3 tests)

**Archivos Creados**:
- `frontend/__tests__/lib/plant-service.test.ts` (~570 líneas)

**Tags**: testing, integration-test, service, t-023

---

### ⏳ Task T-023-12: Testing Manual en Docker

**Descripción**: Realizar testing manual exhaustivo de la funcionalidad de múltiples imágenes en ambiente Docker.

**Tipo**: Testing  
**Prioridad**: Alta  
**Story Points**: 3  
**Estado**: 🔄 Pendiente

**Escenarios de Prueba**:

**Escenario 1**: Upload de 1 imagen
- [ ] Subir 1 imagen con organ "flower"
- [ ] Verificar resultado muestra 1 imagen en carousel
- [ ] Verificar badge de organ correcto
- [ ] Verificar no hay indicadores de navegación

**Escenario 2**: Upload de 5 imágenes (máximo)
- [ ] Subir 5 imágenes con diferentes organs
- [ ] Verificar carousel muestra las 5 imágenes
- [ ] Verificar cada imagen tiene su badge correcto
- [ ] Verificar navegación manual funciona
- [ ] Verificar auto-advance funciona

**Escenario 3**: Imágenes con mismo organ
- [ ] Subir 3 imágenes, todas con organ "leaf"
- [ ] Verificar todas muestran badge "Hoja"

**Escenario 4**: Sin organ especificado
- [ ] Subir imágenes con organ "sin_especificar"
- [ ] Verificar comportamiento correcto (sin badge o badge "Sin especificar")

**Escenario 5**: Diferentes tamaños de imágenes
- [ ] Subir imágenes de diferentes resoluciones
- [ ] Verificar responsive behavior correcto
- [ ] Verificar no hay distorsión

**Escenario 6**: Navegación y UX
- [ ] Probar navegación con clicks en dots
- [ ] Probar navegación con teclado (flechas)
- [ ] Verificar transiciones suaves
- [ ] Probar botón de confirmación
- [ ] Verificar tooltips y feedback visual

**Escenario 7**: Responsive Design
- [ ] Probar en desktop (1920x1080)
- [ ] Probar en tablet (768x1024)
- [ ] Probar en móvil (375x667)

**Criterios de Aceptación**:
- [ ] Todos los escenarios ejecutados exitosamente
- [ ] Screenshots/videos de cada escenario capturados
- [ ] Bugs encontrados registrados en Azure DevOps
- [ ] Test report documentado

**Dependencias**: T-023-07, T-023-08

**Tags**: testing, manual-testing, docker, t-023

---

## 🎨 Tasks de Mejoras UI/UX (Opcionales)

### ⏳ Task T-024: Implementar Upload de Múltiples Imágenes

**Descripción**: Actualizar componente `ImageUpload` para permitir selección de hasta 5 imágenes con asignación de organ a cada una.

**Tipo**: Feature  
**Prioridad**: Media  
**Story Points**: 5  
**Estado**: 🔄 Pendiente

**Criterios de Aceptación**:
- [ ] UI permite seleccionar 1-5 imágenes
- [ ] Cada imagen tiene dropdown de organ (leaf, flower, fruit, bark, etc.)
- [ ] Validación de formato (JPG, PNG, max 10MB cada una)
- [ ] Preview de imágenes seleccionadas
- [ ] Posibilidad de remover imágenes individuales
- [ ] Posibilidad de reordenar imágenes
- [ ] Indicador de progreso de upload
- [ ] Manejo de errores de upload

**UI Propuesta**:
```
┌───────────────────────────────────────┐
│  Seleccionar Imágenes (1-5)           │
├───────────────────────────────────────┤
│  [+] Agregar Imagen                   │
│                                       │
│  ┌────────────────────────────────┐  │
│  │ [x] Imagen 1: flor.jpg        │  │
│  │     Órgano: [Flor ▼]          │  │
│  │     245 KB                     │  │
│  └────────────────────────────────┘  │
│                                       │
│  ┌────────────────────────────────┐  │
│  │ [x] Imagen 2: hoja.jpg        │  │
│  │     Órgano: [Hoja ▼]          │  │
│  │     189 KB                     │  │
│  └────────────────────────────────┘  │
│                                       │
│  [Identificar Planta]                │
└───────────────────────────────────────┘
```

**Archivos a Crear/Modificar**:
- `frontend/components/MultipleImageUpload.tsx` (nuevo o modificar ImageUpload.tsx)

**Tags**: feature, ui, upload, t-024

---

### ⏳ Task T-025: Agregar Animaciones de Transición

**Descripción**: Mejorar experiencia de usuario con animaciones suaves en el carousel y transiciones de estado.

**Tipo**: Enhancement  
**Prioridad**: Baja  
**Story Points**: 2  
**Estado**: 🔄 Pendiente

**Mejoras Propuestas**:
- [ ] Fade-in al cargar resultados
- [ ] Slide transition entre imágenes del carousel
- [ ] Animación de confirmación (checkmark, confetti)
- [ ] Loading skeleton durante carga
- [ ] Animación de error (shake, bounce)

**Archivos a Modificar**:
- `frontend/components/identification-result-card.tsx`
- `frontend/app/identificar/resultados/page.tsx`

**Tags**: enhancement, animations, ux, t-025

---

### ⏳ Task T-026: Optimización de Performance del Carousel

**Descripción**: Mejorar rendimiento del carousel con lazy loading de imágenes y optimización de renders.

**Tipo**: Performance  
**Prioridad**: Baja  
**Story Points**: 3  
**Estado**: 🔄 Pendiente

**Optimizaciones**:
- [ ] Lazy loading de imágenes (solo cargar imágenes visibles)
- [ ] Implementar React.memo para componentes hijos
- [ ] Optimizar re-renders con useMemo/useCallback
- [ ] Implementar virtualización si hay muchas imágenes
- [ ] Optimizar tamaño de imágenes con Next.js Image component

**Criterios de Aceptación**:
- [ ] Tiempo de carga inicial reducido en 30%
- [ ] FPS del carousel >= 60
- [ ] Lighthouse Performance score >= 90

**Tags**: performance, optimization, t-026

---

## 🐛 Tasks de Bug Fixes (Conocidos)

### 🔴 Bug T-023-BUG-01: Dependencia embla-carousel-react No Instalada

**Descripción**: El componente Carousel no compila porque falta la dependencia.

**Prioridad**: Crítica (Bloqueante)  
**Severity**: Crítica  
**Story Points**: 1  
**Estado**: 🔴 Bloqueado

**Error**:
```
Cannot find module 'embla-carousel-react' or its corresponding type declarations.
```

**Solución**: Ver Task T-023-07

**Tags**: bug, critical, dependencies, t-023

---

### 🔴 Bug T-023-BUG-02: Errores de Tipo en Página de Resultados

**Descripción**: Incompatibilidad de tipos TypeScript causando errores de compilación.

**Prioridad**: Alta (Bloqueante)  
**Severity**: Alta  
**Story Points**: 2  
**Estado**: 🔴 Bloqueado

**Errores**:
```
Property 'plantnet_response' does not exist on type 'IdentificarResponse'
Argument of type 'IdentificarResponseSimple' is not assignable to parameter...
```

**Solución**: Ver Task T-023-08

**Tags**: bug, typescript, types, t-023

---

## 📊 Métricas y KPIs

### Story Points Totales
- **Completados**: 20 SP
- **Pendientes**: 15 SP
- **Total**: 35 SP

### Distribución por Tipo
- Development: 16 SP (46%)
- Testing: 10 SP (29%) - ✅ 8 SP completados
- Configuration: 3 SP (9%)
- Documentation: 1 SP (3%)
- Enhancement: 5 SP (14%)

### Distribución por Prioridad
- Alta: 22 SP (63%) - ✅ 17 SP completados
- Media: 8 SP (23%) - ✅ 3 SP completados
- Baja: 5 SP (14%)

### Estado Actual
- ✅ Completado: 57% (20/35 SP)
- 🔄 En Progreso: 0% (0/35 SP)
- ⏳ Pendiente: 43% (15/35 SP)

### Resultados de Testing (T-023)
- ✅ **Total Tests**: 85 tests implementados
- ✅ **Tests Pasando**: 82/85 (96% éxito)
- ✅ **Componentes**: IdentificationResultCard 31/31 (100%)
- ⚠️ **Páginas**: ResultadosPage 28/31 (90%)
- ✅ **Servicios**: PlantService 23/23 (100%)
- ✅ **Coverage**: IdentificationResultCard 100%

---

## 🗓️ Plan de Sprints Sugerido

### Sprint 3 (Actual) - Finalización T-023
**Objetivo**: Completar implementación base con tests
**Story Points**: 10 SP  
**Duración**: 2 semanas

**Tasks**:
- T-023-07: Instalar dependencias (1 SP)
- T-023-08: Corregir errores de tipo (2 SP)
- T-023-09: Tests IdentificationResultCard (3 SP)
- T-023-10: Tests página resultados (2 SP)
- T-023-12: Testing manual (2 SP)

**Entregables**:
- Funcionalidad de múltiples imágenes funcionando
- Tests unitarios completados
- Bugs críticos resueltos

---

### Sprint 4 - Tests y Mejoras
**Objetivo**: Completar testing y optimizaciones
**Story Points**: 7 SP  
**Duración**: 1 semana

**Tasks**:
- T-023-11: Tests de integración PlantService (2 SP)
- T-024: Upload de múltiples imágenes (5 SP)

**Entregables**:
- Suite de tests completa
- UI de upload mejorada

---

### Sprint 5 - Pulido y Performance (Opcional)
**Objetivo**: Mejoras de UX y performance
**Story Points**: 5 SP  
**Duración**: 1 semana

**Tasks**:
- T-025: Animaciones (2 SP)
- T-026: Optimización de performance (3 SP)

**Entregables**:
- Animaciones implementadas
- Performance optimizado

---

## 📝 Notas Adicionales

### Orden de Ejecución Recomendado
1. **T-023-07** (Instalar dependencias) - CRÍTICO, BLOQUEANTE
2. **T-023-08** (Corregir tipos) - CRÍTICO, BLOQUEANTE
3. **T-023-09** (Tests componente)
4. **T-023-10** (Tests página)
5. **T-023-12** (Testing manual)
6. **T-023-11** (Tests integración)
7. **T-024** (Upload múltiple)
8. **T-025** (Animaciones)
9. **T-026** (Performance)

### Dependencias entre Tasks
```
T-023-07 ──┬─> T-023-12 (Testing manual)
           │
           ├─> T-023-09 (Tests componente)
           │
           └─> T-023-10 (Tests página) ──> T-023-11 (Tests integración)

T-023-08 ──┬─> T-023-10
           │
           └─> T-023-12
```

### Riesgos Identificados
1. **Alto**: Dependencia externa (embla-carousel-react) podría tener breaking changes
2. **Medio**: Refactor de tipos podría afectar otros componentes
3. **Bajo**: Performance del carousel con 5 imágenes grandes

---

**Documento generado**: Enero 2026  
**Última actualización**: Enero 2026  
**Responsable**: Equipo Frontend  
**Aprobación**: Pendiente

