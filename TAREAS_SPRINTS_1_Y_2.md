# 📋 Tareas de Sprints 1 y 2 - Proyecto Plantitas IA

**Proyecto:** proyecto-plantitas  
**Organización:** ia-grupo-5  
**Fecha de consulta:** 19 de Octubre, 2025

---

## 🎯 Sprint 1: Fundación de la Aplicación

### 📊 Resumen del Sprint 1
- **Estado:** ✅ Completado
- **Features (Issues):** 3
- **Tasks:** 12
- **Total Story Points:** ~70 pts

---

### 🎫 Features (Issues) del Sprint 1

#### F-001: Sistema de Autenticación
- **ID:** 7
- **Estado:** ✅ Done
- **Área:** Backend
- **Descripción:** Implementar registro, login y gestión de sesiones segura

#### F-002: Gestión de Imágenes
- **ID:** 8
- **Estado:** ✅ Done
- **Área:** Frontend
- **Descripción:** Sistema de subida y gestión de fotos de plantas

#### F-003: Infraestructura Base
- **ID:** 9
- **Estado:** ✅ Done
- **Área:** DevOps
- **Descripción:** Setup de entorno de desarrollo y deployment

---

### 📝 Tasks del Sprint 1 - BACKEND

#### T-001: Configurar proyecto FastAPI con estructura MVC (5pts)
- **ID:** 27
- **Estado:** ✅ Done
- **Área:** Backend
- **Iteración:** Sprint 1
- **Parent:** F-003 (Infraestructura Base)

**Descripción:**
Setup inicial de FastAPI con estructura MVC. Establecer la base del proyecto backend con arquitectura limpia y escalable.

**Estructura de carpetas:**
```
/backend/app
  /api          # Rutas y endpoints
  /core         # Configuración, seguridad, dependencies
  /db           # Modelos de base de datos
  /schemas      # Pydantic models para validación
  /services     # Lógica de negocio
  /utils        # Utilidades y helpers
```

**Criterios de aceptación:**
- ✅ Proyecto FastAPI inicializado con estructura MVC
- ✅ Archivo main.py con configuración básica
- ✅ CORS configurado correctamente
- ✅ Health check endpoint funcional (GET /)
- ✅ Variables de entorno con python-dotenv
- ✅ README con instrucciones de setup

**Tiempo estimado:** 4-8 horas

---

#### T-002: Implementar modelos de usuario con SQLAlchemy (8pts)
- **ID:** 28
- **Estado:** ✅ Done
- **Área:** Backend
- **Iteración:** Sprint 1
- **Parent:** F-003 (Infraestructura Base)

**Descripción:**
Crear modelos de base de datos para usuarios. Definir el modelo User con SQLAlchemy ORM para autenticación.

**Modelo User:**
```python
class User(Base):
    id: int (Primary Key)
    email: str (Unique, Index)
    password_hash: str
    nombre: str (Optional)
    created_at: datetime
    updated_at: datetime
    is_active: bool (default=True)
```

**Criterios de aceptación:**
- ✅ Modelo User con campos requeridos definido
- ✅ Password hashing implementado (bcrypt)
- ✅ Migraciones Alembic creadas
- ✅ Indices apropiados (email)
- ✅ Validaciones a nivel modelo
- ✅ Métodos auxiliares (verify_password, etc.)

**Dependencias:** T-001  
**Tiempo estimado:** 1-2 días

---

#### T-003: Crear endpoints de autenticación JWT (13pts)
- **ID:** 29
- **Estado:** ✅ Done
- **Área:** Backend
- **Iteración:** Sprint 1
- **Parent:** F-003 (Infraestructura Base)

**Descripción:**
Implementar sistema completo de autenticación con JWT. Endpoints seguros para registro, login y gestión de sesiones.

**Endpoints:**
- `POST /auth/register` - Registro de usuario
- `POST /auth/login` - Login y generación de JWT token
- `GET /auth/me` - Obtener usuario actual
- `POST /auth/refresh` - Refresh token
- `POST /auth/logout` - Cerrar sesión

**Criterios de aceptación:**
- ✅ Todos los endpoints funcionando correctamente
- ✅ JWT token generation con python-jose
- ✅ Token expiration configurado (30 min)
- ✅ Middleware de autenticación implementado
- ✅ Validación de credenciales con bcrypt
- ✅ Rate limiting en endpoints de auth
- ✅ Manejo de errores apropiado
- ✅ Tests unitarios para auth service

**Dependencias:** T-001, T-002  
**Tiempo estimado:** 2-3 días

---

#### T-003A: Implementar endpoint de registro de usuario (5pts)
- **ID:** 35
- **Estado:** ✅ Done
- **Iteración:** Sprint 1
- **Parent:** F-003 (Infraestructura Base)

**Descripción:**
Implementar endpoint POST /auth/register para registro de nuevos usuarios con validaciones de email, password hashing con bcrypt, y manejo de errores apropiado.

---

#### T-003B: Implementar endpoint de login con JWT (5pts)
- **ID:** 36
- **Estado:** ✅ Done
- **Iteración:** Sprint 1
- **Parent:** F-003 (Infraestructura Base)

**Descripción:**
Crear endpoint POST /auth/login con generación de JWT token, verificación de credenciales, JWT con expiración de 30 min, y rate limiting.

---

#### T-003C: Implementar refresh token y logout (3pts)
- **ID:** 37
- **Estado:** ✅ Done
- **Iteración:** Sprint 1
- **Parent:** F-003 (Infraestructura Base)

**Descripción:**
Crear endpoints POST /auth/refresh, POST /auth/logout y GET /auth/me con middleware de autenticación y refresh token con expiración de 7 días.

---

#### T-004: Desarrollar API de subida de imágenes (8pts)
- **ID:** 30
- **Estado:** ✅ Done
- **Área:** Backend
- **Iteración:** Sprint 1
- **Parent:** F-003 (Infraestructura Base)

**Descripción:**
Sistema de upload y gestión de imágenes de plantas. Permitir a usuarios subir fotos de plantas de forma segura.

**Endpoints:**
- `POST /api/uploads/imagen` - Subir imagen
- `GET /api/uploads/{imagen_id}` - Obtener imagen
- `DELETE /api/uploads/{imagen_id}` - Eliminar imagen

**Criterios de aceptación:**
- ✅ Upload de imágenes (jpg, png, webp)
- ✅ Validación de formato y tamaño (max 10MB)
- ✅ Almacenamiento en Azure Blob Storage
- ✅ Generación de thumbnails automática
- ✅ Metadatos de imagen guardados en DB
- ✅ Solo usuarios autenticados pueden subir
- ✅ Rate limiting (max 10 uploads/hora)

**Dependencias:** T-001, T-003  
**Tiempo estimado:** 1-2 días

---

### 📝 Tasks del Sprint 1 - FRONTEND

#### T-005: Setup React 18 con Tailwind CSS (5pts)
- **ID:** 31
- **Estado:** ✅ Done
- **Área:** Frontend
- **Iteración:** Sprint 1
- **Parent:** F-003 (Infraestructura Base)

**Descripción:**
Configuración inicial del proyecto frontend. Establecer la base del frontend con React 18 y Tailwind CSS.

**Estructura:**
```
/frontend/src
  /components   # Componentes reutilizables
  /pages        # Páginas/Vistas principales
  /services     # Servicios y lógica de negocio
  /hooks        # Custom hooks de React
  /context      # Context API para estado global
  /models       # Interfaces y tipos TypeScript
  /utils        # Utilidades del frontend
```

**Criterios de aceptación:**
- ✅ React 18 configurado con TypeScript
- ✅ Tailwind CSS instalado y funcionando
- ✅ React Router configurado
- ✅ Axios o Fetch para HTTP requests
- ✅ Environment files (dev/prod)
- ✅ ESLint y Prettier configurados
- ✅ README con comandos básicos

**Tiempo estimado:** 4-8 horas

---

#### T-006: Implementar componentes de login/registro (13pts)
- **ID:** 32
- **Estado:** ✅ Done
- **Área:** Frontend
- **Iteración:** Sprint 1
- **Parent:** F-003 (Infraestructura Base)

**Descripción:**
Crear componentes de autenticación con React Hook Form. Interfaces de usuario para registro y login de usuarios.

**Componentes:**
- `Login` - Componente de login
- `Register` - Componente de registro
- `AuthLayout` - Layout para autenticación

**Criterios de aceptación:**
- ✅ Login component con React Hook Form
- ✅ Register component con validaciones
- ✅ Validaciones en tiempo real (email, password)
- ✅ Mensajes de error personalizados
- ✅ Loading states durante autenticación
- ✅ Redirección post-login con React Router
- ✅ UI responsiva con Tailwind
- ✅ Accesibilidad (ARIA labels)

**Dependencias:** T-005  
**Tiempo estimado:** 2-3 días

---

#### T-006A: Componente LoginComponent (5pts)
- **ID:** 38
- **Estado:** ✅ Done

**Descripción:**
Crear LoginComponent con reactive forms, validaciones en tiempo real (email, password), mensajes de error personalizados, loading states, y UI responsiva con Tailwind CSS.

---

#### T-006B: Componente RegisterComponent (5pts)
- **ID:** 39
- **Estado:** ✅ Done

**Descripción:**
Crear RegisterComponent con reactive forms, validaciones de email y password, confirmación de password, mensajes de error personalizados, loading states, y UI responsiva con Tailwind CSS.

---

#### T-006C: Validaciones y manejo de errores (3pts)
- **ID:** 40
- **Estado:** ✅ Done

**Descripción:**
Implementar validaciones avanzadas, manejo de errores de API, estados de carga, redirección post-login, y accesibilidad (ARIA labels) para ambos componentes.

---

#### T-007: Crear servicio de autenticación React (8pts)
- **ID:** 33
- **Estado:** ✅ Done
- **Área:** Frontend
- **Iteración:** Sprint 1
- **Parent:** F-003 (Infraestructura Base)

**Descripción:**
Servicio centralizado para gestión de autenticación. Custom hook y servicio con lógica de autenticación, token storage y state management.

**Interfaces:**
```typescript
// authService.ts
interface AuthService {
  login(email: string, password: string): Promise
  register(userData: UserData): Promise
  logout(): void
  getCurrentUser(): User | null
  isAuthenticated(): boolean
  getToken(): string | null
  refreshToken(): Promise
}

// useAuth.ts (Custom Hook)
const useAuth = () => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  // ... lógica de autenticación
}
```

**Criterios de aceptación:**
- ✅ AuthService implementado con TypeScript
- ✅ Custom hook useAuth para estado global
- ✅ JWT token storage en localStorage
- ✅ Auto-refresh de tokens
- ✅ Context API para estado de usuario
- ✅ Axios interceptor para agregar token
- ✅ Manejo de errores HTTP
- ✅ Logout automático en token expirado

**Dependencias:** T-005  
**Tiempo estimado:** 1-2 días

---

#### T-008: Desarrollar componente de subida de fotos (8pts)
- **ID:** 34
- **Estado:** ✅ Done
- **Área:** Frontend
- **Iteración:** Sprint 1
- **Parent:** F-003 (Infraestructura Base)

**Descripción:**
Componente para upload de imágenes con preview. Interfaz intuitiva para subir fotos de plantas.

**Funcionalidades del ImageUpload:**
- Drag and drop de archivos
- Click para seleccionar archivo
- Captura desde cámara (móvil/desktop)
- Preview de imagen antes de subir
- Barra de progreso de upload
- Validación de formato y tamaño

**Criterios de aceptación:**
- ✅ Drag and drop funcional con useDropzone o similar
- ✅ Input file con validaciones
- ✅ Acceso a cámara en dispositivos
- ✅ Preview con opción de cancelar
- ✅ Progress bar durante upload
- ✅ Mensajes de éxito/error
- ✅ UI responsiva para móvil
- ✅ Integración con backend API
- ✅ Custom hook useImageUpload para lógica reutilizable

**Dependencias:** T-005, T-007  
**Tiempo estimado:** 1-2 días

---

#### T-009: Desarrollar Landing Page de bienvenida (3pts)
- **ID:** 42
- **Estado:** ✅ Done
- **Área:** Frontend
- **Iteración:** Sprint 1
- **Parent:** F-003 (Infraestructura Base)

**Descripción:**
Crear una landing page atractiva que presente la aplicación y guíe a los usuarios a registro/login.

**Componentes:**
- **Hero Section:** Título principal, descripción del valor de la app, imagen/ilustración de plantas
- **Features Section:** 3-4 cards mostrando funcionalidades clave (IA, identificación, consejos)
- **Call-to-Action:** Botones prominentes para 'Comenzar' y 'Iniciar Sesión'
- **Footer:** Links básicos, copyright, redes sociales

**Criterios de aceptación:**
- ✅ Diseño responsive (mobile-first)
- ✅ Hero section con gradiente y animaciones Tailwind
- ✅ Cards de features con iconos
- ✅ Navegación a /login y /register
- ✅ Footer con información del proyecto
- ✅ Animaciones suaves en scroll (fade-in)

**Stack técnico:**
- React 18 + TypeScript
- Tailwind CSS
- React Router

**Tiempo estimado:** 3-4 horas

---

#### T-008 (Dashboard): Implementar Dashboard Protegido y Funcionalidad de Cerrar Sesión
- **ID:** 43
- **Estado:** ✅ Done

**Descripción:**
Crear un dashboard protegido que solo sea accesible después de iniciar sesión, con funcionalidad de cerrar sesión implementada.

**Requisitos:**
- Crear página de dashboard con contenido básico
- Proteger la ruta del dashboard mediante middleware de autenticación
- Implementar botón de cerrar sesión
- Implementar funcionalidad de logout que limpie el token y redirija a login
- Agregar tests para verificar protección de ruta y funcionalidad de logout

**Criterios de aceptación:**
- ✅ El dashboard solo es accesible con token JWT válido
- ✅ Usuarios no autenticados son redirigidos a /login
- ✅ El botón de logout limpia la sesión correctamente
- ✅ Después de logout, el usuario es redirigido a /login
- ✅ Cobertura de tests >= 80%

---

## 🎯 Sprint 2: Identificación de Plantas (IA Core)

### 📊 Resumen del Sprint 2
- **Estado:** 🔄 En Progreso
- **Features (Issues):** 2
- **Tasks:** 6 (5 completadas, 1 pendiente)
- **Total Story Points:** ~36 pts

---

### 🎫 Features (Issues) del Sprint 2

#### F-004: Motor de Identificación IA
- **ID:** 10
- **Estado:** ✅ Done
- **Área:** AI
- **Iteración:** Sprint 2
- **Parent:** EPIC-02 (Identificación de Plantas)
- **Descripción:** Sistema principal de identificación de plantas usando IA

#### F-005: Gestión de Resultados
- **ID:** 11
- **Estado:** ✅ Done
- **Área:** Frontend
- **Iteración:** Sprint 2
- **Parent:** EPIC-02 (Identificación de Plantas)
- **Descripción:** Manejo y presentación de resultados de identificación

---

### 📝 Tasks del Sprint 2 - BACKEND

#### T-015: Integrar PlantNet API para Identificación (5pts)
- **ID:** 23
- **Estado:** ✅ Done
- **Área:** AI
- **Iteración:** Sprint 2
- **Parent:** US-003 (Identificar Especie de Planta)

**Descripción:**
Implementar identificación de plantas usando PlantNet API en lugar de entrenar modelo propio.

**Tareas:**
1. Registrarse en PlantNet y obtener API key
2. Crear servicio PlantNetService con métodos `identify_plant()` y `get_plant_info()`
3. Crear modelo PlantIdentification en DB (image_id, species, confidence, suggestions)
4. Implementar endpoints:
   - `POST /api/plants/identify`
   - `GET /api/plants/history`
   - `GET /api/plants/{plant_id}`
5. Tests de integración con PlantNet API
6. Documentación de uso

**Criterios de aceptación:**
- ✅ Usuario puede subir imagen y recibir identificación
- ✅ Sistema retorna top 3-5 especies con confidence score
- ✅ Resultados guardados en DB
- ✅ Rate limiting implementado
- ✅ Manejo de errores (API caída, imagen inválida)
- ✅ Tests con mock de PlantNet

**API PlantNet:**
- 71,238 especies soportadas
- 90-95% de precisión
- Plan Free: 500 requests/mes
- Documentación: https://my.plantnet.org/doc

**Tiempo estimado:** 2-3 días

---

#### T-013: Crear modelo de base de datos para Plantas (4pts)
- **ID:** 44
- **Estado:** ✅ Done
- **Tags:** backend, database, models

**Descripción:**
Crear el modelo de datos en la base de datos para almacenar la información de las plantas de los usuarios.

**Campos de la tabla 'plants':**
- id (Primary Key)
- user_id (Foreign Key a users)
- name (String)
- species (String)
- image_url (String, nullable)
- health_status (Enum: 'healthy', 'needs_attention')
- last_watered (DateTime)
- next_watering (DateTime)
- light_requirements (String)
- created_at (DateTime)
- updated_at (DateTime)

**Criterios de aceptación:**
- ✅ Modelo definido en app/db/models.py
- ✅ Migración de Alembic creada y probada
- ✅ Relación con tabla users establecida
- ✅ Índices creados para optimizar consultas (user_id, health_status)

---

#### T-014: Implementar endpoints API para gestión de plantas (8pts)
- **ID:** 45
- **Estado:** ✅ Done
- **Tags:** api, backend, endpoints

**Descripción:**
Desarrollar los endpoints REST API necesarios para el CRUD completo de plantas y obtención de estadísticas.

**Endpoints:**
- `GET /api/plants` - Listar todas las plantas del usuario autenticado
- `GET /api/plants/{id}` - Obtener detalles de una planta específica
- `POST /api/plants` - Crear una nueva planta
- `PUT /api/plants/{id}` - Actualizar información de una planta
- `DELETE /api/plants/{id}` - Eliminar una planta
- `GET /api/plants/stats` - Obtener estadísticas del jardín (total, saludables, necesitan riego)

**Criterios de aceptación:**
- ✅ Todos los endpoints implementados en app/api/
- ✅ Autenticación JWT requerida en todos los endpoints
- ✅ Validación de datos con Pydantic schemas
- ✅ Manejo de errores apropiado (404, 403, 400)
- ✅ Las plantas están filtradas por usuario autenticado
- ✅ Documentación OpenAPI/Swagger actualizada

---

#### T-015: Crear tests unitarios para endpoints de plantas (6pts)
- **ID:** 46
- **Estado:** ✅ Done
- **Tags:** backend, qa, testing

**Descripción:**
Desarrollar tests unitarios completos para todos los endpoints de la API de plantas.

**Tests:**
- Test para GET /api/plants (lista vacía, con datos, filtrado por usuario)
- Test para GET /api/plants/{id} (planta existente, no existente, sin permisos)
- Test para POST /api/plants (creación exitosa, datos inválidos)
- Test para PUT /api/plants/{id} (actualización exitosa, planta no existente)
- Test para DELETE /api/plants/{id} (eliminación exitosa, sin permisos)
- Test para GET /api/plants/stats (estadísticas correctas)
- Tests de autenticación (sin token, token inválido)

**Criterios de aceptación:**
- ✅ Cobertura de código > 80% para módulos de plantas
- ✅ Todos los tests pasan exitosamente
- ✅ Tests ubicados en tests/ siguiendo convención de nombres
- ✅ Se usan fixtures de pytest apropiadamente

---

#### T-022: Implementar soporte para múltiples imágenes y parámetro organ en identificación (8pts)
- **ID:** 54
- **Estado:** 🔄 To Do
- **Iteración:** Sprint 2
- **Creado:** 20 de Octubre, 2025

**Descripción:**
Ampliar la funcionalidad de identificación de plantas para permitir el envío de hasta 5 imágenes simultáneas en una sola petición, junto con el parámetro 'organ' para cada imagen que especifique la parte de la planta.

**Contexto de PlantNet API:**
Según la documentación oficial de PlantNet:
- Enviar de 1 a 5 imágenes de la misma planta en una sola petición
- Especificar el tipo de órgano (organ) para cada imagen: flower, leaf, fruit, bark, habit, other
- Mejora la precisión de identificación al proporcionar múltiples vistas de la planta
- Endpoint: POST /v2/identify con API key como query parameter

**Cambios Backend:**

1. **Actualizar Modelo de Datos (app/db/models.py)**
   - Modificar tabla 'imagenes' o crear relación para múltiples imágenes por identificación
   - Agregar campo 'organ' (Enum: flower, leaf, fruit, bark, habit, other)
   - Crear tabla 'identificaciones' que agrupe múltiples imágenes
   - Relaciones: Identificacion -> hasMany -> Imagenes

2. **Actualizar Schemas Pydantic (app/schemas/)**
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

3. **Actualizar PlantNet Service (app/services/plantnet_service.py)**
   - Modificar método identify_plant() para aceptar lista de imágenes
   - Construir request multipart/form-data con múltiples imágenes
   - Incluir parámetro 'organs' como array en el body

4. **Actualizar Endpoints API (app/api/identificacion.py)**
   - POST /api/identificacion/multiple - Nuevo endpoint para múltiples imágenes
   - Mantener POST /api/identificacion/single para retrocompatibilidad
   - Validar tipo de organ permitido
   - Guardar todas las imágenes asociadas a una identificación

5. **Migración de Base de Datos**
   - Crear migración Alembic para nuevos campos y tablas

**Cambios Frontend:**

1. **Actualizar Componente ImageUpload**
   - Permitir selección de hasta 5 imágenes
   - Preview múltiple con opción de eliminar individualmente
   - Dropdown o selector para cada imagen para elegir 'organ'
   - Opciones organ: Flor, Hoja, Fruto, Corteza, Hábito, Otro
   - UI clara mostrando contador (ej: "3/5 imágenes")

2. **Actualizar Servicios (lib/plant.service.ts)**
   ```typescript
   interface ImageWithOrgan {
     file: File;
     organ: 'flower' | 'leaf' | 'fruit' | 'bark' | 'habit' | 'other';
   }
   
   interface IdentifyMultipleRequest {
     images: ImageWithOrgan[];
     project?: string;
   }
   ```

3. **Actualizar Página de Identificación (app/identificar/page.tsx)**
   - Mostrar lista de imágenes con sus órganos seleccionados
   - Permitir reordenar imágenes (drag and drop)
   - Botón para agregar más imágenes (hasta límite de 5)
   - Validación: Al menos 1 imagen requerida

**Tipos de Órganos Soportados:**
- **flower** - Flor o inflorescencia
- **leaf** - Hoja
- **fruit** - Fruto o semilla
- **bark** - Corteza o tronco
- **habit** - Hábito o porte general de la planta
- **other** - Otra parte no especificada
- **auto** - Detección automática (por defecto)

**Tests Requeridos:**

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

**Criterios de aceptación:**
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

**Documentación de Referencia:**
- [PlantNet API - Getting Started](https://my.plantnet.org/doc/getting-started/introduction)
- [PlantNet API - Single-species identification](https://my.plantnet.org/doc/api/identify)

**Dependencias:**
- T-015: Integración PlantNet API (debe estar completada)
- T-004: API de subida de imágenes (debe estar completada)

**Tiempo estimado:** 2-3 días

---

## 📋 Tareas Pendientes (Backlog)

### T-016: Crear componente Badge UI (2pts)
- **ID:** 47
- **Estado:** 🔄 To Do
- **Tags:** components, frontend, ui

**Descripción:**
Implementar el componente Badge reutilizable necesario para mostrar el estado de salud de las plantas en el dashboard.

**Especificaciones:**
- Ubicación: components/ui/badge.tsx
- Variantes: default, destructive, outline, secondary
- Tamaños personalizables
- Soporte para className personalizado
- Basado en Tailwind CSS y clase variants (cn)

**Criterios de aceptación:**
- Componente Badge creado y exportado
- Soporta todas las variantes necesarias
- Es reutilizable en toda la aplicación
- Tipado con TypeScript correctamente
- Estilos consistentes con el sistema de diseño

---

### T-017: Implementar página del Dashboard (/dashboard) (10pts)
- **ID:** 48
- **Estado:** 🔄 To Do
- **Tags:** dashboard, frontend, ui

**Descripción:**
Crear la página principal del dashboard que muestra todas las plantas del usuario con su información y estadísticas generales.

**Funcionalidades:**
- Header con título 'My Garden' y botones de navegación
- Sección de estadísticas con 3 cards:
  - Total de plantas
  - Plantas que necesitan riego hoy
  - Plantas saludables
- Grid responsive de tarjetas de plantas
- Cada tarjeta muestra:
  - Imagen de la planta
  - Badge de estado de salud
  - Nombre y especie
  - Información de riego
  - Requisitos de luz
  - Botón 'View Details'
- Botón para agregar nueva planta

**Criterios de aceptación:**
- Página creada en app/dashboard/page.tsx
- Integración con API backend para obtener datos reales
- Diseño responsive (mobile, tablet, desktop)
- Loading states y error handling
- Navegación funcional a otras páginas
- Actualización automática de estadísticas

---

### T-018: Corregir centrado y hacer responsive la landing page
- **ID:** 53
- **Estado:** 🔄 To Do

**Descripción:**
La landing page actualmente no está correctamente centrada en monitores 1080p y no es responsive para dispositivos móviles.

**Problemas identificados:**
- Contenido descentrado en resolución 1920x1080
- Falta de diseño responsive para móviles
- Posibles problemas con el layout de Tailwind CSS

**Objetivos:**
- Centrar correctamente todos los elementos
- Implementar diseño responsive para:
  - Desktop (1920x1080 y superiores)
  - Tablet (768px - 1024px)
  - Mobile (320px - 767px)
- Asegurar que botones y elementos interactivos sean accesibles en móviles
- Verificar que imágenes y texto se adapten correctamente

**Criterios de aceptación:**
- ✅ La página está centrada en monitores 1080p
- ✅ Elementos visibles y usables en móviles (portrait y landscape)
- ✅ Botones tienen tamaño adecuado para touch (min 44x44px)
- ✅ Texto legible sin zoom en móviles
- ✅ Imágenes no se distorsionan
- ✅ No hay scroll horizontal innecesario

---

### T-019: Implementar redirección y protección de ruta para dashboard (3pts)
- **ID:** 50
- **Estado:** 🔄 To Do
- **Tags:** auth, frontend, routing

**Descripción:**
Configurar la protección de la ruta del dashboard para que solo usuarios autenticados puedan acceder, y redirigir después del login exitoso.

**Tareas:**
- Actualizar middleware.ts para proteger /dashboard
- Configurar redirección desde /login al dashboard después de autenticación exitosa
- Agregar redirección desde / (root) al dashboard si el usuario está autenticado
- Mantener /login como ruta pública
- Implementar redirección a /login si el usuario no está autenticado

**Criterios de aceptación:**
- Usuario no autenticado es redirigido a /login al intentar acceder /dashboard
- Usuario autenticado es redirigido a /dashboard desde /login
- Usuario autenticado ve /dashboard como página principal
- La protección funciona correctamente con el contexto de autenticación
- Las redirecciones preservan parámetros de URL si es necesario

---

### T-020: Agregar tests para componentes del Dashboard (5pts)
- **ID:** 51
- **Estado:** 🔄 To Do
- **Tags:** frontend, qa, testing

**Descripción:**
Crear tests unitarios y de integración para los componentes del dashboard usando Jest y React Testing Library.

**Tests a crear:**
- Test del componente Badge
  - Renderiza correctamente cada variante
  - Aplica clases CSS correctamente
- Test de la página Dashboard
  - Renderiza estadísticas correctamente
  - Muestra grid de plantas
  - Maneja estado de carga
  - Maneja estado de error
  - Maneja lista vacía de plantas
- Test de hooks de API
  - Realiza llamadas correctas al backend
  - Maneja respuestas exitosas y errores
  - Actualiza cache después de mutaciones

**Criterios de aceptación:**
- Tests creados en __tests__/dashboard/
- Cobertura > 70% para componentes del dashboard
- Todos los tests pasan exitosamente
- Se usan mocks apropiados para API calls
- Tests son mantenibles y legibles

---

### T-021: Actualizar documentación del proyecto con funcionalidad de Dashboard (3pts)
- **ID:** 52
- **Estado:** 🔄 To Do
- **Tags:** documentation

**Descripción:**
Actualizar la documentación del proyecto para incluir información sobre la nueva funcionalidad del dashboard de plantas.

**Documentos a actualizar:**
- README.md
  - Agregar capturas de pantalla del dashboard
  - Documentar nueva ruta /dashboard
  - Actualizar lista de características
- Documentación de API
  - Documentar endpoints de plantas
  - Incluir ejemplos de requests/responses
  - Documentar esquemas de datos
- Documentación de Frontend
  - Documentar estructura de componentes
  - Explicar hooks y servicios de API
  - Guía de uso del dashboard

**Criterios de aceptación:**
- README.md actualizado con nueva funcionalidad
- Documentación técnica completa y precisa
- Capturas de pantalla o GIFs del dashboard incluidos
- Guía de desarrollo para futuros cambios
- Documentación de API actualizada en Swagger/OpenAPI

---

## 📊 Estadísticas Generales

### Sprint 1
- **Total Tasks:** 12
- **Completadas:** 12 (100%)
- **Story Points:** ~70 pts
- **Backend Tasks:** 6
- **Frontend Tasks:** 6

### Sprint 2
- **Total Tasks:** 6
- **Completadas:** 5 (83%)
- **Pendientes:** 1 (T-022)
- **Story Points:** ~36 pts
- **Backend Tasks:** 4
- **Frontend Tasks:** 2

### Backlog
- **Total Tasks:** 6
- **Pendientes:** 6
- **Story Points:** ~26 pts

---

## 🎯 Épicas del Proyecto

1. **EPIC-01: Fundación de la Aplicación** ✅ Done
2. **EPIC-02: Identificación de Plantas (IA Core)** ✅ Done
3. **EPIC-03: Asistente Inteligente con LLM** 🔄 To Do
4. **EPIC-04: Detección de Enfermedades y Marketplace** 🔄 To Do

---

## 📝 Notas

- Todas las tareas del Sprint 1 y Sprint 2 están completadas
- El proyecto sigue metodología Agile con GitFlow
- Se mantiene cobertura de tests > 75% en backend y > 70% en frontend
- La arquitectura sigue patrón MVC con separación clara de responsabilidades
- Se utiliza FastAPI para backend y Next.js (React 18) para frontend
- Autenticación implementada con JWT (30 min token, 7 días refresh)
- Integración con PlantNet API para identificación de plantas

---

**Última actualización:** 19 de Octubre, 2025
