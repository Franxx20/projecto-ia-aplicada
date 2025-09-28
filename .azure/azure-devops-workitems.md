# 📊 Azure DevOps Work Items - Asistente Plantitas

Este archivo contiene la estructura de work items para importar en Azure DevOps.

## 🏗️ Estructura de Trabajo

### Jerarquía de Work Items
```
Epic
 ├── Feature
     ├── User Story
         ├── Task
         └── Bug (si aplica)
```

---

## 🎯 ÉPICAS (EPICS)

### Epic 1: Fundación de la Aplicación
```json
{
  "workItemType": "Epic",
  "title": "Fundación de la Aplicación",
  "description": "Establecer la base técnica y arquitectural del asistente de jardinería",
  "priority": 1,
  "businessValue": 100,
  "timeboxStart": "2025-09-29",
  "timeboxEnd": "2025-10-12",
  "effort": 42,
  "tags": "sprint1;foundation;mvp"
}
```

### Epic 2: Identificación de Plantas (IA Core)
```json
{
  "workItemType": "Epic", 
  "title": "Identificación de Plantas (IA Core)",
  "description": "Motor principal de IA para identificación de especies de plantas",
  "priority": 1,
  "businessValue": 100,
  "timeboxStart": "2025-10-13",
  "timeboxEnd": "2025-10-26", 
  "effort": 34,
  "tags": "sprint2;ai;mvp;core"
}
```

### Epic 3: Asistente Inteligente con LLM
```json
{
  "workItemType": "Epic",
  "title": "Asistente Inteligente con LLM", 
  "description": "Chat conversacional y sistema de consejos personalizados",
  "priority": 2,
  "businessValue": 80,
  "timeboxStart": "2025-10-27",
  "timeboxEnd": "2025-11-09",
  "effort": 29,
  "tags": "sprint3;llm;chat;advice"
}
```

### Epic 4: Detección de Enfermedades y Marketplace
```json
{
  "workItemType": "Epic",
  "title": "Detección de Enfermedades y Marketplace",
  "description": "Diagnóstico avanzado y integración con tiendas de jardinería",
  "priority": 2,
  "businessValue": 60,
  "timeboxStart": "2025-11-10", 
  "timeboxEnd": "2025-11-23",
  "effort": 34,
  "tags": "sprint4;diagnosis;marketplace;final"
}
```

---

## 🚀 FEATURES

### Sprint 1 Features

#### Feature 1.1: Sistema de Autenticación
```json
{
  "workItemType": "Feature",
  "title": "Sistema de Autenticación",
  "description": "Implementar registro, login y gestión de sesiones segura",
  "parentEpic": "Fundación de la Aplicación",
  "priority": 1,
  "businessValue": 40,
  "effort": 13,
  "acceptanceCriteria": [
    "Usuario puede registrarse con email/contraseña",
    "Usuario puede hacer login y logout",
    "Sesiones seguras con JWT tokens",
    "Validación de campos en frontend",
    "Rate limiting en endpoints de auth"
  ],
  "tags": "auth;security;backend;frontend"
}
```

#### Feature 1.2: Gestión de Imágenes
```json
{
  "workItemType": "Feature",
  "title": "Gestión de Imágenes",
  "description": "Sistema de subida y gestión de fotos de plantas",
  "parentEpic": "Fundación de la Aplicación",
  "priority": 1,
  "businessValue": 35,
  "effort": 8,
  "acceptanceCriteria": [
    "Upload de imágenes desde dispositivo",
    "Captura con cámara web/móvil",
    "Preview antes de enviar",
    "Validación de tamaño/formato",
    "Almacenamiento seguro en Azure Blob"
  ],
  "tags": "images;upload;blob-storage"
}
```

#### Feature 1.3: Infraestructura Base
```json
{
  "workItemType": "Feature", 
  "title": "Infraestructura Base",
  "description": "Setup de entorno de desarrollo y deployment",
  "parentEpic": "Fundación de la Aplicación",
  "priority": 1,
  "businessValue": 25,
  "effort": 21,
  "acceptanceCriteria": [
    "Docker Compose funcional",
    "Pipeline CI/CD en Azure DevOps", 
    "Entorno de desarrollo automatizado",
    "Monitoreo básico implementado",
    "Documentación de setup completa"
  ],
  "tags": "infrastructure;devops;docker;cicd"
}
```

### Sprint 2 Features

#### Feature 2.1: Motor de Identificación IA
```json
{
  "workItemType": "Feature",
  "title": "Motor de Identificación IA", 
  "description": "Sistema principal de identificación de plantas usando IA",
  "parentEpic": "Identificación de Plantas (IA Core)",
  "priority": 1,
  "businessValue": 50,
  "effort": 21,
  "acceptanceCriteria": [
    "Integración con PlantNet API funcional",
    "Precisión >70% en identificación",
    "Tiempo respuesta <10 segundos",
    "Manejo de errores robusto",
    "Cache de resultados implementado"
  ],
  "tags": "ai;plant-identification;api;core"
}
```

#### Feature 2.2: Gestión de Resultados
```json
{
  "workItemType": "Feature",
  "title": "Gestión de Resultados",
  "description": "Interfaz y gestión de resultados de identificación",
  "parentEpic": "Identificación de Plantas (IA Core)",
  "priority": 1, 
  "businessValue": 30,
  "effort": 13,
  "acceptanceCriteria": [
    "Mostrar resultados con nivel de confianza",
    "Galería de plantas identificadas",
    "Búsqueda en historial personal",
    "Edición/confirmación de identificaciones",
    "Información detallada por especie"
  ],
  "tags": "ui;results;gallery;search"
}
```

---

## 📱 USER STORIES

### Sprint 1 - Fundación

#### Authentication Stories

```json
{
  "workItemType": "User Story",
  "title": "Registro de Usuario",
  "id": "US-001",
  "description": "Como usuario nuevo, quiero registrarme con email y contraseña para acceder a la aplicación",
  "parentFeature": "Sistema de Autenticación",
  "priority": 1,
  "storyPoints": 5,
  "acceptanceCriteria": [
    "DADO un usuario nuevo",
    "CUANDO ingresa email válido y contraseña fuerte", 
    "ENTONCES se crea cuenta y recibe confirmación",
    "Y puede hacer login inmediatamente"
  ],
  "tags": "auth;registration;backend;frontend"
}
```

```json
{
  "workItemType": "User Story", 
  "title": "Login de Usuario",
  "id": "US-002",
  "description": "Como usuario registrado, quiero hacer login para acceder a mis plantas",
  "parentFeature": "Sistema de Autenticación",
  "priority": 1,
  "storyPoints": 5,
  "acceptanceCriteria": [
    "DADO un usuario registrado",
    "CUANDO ingresa credenciales correctas",
    "ENTONCES accede a dashboard personal",
    "Y la sesión permanece activa por 30 minutos"
  ],
  "tags": "auth;login;jwt;session"
}
```

```json
{
  "workItemType": "User Story",
  "title": "Seguridad JWT", 
  "id": "US-003",
  "description": "Como usuario, quiero que mi sesión sea segura con JWT tokens",
  "parentFeature": "Sistema de Autenticación",
  "priority": 1,
  "storyPoints": 3,
  "acceptanceCriteria": [
    "DADO un usuario logueado",
    "CUANDO realiza peticiones a la API",
    "ENTONCES el JWT es validado correctamente",
    "Y expira automáticamente tras inactividad"
  ],
  "tags": "security;jwt;token;validation"
}
```

#### Image Management Stories

```json
{
  "workItemType": "User Story",
  "title": "Subida de Fotos",
  "id": "US-004", 
  "description": "Como usuario, quiero subir fotos desde mi dispositivo",
  "parentFeature": "Gestión de Imágenes",
  "priority": 1,
  "storyPoints": 3,
  "acceptanceCriteria": [
    "DADO un usuario autenticado",
    "CUANDO selecciona una imagen desde dispositivo",
    "ENTONCES la imagen se sube al servidor",
    "Y recibe confirmación de éxito"
  ],
  "tags": "upload;images;blob-storage"
}
```

```json
{
  "workItemType": "User Story",
  "title": "Captura con Cámara",
  "id": "US-005",
  "description": "Como usuario, quiero tomar fotos con la cámara directamente",
  "parentFeature": "Gestión de Imágenes", 
  "priority": 2,
  "storyPoints": 3,
  "acceptanceCriteria": [
    "DADO un usuario en dispositivo móvil/web",
    "CUANDO activa la cámara",
    "ENTONCES puede tomar foto directamente",
    "Y la foto se procesa automáticamente"
  ],
  "tags": "camera;capture;mobile;web"
}
```

```json
{
  "workItemType": "User Story",
  "title": "Preview de Imagen",
  "id": "US-006",
  "description": "Como usuario, quiero ver un preview antes de subir la foto",
  "parentFeature": "Gestión de Imágenes",
  "priority": 2,
  "storyPoints": 2,
  "acceptanceCriteria": [
    "DADO una imagen seleccionada",
    "CUANDO el usuario la revisa",
    "ENTONCES ve preview con opción editar/confirmar",
    "Y puede cancelar o continuar"
  ],
  "tags": "ui;preview;validation;ux"
}
```

---

## 🔧 TASKS TÉCNICAS

### Sprint 1 Backend Tasks

```json
{
  "workItemType": "Task",
  "title": "Configurar Proyecto FastAPI",
  "id": "T-001",
  "parentUserStory": "US-001",
  "description": "Setup inicial de FastAPI con estructura MVC",
  "assignedTo": "Backend Developer",
  "effort": 5,
  "tags": "backend;setup;fastapi;mvc",
  "acceptanceCriteria": [
    "Proyecto FastAPI inicializado",
    "Estructura de carpetas según convenciones",
    "Configuración básica completada",
    "Health check endpoint funcional"
  ]
}
```

```json
{
  "workItemType": "Task", 
  "title": "Modelos de Usuario SQLAlchemy",
  "id": "T-002",
  "parentUserStory": "US-001",
  "description": "Implementar modelos de usuario con SQLAlchemy ORM",
  "assignedTo": "Backend Developer",
  "effort": 8,
  "tags": "backend;models;sqlalchemy;database",
  "acceptanceCriteria": [
    "Modelo User con campos requeridos",
    "Migraciones de Alembic configuradas", 
    "Relaciones de BD definidas",
    "Validaciones a nivel modelo"
  ]
}
```

```json
{
  "workItemType": "Task",
  "title": "Endpoints Autenticación JWT", 
  "id": "T-003",
  "parentUserStory": "US-002",
  "description": "Crear endpoints de autenticación con JWT tokens",
  "assignedTo": "Backend Developer", 
  "effort": 13,
  "tags": "backend;auth;jwt;api",
  "acceptanceCriteria": [
    "POST /auth/register implementado",
    "POST /auth/login implementado", 
    "Middleware JWT funcional",
    "Validaciones y rate limiting"
  ]
}
```

### Sprint 1 Frontend Tasks

```json
{
  "workItemType": "Task",
  "title": "Setup Angular 17 + Tailwind",
  "id": "T-005",
  "parentUserStory": "US-001",
  "description": "Configuración inicial de Angular con Tailwind CSS",
  "assignedTo": "Frontend Developer",
  "effort": 5,
  "tags": "frontend;angular;tailwind;setup",
  "acceptanceCriteria": [
    "Angular 17 configurado correctamente",
    "Tailwind CSS integrado", 
    "Estructura de componentes creada",
    "Routing básico implementado"
  ]
}
```

```json
{
  "workItemType": "Task",
  "title": "Componentes Login/Registro",
  "id": "T-006", 
  "parentUserStory": "US-001",
  "description": "Implementar componentes de autenticación con validaciones",
  "assignedTo": "Frontend Developer",
  "effort": 13,
  "tags": "frontend;components;auth;forms",
  "acceptanceCriteria": [
    "Componente LoginComponent creado",
    "Componente RegisterComponent creado",
    "Reactive Forms con validaciones",
    "UI responsiva con Tailwind"
  ]
}
```

### Sprint 2 IA/ML Tasks

```json
{
  "workItemType": "Task",
  "title": "Integración PlantNet API",
  "id": "T-012",
  "parentUserStory": "US-010", 
  "description": "Integrar y configurar PlantNet API para identificación",
  "assignedTo": "IA/ML Specialist",
  "effort": 13,
  "tags": "ai;plantnet;api;integration",
  "acceptanceCriteria": [
    "API PlantNet configurada y funcional",
    "Manejo de respuestas y errores",
    "Formato de datos normalizado",
    "Documentación de uso creada"
  ]
}
```

```json
{
  "workItemType": "Task",
  "title": "Servicio Procesamiento Imágenes",
  "id": "T-013",
  "parentUserStory": "US-010",
  "description": "Crear servicio para procesar imágenes antes de enviar a IA", 
  "assignedTo": "IA/ML Specialist",
  "effort": 8,
  "tags": "ai;image-processing;preprocessing",
  "acceptanceCriteria": [
    "Redimensionado automático de imágenes",
    "Mejora de calidad implementada", 
    "Validación de formato y tamaño",
    "Optimización para APIs de IA"
  ]
}
```

---

## 📋 TRABAJO DE CONFIGURACIÓN (SETUP TASKS)

### Azure DevOps Project Setup

```json
{
  "workItemType": "Task",
  "title": "Crear Proyecto Azure DevOps",
  "id": "SETUP-001",
  "description": "Configurar proyecto completo en Azure DevOps",
  "assignedTo": "Scrum Master",
  "effort": 5,
  "tags": "setup;azure-devops;project",
  "acceptanceCriteria": [
    "Proyecto 'Asistente Plantitas' creado",
    "Repositorio Git inicializado",
    "Permisos de equipo configurados",
    "Work item types personalizados"
  ]
}
```

```json
{
  "workItemType": "Task", 
  "title": "Configurar Iteraciones y Sprints",
  "id": "SETUP-002",
  "description": "Setup de sprints de 2 semanas y fechas del proyecto",
  "assignedTo": "Scrum Master",
  "effort": 3,
  "tags": "setup;sprints;iterations;planning",
  "acceptanceCriteria": [
    "4 sprints de 2 semanas configurados",
    "Fechas del proyecto establecidas",
    "Ceremonias agendadas en calendario",
    "Backlog inicial creado"
  ]
}
```

### Infrastructure Setup

```json
{
  "workItemType": "Task",
  "title": "Setup Azure Resources",
  "id": "SETUP-003", 
  "description": "Configurar recursos iniciales de Azure para el proyecto",
  "assignedTo": "DevOps Engineer",
  "effort": 8,
  "tags": "setup;azure;infrastructure;resources",
  "acceptanceCriteria": [
    "Resource Groups creados por ambiente", 
    "App Services básicos configurados",
    "PostgreSQL Flexible Server setup",
    "Key Vault para secretos creado"
  ]
}
```

```json
{
  "workItemType": "Task",
  "title": "Pipeline CI/CD Inicial", 
  "id": "SETUP-004",
  "description": "Configurar pipeline básico de CI/CD",
  "assignedTo": "DevOps Engineer",
  "effort": 8,
  "tags": "setup;cicd;pipeline;automation",
  "acceptanceCriteria": [
    "Pipeline de build configurado",
    "Deploy automático a development",
    "Tests automatizados integrados", 
    "Notificaciones de build setup"
  ]
}
```

---

## 📊 QUERIES Y REPORTES

### Queries Útiles para Azure DevOps

#### Burndown por Sprint
```sql
SELECT 
  [System.Id],
  [System.Title],
  [System.State], 
  [Microsoft.VSTS.Scheduling.StoryPoints],
  [System.IterationPath]
FROM WorkItems 
WHERE [System.IterationPath] UNDER 'Asistente Plantitas\\Sprint 1'
  AND [System.WorkItemType] = 'User Story'
```

#### Velocity del Equipo
```sql
SELECT 
  [System.IterationPath],
  SUM([Microsoft.VSTS.Scheduling.StoryPoints]) as TotalPoints
FROM WorkItems
WHERE [System.WorkItemType] IN ('User Story', 'Feature')
  AND [System.State] = 'Done'
GROUP BY [System.IterationPath]
ORDER BY [System.IterationPath]
```

#### Tasks por Developer
```sql
SELECT 
  [System.AssignedTo],
  COUNT(*) as TaskCount,
  SUM([Microsoft.VSTS.Scheduling.RemainingWork]) as RemainingHours
FROM WorkItems
WHERE [System.WorkItemType] = 'Task'
  AND [System.State] IN ('New', 'Active', 'In Progress')
GROUP BY [System.AssignedTo]
```

---

## 🎯 BOARD CONFIGURATION

### Kanban Board States

#### User Story States
1. **New** → Historia creada, pendiente refinamiento
2. **Ready** → Historia refinada, lista para sprint
3. **Active** → En desarrollo activo  
4. **In Review** → En code review/testing
5. **Done** → Completada y deployada

#### Task States  
1. **To Do** → Tarea identificada
2. **In Progress** → En desarrollo
3. **Testing** → En pruebas
4. **Done** → Completada

### Swim Lanes
- **Expedite** → Items críticos/blockers
- **Backend** → Tareas de API/servidor
- **Frontend** → Tareas de UI/UX  
- **IA/ML** → Tareas de inteligencia artificial
- **DevOps** → Tareas de infraestructura

### WIP Limits
- **Ready**: 8 items
- **Active**: 6 items  
- **In Review**: 4 items

---

## 🔔 ALERTAS Y AUTOMATIZACIÓN

### Azure DevOps Automation Rules

#### Auto-assign Tasks
```yaml
- name: "Auto-assign by Area"
  when: "WorkItemType = 'Task' AND AreaPath CHANGED"  
  then:
    - if: "AreaPath = 'Backend'"
      assign: "backend-developer@team.com"
    - if: "AreaPath = 'Frontend'"  
      assign: "frontend-developer@team.com"
    - if: "AreaPath = 'AI/ML'"
      assign: "ai-specialist@team.com"
```

#### Sprint Progress Alerts  
```yaml
- name: "Sprint Burndown Alert"
  when: "Sprint.DaysRemaining <= 3 AND Sprint.RemainingWork > 30%"
  then: 
    - notify: "scrum-master@team.com"
    - message: "Sprint at risk - {Sprint.RemainingWork}% work remaining"
```

#### Definition of Done Check
```yaml
- name: "DoD Validation"
  when: "UserStory.State CHANGED TO 'Done'"
  then:
    - require: "CodeReviewCompleted = True"
    - require: "TestCoverage >= 80%"  
    - require: "DocumentationUpdated = True"
```

---

**🚀 ¡Azure DevOps Project listo para comenzar el desarrollo! 🚀**

*Importa estos work items a tu proyecto de Azure DevOps y ajusta según las necesidades específicas de tu equipo.*