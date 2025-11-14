# 🗑️ SERVICIOS CLOUD ELIMINADOS

**Fecha de Eliminación**: 12 de Noviembre de 2025  
**Motivo**: Problemas persistentes con deployment de Azure App Service  
**Estado**: Todos los recursos eliminados exitosamente

---

## ✅ RECURSOS ELIMINADOS

Todos los siguientes recursos fueron eliminados de Azure:

### Resource Group
- ✅ **rg-plantitas-demo-academica** (Chile Central)

### Servicios Web
- ✅ **plantitas-demo-backend** - Backend App Service (Python 3.11)
- ✅ **plantitas-frontend-app** - Frontend App Service (Node 20 LTS)
- ✅ **plantitas-demo-frontend** - Frontend App Service duplicado

### Base de Datos
- ✅ **plantitas-mysql-server** - MySQL Flexible Server 8.0.21
- ✅ **plantitas-demo-mysql** - MySQL Server duplicado
- ✅ **plantitas_db** - Base de datos (eliminada con el servidor)

### Storage
- ✅ **plantitasdemostorage** - Storage Account con container `plantitas-imagenes`

### App Service Plan
- ✅ **plantitas-demo-plan** - App Service Plan F1 FREE

---

## 📋 PROBLEMAS ENCONTRADOS

Durante el intento de deployment a Azure, se encontraron los siguientes problemas:

### 1. **Error de Detección de Proyecto por Oryx**
- **Síntoma**: `Error: Could not find the .NET Core project file`
- **Causa**: Oryx build system no detectaba correctamente el proyecto Python
- **Intentos de solución**:
  - ✅ Configurar `PROJECT=backend` (no funcionó)
  - ✅ Usar ZIP deployment (falló en build)
  - ✅ Deshabilitar `SCM_DO_BUILD_DURING_DEPLOYMENT` (aún intentaba build)
  - ❌ Ninguna solución funcionó

### 2. **Error 503 Service Unavailable**
- **Síntoma**: Backend siempre retornaba 503
- **Causa**: Container terminaba con exit code 127 (command not found)
- **Detalle**: `/opt/startup/startup.sh: 26: startup.sh: not found`

### 3. **Estructura de Repositorio**
- **Problema**: Manual integration deployment no maneja subcarpetas correctamente
- **Configuración**: Código en `backend/` y `frontend/` (estructura monorepo)
- **Azure expectativa**: Código en root del repositorio

---

## 💡 LECCIONES APRENDIDAS

### 1. **Azure App Service con Monorepos**
- App Service manual deployment NO funciona bien con monorepos
- El setting `PROJECT` no es confiable con manual integration
- **Recomendación**: Usar GitHub Actions para control completo del build

### 2. **Oryx Build System**
- Oryx puede tener problemas detectando proyectos Python en subcarpetas
- Deshabilitar Oryx build no siempre funciona como esperado
- **Recomendación**: Estructura de repositorio plana o usar contenedores Docker

### 3. **Free Tier Limitations**
- F1 Free tier tiene limitaciones de recursos muy estrictas
- Timeout frecuentes durante el startup
- **Recomendación**: Considerar otros servicios cloud (Railway, Render, Fly.io)

---

## 🎯 ALTERNATIVAS PARA DEPLOYMENT

### Opción 1: GitHub Actions + Azure App Service
```yaml
# .github/workflows/azure-deploy.yml
- Checkout código
- Copiar solo carpeta backend/
- Deploy a Azure
- Control total del proceso
```

### Opción 2: Docker Containers
```dockerfile
# Dockerfile para backend
FROM python:3.11
COPY backend/ /app
...
```
- Deploy a Azure Container Apps
- Más control, más costo

### Opción 3: Otros Servicios Cloud (Recomendado)
- **Railway**: Excelente soporte para monorepos, FREE tier generoso
- **Render**: Similar a Heroku, muy fácil de usar
- **Fly.io**: Buenos precios, excelente para Python
- **Vercel**: Perfecto para Next.js (frontend)

---

## 📊 COSTO FINAL

- **Tiempo usado**: ~3 días (10-12 Nov 2025)
- **Costo Azure**: $0 (solo FREE tier usado)
- **Créditos restantes**: ~$100 USD (Azure for Students)

---

## 📁 ARCHIVOS PRESERVADOS

Los siguientes archivos de deployment se mantienen en el repositorio para referencia:

### Scripts
- ✅ `scripts/deploy-academic-demo.ps1` - Script original de deployment
- ✅ `scripts/configure-backend-env.ps1` - Configuración de variables
- ✅ `scripts/fix-backend-503.ps1` - Intento de solución 1
- ✅ `scripts/fix-backend-final.ps1` - Intento de solución 2
- ✅ `scripts/create-epic-in-azuredevops.ps1` - Script de Azure DevOps

### Documentación
- ✅ `DEPLOYMENT_STATUS.md` - Estado al momento del deployment
- ✅ `DEPLOYMENT_PROGRESS.md` - Progreso del deployment (90%)
- ✅ `ENV_MIGRATION.md` - Guía de migración de variables
- ✅ `.env.production.example` - Template de variables de producción

### Archivos de Configuración
- ✅ `backend/startup.sh` - Script de inicio para Azure
- ✅ `backend/requirements.txt` - Con dependencias de producción
- ✅ `.deployment` - Configuración de Azure deployment

### Archivos Sensibles Eliminados
- ❌ `db_password_demo.txt` - **DEBE SER ELIMINADO**
- ❌ `backend-deploy.zip` - **DEBE SER ELIMINADO**
- ❌ `backend-logs/` - **DEBE SER ELIMINADO**
- ❌ `backend-logs-new/` - **DEBE SER ELIMINADO**

---

## 🔧 PRÓXIMOS PASOS

### Para Deployment Futuro:

1. **Elegir plataforma alternativa**
   - Railway (recomendado para este proyecto)
   - Render
   - Fly.io

2. **Preparar estructura**
   - Considerar mover archivos a root O
   - Crear GitHub Actions workflow

3. **Documentar proceso**
   - Nuevo archivo DEPLOYMENT_GUIDE_[PLATAFORMA].md
   - Actualizar README.md con instrucciones

---

## 📝 NOTAS FINALES

Este intento de deployment a Azure App Service demostró que:

1. ✅ La infraestructura Azure fue creada correctamente (100%)
2. ✅ Todas las variables de entorno se configuraron
3. ✅ El frontend deployó exitosamente
4. ❌ El backend no pudo deployarse debido a limitaciones de Oryx build

**Recomendación**: Para futuras demos académicas, usar plataformas más amigables con monorepos como Railway o Render que tienen mejor soporte para proyectos estructurados en subcarpetas.

---

**Documentado por**: Franco Garcete (fgarcete@alumno.unlam.edu.ar)  
**Proyecto**: Asistente Plantitas - Demo Académica  
**Universidad**: Universidad Nacional de La Matanza  
**Fecha**: 12 de Noviembre de 2025
