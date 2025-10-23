# T-023: Implementar UI de Resultados de Identificación con Múltiples Imágenes

**ID en Azure DevOps:** 55  
**Estado:** To Do  
**Sprint:** Sprint 2  
**Story Points:** 13  
**Prioridad:** Alta  
**Complejidad:** Alta  
**Tiempo estimado:** 3-4 días  

---

## 📋 Descripción

Implementar la interfaz de usuario completa para mostrar los resultados de identificación de plantas con soporte para múltiples imágenes, permitiendo al usuario visualizar todas las imágenes con sus organ labels en un carousel, ver las coincidencias ordenadas por confianza, seleccionar una especie para agregar a su jardín, y visualizarla posteriormente en el dashboard.

## 🎯 Contexto

Esta tarea integra la UI de resultados con el backend ya implementado en T-022 (múltiples imágenes con organ). La implementación de referencia se encuentra en la carpeta `proyecto-plantitas` y debe adaptarse al proyecto actual manteniendo la arquitectura MVC y los estándares del equipo.

---

## 🔧 Componentes a Implementar/Actualizar

### 1. Página de Resultados (`app/identificar/resultados/page.tsx`)

**Responsabilidades:**
- Cargar resultados desde el endpoint existente
- Mostrar información general de la identificación
- Lista de resultados ordenados por confianza
- Integración con IdentificationResultCard component
- Estados: loading, error, success
- Navegación: volver a identificar, ir al dashboard
- Información educativa sobre niveles de confianza
- Footer con créditos a PlantNet

**Referencia:** `proyecto-plantitas/app/identify/results/page.tsx`

### 2. Componente IdentificationResultCard

**Estado actual:**
- ✅ YA IMPLEMENTADO: Carousel de imágenes con organ labels
- ✅ YA IMPLEMENTADO: Badge de confianza visual
- ✅ YA IMPLEMENTADO: Información científica (nombre, género, familia)

**Por implementar:**
- Botón 'Confirmar esta planta' funcional
- Estado visual de confirmación
- Responsive design para mobile y desktop

### 3. Servicios y API Integration

**Nuevas funciones necesarias:**
- `agregarPlantaAlJardin()` - Agregar planta al jardín del usuario
- `obtenerMisPlantas()` - Obtener plantas del usuario
- `obtenerDetalleIdentificacion()` - Obtener detalles completos de identificación
- Manejo de errores y estados de carga
- Integración con AuthContext para usuario actual

### 4. Actualizar Dashboard

**Funcionalidad nueva:**
- Mostrar plantas agregadas desde identificaciones
- Card de planta con imagen, nombre científico y común
- Enlace a detalles de la planta
- Indicador de origen (identificación vs manual)

---

## 👤 Flujo de Usuario Completo

1. Usuario sube 1-5 imágenes en `/identificar`
2. Sistema procesa y redirige a `/identificar/resultados?identificacionId=X`
3. Página muestra resultados con carousel de imágenes
4. Usuario revisa resultados ordenados por confianza
5. Usuario hace clic en "Confirmar esta planta" en el resultado deseado
6. Sistema guarda la planta en el jardín del usuario
7. Feedback visual de confirmación exitosa
8. Usuario puede ir al dashboard para ver su nueva planta

---

## 🔌 Endpoints Backend Necesarios

### Ya Implementados:
- `GET /api/identificacion/{id}` - Obtener detalle de identificación
- `POST /api/identificacion/multiple` - Crear identificación múltiple

### Por Implementar (si no existen):

#### POST /api/plantas/agregar
Agregar planta al jardín del usuario

**Request:**
```json
{
  "identificacion_id": 123,
  "especie_id": 456,
  "nombre_personalizado": "Mi Monstera favorita"
}
```

**Response:**
```json
{
  "planta_id": 789,
  "mensaje": "Planta agregada exitosamente"
}
```

**Auth:** JWT required

#### GET /api/plantas/mis-plantas
Obtener plantas del usuario

**Response:**
```json
[
  {
    "id": 789,
    "nombre": "Mi Monstera favorita",
    "especie": "Monstera deliciosa",
    "imagen_principal": "https://...",
    "fecha_agregada": "2025-10-20T10:30:00Z"
  }
]
```

**Auth:** JWT required

---

## 📦 Modelos y Types TypeScript

```typescript
// Extender tipos existentes en models/plant.types.ts

interface AgregarPlantaRequest {
  identificacion_id: number;
  especie_id?: number;
  nombre_personalizado?: string;
  notas?: string;
}

interface PlantaUsuario {
  id: number;
  usuario_id: number;
  especie_id: number | null;
  nombre_cientifico: string;
  nombres_comunes: string[];
  nombre_personalizado?: string;
  imagen_principal: string;
  fecha_agregada: string;
  origen: 'identificacion' | 'manual';
  identificacion_id?: number;
}
```

---

## 🧪 Tests Requeridos

### Unit Tests (Jest + React Testing Library)

#### 1. tests/identificar-resultados.test.tsx
- [ ] Renderiza loading state correctamente
- [ ] Renderiza error state con mensaje apropiado
- [ ] Renderiza lista de resultados correctamente
- [ ] Ordena resultados por confianza descendente
- [ ] Navega a identificar al hacer clic en 'Volver'

#### 2. tests/components/identification-result-card.test.tsx
- [ ] Renderiza información científica correctamente
- [ ] Muestra badge de confianza con color apropiado
- [ ] Carousel funciona y cambia imágenes automáticamente
- [ ] Muestra organ labels en cada imagen
- [ ] Botón confirmar llama a onConfirm callback
- [ ] Estado confirmado muestra feedback visual

#### 3. tests/lib/plant-service.test.ts
- [ ] agregarPlantaAlJardin() crea planta correctamente
- [ ] obtenerMisPlantas() retorna lista de plantas del usuario
- [ ] Maneja errores de autenticación
- [ ] Maneja errores de red

#### 4. tests/dashboard-plantas.test.tsx
- [ ] Renderiza lista de plantas del usuario
- [ ] Muestra mensaje cuando no hay plantas
- [ ] Filtra plantas por origen
- [ ] Navega a detalle de planta al hacer clic

### Integration Tests (Pruebas manuales en contenedores)

- [ ] Flujo completo: identificar → confirmar → ver en dashboard
- [ ] Identificación con 1 imagen funciona
- [ ] Identificación con 5 imágenes funciona
- [ ] Confirmación guarda planta en BD
- [ ] Dashboard muestra plantas agregadas
- [ ] Autenticación requerida para confirmar plantas
- [ ] Manejo de errores de red
- [ ] Responsive design en mobile

---

## ✅ Criterios de Aceptación

- [ ] Página de resultados muestra todas las imágenes en carousel
- [ ] Cada imagen muestra su organ label correctamente
- [ ] Resultados ordenados por confianza (mayor a menor)
- [ ] Usuario puede confirmar una especie para agregar a su jardín
- [ ] Confirmación exitosa muestra feedback visual inmediato
- [ ] Planta confirmada aparece en el dashboard del usuario
- [ ] Dashboard muestra imagen principal y nombres de la planta
- [ ] Navegación fluida entre páginas
- [ ] Estados de loading y error bien manejados
- [ ] UI responsive funciona en mobile y desktop
- [ ] Tests unitarios con cobertura > 80%
- [ ] Tests de integración completados exitosamente
- [ ] Documentación actualizada en código
- [ ] Respeta arquitectura MVC y estándares del equipo

---

## 🎨 Mejoras UI Recomendadas

- Animaciones suaves en transiciones
- Skeleton loaders durante carga
- Toast notifications para confirmaciones
- Modal de confirmación antes de agregar planta
- Sección de cuidados básicos en resultados
- Botón para compartir identificación
- Historial de identificaciones en perfil

---

## 🔗 Dependencias

- ✅ T-022: Implementar soporte para múltiples imágenes y parámetro organ (Completada)
- ✅ T-008: Componente de subida de fotos (Completada)
- ✅ T-017: API de identificación (Completada)
- ✅ AuthContext implementado (Completado)

---

## 📁 Archivos Principales a Modificar/Crear

### Frontend

```
frontend/
├── app/
│   ├── identificar/
│   │   └── resultados/
│   │       └── page.tsx [ACTUALIZAR]
│   └── dashboard/
│       └── page.tsx [ACTUALIZAR]
├── components/
│   └── identification-result-card.tsx [YA EXISTE]
├── lib/
│   ├── plant.service.ts [ACTUALIZAR]
│   └── dashboard.service.ts [CREAR/ACTUALIZAR]
├── models/
│   └── plant.types.ts [ACTUALIZAR]
└── __tests__/
    ├── identificar-resultados.test.tsx [CREAR]
    ├── dashboard-plantas.test.tsx [CREAR]
    ├── components/
    │   └── identification-result-card.test.tsx [ACTUALIZAR]
    └── lib/
        └── plant-service.test.ts [ACTUALIZAR]
```

### Backend

```
backend/
├── app/
│   ├── api/
│   │   └── plantas.py [CREAR/ACTUALIZAR]
│   ├── schemas/
│   │   └── planta_schemas.py [CREAR/ACTUALIZAR]
│   └── services/
│       └── planta_service.py [CREAR/ACTUALIZAR]
└── tests/
    └── test_plantas_api.py [CREAR]
```

---

## 📝 Notas Técnicas

- Usar componentes UI de shadcn/ui existentes
- Mantener consistencia con diseño actual
- Implementar lazy loading de imágenes
- Cachear resultados de identificación en sessionStorage
- Optimizar queries de BD para evitar N+1 problems
- Implementar paginación si usuario tiene muchas plantas

---

## 📚 Referencias

- **Implementación de referencia:** `proyecto-plantitas/app/identify/results/page.tsx`
- **Documentación PlantNet:** https://my.plantnet.org/doc
- **Componente actual:** `frontend/app/identificar/resultados/page.tsx`
- **Diseño en Figma:** [pendiente]

---

## 🚀 Plan de Implementación Sugerido

### Día 1: Backend (4-5 horas)
1. Crear endpoints de plantas (POST /agregar, GET /mis-plantas)
2. Implementar schemas y servicios
3. Tests unitarios backend
4. Probar endpoints con Postman/Thunder Client

### Día 2: Frontend - Servicios y Tipos (4-5 horas)
1. Actualizar models/plant.types.ts
2. Implementar funciones en plant.service.ts
3. Crear dashboard.service.ts
4. Tests unitarios de servicios
5. Integración con AuthContext

### Día 3: Frontend - UI (6-7 horas)
1. Actualizar página de resultados
2. Hacer funcional el botón de confirmación
3. Actualizar dashboard para mostrar plantas
4. Implementar estados de loading/error
5. Agregar animaciones y transiciones

### Día 4: Testing y Refinamiento (4-5 horas)
1. Tests de componentes React
2. Tests de integración en contenedores
3. Corrección de bugs encontrados
4. Refinamiento de UI/UX
5. Documentación final
6. Code review

---

## 🔍 Verificación Final

Antes de marcar como completada, verificar:

1. ✅ Todos los tests unitarios pasan
2. ✅ Cobertura de tests > 80%
3. ✅ Pruebas en contenedores exitosas
4. ✅ Flujo completo funciona end-to-end
5. ✅ UI responsive en mobile y desktop
6. ✅ Documentación actualizada
7. ✅ Code review aprobado
8. ✅ Commits con mensajes descriptivos
9. ✅ Branch mergeada a develop/main

---

**Creado:** 20 de octubre de 2025  
**Creado por:** GitHub Copilot  
**Link Azure DevOps:** https://dev.azure.com/ia-grupo-5/proyecto-plantitas/_workitems/edit/55
