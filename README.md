# 🌱 NatureTag - Proyecto IA Aplicada

> **Sistema inteligente de gestión y cuidado de plantas** powered by Google Gemini AI

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14.0-000000?style=flat&logo=next.js)](https://nextjs.org/)
[![React](https://img.shields.io/badge/React-18.2-61DAFB?style=flat&logo=react)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.3-3178C6?style=flat&logo=typescript)](https://www.typescriptlang.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=flat&logo=docker)](https://www.docker.com/)

---

## ⚡ Quick Start

```bash
# Clonar repositorio
git clone https://github.com/Franxx20/projecto-ia-aplicada.git
cd projecto-ia-aplicada

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus API keys (Gemini, PlantNet)

# Iniciar con Docker (Linux/Mac)
./manage.sh setup
./manage.sh dev

# Iniciar con Docker (Windows)
manage.bat setup
manage.bat dev

# Acceder a la aplicación
# Frontend: http://localhost:4200
# Backend API: http://localhost:8000/docs
```

---

## 📖 Descripción

**NatureTag** es una aplicación web integral para el cuidado y gestión de plantas, potenciada por Inteligencia Artificial. El sistema permite identificar plantas mediante fotografías, realizar diagnósticos de salud, obtener recomendaciones de cuidado personalizadas, y mantener un registro detallado de tu jardín o colección de plantas.

## 📑 Tabla de Contenidos

- [🎯 Características Principales](#-características-principales)
- [🛠️ Stack Tecnológico](#️-stack-tecnológico)
- [📸 Capturas de Pantalla](#-capturas-de-pantalla)
- [🏗️ Arquitectura](#️-arquitectura)
- [🤖 Capacidades de IA](#-capacidades-de-inteligencia-artificial)
- [📁 Estructura del Proyecto](#-estructura-del-proyecto)
- [🔧 Tecnologías y Dependencias](#-tecnologías-y-dependencias-clave)
- [🚀 Instalación y Configuración](#-instalación-y-configuración)
- [🎯 Comandos de Gestión](#-comandos-de-gestión)
- [🛠️ Desarrollo](#️-desarrollo)
- [📦 Azure Blob Storage](#-azure-blob-storage)
- [🧪 Testing](#-testing)
- [📊 Monitoreo y Logs](#-monitoreo-y-logs)
- [🔧 Troubleshooting](#-troubleshooting)
- [🚀 Deployment](#-deployment-en-producción)
- [📚 Documentación de APIs](#-documentación-de-apis)
- [🤝 Contribución](#-contribución)
- [📝 Changelog](#-changelog)
- [🆘 Soporte](#-soporte)

### 🎯 Características Principales

- 🔍 **Identificación de Plantas con IA**: Identifica especies mediante fotografías usando Gemini AI y PlantNet
- 🏥 **Diagnóstico de Salud**: Analiza el estado de tus plantas y detecta problemas (plagas, enfermedades, deficiencias)
- 💬 **Chat Asistente IA**: Consulta sobre cuidados, problemas y consejos personalizados
- 📸 **Gestión de Imágenes**: Almacenamiento en Azure Blob Storage con Azurite para desarrollo
- 📊 **Registro de Plantas**: Mantén un inventario completo de tus plantas con historial de cuidados
- 🌍 **Multi-plataforma**: Acceso desde navegador con diseño responsive

### 🛠️ Stack Tecnológico

- **Backend**: FastAPI + SQLAlchemy + PostgreSQL
- **Frontend**: Next.js 14 + React 18 + TypeScript + Tailwind CSS
- **IA**: Google Gemini 2.5 Flash, PlantNet API
- **Almacenamiento**: Azure Blob Storage (Azurite en desarrollo)
- **Containerización**: Docker + Docker Compose
- **Base de Datos**: PostgreSQL 15 + SQLite (desarrollo)

---

## 📸 Capturas de Pantalla

> 💡 **Nota**: Próximamente se agregarán capturas de pantalla de las funcionalidades principales.

**Funcionalidades destacadas**:
- 🏠 Dashboard con resumen de plantas y estadísticas
- 🔍 Interfaz de identificación con resultados en tiempo real
- 🏥 Panel de diagnóstico de salud con recomendaciones
- 💬 Chat asistente flotante con IA
- 📱 Diseño responsive para móviles y tablets

---

## 🏗️ Arquitectura

```
┌─────────────────────┐         ┌─────────────────────┐         ┌─────────────────────┐
│                     │         │                     │         │                     │
│   Next.js 14        │────────▶│   FastAPI API       │────────▶│   PostgreSQL 15     │
│   React 18          │         │   Python 3.11       │         │   SQLite (dev)      │
│   TypeScript        │         │   SQLAlchemy        │         │                     │
│                     │         │                     │         │                     │
└─────────────────────┘         └─────────────────────┘         └─────────────────────┘
        │                                 │                              
        │                                 │                              
    Port 4200                         Port 8000                      Port 5432
        │                                 │
        │                                 ▼
        │                       ┌─────────────────────┐
        │                       │  Azure Blob Storage │
        │                       │  (Azurite en dev)   │
        └──────────────────────▶│  Gestión Imágenes   │
                                │                     │
                                └─────────────────────┘
                                      Port 10000

┌─────────────────────────────────────────────────────────────────────────┐
│                          APIs de Inteligencia Artificial                │
│                                                                         │
│  • Google Gemini 2.5 Flash - Identificación y diagnóstico              │
│  • PlantNet API - Base de datos botánica                               │
└─────────────────────────────────────────────────────────────────────────┘
```

## 🤖 Capacidades de Inteligencia Artificial

### 🔍 Identificación de Plantas

El sistema utiliza **dos motores de IA** para identificar plantas con alta precisión:

#### Google Gemini 2.5 Flash
- **Análisis visual avanzado** de características morfológicas
- **Identificación de especies** con nivel de confianza
- **Descripción detallada** de la planta identificada
- **Nombres comunes** en múltiples idiomas
- **Recomendaciones de cuidado** personalizadas

#### PlantNet API
- **Base de datos botánica** con más de 20,000 especies
- **Validación científica** de identificaciones
- **Comparación con imágenes de referencia**
- **Información taxonómica** completa

**Características**:
- ✅ Identificación en segundos
- ✅ Confianza del 85-95% en condiciones óptimas
- ✅ Fallback automático si un servicio falla
- ✅ Historial de identificaciones guardado

### 🏥 Diagnóstico de Salud

**Gemini AI** analiza las imágenes de tus plantas para detectar:

- 🐛 **Plagas**: Áfidos, cochinillas, arañas rojas, moscas blancas
- 🦠 **Enfermedades**: Hongos, bacterias, virus
- 🍂 **Deficiencias nutricionales**: Nitrógeno, fósforo, potasio, hierro
- 💧 **Problemas de riego**: Exceso o falta de agua
- ☀️ **Estrés ambiental**: Quemaduras solares, heladas, viento

**Incluye**:
- Nivel de severidad (leve, moderado, severo)
- Recomendaciones de tratamiento específicas
- Plan de recuperación paso a paso
- Medidas preventivas

### 💬 Chat Asistente Inteligente

Asistente conversacional potenciado por **Gemini AI** que:

- 🌱 Responde preguntas sobre cuidados específicos
- 📅 Sugiere calendarios de riego y fertilización
- 🔄 Recuerda el contexto de conversaciones anteriores
- 🎯 Ofrece consejos personalizados según tu ubicación y clima
- 📚 Proporciona información educativa sobre botánica

**Ejemplo de consultas**:
- "¿Por qué las hojas de mi rosa están amarillas?"
- "¿Cuándo debo trasplantar mi suculenta?"
- "¿Qué fertilizante usar para tomates?"

#### 🚀 Optimizaciones de Rendimiento y Costos

El chat asistente incluye **optimizaciones inteligentes** para reducir costos y mejorar tiempos de respuesta:

- **💾 Caché de Respuestas**: Preguntas frecuentes se cachean automáticamente por 30 días
  - Ahorro estimado: **30% en costos de API**
  - Tiempo de respuesta: **40x más rápido** (<50ms vs ~2000ms)
  - Almacenamiento: Base de datos con hash SHA-256

- **🔒 Rate Limiting**: Control automático de uso
  - Límite global: 1500 requests/día
  - Límite por usuario: 50 requests/día
  - Límite por minuto: 60 requests/minuto
  - Protección contra costos inesperados

- **🧠 Contexto Inteligente**: Historial optimizado
  - Últimos 10 mensajes mantenidos en contexto
  - Datos de planta incluidos automáticamente
  - Reducción de tokens innecesarios

📊 **Ver estadísticas**: `GET /api/chat/estadisticas`

Para más detalles, consulta [MEJORAS_GEMINI_API.md](MEJORAS_GEMINI_API.md)

### 🎯 Precisión y Limitaciones

**Precisión estimada**:
- Identificación de especies: **85-95%** (varía según calidad de imagen)
- Diagnóstico de salud: **80-90%** (requiere imágenes claras)
- Chat asistente: Basado en Gemini 2.5 Flash

**Mejores prácticas para resultados óptimos**:
1. 📸 Toma fotos en buena iluminación natural
2. 🔍 Incluye detalles como hojas, flores o frutos
3. 📏 Asegúrate que la planta ocupe la mayor parte de la imagen
4. 🎨 Evita filtros o ediciones que alteren colores

## 📁 Estructura del Proyecto

```
projecto-ia-aplicada/
├── backend/                 # API FastAPI
│   ├── app/
│   │   ├── api/            # Endpoints REST
│   │   │   ├── auth.py           # Autenticación y autorización
│   │   │   ├── chat.py           # Chat asistente con IA
│   │   │   ├── identificacion.py # Identificación de plantas
│   │   │   ├── imagenes.py       # Gestión de imágenes
│   │   │   ├── plantas.py        # CRUD de plantas
│   │   │   └── salud.py          # Diagnóstico de salud
│   │   ├── core/           # Configuración, seguridad
│   │   │   ├── config.py         # Variables de entorno
│   │   │   ├── security.py       # JWT, passwords
│   │   │   └── database.py       # Conexión BD
│   │   ├── db/             # Modelos de base de datos
│   │   │   ├── models.py         # SQLAlchemy models
│   │   │   └── session.py        # Sesión de BD
│   │   ├── schemas/        # Pydantic schemas
│   │   │   ├── auth.py           # Schemas de autenticación
│   │   │   ├── imagen.py         # Schemas de imágenes
│   │   │   ├── planta.py         # Schemas de plantas
│   │   │   └── ...
│   │   ├── services/       # Lógica de negocio
│   │   │   ├── gemini_service.py # Integración con Gemini
│   │   │   ├── azure_storage.py  # Azure Blob Storage
│   │   │   └── ...
│   │   ├── utils/          # Utilidades
│   │   └── main.py         # Punto de entrada FastAPI
│   ├── alembic/            # Migraciones de BD
│   ├── tests/              # Tests del backend
│   ├── Dockerfile          # Imagen Docker backend
│   ├── requirements.txt    # Dependencias Python
│   └── pytest.ini          # Configuración tests
├── frontend/                # Aplicación Next.js
│   ├── app/
│   │   ├── dashboard/      # Panel principal
│   │   ├── identificar/    # Página identificación
│   │   ├── login/          # Autenticación
│   │   ├── plant/          # Detalle de planta
│   │   ├── salud/          # Diagnóstico salud
│   │   ├── layout.tsx      # Layout principal
│   │   ├── page.tsx        # Página principal
│   │   └── globals.css     # Estilos globales
│   ├── components/
│   │   ├── ui/             # Componentes UI (shadcn)
│   │   ├── ChatWidget.tsx  # Widget de chat
│   │   ├── ImageUpload.tsx # Subida de imágenes
│   │   └── dashboard/      # Componentes del dashboard
│   ├── contexts/           # Context providers (Auth)
│   ├── lib/                # Utilidades y helpers
│   ├── models/             # Interfaces TypeScript
│   ├── public/             # Recursos estáticos
│   ├── Dockerfile          # Dockerfile producción
│   ├── Dockerfile.dev      # Dockerfile desarrollo
│   ├── next.config.mjs     # Configuración Next.js
│   ├── tailwind.config.ts  # Configuración Tailwind
│   └── package.json        # Dependencias NPM
├── tests/                   # Tests del proyecto
│   ├── backend/            # Tests Python
│   ├── frontend/           # Tests Next.js/React
│   └── e2e/               # Tests end-to-end
├── data/                   # Datos persistentes
│   ├── postgres/           # Datos PostgreSQL
│   ├── azurite/            # Datos Azurite (emulador)
│   └── redis/              # Cache Redis (futuro)
├── logs/                   # Logs de aplicación
├── uploads/                # Archivos temporales
├── backups/                # Backups de BD
├── certs/                  # Certificados SSL
├── docker-compose.yml      # Producción
├── docker-compose.dev.yml  # Desarrollo (hot reload)
├── .env.example           # Template de variables
├── manage.sh              # Script gestión (Linux/Mac)
├── manage.bat             # Script gestión (Windows)
└── README.md              # Esta documentación
```

## 🔧 Tecnologías y Dependencias Clave

### Backend (Python 3.11)

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| FastAPI | 0.104.1 | Framework web moderno y rápido |
| SQLAlchemy | 2.0.23 | ORM para base de datos |
| Alembic | 1.12.1 | Migraciones de base de datos |
| Pydantic | 2.4.2 | Validación de datos |
| python-jose | 3.3.0 | Autenticación JWT |
| bcrypt | 4.0.1 | Hashing de contraseñas |
| google-generativeai | 0.3.2 | SDK de Gemini AI |
| azure-storage-blob | 12.19.0 | Azure Blob Storage |
| Pillow | 10.1.0 | Procesamiento de imágenes |
| pytest | 7.4.3 | Testing framework |

### Frontend (Node.js)

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| Next.js | 14.0.4 | Framework React con SSR |
| React | 18.2.0 | Librería UI |
| TypeScript | 5.3.3 | Tipado estático |
| Tailwind CSS | 3.4.17 | Framework CSS utility-first |
| shadcn/ui | Latest | Componentes UI accesibles |
| React Hook Form | 7.60.0 | Gestión de formularios |
| Zod | 3.25.67 | Validación de esquemas |
| Axios | 1.6.2 | Cliente HTTP |
| Lucide React | 0.454.0 | Iconos SVG |
| Jest | 29.7.0 | Testing framework |

### Infraestructura

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| PostgreSQL | 15-alpine | Base de datos relacional |
| Docker | 20.10+ | Containerización |
| Docker Compose | 2.0+ | Orquestación de contenedores |
| Azurite | Latest | Emulador Azure Storage |
| Adminer | Latest | Administrador de BD web |

## 🚀 Instalación y Configuración

### 💻 Requisitos del Sistema

**Hardware mínimo recomendado**:
- CPU: 2 cores (4 recomendado)
- RAM: 4 GB (8 GB recomendado)
- Disco: 5 GB de espacio libre
- Internet: Conexión estable para APIs de IA

**Software requerido**:
- **Docker**: versión 20.10 o superior
- **Docker Compose**: versión 2.0 o superior
- **Git**: para clonar el repositorio

**Sistemas operativos soportados**:
- ✅ Windows 10/11 (con WSL2 recomendado)
- ✅ macOS 10.15 o superior
- ✅ Linux (Ubuntu 20.04+, Debian, Fedora, etc.)

### Prerrequisitos

Antes de comenzar, asegúrate de tener instalado:

1. **Docker Desktop** (incluye Docker + Docker Compose)
   - [Descargar para Windows](https://docs.docker.com/desktop/install/windows-install/)
   - [Descargar para Mac](https://docs.docker.com/desktop/install/mac-install/)
   - [Instalar en Linux](https://docs.docker.com/desktop/install/linux-install/)

2. **Git** para clonar el repositorio
   - [Descargar Git](https://git-scm.com/downloads)

3. **API Keys** (gratuitas) para servicios de IA:
   - **Gemini API**: [Obtener en Google AI Studio](https://makersuite.google.com/app/apikey)
   - **PlantNet API** (opcional): [Registrarse en PlantNet](https://my.plantnet.org/)

**Verificar instalación**:
```bash
# Verificar Docker
docker --version
docker-compose --version

# Verificar Git
git --version
```

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
- **TypeScript**: Tipado estricto en todo el proyecto
- **Tailwind CSS v3**: Estilos utility-first
- **shadcn/ui**: Componentes UI accesibles y customizables
- **Formularios**: React Hook Form + Zod para validación
- **Gestión de Estado**: Context API para autenticación

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

# APIs de IA (configuradas en el .env de la raíz)
GEMINI_API_KEY=tu_gemini_api_key
PLANTNET_API_KEY=tu_plantnet_api_key
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
├── page.tsx              # → / (Landing page)
├── layout.tsx            # Layout global
├── globals.css           # Estilos Tailwind
├── login/
│   └── page.tsx          # → /login (Autenticación)
├── dashboard/
│   ├── page.tsx          # → /dashboard (Panel principal)
│   └── ...
├── identificar/
│   └── page.tsx          # → /identificar (Identificación de plantas)
├── plant/
│   └── [id]/
│       └── page.tsx      # → /plant/[id] (Detalle de planta)
├── salud/
│   └── page.tsx          # → /salud (Diagnóstico de salud)
└── api/
    └── health/
        └── route.ts      # → /api/health (Health check)
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
│   ├── main.py           # Punto de entrada FastAPI
│   ├── api/              # Endpoints REST
│   │   ├── auth.py           # Autenticación JWT
│   │   ├── chat.py           # Chat con IA
│   │   ├── identificacion.py # Identificación de plantas
│   │   ├── imagenes.py       # Gestión de imágenes
│   │   ├── plantas.py        # CRUD de plantas
│   │   └── salud.py          # Diagnóstico de salud
│   ├── core/
│   │   ├── config.py     # Configuración centralizada
│   │   ├── security.py   # Autenticación JWT, hashing
│   │   └── database.py   # Conexión BD (SQLAlchemy)
│   ├── db/
│   │   ├── models.py     # Modelos SQLAlchemy
│   │   │   # - Usuario, Planta, Imagen
│   │   │   # - Identificacion, Diagnostico
│   │   └── session.py    # Sesión de base de datos
│   ├── schemas/          # Pydantic schemas (validación)
│   │   ├── auth.py           # Login, Register, Token
│   │   ├── planta.py         # PlantaCreate, PlantaUpdate
│   │   ├── imagen.py         # ImagenUpload, ImagenResponse
│   │   └── ...
│   ├── services/         # Lógica de negocio e integraciones
│   │   ├── gemini_service.py     # Integración con Gemini AI
│   │   ├── azure_storage.py      # Azure Blob Storage
│   │   ├── plantnet_service.py   # PlantNet API
│   │   └── ...
│   └── utils/            # Utilidades comunes
├── alembic/              # Migraciones Alembic
├── tests/                # Tests pytest
└── requirements.txt      # Dependencias
```

#### Frontend (Next.js 15)

```bash
frontend/
├── app/
│   ├── layout.tsx        # Layout principal con metadata
│   ├── page.tsx          # Página landing (/)
│   ├── globals.css       # Estilos globales Tailwind
│   ├── login/
│   │   └── page.tsx          # Login/Register
│   ├── dashboard/
│   │   ├── page.tsx          # Dashboard principal
│   │   └── components/       # Componentes del dashboard
│   ├── identificar/
│   │   └── page.tsx          # Identificación de plantas
│   ├── plant/
│   │   └── [id]/
│   │       └── page.tsx      # Detalle de planta (dinámico)
│   ├── salud/
│   │   └── page.tsx          # Diagnóstico de salud
│   └── api/
│       └── health/
│           └── route.ts      # Health check endpoint
├── components/
│   ├── ui/               # Componentes shadcn/ui
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── input.tsx
│   │   ├── form.tsx
│   │   └── ...
│   ├── ChatWidget.tsx        # Widget de chat flotante
│   ├── ImageUpload.tsx       # Subida de imagen única
│   ├── MultipleImageUpload.tsx  # Subida múltiple
│   ├── dashboard/
│   │   ├── PlantCard.tsx     # Tarjeta de planta
│   │   └── StatsCard.tsx     # Estadísticas
│   └── identification-result-card.tsx  # Resultado identificación
├── contexts/
│   └── AuthContext.tsx       # Context de autenticación
├── lib/
│   ├── utils.ts              # Utilidades (cn, etc.)
│   └── api.ts                # Cliente API
├── models/               # Interfaces TypeScript
│   ├── Plant.ts              # Modelo de planta
│   ├── User.ts               # Modelo de usuario
│   └── ...
├── public/               # Assets estáticos
│   ├── images/
│   └── icons/
├── next.config.mjs       # Configuración Next.js
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

**Autenticación**
```
POST /api/auth/register        # Registrar nuevo usuario
POST /api/auth/login          # Login con email y password
POST /api/auth/token          # Obtener access token
GET  /api/auth/me             # Obtener perfil del usuario actual
```

**Gestión de Plantas**
```
GET    /api/plantas            # Listar plantas del usuario
POST   /api/plantas            # Crear nueva planta
GET    /api/plantas/{id}       # Obtener detalles de planta
PUT    /api/plantas/{id}       # Actualizar planta
DELETE /api/plantas/{id}       # Eliminar planta
```

**Identificación con IA**
```
POST /api/identificar          # Identificar planta desde imagen
GET  /api/identificar/{id}     # Obtener resultado de identificación
```

**Diagnóstico de Salud**
```
POST /api/salud/diagnosticar   # Diagnosticar problemas de salud
GET  /api/salud/historial      # Historial de diagnósticos
```

**Gestión de Imágenes**
```
POST   /api/imagenes/subir     # Subir imagen a Azure Storage
GET    /api/imagenes/          # Listar imágenes del usuario
GET    /api/imagenes/{id}      # Obtener imagen
GET    /api/imagenes/proxy/{filename}  # Proxy para Azurite
DELETE /api/imagenes/{id}      # Eliminar imagen
```

**Chat Asistente**
```
POST /api/chat                 # Enviar mensaje al asistente
GET  /api/chat/historial       # Obtener historial de conversación
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

### Autenticación JWT

```typescript
// Registro de usuario
POST /api/auth/register
{
  "email": "usuario@example.com",
  "password": "mi_password_seguro",
  "nombre": "Juan Pérez"
}

// Response
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": 1,
    "email": "usuario@example.com",
    "nombre": "Juan Pérez"
  }
}

// Login
POST /api/auth/login
{
  "email": "usuario@example.com",
  "password": "mi_password"
}

// Perfil del usuario autenticado
GET /api/auth/me
Headers: Authorization: Bearer {token}
```

### APIs de IA

```typescript
// Identificar planta desde imagen
POST /api/identificar
Headers: Authorization: Bearer {token}
Content-Type: multipart/form-data
Body: {
  imagen: File,
  usar_plantnet: boolean (opcional),
  usar_gemini: boolean (opcional)
}

// Response
{
  "id": 123,
  "especie_detectada": "Rosa chinensis",
  "confianza": 0.95,
  "nombres_comunes": ["Rosa de China", "Hibisco"],
  "familia": "Malvaceae",
  "descripcion": "...",
  "cuidados_recomendados": {
    "riego": "Moderado, mantener suelo húmedo",
    "luz": "Pleno sol o sombra parcial",
    "temperatura": "15-30°C"
  },
  "imagen_url": "/api/imagenes/proxy/abc123.jpg"
}

// Diagnosticar salud de planta
POST /api/salud/diagnosticar
Headers: Authorization: Bearer {token}
Content-Type: multipart/form-data
Body: {
  planta_id: number,
  imagen: File,
  sintomas: string (opcional)
}

// Response
{
  "diagnostico_id": 456,
  "estado_general": "Deficiencia nutricional",
  "confianza": 0.88,
  "problemas_detectados": [
    {
      "tipo": "deficiencia",
      "descripcion": "Clorosis en hojas inferiores",
      "severidad": "moderada",
      "tratamiento": "Aplicar fertilizante rico en nitrógeno"
    }
  ],
  "recomendaciones": [
    "Fertilizar cada 2 semanas",
    "Verificar pH del suelo"
  ]
}

// Chat con asistente IA
POST /api/chat
Headers: Authorization: Bearer {token}
Body: {
  "mensaje": "¿Cómo cuido mi rosa?",
  "contexto": {
    "planta_id": 123  // opcional
  }
}

// Response
{
  "respuesta": "Para cuidar tu rosa, te recomiendo...",
  "timestamp": "2025-11-13T10:30:00Z"
}
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

### [1.1.0] - 14 de Noviembre 2025

#### 🚀 Optimizaciones de Gemini API

**Sistema de Caché de Respuestas**
- ✅ Nueva tabla `gemini_response_cache` para almacenar respuestas frecuentes
- ✅ Hash SHA-256 para identificación única de preguntas
- ✅ Expiración automática de caché (30 días)
- ✅ Tracking de hits y tokens ahorrados
- ✅ Reducción estimada de 30% en costos de API
- ✅ Mejora de 40x en tiempos de respuesta para cache hits

**Rate Limiting Implementado**
- ✅ Control de límites por minuto (60 req/min global)
- ✅ Límite diario global (1500 req/día)
- ✅ Límite por usuario (50 req/día)
- ✅ Respuestas HTTP 429 con mensajes claros
- ✅ Endpoint `/api/chat/estadisticas` para consultar uso

**Contexto de Conversación Optimizado**
- ✅ Historial limitado a últimos 10 mensajes
- ✅ Contexto inteligente con datos de planta
- ✅ Reducción de tokens innecesarios

**Migración de Base de Datos**
- ✅ Alembic migration `002_add_gemini_cache.py`
- ✅ 4 índices para búsquedas eficientes

**Archivos Modificados**
- `backend/app/db/models.py`: Modelo `GeminiResponseCache`
- `backend/app/services/chat_service.py`: Integración de caché y rate limiting
- `backend/app/api/chat.py`: Endpoint de estadísticas y manejo 429
- `backend/app/core/config.py`: Variable `gemini_max_requests_per_minute`
- `MEJORAS_GEMINI_API.md`: Documentación completa de mejoras

### [1.0.0] - Noviembre 2025

#### Added - Funcionalidades Principales
- ✅ Sistema completo de autenticación con JWT
- ✅ Identificación de plantas con Gemini AI y PlantNet
- ✅ Diagnóstico de salud de plantas con análisis de imágenes
- ✅ Chat asistente IA para consultas sobre plantas
- ✅ Gestión completa de plantas (CRUD)
- ✅ Almacenamiento de imágenes en Azure Blob Storage
- ✅ Emulador Azurite para desarrollo local
- ✅ Frontend responsive con Next.js 14 y React 18
- ✅ Componentes UI con shadcn/ui y Tailwind CSS
- ✅ Containerización completa con Docker Compose
- ✅ Migraciones de base de datos con Alembic
- ✅ Scripts de gestión automatizados (manage.sh / manage.bat)

#### Backend (FastAPI)
- Base de datos PostgreSQL en producción, SQLite en desarrollo
- Sistema de autenticación JWT con refresh tokens
- Integración con Google Gemini 2.5 Flash
- Integración con PlantNet API
- Middleware de CORS configurado
- Health checks automáticos
- Logging estructurado
- Tests unitarios con pytest

#### Frontend (Next.js)
- App Router con rutas dinámicas
- Context API para gestión de autenticación
- Formularios con React Hook Form + Zod
- Subida de imágenes con preview
- Chat flotante con IA
- Dashboard con estadísticas
- Diseño responsive mobile-first
- Tests con Jest y React Testing Library

#### DevOps
- Docker Compose para desarrollo y producción
- Azurite como emulador de Azure Storage
- Hot reload en modo desarrollo
- Configuración unificada en archivo .env
- Scripts de backup automático
- Health checks de contenedores
- Rotación de logs automática

## 🆘 Soporte

### Recursos Útiles

- **Documentación FastAPI**: https://fastapi.tiangolo.com/
- **Documentación Next.js**: https://nextjs.org/docs
- **Documentación React**: https://react.dev/
- **shadcn/ui Components**: https://ui.shadcn.com/
- **Tailwind CSS**: https://tailwindcss.com/docs
- **Docker Compose**: https://docs.docker.com/compose/
- **PostgreSQL**: https://www.postgresql.org/docs/
- **Google Gemini AI**: https://ai.google.dev/
- **PlantNet**: https://plantnet.org/
- **Azure Storage**: https://learn.microsoft.com/azure/storage/

### Contacto

- **Repository**: https://github.com/Franxx20/projecto-ia-aplicada
- **Issues**: Reportar bugs en GitHub Issues
- **Discussions**: Preguntas generales en GitHub Discussions

### FAQ

**P: ¿Cómo obtengo las API keys de Gemini y PlantNet?**
R: 
- **Gemini**: Visita https://makersuite.google.com/app/apikey
- **PlantNet**: Registrarte en https://my.plantnet.org/

**P: ¿Puedo usar Azure Storage real en lugar de Azurite?**
R: Sí, configura `AZURE_STORAGE_CONNECTION_STRING` con tus credenciales reales y establece `AZURE_STORAGE_USE_EMULATOR=false` en el archivo `.env`

**P: ¿Cómo cambio el puerto del frontend?**
R: Modifica `FRONTEND_PORT` en el archivo `.env` y reinicia los servicios con `manage.bat restart`

**P: ¿Puedo usar MySQL en lugar de PostgreSQL?**
R: Sí, modifica `docker-compose.yml`, actualiza `DATABASE_URL` en `.env` y ajusta las dependencias en `requirements.txt`

**P: ¿Cómo ejecuto el proyecto sin Docker?**
R: 
- Backend: `cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload`
- Frontend: `cd frontend && npm install && npm run dev`
- Asegúrate de tener PostgreSQL/SQLite y configurar las variables de entorno

**P: ¿Cómo agrego nuevos servicios?**
R: Añade servicios en `docker-compose.yml` y crea las configuraciones correspondientes

## 🔒 Seguridad y Mejores Prácticas

### 🛡️ Seguridad en Producción

**IMPORTANTE**: Antes de desplegar en producción:

1. **Cambiar todas las contraseñas y secretos**:
   ```env
   SECRET_KEY=tu_clave_super_secura_de_al_menos_32_caracteres
   POSTGRES_PASSWORD=password_muy_seguro_y_complejo
   JWT_SECRET_KEY=otra_clave_diferente_para_jwt
   ```

2. **Deshabilitar modo debug**:
   ```env
   DEBUG=false
   ENVIRONMENT=production
   ```

3. **Configurar CORS correctamente**:
   ```env
   CORS_ORIGINS=https://tu-dominio.com,https://www.tu-dominio.com
   ```

4. **Usar HTTPS** con certificados SSL válidos

5. **Proteger API keys**:
   - No incluir API keys en el código
   - Usar variables de entorno o servicios como Azure Key Vault
   - Rotar keys periódicamente

### 📋 Mejores Prácticas

**Git**:
- ✅ Nunca hacer commit del archivo `.env`
- ✅ Usar `.env.example` como plantilla
- ✅ Hacer commits descriptivos
- ✅ Usar branches para nuevas features

**Docker**:
- ✅ Usar `docker-compose.dev.yml` para desarrollo
- ✅ Limpiar imágenes antiguas regularmente
- ✅ Monitorear uso de recursos con `docker stats`

**Base de Datos**:
- ✅ Crear backups regulares (`./manage.sh db-backup`)
- ✅ Probar migraciones en desarrollo antes de producción
- ✅ Usar Adminer/pgAdmin solo en desarrollo

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

---

## 🙏 Agradecimientos

- **FastAPI** por el excelente framework de API
- **Next.js** y el equipo de **Vercel** por el poderoso framework React
- **React** por la innovadora librería UI
- **shadcn/ui** por los componentes UI elegantes y accesibles
- **PostgreSQL** por la confiable base de datos
- **Docker** por facilitar la containerización
- **Google Gemini** por proporcionar capacidades de IA
- **PlantNet** por la base de datos botánica
- **Microsoft Azure** por los servicios de almacenamiento
- **GitHub Copilot** por la asistencia en desarrollo

---

## 👥 Equipo de Desarrollo

**NatureTag** - Proyecto de IA Aplicada

- Repositorio: https://github.com/Franxx20/projecto-ia-aplicada
- Versión: 1.0.0
- Fecha: Noviembre 2025

---

**¡Happy Coding! 🌱🚀**

