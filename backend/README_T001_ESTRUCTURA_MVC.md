# 🏗️ T-001: Estructura MVC - Asistente Plantitas Backend

## 📋 Información de la Tarea

**ID**: T-001  
**Sprint**: Sprint 1 (29 Sep - 12 Oct 2025)  
**Story Points**: 5 pts  
**Estado**: ✅ Completado  
**Tiempo estimado**: 4-8 horas  

## 🎯 Objetivo

Establecer la estructura base del proyecto FastAPI siguiendo el patrón arquitectónico MVC (Model-View-Controller) con separación clara de responsabilidades.

## 📁 Estructura de Carpetas Creada

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # Aplicación principal FastAPI
│   │
│   ├── api/                       # 🔌 Rutas y Endpoints (Controller)
│   │   └── __init__.py
│   │
│   ├── core/                      # ⚙️ Configuración y componentes centrales
│   │   ├── __init__.py
│   │   └── config.py              # Gestión de configuración con Pydantic
│   │
│   ├── db/                        # 💾 Modelos de Base de Datos (Model)
│   │   └── __init__.py
│   │
│   ├── schemas/                   # 📝 Modelos de Validación (Pydantic)
│   │   └── __init__.py
│   │
│   ├── services/                  # 🛠️ Lógica de Negocio
│   │   └── __init__.py
│   │
│   └── utils/                     # 🔧 Utilidades y Helpers
│       └── __init__.py
│
├── tests/                         # 🧪 Tests
│   ├── test_main.py
│   └── test_t001_estructura_mvc.py
│
├── .env                           # Variables de entorno (local)
├── .env.example                   # Plantilla de variables de entorno
├── requirements.txt               # Dependencias Python
└── pytest.ini                     # Configuración de pytest
```

## 📦 Descripción de Módulos

### `/api` - Endpoints REST (Controller)
Contiene todos los endpoints REST de la aplicación organizados por recursos.

**Estructura futura:**
```
/api
├── __init__.py
├── endpoints/
│   ├── auth.py          # Endpoints de autenticación
│   ├── usuarios.py      # Endpoints de usuarios
│   ├── plantas.py       # Endpoints de plantas
│   └── imagenes.py      # Endpoints de imágenes
├── dependencies.py      # Dependencias compartidas
└── router.py            # Router principal
```

### `/core` - Configuración Central
Componentes centrales y configuración de la aplicación.

**Archivos:**
- `config.py`: Gestión centralizada de configuración usando Pydantic Settings

**Características:**
- ✅ Patrón Singleton para configuración
- ✅ Soporte para variables de entorno
- ✅ Validación automática con Pydantic
- ✅ Valores por defecto sensatos

### `/db` - Modelos de Base de Datos (Model)
Modelos SQLAlchemy y configuración de base de datos.

**Estructura futura:**
```
/db
├── __init__.py
├── base.py              # Clase base para modelos
├── session.py           # Configuración de sesiones
└── models/
    ├── usuario.py       # Modelo de usuario
    ├── planta.py        # Modelo de planta
    └── imagen.py        # Modelo de imagen
```

### `/schemas` - Validación con Pydantic
Schemas para validación de entrada/salida de datos.

**Estructura futura:**
```
/schemas
├── __init__.py
├── request/             # Schemas para requests
│   ├── usuario.py
│   └── planta.py
└── response/            # Schemas para responses
    ├── usuario.py
    └── planta.py
```

### `/services` - Lógica de Negocio
Capa de servicios con la lógica de negocio separada de los endpoints.

**Estructura futura:**
```
/services
├── __init__.py
├── auth_service.py      # Lógica de autenticación
├── user_service.py      # Lógica de usuarios
├── plant_service.py     # Lógica de plantas
└── image_service.py     # Lógica de imágenes
```

### `/utils` - Utilidades
Funciones auxiliares y utilidades comunes.

**Estructura futura:**
```
/utils
├── __init__.py
├── security.py          # Hashing, tokens, etc.
├── validators.py        # Validadores personalizados
├── formatters.py        # Formateadores de datos
└── logger.py            # Configuración de logging
```

## ⚙️ Configuración

### Variables de Entorno

Todas las configuraciones se gestionan mediante variables de entorno. 

**Archivo `.env` (crear basándose en `.env.example`):**

```bash
# Aplicación
NOMBRE_APP="Asistente Plantitas - Backend API"
VERSION="0.1.0"
DEBUG=true
ENTORNO="desarrollo"

# Base de Datos
URL_BASE_DATOS="sqlite:///./plantitas_dev.db"

# Seguridad
JWT_SECRET_KEY="CHANGE_THIS_IN_PRODUCTION"
JWT_ALGORITHM="HS256"
JWT_EXPIRACION_MINUTOS=30

# CORS
ORIGENES_CORS='["http://localhost:4200","http://localhost:3000"]'

# Servidor
HOST="0.0.0.0"
PUERTO=8000
```

### Uso de Configuración

```python
from app.core.config import obtener_configuracion

config = obtener_configuracion()
print(config.nombre_app)        # "Asistente Plantitas - Backend API"
print(config.url_base_datos)   # "sqlite:///./plantitas_dev.db"
print(config.origenes_cors)    # ["http://localhost:4200", ...]
```

## 🚀 Endpoints Disponibles

### Endpoints del Sistema

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/` | GET | Información de bienvenida |
| `/salud` | GET | Health check del servicio |
| `/info` | GET | Información del sistema |
| `/metricas` | GET | Métricas básicas |
| `/docs` | GET | Documentación Swagger UI |
| `/redoc` | GET | Documentación ReDoc |
| `/openapi.json` | GET | Schema OpenAPI |

### Ejemplo de Health Check Response

```json
{
  "estado": "saludable",
  "servicio": "asistente-plantitas-api",
  "version": "0.1.0",
  "entorno": "desarrollo",
  "timestamp": "2025-10-05T12:00:00",
  "componentes": {
    "api": {
      "estado": "operacional",
      "mensaje": "API REST funcionando correctamente"
    },
    "base_datos": {
      "estado": "pendiente",
      "mensaje": "Configuración pendiente (T-002)"
    },
    "almacenamiento": {
      "estado": "operacional",
      "mensaje": "Directorio uploads: ./uploads"
    }
  }
}
```

## 🧪 Tests

### Ejecutar Tests

```bash
# Todos los tests
pytest

# Solo tests de T-001
pytest tests/test_t001_estructura_mvc.py

# Con cobertura
pytest --cov=app --cov-report=html

# Modo verbose
pytest -v
```

### Cobertura Alcanzada

- **31 tests** ejecutados
- **84.16%** de cobertura (requisito: 75%)
- **100%** de tests pasando ✅

### Tests Implementados

1. **Estructura de Carpetas** (8 tests)
   - Verificación de existencia de todas las carpetas MVC
   - Verificación de archivos `__init__.py`

2. **Configuración** (5 tests)
   - Importación correcta
   - Atributos requeridos
   - Patrón Singleton
   - Valores por defecto

3. **Aplicación FastAPI** (3 tests)
   - Creación de aplicación
   - Configuración correcta
   - Middleware CORS

4. **Endpoints** (9 tests)
   - Respuestas 200 OK
   - Estructura de respuestas
   - Health check
   - CORS headers

5. **Documentación** (2 tests)
   - Swagger UI disponible
   - OpenAPI schema

6. **Archivos de Configuración** (3 tests)
   - `.env.example`
   - `requirements.txt`
   - `pytest.ini`

## ✅ Criterios de Aceptación (T-001)

- [x] **Estructura de carpetas MVC completa**
  - `/api` - Endpoints REST
  - `/core` - Configuración central
  - `/db` - Modelos de base de datos
  - `/schemas` - Validación Pydantic
  - `/services` - Lógica de negocio
  - `/utils` - Utilidades

- [x] **`main.py` configurado**
  - FastAPI con metadata correcta
  - CORS configurado
  - Endpoints básicos funcionando
  - Event handlers (startup/shutdown)

- [x] **Configuración con `.env`**
  - `config.py` con Pydantic Settings
  - Soporte para variables de entorno
  - `.env.example` documentado
  - Patrón Singleton implementado

- [x] **Health check endpoint**
  - Endpoint `/salud` funcional
  - Verificación de componentes
  - Respuestas estructuradas

- [x] **Tests con >75% cobertura**
  - 31 tests implementados
  - 84.16% de cobertura alcanzada
  - Todos los tests pasando

- [x] **Documentación**
  - README completo
  - Comentarios en código
  - Docstrings en funciones

## 🔄 Próximos Pasos

### T-002: Implementar modelos de usuario con SQLAlchemy (8pts)
- Crear modelos en `/db/models/`
- Configurar sesiones de base de datos
- Implementar migraciones con Alembic

### T-003: Crear endpoints de autenticación JWT (13pts)
- Implementar endpoints en `/api/endpoints/auth.py`
- Servicios de autenticación en `/services/auth_service.py`
- Schemas de request/response en `/schemas/`

### T-005: Setup Angular 17 con Tailwind CSS (5pts) [Frontend]
- Configurar proyecto Angular
- Instalar y configurar Tailwind
- Crear estructura de carpetas frontend

## 📚 Referencias

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Azure DevOps - Sprint 1](https://dev.azure.com/ia-grupo-5/proyecto-plantitas)

## 👥 Equipo

- **Backend Developers**: Configuración FastAPI y estructura MVC
- **DevOps**: Configuración de tests y CI/CD
- **Scrum Master**: Validación de criterios de aceptación

## 📝 Notas

- La estructura está preparada para escalar en sprints futuros
- TODOs documentados para implementaciones pendientes
- Código sigue convenciones Python (snake_case, PEP 8)
- Comentarios y docstrings en español según directivas del proyecto

---

**Status**: ✅ T-001 Completado exitosamente  
**Fecha**: 5 de octubre de 2025  
**Sprint**: Sprint 1 - Fundación de la Aplicación
