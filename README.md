# 🤖 Proyecto IA Aplicada

## 📖 Descripción

Proyecto de Inteligencia Artificial Aplicada desarrollado con arquitectura moderna y escalable:

- **Backend**: FastAPI + SQLAlchemy + PostgreSQL
- **Frontend**: Next.js 15 + React 19 + TypeScript + Tailwind CSS
- **IA**: Claude Sonnet 4
- **Containerización**: Docker + Docker Compose
- **Base de Datos**: PostgreSQL

## 🏗️ Arquitectura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│                 │    │                 │    │                 │
│   Next.js 15    │────│   FastAPI API   │────│   PostgreSQL    │
│   (Frontend)    │    │   (Backend)     │    │   (Database)    │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                        │                        │
        │                        │                        │
    Port 4200                Port 8000                Port 5432
```

## 📁 Estructura del Proyecto

```
projecto-ia-aplicada/
├── backend/                 # API FastAPI
│   ├── app/
│   │   ├── api/            # Rutas y endpoints
│   │   ├── core/           # Configuración, seguridad
│   │   ├── db/             # Modelos de base de datos
│   │   ├── schemas/        # Pydantic models
│   │   ├── services/       # Lógica de negocio
│   │   └── utils/          # Utilidades
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .dockerignore
├── frontend/                # Aplicación Next.js
│   ├── app/
│   │   ├── api/            # API Routes de Next.js
│   │   ├── layout.tsx      # Layout principal
│   │   ├── page.tsx        # Página principal
│   │   └── globals.css     # Estilos globales
│   ├── components/
│   │   ├── ui/             # Componentes UI (shadcn)
│   │   └── ...             # Componentes personalizados
│   ├── lib/                # Utilidades y helpers
│   ├── models/             # Interfaces TypeScript
│   ├── public/             # Recursos estáticos
│   ├── Dockerfile          # Dockerfile producción
│   ├── Dockerfile.dev      # Dockerfile desarrollo
│   ├── next.config.ts      # Configuración Next.js
│   ├── tailwind.config.ts  # Configuración Tailwind
│   └── package.json        # Dependencias NPM
├── tests/                   # Tests del proyecto
│   ├── backend/            # Tests Python
│   ├── frontend/           # Tests Next.js/React
│   └── e2e/               # Tests end-to-end
├── data/                   # Datos persistentes
├── logs/                   # Logs de aplicación
├── uploads/                # Archivos subidos
├── backups/                # Backups de BD
├── docker-compose.yml      # Producción
├── docker-compose.dev.yml  # Desarrollo
├── .env.example           # Template de variables
├── manage.sh              # Script gestión (Linux/Mac)
├── manage.bat             # Script gestión (Windows)
└── README.md              # Este archivo
```

## 🚀 Instalación y Configuración

### Prerrequisitos

- **Docker** (versión 20.10 o superior)
- **Docker Compose** (versión 2.0 o superior)
- **Git**

### 📋 Pasos de Instalación

#### 1. Clonar el Repositorio

```bash
git clone <url-del-repositorio>
cd projecto-ia-aplicada
```

#### 2. Configurar Variables de Entorno

**⚠️ IMPORTANTE: Configuración Unificada**

El proyecto ahora usa un **ÚNICO archivo `.env`** en la raíz para toda la configuración (backend, frontend, Docker, APIs externas, etc.). Ya no se necesitan archivos `.env` separados en `backend/` o `frontend/`.

```bash
# Copiar el template de configuración
cp .env.example .env

# Editar las variables según tu entorno
# Windows: notepad .env
# Linux/Mac: nano .env
```

**Variables importantes a configurar:**

```env
# ==================== Seguridad ====================
# CAMBIAR ESTAS CONTRASEÑAS EN PRODUCCIÓN
POSTGRES_PASSWORD=tu_password_seguro
SECRET_KEY=tu_clave_secreta_muy_larga_y_segura_min_32_chars
JWT_SECRET_KEY=tu_jwt_secret_key_diferente
REDIS_PASSWORD=tu_redis_password

# ==================== Puertos ====================
# Ajustar si están ocupados en tu sistema
FRONTEND_PORT=4200
BACKEND_PORT=8000
POSTGRES_PORT=5432
ADMINER_PORT=8080

# ==================== APIs de IA ====================
# Obtener en: https://my.plantnet.org/
PLANTNET_API_KEY=tu_plantnet_api_key

# Obtener en: https://makersuite.google.com/app/apikey
GEMINI_API_KEY=tu_gemini_api_key

# Opcional - Otras APIs de IA
CLAUDE_API_KEY=tu_claude_api_key
AZURE_OPENAI_API_KEY=tu_azure_openai_key

# ==================== Azure Storage ====================
# Para producción: usar credenciales reales de Azure
AZURE_STORAGE_CONNECTION_STRING=tu_connection_string
AZURE_STORAGE_CONTAINER_NAME=plantitas-imagenes

# Para desarrollo: usar emulador Azurite
AZURE_STORAGE_USE_EMULATOR=true

# ==================== Rutas de Volúmenes ====================
POSTGRES_DATA_PATH=./data/postgres
BACKEND_CODE_PATH=./backend
FRONTEND_CODE_PATH=./frontend
AZURITE_DATA_PATH=./data/azurite
```

**📌 Notas sobre el archivo `.env`:**
- ✅ Un solo archivo `.env` en la raíz del proyecto
- ✅ Backend y frontend leen del mismo archivo
- ✅ Docker Compose también usa el mismo archivo
- ✅ El archivo está en `.gitignore` - nunca se sube a Git
- ✅ Usa `.env.example` como referencia completa

#### 3. Configuración Inicial

**Windows:**
```cmd
# Configuración automática
manage.bat setup
```

**Linux/Mac:**
```bash
# Dar permisos de ejecución
chmod +x manage.sh

# Configuración automática
./manage.sh setup
```

## 🎯 Comandos de Gestión

### Desarrollo (con hot reload)

**Windows:**
```cmd
manage.bat dev
```

**Linux/Mac:**
```bash
./manage.sh dev
```

**URLs de desarrollo:**
- Frontend (Next.js): http://localhost:4200
- Backend (FastAPI): http://localhost:8000
- API Docs (Swagger): http://localhost:8000/docs
- API Docs (ReDoc): http://localhost:8000/redoc

### Producción

**Windows:**
```cmd
manage.bat prod
```

**Linux/Mac:**
```bash
./manage.sh prod
```

**URLs de producción:**
- Frontend (Next.js): http://localhost:4200
- Backend (FastAPI): http://localhost:8000
- Admin BD (Adminer): http://localhost:8080

### Otros Comandos Útiles

```bash
# Ver logs
manage.bat logs                # Todos los servicios
manage.bat logs backend        # Solo backend
manage.bat logs frontend       # Solo frontend

# Acceder al shell de contenedores
manage.bat shell backend       # Shell del backend
manage.bat shell frontend      # Shell del frontend
manage.bat shell db           # PostgreSQL CLI

# Gestión de base de datos
manage.bat db-backup          # Crear backup
manage.bat db-restore backup.sql  # Restaurar backup

# Detener servicios
manage.bat stop

# Reiniciar servicios
manage.bat restart

# Limpiar todo (CUIDADO)
manage.bat clean

# Rebuild de imágenes
manage.bat build

# Ejecutar tests
manage.bat test
```

## 🛠️ Desarrollo

### 🎨 Frontend con Next.js 15

Este proyecto utiliza **Next.js 15** con las últimas características:

#### Características Principales
- **App Router**: Enrutamiento moderno basado en carpetas
- **React Server Components**: Componentes del servidor por defecto
- **Streaming**: Renderizado progresivo con Suspense
- **TypeScript**: Tipado estricto en todo el proyecto
- **Tailwind CSS v3**: Estilos utility-first
- **shadcn/ui**: Componentes UI accesibles y customizables

#### Comandos de Desarrollo

```bash
# Desarrollo local (fuera de Docker)
cd frontend
npm install
npm run dev

# Build de producción
npm run build

# Iniciar servidor de producción
npm start

# Linting
npm run lint

# Tests
npm test
```

#### Variables de Entorno

**⚠️ NOTA: El frontend ahora usa el archivo `.env` unificado en la raíz del proyecto.**

Ya no es necesario crear un archivo `.env.local` en el directorio `frontend/`. Todas las variables se configuran en el archivo `.env` de la raíz:

```env
# Estas variables se leen del archivo .env en la raíz del proyecto
NEXT_PUBLIC_API_URL=http://localhost:8000
INTERNAL_API_URL=http://backend:8000  # Para llamadas server-side dentro de Docker
```

Para desarrollo local fuera de Docker, solo necesitas ajustar `NEXT_PUBLIC_API_URL` en el archivo `.env` de la raíz.

#### Agregar Componentes shadcn/ui

```bash
# Instalar CLI de shadcn
npx shadcn@latest init

# Agregar componentes individuales
npx shadcn@latest add button
npx shadcn@latest add card
npx shadcn@latest add input
npx shadcn@latest add form

# Ver todos los componentes disponibles
npx shadcn@latest add
```

#### Estructura de Rutas

```
app/
├── page.tsx              # → /
├── layout.tsx            # Layout global
├── login/
│   └── page.tsx          # → /login
├── dashboard/
│   ├── page.tsx          # → /dashboard
│   └── layout.tsx        # Layout del dashboard
└── api/
    └── health/
        └── route.ts      # → /api/health (API Route)
```

#### Docker con Next.js

El proyecto incluye dos Dockerfiles:

- **`Dockerfile`**: Build optimizado para producción con output standalone
- **`Dockerfile.dev`**: Desarrollo con hot reload y volume mounting

```bash
# Build de producción
docker build -t frontend-prod -f Dockerfile .

# Build de desarrollo
docker build -t frontend-dev -f Dockerfile.dev .

# Ejecutar contenedor de desarrollo
docker run -p 4200:4200 -v $(pwd):/app frontend-dev
```

### Estructura de Desarrollo

#### Backend (FastAPI)

```bash
backend/
├── app/
│   ├── main.py           # Punto de entrada
│   ├── api/              # Endpoints REST
│   ├── core/
│   │   ├── config.py     # Configuración
│   │   ├── security.py   # Autenticación JWT
│   │   └── database.py   # Conexión BD
│   ├── db/
│   │   ├── models.py     # Modelos SQLAlchemy
│   │   └── init_db.py    # Inicialización
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # Lógica de negocio
│   └── utils/            # Utilidades
├── tests/                # Tests pytest
└── requirements.txt      # Dependencias
```

#### Frontend (Next.js 15)

```bash
frontend/
├── app/
│   ├── layout.tsx        # Layout principal con metadata
│   ├── page.tsx          # Página de inicio (/)
│   ├── globals.css       # Estilos globales Tailwind
│   └── api/
│       └── health/
│           └── route.ts  # Health check endpoint
├── components/
│   ├── ui/               # Componentes shadcn/ui
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   └── ...
│   └── ...               # Componentes personalizados
├── lib/
│   └── utils.ts          # Utilidades (cn, etc.)
├── models/               # Interfaces TypeScript
├── public/               # Assets estáticos
├── next.config.ts        # Configuración Next.js
├── tailwind.config.ts    # Configuración Tailwind
└── package.json          # Dependencias
```

### Flujo de Desarrollo

1. **Levantar entorno de desarrollo**: `manage.bat dev`
2. **Hacer cambios** en el código (hot reload automático)
3. **Ejecutar tests**: `manage.bat test`
4. **Verificar logs**: `manage.bat logs [servicio]`
5. **Commit y push**

### APIs Disponibles

#### Documentación Interactiva
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

#### Endpoints Principales
```
GET  /                    # Health check
GET  /api/v1/users        # Listar usuarios
POST /api/v1/users        # Crear usuario
GET  /api/v1/auth/login   # Login
POST /api/v1/auth/token   # Obtener token
```

## 📦 Azure Blob Storage

### Configuración de Almacenamiento de Imágenes

Este proyecto utiliza **Azure Blob Storage** para gestionar las imágenes de plantas. Para desarrollo local, usamos **Azurite**, el emulador oficial de Azure Storage.

#### ¿Qué es Azurite?

Azurite es un emulador de Azure Storage que proporciona:
- ✅ **API 100% compatible** con Azure Storage
- ✅ **Desarrollo local gratuito** sin costos de Azure
- ✅ **Latencia mínima** (<1ms)
- ✅ **Fácil transición** a producción

#### Servicios Disponibles

| Servicio | Puerto | Descripción |
|----------|--------|-------------|
| Blob | 10000 | Almacenamiento de archivos (imágenes) |
| Queue | 10001 | Colas de mensajes |
| Table | 10002 | Almacenamiento NoSQL |

#### Configuración Automática

Azurite ya está configurado en `docker-compose.dev.yml` y se inicia automáticamente con:

```bash
manage.bat dev
```

#### Variables de Entorno

**⚠️ Configurar en el archivo `.env` de la raíz del proyecto:**

```env
# Azure Storage (Azurite para desarrollo)
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint=http://azurite:10000/devstoreaccount1;
AZURE_STORAGE_CONTAINER_NAME=plantitas-imagenes
AZURE_STORAGE_USE_EMULATOR=true
```

Estas variables ya están pre-configuradas en `.env.example`. Para producción, cambia a las credenciales reales de Azure Storage y establece `AZURE_STORAGE_USE_EMULATOR=false`.

#### Probar Conectividad

```bash
# Test de conexión a Azure Storage/Azurite
docker-compose -f docker-compose.dev.yml exec backend python test_azure_storage.py

# Test completo de API de imágenes
docker-compose -f docker-compose.dev.yml exec backend python test_api_imagenes.py
```

#### API de Imágenes

```bash
# Endpoints disponibles
POST   /api/imagenes/subir       # Subir imagen
GET    /api/imagenes/            # Listar imágenes
GET    /api/imagenes/{id}        # Obtener imagen
PATCH  /api/imagenes/{id}        # Actualizar descripción
DELETE /api/imagenes/{id}        # Eliminar imagen
```

#### Configuración para Producción

Para usar Azure Storage real en producción:

1. Crear Storage Account en Azure
2. Actualizar el connection string en `.env`:
```env
AZURE_STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=tuaccount;..."
AZURE_STORAGE_USE_EMULATOR="false"
```

📖 **Documentación completa**: Ver [AZURE_STORAGE_SETUP.md](./AZURE_STORAGE_SETUP.md)

---

## 🧪 Testing

### Tests del Backend

```bash
# Ejecutar todos los tests
manage.bat shell backend
pytest tests/ -v

# Tests con cobertura
pytest tests/ --cov=app --cov-report=html

# Tests específicos
pytest tests/test_auth.py -v

# Tests de Azure Storage
pytest tests/test_t004* -v
```

### Tests del Frontend

```bash
# Unit tests con Vitest
manage.bat shell frontend
npm test

# Tests en modo watch
npm run test:watch

# Tests con coverage
npm run test:coverage

# Build de producción
npm run build

# Desarrollo local
npm run dev
```

### Tests End-to-End

```bash
# Con Cypress
npm run cypress:open
npm run cypress:run
```

## 📊 Monitoreo y Logs

### Ver Logs en Tiempo Real

```bash
# Todos los servicios
manage.bat logs

# Servicio específico
manage.bat logs backend
manage.bat logs frontend
manage.bat logs db
```

### Health Checks

- **Backend**: http://localhost:8000/health
- **Frontend**: http://localhost/
- **Base de datos**: Automático en Docker

### Métricas

Los contenedores incluyen health checks automáticos:
- Verificación cada 30 segundos
- Timeout de 10 segundos
- 3 reintentos antes de marcar como unhealthy

## 🔧 Troubleshooting

### Problemas Comunes

#### 1. Puerto Ocupado
```bash
# Error: Port already in use
# Solución: Cambiar puertos en .env
FRONTEND_PORT=8080
BACKEND_PORT=8001
```

#### 2. Problemas de Permisos
```bash
# Windows: Ejecutar como Administrador
# Linux/Mac: Usar sudo si es necesario
sudo ./manage.sh setup
```

#### 3. Contenedores No Inician
```bash
# Verificar logs
manage.bat logs

# Limpiar y rebuild
manage.bat clean
manage.bat setup
```

#### 4. Base de Datos No Conecta
```bash
# Verificar estado de PostgreSQL
manage.bat shell db

# En el contenedor:
psql -U postgres -l
```

#### 5. Frontend No Carga
```bash
# Verificar build de Next.js
manage.bat shell frontend
npm run build

# Verificar logs del contenedor
manage.bat logs frontend

# Verificar variables de entorno en la raíz del proyecto
cat .env  # Linux/Mac
type .env # Windows

# Verificar que NEXT_PUBLIC_API_URL esté correctamente configurado
grep NEXT_PUBLIC_API_URL .env  # Linux/Mac
findstr NEXT_PUBLIC_API_URL .env  # Windows
```

### Comandos de Diagnóstico

```bash
# Estado de contenedores
docker-compose ps

# Uso de recursos
docker stats

# Inspeccionar contenedor
docker inspect projecto-ia_backend

# Logs detallados
docker-compose logs --tail=100 backend
```

### Reinicio Completo

```bash
# Detener todo
manage.bat stop

# Limpiar contenedores
docker-compose down -v

# Rebuild completo
manage.bat setup
manage.bat prod
```

## 🚀 Deployment en Producción

### Preparación para Producción

1. **Configurar variables de entorno de producción**:
```env
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=clave_super_segura_de_32_caracteres_minimo
POSTGRES_PASSWORD=password_muy_seguro
```

2. **Configurar HTTPS**:
```env
SSL_CERT_PATH=./certs/cert.pem
SSL_KEY_PATH=./certs/key.pem
```

3. **Configurar CORS para dominio de producción**:
```env
CORS_ORIGINS=https://tu-dominio.com,https://www.tu-dominio.com
```

### Deployment con Docker

```bash
# Producción local
manage.bat prod

# Producción con SSL
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Deployment en Cloud (Azure/AWS/GCP)

#### Usando Azure Container Instances
```bash
# Build y push a registry
docker-compose build
docker tag projecto-ia_backend your-registry.azurecr.io/backend:latest
docker push your-registry.azurecr.io/backend:latest

# Deploy usando Azure CLI
az container create \
  --resource-group myResourceGroup \
  --name projecto-ia \
  --image your-registry.azurecr.io/backend:latest
```

#### Variables de Entorno en Cloud
```bash
# Azure Key Vault para secretos
SECRET_KEY=@Microsoft.KeyVault(SecretUri=https://vault.vault.azure.net/secrets/secret-key/)
POSTGRES_PASSWORD=@Microsoft.KeyVault(SecretUri=https://vault.vault.azure.net/secrets/db-password/)
```

## 📚 Documentación de APIs

### Autenticación

```typescript
// Login
POST /api/v1/auth/login
{
  "email": "usuario@example.com",
  "password": "mi_password"
}

// Response
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Endpoints Principales

```typescript
// Usuarios
GET    /api/v1/users           # Listar usuarios
POST   /api/v1/users           # Crear usuario
GET    /api/v1/users/{id}      # Obtener usuario
PUT    /api/v1/users/{id}      # Actualizar usuario
DELETE /api/v1/users/{id}      # Eliminar usuario

// IA
POST   /api/v1/ia/chat         # Chat con IA
POST   /api/v1/ia/analyze      # Analizar datos
GET    /api/v1/ia/models       # Modelos disponibles
```

## 🔧 Troubleshooting

### Primera Instalación

Si es tu primera vez instalando el proyecto, sigue estos pasos:

#### 1. Verificar Prerequisitos

```bash
# Linux/Mac
bash check_prerequisites.sh

# Windows
check_prerequisites.bat
```

Este script verificará:
- ✅ Docker y Docker Compose instalados
- ✅ Puertos 4200, 8000, 5432, 8080 disponibles
- ✅ Permisos de escritura en directorios
- ✅ Espacio en disco suficiente (mínimo 2GB)
- ✅ Archivo .env unificado configurado en la raíz del proyecto

#### 2. Ejecutar Setup

```bash
# Linux/Mac
./manage.sh setup

# Windows
manage.bat setup
```

#### 3. Validar Instalación

```bash
# Linux/Mac
bash validate_installation.sh
```

Este script verificará:
- ✅ Contenedores funcionando
- ✅ Endpoints respondiendo
- ✅ Base de datos accesible
- ✅ Migraciones aplicadas

---

### Problemas Comunes

#### ❌ Error: "Docker no está funcionando"

**Síntoma**: El comando `docker ps` falla o muestra error.

**Solución**:
```bash
# Windows
- Abre Docker Desktop desde el menú inicio
- Espera a que muestre "Docker Desktop is running"

# Linux
sudo systemctl start docker

# Mac
- Abre Docker Desktop desde Applications
```

---

#### ❌ Error: "Puerto ya en uso"

**Síntoma**: Mensaje como `Bind for 0.0.0.0:4200 failed: port is already allocated`

**Solución**:

1. **Identificar qué proceso usa el puerto**:
```bash
# Linux/Mac
lsof -i :4200
lsof -i :8000
lsof -i :5432

# Windows
netstat -ano | findstr :4200
netstat -ano | findstr :8000
netstat -ano | findstr :5432
```

2. **Detener el proceso** o **cambiar puertos en `.env`**:
```bash
# Editar .env
FRONTEND_PORT=8080
BACKEND_PORT=8001
POSTGRES_PORT=5433
```

3. **Reiniciar servicios**:
```bash
./manage.sh restart
```

---

#### ❌ Error: "Base de datos no está lista"

**Síntoma**: Migraciones fallan con error de conexión a PostgreSQL.

**Solución**:

1. **Ver logs de PostgreSQL**:
```bash
./manage.sh logs db
```

2. **Verificar healthcheck**:
```bash
docker-compose ps
# Busca "health: starting" o "unhealthy" en columna STATUS
```

3. **Reiniciar solo la BD**:
```bash
docker-compose restart db
# Esperar 10 segundos
./manage.sh db-migrate
```

4. **Si persiste, verificar variables en `.env`**:
```bash
POSTGRES_DB=proyecto_ia_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres123
```

---

#### ❌ Error en Migraciones (Merge Heads)

**Síntoma**: Mensaje "Detected multiple heads" o "alembic merge heads required"

**Solución**:

1. **Verificar heads actuales**:
```bash
docker-compose exec backend alembic heads
# Mostrará los heads conflictivos
```

2. **Hacer merge**:
```bash
docker-compose exec backend alembic merge heads -m "merge migration branches"
```

3. **Aplicar nuevamente**:
```bash
./manage.sh db-migrate
```

4. **Ver estado actual**:
```bash
docker-compose exec backend alembic current
```

---

#### ❌ Error: "npm install failed" (Frontend)

**Síntoma**: Build del frontend falla durante `npm install`

**Solución**:

1. **Limpiar cache de npm**:
```bash
# Eliminar node_modules
rm -rf frontend/node_modules

# Linux/Mac
./manage.sh clean

# Windows
manage.bat clean
```

2. **Rebuild con --no-cache**:
```bash
docker-compose build --no-cache frontend
```

3. **Instalar dependencias manualmente**:
```bash
docker-compose run --rm frontend npm install
```

---

#### ❌ Error: "CORS blocked" en Frontend

**Síntoma**: Consola del navegador muestra error CORS al llamar API

**Solución**:

1. **Verificar `CORS_ORIGINS` en `.env`**:
```bash
CORS_ORIGINS=http://localhost:4200,http://localhost:80
```

2. **Agregar tu URL**:
```bash
CORS_ORIGINS=http://localhost:4200,http://localhost:3000,http://localhost:80
```

3. **Reiniciar backend**:
```bash
docker-compose restart backend
```

---

#### ❌ Error: "Permission denied" (Linux/Mac)

**Síntoma**: Error al crear directorios o escribir archivos

**Solución**:

1. **Dar permisos a scripts**:
```bash
chmod +x manage.sh
chmod +x check_prerequisites.sh
chmod +x validate_installation.sh
```

2. **Dar permisos a directorios**:
```bash
sudo chown -R $USER:$USER data/ logs/ uploads/ backups/
```

3. **Ejecutar sin sudo** (usar Docker sin sudo):
```bash
sudo usermod -aG docker $USER
# Cerrar sesión y volver a entrar
```

---

#### ❌ Error: "Slow build times"

**Síntoma**: Build de Docker toma mucho tiempo

**Solución**:

1. **Usar cache de Docker** (ya implementado en manage scripts):
```bash
# Ahora el setup NO usa --no-cache por defecto
./manage.sh setup
```

2. **Limpiar imágenes antiguas**:
```bash
docker system prune -a
```

3. **Usar multi-stage builds** (ya implementado en Dockerfiles)

---

#### ❌ Logs muy grandes

**Síntoma**: Archivos de log consumen mucho espacio

**Solución**:

Los logs ahora están configurados con rotación automática:
```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

Para limpiar logs manualmente:
```bash
docker-compose down
rm -rf data/postgres/pg_log/*
docker-compose up -d
```

---

### Comandos Útiles de Diagnóstico

```bash
# Ver estado de todos los servicios
docker-compose ps

# Ver logs en tiempo real
./manage.sh logs              # Todos los servicios
./manage.sh logs backend      # Solo backend
./manage.sh logs db           # Solo base de datos

# Ver uso de recursos
docker stats

# Acceder al shell de un contenedor
./manage.sh shell backend     # Backend
./manage.sh shell db          # PostgreSQL
./manage.sh shell frontend    # Frontend

# Ver migraciones aplicadas
docker-compose exec backend alembic history
docker-compose exec backend alembic current

# Verificar conectividad BD desde backend
docker-compose exec backend python -c "from app.core.config import configuracion; print(configuracion.database_url)"

# Verificar salud de contenedores
docker inspect --format='{{json .State.Health}}' projecto-ia_backend
```

---

### Recursos Adicionales

Si ninguna solución funciona:

1. **Limpieza completa**:
```bash
./manage.sh clean
./manage.sh setup
```

2. **Ver documentación de errores en logs**:
```bash
./manage.sh logs backend > backend_logs.txt
./manage.sh logs db > db_logs.txt
```

3. **Reportar issue** en GitHub con:
   - Logs completos
   - Versión de Docker (`docker --version`)
   - Sistema operativo
   - Contenido de `.env` (sin passwords)

---

## 🤝 Contribución

### Proceso de Contribución

1. **Fork** del repositorio
2. **Crear rama** para feature: `git checkout -b feature/nueva-funcionalidad`
3. **Realizar cambios** siguiendo las convenciones del proyecto
4. **Ejecutar tests**: `manage.bat test`
5. **Commit** con mensaje descriptivo: `git commit -m "feat: agregar nueva funcionalidad"`
6. **Push** a tu fork: `git push origin feature/nueva-funcionalidad`
7. **Crear Pull Request**

### Convenciones de Código

#### Python (Backend)
- **Estilo**: PEP 8
- **Docstrings**: Google Style
- **Type hints**: Obligatorios
- **Tests**: pytest con cobertura mínima 80%

#### TypeScript (Frontend)
- **Estilo**: Next.js conventions
- **Linting**: ESLint con eslint-config-next
- **Naming**: camelCase para variables, PascalCase para componentes
- **Tests**: Vitest + React Testing Library
- **Componentes**: Usar shadcn/ui como base

#### Git Commits
```bash
# Formato
tipo(scope): descripción

# Ejemplos
feat(auth): agregar login con JWT
fix(api): corregir validación de email
docs(readme): actualizar instrucciones de instalación
test(users): agregar tests unitarios
```

### Estructura de Tests

```bash
tests/
├── backend/
│   ├── test_auth.py
│   ├── test_users.py
│   └── test_ia.py
├── frontend/
│   ├── components/
│   └── services/
└── e2e/
    ├── auth.spec.ts
    └── users.spec.ts
```

## 📝 Changelog

### [1.0.0] - 2025-10-10
#### Added
- Configuración inicial del proyecto
- Backend FastAPI con autenticación JWT
- Frontend Next.js 15 con React 19
- Migración de Vite a Next.js
- Componentes UI con shadcn/ui
- Containerización completa con Docker
- Scripts de gestión automatizados
- Documentación completa

#### Changed
- Frontend migrado de Angular/Vite a Next.js 15
- Tailwind CSS actualizado a v3.4
- Puerto frontend estandarizado a 4200

## 🆘 Soporte

### Recursos Útiles

- **Documentación FastAPI**: https://fastapi.tiangolo.com/
- **Documentación Next.js**: https://nextjs.org/docs
- **Documentación React**: https://react.dev/
- **shadcn/ui Components**: https://ui.shadcn.com/
- **Docker Compose**: https://docs.docker.com/compose/
- **PostgreSQL**: https://www.postgresql.org/docs/

### Contacto

- **Issues**: Reportar bugs en GitHub Issues
- **Discussions**: Preguntas generales en GitHub Discussions
- **Email**: [tu-email@example.com]

### FAQ

**P: ¿Cómo cambio la base de datos a MySQL?**
R: Modifica `docker-compose.yml` y cambia las configuraciones de conexión en `backend/app/core/database.py`

**P: ¿Puedo usar Vue en lugar de Next.js?**
R: Sí, reemplaza el contenido de `frontend/` con tu proyecto Vue y ajusta el `Dockerfile`

**P: ¿Cómo agrego nuevos servicios?**
R: Añade servicios en `docker-compose.yml` y crea las configuraciones correspondientes

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

---

## 🙏 Agradecimientos

- **FastAPI** por el excelente framework de API
- **Next.js** por el poderoso framework React
- **React** por la librería UI innovadora
- **shadcn/ui** por los componentes UI elegantes
- **PostgreSQL** por la confiable base de datos
- **Docker** por la containerización seamless
- **Claude AI** por la asistencia en desarrollo

---

**¡Happy Coding! 🚀**

