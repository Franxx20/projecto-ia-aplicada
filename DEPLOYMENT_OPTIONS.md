# 🚀 Opciones de Deployment - Asistente Plantitas

**Última actualización**: 12 de Noviembre de 2025  
**Estado del proyecto**: Desarrollo local completo, pendiente deployment en cloud  
**Estructura**: Monorepo con `backend/` (FastAPI + Python) y `frontend/` (Next.js + TypeScript)

---

## 📋 Índice

1. [Contexto y Lecciones Aprendidas](#contexto)
2. [Requisitos del Proyecto](#requisitos)
3. [Opción 1: Railway (⭐ Recomendada)](#opcion-1-railway)
4. [Opción 2: Render](#opcion-2-render)
5. [Opción 3: Fly.io](#opcion-3-flyio)
6. [Opción 4: Vercel + Railway](#opcion-4-vercel--railway)
7. [Opción 5: Docker + Azure Container Apps](#opcion-5-docker--azure-container-apps)
8. [Comparación de Opciones](#comparacion)
9. [Variables de Entorno Necesarias](#variables-de-entorno)
10. [Checklist de Deployment](#checklist)

---

## 🎯 Contexto y Lecciones Aprendidas {#contexto}

### Intento Previo: Azure App Service (10-12 Nov 2025)

**Resultado**: ❌ No exitoso

**Problemas encontrados**:
1. **Oryx Detection Error**: Azure no detectaba correctamente el proyecto Python en subcarpetas
2. **Manual Deployment**: No funciona bien con estructura monorepo
3. **Backend 503**: Container terminaba con exit code 127 (startup.sh not found)

**Conclusión**: Azure App Service con manual integration NO es adecuado para proyectos monorepo estructurados en subcarpetas.

### Lecciones Clave

✅ **Lo que funciona**:
- Plataformas que soportan nativamente monorepos (Railway, Render)
- Deployments con configuración explícita de rutas
- Docker para control total del build

❌ **Lo que NO funciona**:
- Manual integration con subcarpetas en Azure App Service
- Depender de auto-detección de proyecto (Oryx build)
- Configuración `PROJECT=backend` en Azure (no confiable)

---

## 📦 Requisitos del Proyecto {#requisitos}

### Backend (FastAPI)
- **Runtime**: Python 3.11+
- **Framework**: FastAPI + Uvicorn
- **Base de datos**: PostgreSQL (dev) / MySQL (Azure intentado)
- **Storage**: Azure Blob Storage o compatible S3
- **ORM**: SQLAlchemy + Alembic para migraciones
- **Ubicación**: `./backend/`

### Frontend (Next.js)
- **Runtime**: Node.js 20 LTS
- **Framework**: Next.js 14.2+ con TypeScript
- **UI**: Tailwind CSS + shadcn/ui
- **Build**: Standalone output mode
- **Ubicación**: `./frontend/`

### Recursos Necesarios
- Base de datos PostgreSQL/MySQL
- Storage para imágenes (Blob/S3)
- 2 servicios web (backend y frontend)
- Variables de entorno seguras

---

## ⭐ Opción 1: Railway (Recomendada) {#opcion-1-railway}

**Por qué Railway**: Excelente soporte para monorepos, FREE tier generoso, deployment sencillo.

### Ventajas
- ✅ Soporte nativo para monorepos
- ✅ FREE tier: $5 USD/mes de crédito
- ✅ PostgreSQL incluido (FREE hasta 500 MB)
- ✅ Deployment automático desde GitHub
- ✅ Variables de entorno por servicio
- ✅ Logs en tiempo real
- ✅ Domains automáticos HTTPS

### Desventajas
- ⚠️ Límite de $5/mes en FREE tier (puede quedarse corto)
- ⚠️ No incluye blob storage (usar Cloudinary FREE)

### Costo Estimado
- **FREE tier**: $0/mes (con $5 crédito incluido)
- **Hobby plan**: $5/mes + uso
- **Estimado para este proyecto**: $0-8/mes

### Pasos de Deployment

#### 1. Crear cuenta en Railway
```bash
# Instalar Railway CLI
npm i -g @railway/cli

# Login
railway login
```

#### 2. Crear proyecto y servicios

**En Railway Dashboard**:
1. Crear nuevo proyecto
2. Conectar repositorio GitHub: `Franxx20/projecto-ia-aplicada`
3. Agregar servicio: **Backend**
   - Root Directory: `/backend`
   - Start Command: `gunicorn app.main:app --worker-class uvicorn.workers.UvicornWorker --workers 1 --bind 0.0.0.0:$PORT`
   - Python Version: `3.11`
4. Agregar servicio: **Frontend**
   - Root Directory: `/frontend`
   - Build Command: `npm install && npm run build`
   - Start Command: `npm start`
5. Agregar servicio: **PostgreSQL** (desde Templates)

#### 3. Configurar variables de entorno

**Backend**:
```bash
# Database (auto-generado por Railway)
DATABASE_URL=${{Postgres.DATABASE_URL}}

# JWT
JWT_SECRET_KEY=<generar-64-caracteres-aleatorios>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Storage (usar Cloudinary FREE)
CLOUDINARY_CLOUD_NAME=<tu-cloud-name>
CLOUDINARY_API_KEY=<tu-api-key>
CLOUDINARY_API_SECRET=<tu-api-secret>

# App
ENVIRONMENT=production
DEBUG=false
CORS_ORIGINS=${{Frontend.RAILWAY_PUBLIC_DOMAIN}}
```

**Frontend**:
```bash
NEXT_PUBLIC_API_URL=${{Backend.RAILWAY_PUBLIC_DOMAIN}}
NODE_ENV=production
```

#### 4. Configurar Storage Alternativo (Cloudinary)

**Registro**: https://cloudinary.com/users/register_free
- FREE tier: 25 GB almacenamiento, 25 GB bandwidth/mes

**Modificar código backend** (`app/services/imagen_service.py`):
```python
# Cambiar de Azure Blob a Cloudinary
import cloudinary
import cloudinary.uploader

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

# Subir imagen
result = cloudinary.uploader.upload(file)
return result['secure_url']
```

#### 5. Deploy

```bash
# Railway hace deploy automático al hacer push a GitHub
git push origin main
```

**URLs resultantes**:
- Backend: `https://plantitas-backend.up.railway.app`
- Frontend: `https://plantitas-frontend.up.railway.app`

---

## 🎨 Opción 2: Render {#opcion-2-render}

**Por qué Render**: Similar a Heroku, muy fácil de usar, buen FREE tier.

### Ventajas
- ✅ FREE tier generoso (750 hrs/mes)
- ✅ PostgreSQL incluido (FREE hasta 1 GB)
- ✅ Soporte para monorepos
- ✅ Auto-deploy desde GitHub
- ✅ SSL automático
- ✅ Configuración visual simple

### Desventajas
- ⚠️ FREE tier: apps se duermen después de 15 min inactividad
- ⚠️ Cold start lento (~30-60 segundos)
- ⚠️ No incluye storage (usar Cloudinary)

### Costo Estimado
- **FREE tier**: $0/mes
- **Starter**: $7/mes por servicio
- **Estimado para este proyecto**: $0/mes (FREE) o $14/mes (2 servicios Starter)

### Pasos de Deployment

#### 1. Crear cuenta en Render
https://render.com/

#### 2. Crear servicios

**Backend (Web Service)**:
- Repository: `Franxx20/projecto-ia-aplicada`
- Name: `plantitas-backend`
- Root Directory: `backend`
- Environment: Python 3.11
- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn app.main:app --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT`

**Frontend (Web Service)**:
- Repository: `Franxx20/projecto-ia-aplicada`
- Name: `plantitas-frontend`
- Root Directory: `frontend`
- Environment: Node 20
- Build Command: `npm install && npm run build`
- Start Command: `npm start`

**PostgreSQL (Database)**:
- Create PostgreSQL database
- FREE tier: 1 GB, 90 días de retención

#### 3. Variables de entorno

Similar a Railway (ver sección anterior).

#### 4. Deploy

Render hace deployment automático al detectar cambios en GitHub.

---

## ✈️ Opción 3: Fly.io {#opcion-3-flyio}

**Por qué Fly.io**: Buenos precios, control con Docker, deployment global.

### Ventajas
- ✅ FREE allowance: $5/mes incluido
- ✅ Control total con Dockerfiles
- ✅ Deploy global en múltiples regiones
- ✅ PostgreSQL incluido
- ✅ Buena performance

### Desventajas
- ⚠️ Requiere Dockerfile (más complejo)
- ⚠️ CLI required (no dashboard visual completo)
- ⚠️ Curva de aprendizaje mayor

### Costo Estimado
- **FREE allowance**: $5/mes incluido
- **Estimado**: $0-5/mes

### Pasos de Deployment

#### 1. Instalar Fly CLI
```bash
# Windows (PowerShell)
iwr https://fly.io/install.ps1 -useb | iex

# Login
fly auth login
```

#### 2. Crear Dockerfiles

**`backend/Dockerfile`**:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "app.main:app", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8080"]
```

**`frontend/Dockerfile`**:
```dockerfile
FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

CMD ["npm", "start"]
```

#### 3. Deploy cada servicio

```bash
# Backend
cd backend
fly launch --name plantitas-backend
fly deploy

# Frontend
cd ../frontend
fly launch --name plantitas-frontend
fly deploy

# PostgreSQL
fly postgres create --name plantitas-db
```

#### 4. Configurar variables

```bash
fly secrets set DATABASE_URL=<connection-string> -a plantitas-backend
fly secrets set JWT_SECRET_KEY=<secret> -a plantitas-backend
```

---

## 🔷 Opción 4: Vercel + Railway {#opcion-4-vercel--railway}

**Por qué esta combinación**: Vercel es perfecto para Next.js, Railway para backend.

### Ventajas
- ✅ Vercel es EXCELENTE para Next.js
- ✅ FREE tier muy generoso de Vercel
- ✅ Railway para backend con PostgreSQL
- ✅ Performance óptima para frontend

### Desventajas
- ⚠️ Dos plataformas diferentes (más gestión)
- ⚠️ CORS configuration necesaria

### Costo Estimado
- **Vercel FREE**: $0/mes (frontend)
- **Railway**: $0-5/mes (backend + DB)
- **Total**: $0-5/mes

### Pasos de Deployment

#### Frontend en Vercel
1. https://vercel.com/ → Crear cuenta
2. Import Git Repository: `Franxx20/projecto-ia-aplicada`
3. Framework Preset: **Next.js**
4. Root Directory: `frontend`
5. Environment Variables:
   ```
   NEXT_PUBLIC_API_URL=https://plantitas-backend.up.railway.app
   NODE_ENV=production
   ```
6. Deploy

#### Backend en Railway
Seguir pasos de "Opción 1: Railway" solo para backend.

---

## 🐳 Opción 5: Docker + Azure Container Apps {#opcion-5-docker--azure-container-apps}

**Por qué Container Apps**: Control total con Docker, evita problemas de Oryx.

### Ventajas
- ✅ Control total con Dockerfiles
- ✅ Evita problemas de detección de Oryx
- ✅ Escalamiento automático
- ✅ Integración con Azure services

### Desventajas
- ⚠️ Costo mayor ($15-30/mes)
- ⚠️ Más complejo de configurar
- ⚠️ Requiere conocimiento de Docker

### Costo Estimado
- **Consumption tier**: $0.000012/vCPU-s + $0.000002/GiB-s
- **Estimado**: $15-30/mes

### Pasos de Deployment

Ver documentación oficial de Azure Container Apps:
https://learn.microsoft.com/azure/container-apps/

**No recomendado para demo académica** debido al costo y complejidad.

---

## 📊 Comparación de Opciones {#comparacion}

| Característica | Railway | Render | Fly.io | Vercel+Railway | Azure CA |
|----------------|---------|--------|--------|----------------|----------|
| **Costo (FREE)** | $0/mes | $0/mes | $0-5/mes | $0-5/mes | $15-30/mes |
| **Facilidad** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| **Monorepo** | ✅ Nativo | ✅ Bueno | ⚠️ Docker | ✅ Separado | ✅ Docker |
| **PostgreSQL** | ✅ Incluido | ✅ Incluido | ✅ Incluido | ✅ Incluido | ❌ Separado |
| **Storage** | ❌ Externo | ❌ Externo | ❌ Externo | ❌ Externo | ✅ Incluido |
| **Cold Start** | ✅ No | ⚠️ Sí (15min) | ✅ No | ✅ No | ✅ No |
| **Performance** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **CI/CD** | ✅ Auto | ✅ Auto | ⚠️ CLI | ✅ Auto | ⚠️ Manual |

### Recomendación por Caso de Uso

| Caso de Uso | Mejor Opción | Razón |
|-------------|--------------|-------|
| **Demo académica** | **Railway** | Fácil, rápido, FREE tier suficiente |
| **Prototipo rápido** | **Render** | Muy fácil, FREE tier generoso |
| **Producción pequeña** | **Railway** | Balance precio/features |
| **Producción performance** | **Fly.io** o **Vercel+Railway** | Mejor rendimiento |
| **Aprendizaje Docker** | **Fly.io** | Requiere Dockerfile |
| **Budget ilimitado** | **Azure Container Apps** | Features enterprise |

---

## 🔐 Variables de Entorno Necesarias {#variables-de-entorno}

### Backend (Obligatorias)

```bash
# Base de datos
DATABASE_URL=postgresql://user:pass@host:5432/dbname
# o para MySQL
DATABASE_URL=mysql+pymysql://user:pass@host:3306/dbname

# JWT Authentication
JWT_SECRET_KEY=<64-caracteres-aleatorios>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Storage (Cloudinary recomendado para FREE tier)
CLOUDINARY_CLOUD_NAME=<tu-cloud-name>
CLOUDINARY_API_KEY=<tu-api-key>
CLOUDINARY_API_SECRET=<tu-api-secret>

# Application
ENVIRONMENT=production
DEBUG=false
CORS_ORIGINS=https://tu-frontend.com
```

### Backend (Opcionales)

```bash
# Gemini API (para identificación de plantas)
GEMINI_API_KEY=<tu-api-key>

# Logging
LOG_LEVEL=INFO

# Timezone
TZ=America/Argentina/Buenos_Aires
```

### Frontend

```bash
NEXT_PUBLIC_API_URL=https://tu-backend.com
NODE_ENV=production
```

### Generar JWT Secret

```bash
# Opción 1: Python
python -c "import secrets; print(secrets.token_urlsafe(48))"

# Opción 2: PowerShell
-join ((65..90) + (97..122) + (48..57) | Get-Random -Count 64 | ForEach-Object {[char]$_})

# Opción 3: Online
# https://generate-secret.vercel.app/64
```

---

## ✅ Checklist de Deployment {#checklist}

### Pre-Deployment

- [ ] Código en branch `main` actualizado
- [ ] Tests pasando localmente
- [ ] Variables de entorno documentadas
- [ ] `.env.example` actualizado
- [ ] README con instrucciones de deployment

### Elección de Plataforma

- [ ] Plataforma elegida (Railway recomendado)
- [ ] Cuenta creada en la plataforma
- [ ] Billing configurado (si aplica)

### Configuración de Servicios

- [ ] Repository conectado
- [ ] Backend configurado (root directory: `backend`)
- [ ] Frontend configurado (root directory: `frontend`)
- [ ] Base de datos creada
- [ ] Storage configurado (Cloudinary u otro)

### Variables de Entorno

- [ ] `DATABASE_URL` configurado
- [ ] `JWT_SECRET_KEY` generado y configurado
- [ ] Storage credentials configuradas
- [ ] `CORS_ORIGINS` configurado con URL del frontend
- [ ] `NEXT_PUBLIC_API_URL` configurado con URL del backend

### Post-Deployment

- [ ] Backend accesible (probar `/docs`)
- [ ] Frontend carga correctamente
- [ ] Login funciona
- [ ] Subida de imágenes funciona
- [ ] Identificación de plantas funciona
- [ ] HTTPS habilitado
- [ ] Custom domain configurado (opcional)

### Monitoreo

- [ ] Logs del backend revisados
- [ ] Logs del frontend revisados
- [ ] Métricas de uso monitoreadas
- [ ] Alertas configuradas (opcional)

---

## 📚 Recursos Adicionales

### Documentación Oficial

- **Railway**: https://docs.railway.app/
- **Render**: https://render.com/docs
- **Fly.io**: https://fly.io/docs/
- **Vercel**: https://vercel.com/docs
- **Cloudinary**: https://cloudinary.com/documentation

### Tutoriales

- **Railway + FastAPI**: https://docs.railway.app/guides/fastapi
- **Render + Next.js**: https://render.com/docs/deploy-nextjs
- **Fly.io + Python**: https://fly.io/docs/python/

### Soporte

- **Railway Discord**: https://discord.gg/railway
- **Render Community**: https://community.render.com/
- **Fly.io Community**: https://community.fly.io/

---

## 🆘 Troubleshooting Común

### Problema: "Module not found"
**Solución**: Verificar que `requirements.txt` o `package.json` estén actualizados.

### Problema: "Database connection failed"
**Solución**: Verificar `DATABASE_URL` y que la base de datos esté corriendo.

### Problema: "CORS error"
**Solución**: Configurar `CORS_ORIGINS` en backend con la URL exacta del frontend.

### Problema: "Cold start lento" (Render FREE)
**Solución**: Usar Render Starter ($7/mes) para evitar sleep, o usar Railway.

### Problema: "Build failed"
**Solución**: Revisar logs de build, verificar comandos de build/start.

---

## 📧 Contacto

**Proyecto**: Asistente Plantitas  
**Universidad**: Universidad Nacional de La Matanza  
**Autor**: Franco Garcete (fgarcete@alumno.unlam.edu.ar)  
**Repositorio**: https://github.com/Franxx20/projecto-ia-aplicada

---

**Última actualización**: 12 de Noviembre de 2025  
**Versión**: 1.0  
**Estado**: Pendiente deployment en cloud
