# Tareas de Azure DevOps - Sprints 1 y 2
**Proyecto:** proyecto-plantitas  
**Fecha de consulta:** 20 de octubre de 2025  
**Organización:** ia-grupo-5

---

## 📊 Resumen Ejecutivo

### Sprint 1
- **Estado:** Mayormente completado
- **Tareas totales:** 13 tareas
- **Completadas:** 12 tareas ✅
- **En progreso:** 1 tarea 🔄
- **Puntos totales:** 94 pts
- **Puntos completados:** 86 pts (91.5%)

### Sprint 2
- **Estado:** Iniciado
- **Tareas totales:** 2 tareas
- **Pendientes:** 2 tareas ⏳
- **Puntos totales:** 21 pts

---

## 🎯 Sprint 1 - Tareas Detalladas

### ✅ Tareas Completadas (12)

#### 1. T-001: Configurar proyecto FastAPI con estructura MVC (5pts)
- **Estado:** ✅ Done
- **ID:** 27
- **Parent:** F-003: Infraestructura Base
- **Descripción:**
  - Estructura MVC completa implementada
  - Configuración con Pydantic Settings
  - 6 endpoints operacionales (/, /salud, /info, /metricas, /docs, /openapi.json)
  - 31 tests con 84.16% de cobertura
  - README de 400+ líneas
  - Archivos: /api, /core, /db, /schemas, /services, /utils

#### 2. T-002: Implementar modelos de usuario con SQLAlchemy (8pts)
- **Estado:** ✅ Done
- **ID:** 28
- **Parent:** F-003: Infraestructura Base
- **Descripción:**
  - Modelos de usuario con SQLAlchemy
  - Relaciones de base de datos
  - Migraciones con Alembic

#### 3. T-003: Crear endpoints de autenticación JWT (13pts)
- **Estado:** ✅ Done
- **ID:** 29
- **Parent:** F-003: Infraestructura Base
- **Subtareas incluidas:**
  - T-003A: Endpoint de registro de usuario (5pts) - ✅ Done
  - T-003B: Endpoint de login con JWT (5pts) - ✅ Done
  - T-003C: Refresh token y logout (3pts) - ✅ Done
- **Descripción:**
  - Sistema completo de autenticación
  - JWT tokens implementados
  - Refresh token functionality
  - Endpoints de logout

#### 4. T-004: Desarrollar API de subida de imágenes (8pts)
- **Estado:** ✅ Done
- **ID:** 30
- **Parent:** F-003: Infraestructura Base
- **Descripción:**
  - API para subir imágenes
  - Validación de formatos
  - Almacenamiento de archivos

#### 5. T-005: Setup React 18 con Tailwind CSS (5pts)
- **Estado:** ✅ Done
- **ID:** 31
- **Parent:** F-003: Infraestructura Base
- **Descripción:**
  - Configuración de Next.js
  - Integración de Tailwind CSS
  - Estructura inicial del frontend

#### 6. T-006: Implementar componentes de login/registro (13pts)
- **Estado:** ✅ Done
- **ID:** 32
- **Parent:** F-003: Infraestructura Base
- **Descripción:**
  - Componentes React para login
  - Componentes React para registro
  - Validación de formularios
  - UI/UX con Tailwind

#### 7. T-007: Crear servicio de autenticación React (8pts)
- **Estado:** ✅ Done
- **ID:** 33
- **Parent:** F-003: Infraestructura Base
- **Descripción:**
  - Servicio de autenticación en React
  - Manejo de tokens
  - Context API para autenticación
  - Interceptores HTTP

#### 8. T-008: Desarrollar componente de subida de fotos (8pts)
- **Estado:** ✅ Done
- **ID:** 34
- **Parent:** F-003: Infraestructura Base
- **Descripción:**
  - Componente de upload de imágenes
  - Preview de imágenes
  - Drag and drop
  - Validación de tamaño y formato

#### 9. T-009: Desarrollar Landing Page de bienvenida (3pts)
- **Estado:** ✅ Done
- **ID:** 42
- **Parent:** F-003: Infraestructura Base
- **Descripción:**
  - Página de bienvenida
  - Diseño responsive
  - Información del proyecto

#### 10. T-012: Configurar infraestructura pytest para backend (5pts)
- **Estado:** ✅ Done
- **ID:** 24
- **Parent:** F-003: Infraestructura Base
- **Descripción:**
  - Configuración de pytest
  - pytest-asyncio
  - Fixtures básicos
  - pytest.ini configurado

#### 11. T-013: Crear tests unitarios para endpoints FastAPI (8pts)
- **Estado:** ✅ Done
- **ID:** 25
- **Parent:** F-003: Infraestructura Base
- **Descripción:**
  - Tests para endpoints de autenticación
  - Tests para endpoints de imágenes
  - Tests con mocks
  - Cobertura > 75%

#### 12. T-015: Integrar PlantNet API para Identificación (5pts)
- **Estado:** ✅ Done
- **ID:** 23
- **Parent:** US-003: Identificar Especie de Planta
- **Descripción:**
  - Integración con PlantNet API
  - Servicio de identificación
  - Manejo de respuestas
  - Error handling

---

### 🔄 Tareas En Progreso (1)

#### 13. T-014: Configurar Azure Pipelines CI/CD (8pts)
- **Estado:** 🔄 Doing
- **ID:** 26
- **Parent:** F-003: Infraestructura Base
- **Descripción completa:**
  
  **Pipeline completo de CI/CD con múltiples stages:**
  
  ✅ **COMPLETADO:**
  - azure-pipelines.yml con 400+ líneas
  - 4 Stages implementados:
    1. **Test Stage:** pytest con coverage + flake8 linting + quality gates
    2. **Build Stage:** Docker images para backend y frontend + push a ACR
    3. **Deploy Stage:** Deployment a Azure Container Apps
    4. **PostDeployment Stage:** Smoke tests y validación
  
  🔧 **Características:**
  - Integración con Azure Container Registry (ACR)
  - Integración con Azure Subscription
  - Cache de dependencias (pip y npm)
  - Conditional deployment (solo rama main)
  - Work items integration
  - Quality gates (coverage > 75%, max 5 fallos en linting)
  
  📊 **Configuración:**
  - Variables de entorno configuradas
  - Service connections listas para usar
  - Triggers en push y PR

---

## 🚀 Sprint 2 - Tareas Pendientes

### ⏳ Tareas Por Realizar (2)

#### 1. T-022: Implementar soporte para múltiples imágenes y parámetro organ en identificación (8pts)
- **Estado:** ⏳ To Do
- **ID:** 54
- **Sprint:** Sprint 2
- **Story Points:** 8
- **Complejidad:** Media-Alta
- **Tiempo estimado:** 2-3 días

**📋 Descripción:**
Ampliar la funcionalidad de identificación de plantas para permitir el envío de hasta 5 imágenes simultáneas en una sola petición, junto con el parámetro 'organ' para cada imagen que especifique la parte de la planta (flor, hoja, fruto, corteza, etc.).

**🌿 Contexto de PlantNet API:**
Según la documentación oficial de PlantNet, el servicio permite:
- Enviar de 1 a 5 imágenes de la misma planta en una sola petición
- Especificar el tipo de órgano (organ) para cada imagen: flower, leaf, fruit, bark, habit, other
- Mejora la precisión de identificación al proporcionar múltiples vistas de la planta
- Endpoint: `POST /v2/identify` con API key como query parameter

**🔧 Cambios Requeridos - Backend:**

1. **Actualizar Modelo de Datos** (`app/db/models.py`)
   - Modificar tabla 'imagenes' o crear relación para múltiples imágenes por identificación
   - Agregar campo 'organ' (Enum: flower, leaf, fruit, bark, habit, other)
   - Crear tabla 'identificaciones' que agrupe múltiples imágenes
   - Relaciones: Identificacion -> hasMany -> Imagenes

2. **Actualizar Schemas Pydantic** (`app/schemas/`)
```python
class ImagenIdentificacionCreate(BaseModel):
    imagen_base64: str
    organ: Optional[str] = 'auto'  # flower, leaf, fruit, bark, habit, other

class IdentificacionMultipleRequest(BaseModel):
    imagenes: List[ImagenIdentificacionCreate]  # Max 5
    project: str = 'all'
    
    @validator('imagenes')
    def validar_cantidad_imagenes(cls, v):
        if len(v) < 1 or len(v) > 5:
            raise ValueError('Debe enviar entre 1 y 5 imágenes')
        return v
```

3. **Actualizar PlantNet Service** (`app/services/plantnet_service.py`)
   - Modificar método `identify_plant()` para aceptar lista de imágenes
   - Construir request multipart/form-data con múltiples imágenes
   - Incluir parámetro 'organs' como array en el body
   - Ejemplo de llamada API:
```
POST /v2/identify/{project}?api-key={key}
Content-Type: multipart/form-data

images: [file1, file2, file3]
organs: ['flower', 'leaf', 'fruit']
```

4. **Actualizar Endpoints API** (`app/api/identificacion.py`)
   - POST `/api/identificacion/multiple` - Nuevo endpoint para múltiples imágenes
   - Mantener POST `/api/identificacion/single` para retrocompatibilidad
   - Validar tipo de organ permitido
   - Guardar todas las imágenes asociadas a una identificación
   - Retornar ID de identificación con resultados agregados

5. **Migración de Base de Datos**
   - Crear migración Alembic para nuevos campos y tablas
   - Script de migración para datos existentes (si aplica)

**🎨 Cambios Requeridos - Frontend:**

1. **Actualizar Componente ImageUpload**
   - Permitir selección de hasta 5 imágenes
   - Preview múltiple con opción de eliminar individualmente
   - Dropdown o selector para cada imagen para elegir 'organ'
   - Opciones organ: Flor, Hoja, Fruto, Corteza, Hábito, Otro
   - UI clara mostrando contador (ej: "3/5 imágenes")

2. **Actualizar Servicios** (`lib/plant.service.ts`)
```typescript
interface ImageWithOrgan {
  file: File;
  organ: 'flower' | 'leaf' | 'fruit' | 'bark' | 'habit' | 'other';
}

interface IdentifyMultipleRequest {
  images: ImageWithOrgan[];
  project?: string;
}

export const identifyPlantMultiple = async (data: IdentifyMultipleRequest) => {
  const formData = new FormData();
  data.images.forEach((img, index) => {
    formData.append(`images`, img.file);
    formData.append(`organs`, img.organ);
  });
  // ...
}
```

3. **Actualizar Página de Identificación** (`app/identificar/page.tsx`)
   - Mostrar lista de imágenes con sus órganos seleccionados
   - Permitir reordenar imágenes (drag and drop)
   - Botón para agregar más imágenes (hasta límite de 5)
   - Validación: Al menos 1 imagen requerida

**🌱 Tipos de Órganos (Organ) Soportados:**
- **flower** - Flor o inflorescencia
- **leaf** - Hoja
- **fruit** - Fruto o semilla
- **bark** - Corteza o tronco
- **habit** - Hábito o porte general de la planta
- **other** - Otra parte no especificada
- **auto** - Detección automática (por defecto si no se especifica)

**📝 Ejemplo de Request API PlantNet:**
```
POST https://my-api.plantnet.org/v2/identify/all?api-key=YOUR_API_KEY
Content-Type: multipart/form-data

images: [imagen1.jpg, imagen2.jpg, imagen3.jpg]
organs: ['flower', 'leaf', 'fruit']
```

**📦 Ejemplo de Response Esperado:**
```json
{
  "query": {
    "project": "all",
    "images": ["image_1", "image_2", "image_3"],
    "organs": ["flower", "leaf", "fruit"]
  },
  "results": [
    {
      "score": 0.9952,
      "species": {
        "scientificNameWithoutAuthor": "Hibiscus rosa-sinensis",
        "commonNames": ["Chinese hibiscus"]
      }
    }
  ],
  "remainingIdentificationRequests": 1228
}
```

**🧪 Tests Requeridos:**

Backend:
- Test con 1 imagen (caso mínimo)
- Test con 5 imágenes (caso máximo)
- Test con 6 imágenes (debe fallar validación)
- Test con diferentes tipos de organ
- Test de integración con PlantNet API mock
- Test de guardado en DB con múltiples imágenes

Frontend:
- Test de selección múltiple de imágenes
- Test de límite de 5 imágenes
- Test de selector de organ por imagen
- Test de eliminación de imagen individual
- Test de envío de formulario con datos válidos

**✅ Criterios de Aceptación:**
- ✅ Usuario puede subir entre 1 y 5 imágenes en una sola identificación
- ✅ Para cada imagen, usuario puede seleccionar el tipo de órgano
- ✅ El sistema envía correctamente todas las imágenes y órganos a PlantNet API
- ✅ Resultados de identificación muestran qué imágenes fueron usadas
- ✅ Validación impide enviar más de 5 imágenes
- ✅ UI muestra claramente el contador de imágenes y límite
- ✅ Migración de BD ejecutada correctamente
- ✅ Tests backend y frontend con cobertura > 80%
- ✅ Documentación actualizada (README, Swagger)
- ✅ Retrocompatibilidad con endpoint de imagen única mantenida

**📚 Documentación de Referencia:**
- [PlantNet API - Getting Started](https://my.plantnet.org/doc/getting-started/introduction)
- [PlantNet API - Single-species identification](https://my.plantnet.org/doc/api/identify)

**🔗 Dependencias:**
- T-015: Integración PlantNet API (✅ completada)
- T-004: API de subida de imágenes (✅ completada)

**💡 Impacto:**
Esta mejora aumentará significativamente la precisión de las identificaciones al permitir que los usuarios proporcionen múltiples vistas de la misma planta, siguiendo las mejores prácticas recomendadas por PlantNet.

---

#### 2. T-023: Implementar UI de Resultados de Identificación con Múltiples Imágenes (13pts)
- **Estado:** ⏳ To Do
- **ID:** 55
- **Sprint:** Sprint 2
- **Story Points:** 13
- **Complejidad:** Alta
- **Tiempo estimado:** 3-4 días
- **Prioridad:** Alta

**📋 Descripción:**
Implementar la interfaz de usuario completa para mostrar los resultados de identificación de plantas con soporte para múltiples imágenes, permitiendo al usuario visualizar todas las imágenes con sus organ labels en un carousel, ver las coincidencias ordenadas por confianza, seleccionar una especie para agregar a su jardín, y visualizarla posteriormente en el dashboard.

**🎯 Contexto:**
Esta tarea integra la UI de resultados con el backend ya implementado en T-022 (múltiples imágenes con organ). La implementación de referencia se encuentra en la carpeta `proyecto-plantitas` y debe adaptarse al proyecto actual manteniendo la arquitectura MVC y los estándares del equipo.

**🔧 Componentes Principales:**

1. **Página de Resultados** (`app/identificar/resultados/page.tsx`)
   - Cargar resultados desde el endpoint existente
   - Mostrar información general de la identificación
   - Lista de resultados ordenados por confianza
   - Integración con IdentificationResultCard component
   - Estados: loading, error, success
   - Navegación fluida entre páginas

2. **Componente IdentificationResultCard**
   - ✅ YA IMPLEMENTADO: Carousel de imágenes con organ labels
   - ✅ YA IMPLEMENTADO: Badge de confianza visual
   - ✅ YA IMPLEMENTADO: Información científica
   - Botón "Confirmar esta planta" funcional
   - Estado visual de confirmación
   - Responsive design

3. **Servicios y API Integration**
   - Función `agregarPlantaAlJardin()` - Agregar planta al jardín del usuario
   - Función `obtenerMisPlantas()` - Obtener plantas del usuario
   - Manejo de errores y estados de carga
   - Integración con AuthContext

4. **Actualizar Dashboard**
   - Mostrar plantas agregadas desde identificaciones
   - Card de planta con imagen, nombre científico y común
   - Enlace a detalles de la planta
   - Indicador de origen (identificación vs manual)

**👤 Flujo de Usuario:**
1. Usuario sube 1-5 imágenes en `/identificar`
2. Sistema procesa y redirige a `/identificar/resultados?identificacionId=X`
3. Página muestra resultados con carousel de imágenes
4. Usuario revisa resultados ordenados por confianza
5. Usuario hace clic en "Confirmar esta planta" en el resultado deseado
6. Sistema guarda la planta en el jardín del usuario
7. Feedback visual de confirmación exitosa
8. Usuario puede ir al dashboard para ver su nueva planta

**🔌 Endpoints Backend Necesarios:**

*Ya Implementados:*
- `GET /api/identificacion/{id}` - Obtener detalle de identificación
- `POST /api/identificacion/multiple` - Crear identificación múltiple

*Por Implementar (si no existen):*
- `POST /api/plantas/agregar` - Agregar planta al jardín del usuario
  - Request: `{ identificacion_id, especie_id?, nombre_personalizado? }`
  - Response: `{ planta_id, mensaje }`
  - Auth: JWT required

- `GET /api/plantas/mis-plantas` - Obtener plantas del usuario
  - Response: `[{ id, nombre, especie, imagen_principal, fecha_agregada }]`
  - Auth: JWT required

**🧪 Tests Requeridos:**

*Unit Tests (Jest + React Testing Library):*
- `tests/identificar-resultados.test.tsx`
  - Renderiza loading state correctamente
  - Renderiza error state con mensaje apropiado
  - Renderiza lista de resultados correctamente
  - Ordena resultados por confianza descendente
  - Navega a identificar al hacer clic en 'Volver'

- `tests/components/identification-result-card.test.tsx`
  - Renderiza información científica correctamente
  - Muestra badge de confianza con color apropiado
  - Carousel funciona y cambia imágenes automáticamente
  - Muestra organ labels en cada imagen
  - Botón confirmar llama a onConfirm callback
  - Estado confirmado muestra feedback visual

- `tests/lib/plant-service.test.ts`
  - agregarPlantaAlJardin() crea planta correctamente
  - obtenerMisPlantas() retorna lista de plantas del usuario
  - Maneja errores de autenticación y red

- `tests/dashboard-plantas.test.tsx`
  - Renderiza lista de plantas del usuario
  - Muestra mensaje cuando no hay plantas
  - Filtra plantas por origen
  - Navega a detalle de planta al hacer clic

*Integration Tests (Pruebas manuales en contenedores):*
- Flujo completo: identificar → confirmar → ver en dashboard
- Identificación con 1 y 5 imágenes funciona
- Confirmación guarda planta en BD
- Dashboard muestra plantas agregadas
- Autenticación requerida para confirmar plantas
- Manejo de errores de red
- Responsive design en mobile

**✅ Criterios de Aceptación:**
- ✅ Página de resultados muestra todas las imágenes en carousel
- ✅ Cada imagen muestra su organ label correctamente
- ✅ Resultados ordenados por confianza (mayor a menor)
- ✅ Usuario puede confirmar una especie para agregar a su jardín
- ✅ Confirmación exitosa muestra feedback visual inmediato
- ✅ Planta confirmada aparece en el dashboard del usuario
- ✅ Dashboard muestra imagen principal y nombres de la planta
- ✅ Navegación fluida entre páginas
- ✅ Estados de loading y error bien manejados
- ✅ UI responsive funciona en mobile y desktop
- ✅ Tests unitarios con cobertura > 80%
- ✅ Tests de integración completados exitosamente
- ✅ Documentación actualizada en código
- ✅ Respeta arquitectura MVC y estándares del equipo

**🎨 Mejoras UI Recomendadas:**
- Animaciones suaves en transiciones
- Skeleton loaders durante carga
- Toast notifications para confirmaciones
- Modal de confirmación antes de agregar planta
- Sección de cuidados básicos en resultados
- Botón para compartir identificación
- Historial de identificaciones en perfil

**🔗 Dependencias:**
- T-022: Implementar soporte para múltiples imágenes y parámetro organ (✅ Completada)
- T-008: Componente de subida de fotos (✅ Completada)
- T-017: API de identificación (✅ Completada)
- AuthContext implementado (✅ Completado)

**📁 Archivos Principales:**

*Frontend:*
- `app/identificar/resultados/page.tsx` [ACTUALIZAR]
- `app/dashboard/page.tsx` [ACTUALIZAR]
- `components/identification-result-card.tsx` [YA EXISTE]
- `lib/plant.service.ts` [ACTUALIZAR]
- `lib/dashboard.service.ts` [CREAR/ACTUALIZAR]
- `models/plant.types.ts` [ACTUALIZAR]
- Tests correspondientes [CREAR/ACTUALIZAR]

*Backend:*
- `app/api/plantas.py` [CREAR/ACTUALIZAR]
- `app/schemas/planta_schemas.py` [CREAR/ACTUALIZAR]
- `app/services/planta_service.py` [CREAR/ACTUALIZAR]
- `tests/test_plantas_api.py` [CREAR]

**📝 Notas Técnicas:**
- Usar componentes UI de shadcn/ui existentes
- Mantener consistencia con diseño actual
- Implementar lazy loading de imágenes
- Cachear resultados de identificación en sessionStorage
- Optimizar queries de BD para evitar N+1 problems
- Implementar paginación si usuario tiene muchas plantas

**📚 Referencias:**
- [Implementación de referencia](file:///c:/Users/franq/Downloads/asdf/azure/project/projecto-ia-aplicada/proyecto-plantitas/app/identify/results/page.tsx)
- [Documentación PlantNet](https://my.plantnet.org/doc)
- [Tarea detallada](file:///c:/Users/franq/Downloads/asdf/azure/project/projecto-ia-aplicada/TAREA_T023_UI_RESULTADOS.md)

**💡 Impacto:**
Esta implementación completará el flujo de usuario end-to-end desde la identificación hasta la gestión de plantas en el dashboard, proporcionando una experiencia de usuario completa y profesional que integra múltiples componentes del sistema.

---

## 📈 Estadísticas Generales

### Por Estado
- ✅ **Done:** 12 tareas (86 pts)
- 🔄 **Doing:** 1 tarea (8 pts)
- ⏳ **To Do:** 2 tareas (21 pts)

### Por Tipo
- **Backend:** 8 tareas (T-001, T-002, T-003, T-004, T-012, T-013, T-014, T-015)
- **Frontend:** 4 tareas (T-005, T-006, T-007, T-008, T-009)
- **FullStack:** 2 tareas (T-022, T-023)

### Distribución de Puntos
- **Sprint 1:** 94 pts totales
  - Completados: 86 pts (91.5%)
  - En progreso: 8 pts (8.5%)
- **Sprint 2:** 21 pts totales
  - Pendientes: 21 pts (100%)

---

## 🎯 Próximos Pasos Recomendados

1. **Completar T-014** (Azure Pipelines CI/CD)
   - Finalizar configuración pendiente
   - Ejecutar pruebas del pipeline
   - Validar deployment

2. **Iniciar T-022** (Múltiples imágenes)
   - Revisar documentación de PlantNet
   - Planificar cambios en modelos de datos
   - Crear migración de base de datos
   - Implementar backend primero
   - Actualizar frontend después

3. **Iniciar T-023** (UI de Resultados)
   - Analizar implementación de referencia en proyecto-plantitas
   - Adaptar página de resultados existente
   - Implementar funcionalidad de confirmación
   - Actualizar dashboard para mostrar plantas
   - Realizar tests unitarios y de integración
   - Probar en contenedores Docker

4. **Planificar Sprint 3**
   - Definir nuevas tareas
   - Estimar story points
   - Asignar responsables

---

**Generado por:** GitHub Copilot  
**Fecha:** 20 de octubre de 2025  
**Fuente:** Azure DevOps - Organización ia-grupo-5
