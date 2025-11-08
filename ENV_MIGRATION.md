# 📝 Migración de Archivos .env - Configuración Unificada

## 🎯 Objetivo

Se ha unificado toda la configuración del proyecto en un **ÚNICO archivo `.env`** ubicado en la raíz del proyecto. Esto elimina la confusión y los problemas de sincronización causados por tener múltiples archivos `.env` dispersos.

## ✅ Cambios Realizados

### Antes (Configuración Dispersa)
```
projecto-ia-aplicada/
├── .env.example           # Variables de Docker/infraestructura
├── backend/
│   └── .env.example       # Variables del backend
└── frontend/
    └── .env.local.example # Variables del frontend
```

**Problemas identificados:**
- ❌ Tres archivos diferentes para configurar
- ❌ Variables duplicadas entre archivos
- ❌ Difícil mantener sincronización
- ❌ Confusión al primer inicio del proyecto
- ❌ Riesgo de configuraciones inconsistentes

### Después (Configuración Unificada)
```
projecto-ia-aplicada/
├── .env.example           # ÚNICO archivo con TODA la configuración
├── backend/               # Sin archivos .env
└── frontend/              # Sin archivos .env
```

**Beneficios:**
- ✅ Un solo archivo `.env` para todo el proyecto
- ✅ Configuración centralizada y clara
- ✅ Fácil de mantener y actualizar
- ✅ Sin duplicación de variables
- ✅ Mejor experiencia al primer inicio

## 🔧 Archivos Modificados

### 1. `.env.example` (Raíz)
- **Acción**: Unificado y expandido
- **Contenido**: Ahora incluye TODAS las variables necesarias:
  - Información general del proyecto
  - PostgreSQL y base de datos
  - Backend (FastAPI)
  - Frontend (Next.js)
  - Seguridad y JWT
  - CORS
  - Azure Storage / Azurite
  - PlantNet API
  - Google Gemini API
  - Otras APIs de IA
  - Redis
  - Logging
  - Rate limiting
  - Producción

### 2. `backend/app/core/config.py`
- **Acción**: Modificado el path del archivo `.env`
- **Cambio**: Ahora busca `.env` en la raíz del proyecto
  ```python
  env_file = os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env")
  ```
- **Antes**: Buscaba en `backend/.env`
- **Después**: Busca en `projecto-ia-aplicada/.env`

### 3. `docker-compose.yml`
- **Acción**: Agregado comentario explicativo
- **Nota**: Docker Compose ya buscaba el `.env` en la raíz por defecto
- **Sin cambios funcionales**: Solo documentación mejorada

### 4. `docker-compose.dev.yml`
- **Acción**: Agregado comentario explicativo
- **Nota**: Ya estaba correctamente configurado
- **Sin cambios funcionales**: Solo documentación mejorada

### 5. `README.md`
- **Acción**: Actualizado toda la documentación
- **Secciones actualizadas**:
  - Estructura del proyecto (eliminada referencia a `frontend/.env.local`)
  - Configuración de variables de entorno
  - Sección de desarrollo del frontend
  - Azure Storage
  - Troubleshooting
  - Checklist de primer inicio

### 6. Archivos Eliminados
- ❌ `backend/.env.example` - Ya no necesario
- ❌ `frontend/.env.local.example` - Ya no necesario

### 7. Scripts de Gestión
- `manage.sh` y `manage.bat`
- **Acción**: Verificado (ya estaban correctos)
- **Nota**: Ya buscaban `.env` en la raíz

## 📖 Guía de Migración para Desarrolladores

### Si ya tienes archivos `.env` antiguos:

1. **Respalda tus configuraciones actuales**:
   ```bash
   # Si tienes archivos .env existentes, haz backup
   cp .env .env.backup
   cp backend/.env backend/.env.backup 2>/dev/null || true
   cp frontend/.env.local frontend/.env.local.backup 2>/dev/null || true
   ```

2. **Copia el nuevo template**:
   ```bash
   cp .env.example .env
   ```

3. **Migra tus valores personalizados al nuevo .env**:
   - Abre tu backup y el nuevo `.env`
   - Copia tus valores personalizados (API keys, contraseñas, etc.)
   - El nuevo `.env.example` tiene comentarios detallados sobre cada variable

4. **Elimina archivos `.env` antiguos** (opcional pero recomendado):
   ```bash
   rm backend/.env 2>/dev/null || true
   rm frontend/.env.local 2>/dev/null || true
   ```

5. **Reinicia los contenedores**:
   ```bash
   # Windows
   manage.bat restart

   # Linux/Mac
   ./manage.sh restart
   ```

## 🔍 Variables de Entorno Clave

### Backend
```env
DATABASE_URL=sqlite:///./plantitas_dev.db
SECRET_KEY=tu_secret_key_aqui
JWT_SECRET_KEY=tu_jwt_secret_aqui
BACKEND_PORT=8000
```

### Frontend
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
INTERNAL_API_URL=http://backend:8000
FRONTEND_PORT=4200
```

### APIs Externas
```env
PLANTNET_API_KEY=tu_api_key_aqui
GEMINI_API_KEY=tu_api_key_aqui
```

### Azure Storage (Desarrollo)
```env
AZURE_STORAGE_USE_EMULATOR=true
AZURE_STORAGE_CONTAINER_NAME=plantitas-imagenes
```

## ✨ Beneficios de la Unificación

1. **Simplicidad**: Un solo archivo para configurar
2. **Consistencia**: Mismos valores en todo el stack
3. **Mantenibilidad**: Cambios en un solo lugar
4. **Documentación**: Comentarios claros en un solo archivo
5. **Onboarding**: Más fácil para nuevos desarrolladores
6. **Menos errores**: Sin problemas de sincronización

## 🆘 Solución de Problemas

### El backend no encuentra las variables
**Causa**: Backend busca el `.env` en la raíz, no en `backend/.env`

**Solución**:
```bash
# Asegúrate de que .env esté en la raíz
ls -la .env  # Linux/Mac
dir .env     # Windows

# Si está en backend/, muévelo
mv backend/.env ./.env
```

### El frontend no encuentra NEXT_PUBLIC_API_URL
**Causa**: Frontend también lee del `.env` de la raíz

**Solución**:
```bash
# Verifica que la variable esté en el .env de la raíz
grep NEXT_PUBLIC_API_URL .env

# Asegúrate de que tenga el prefijo NEXT_PUBLIC_
# Variables sin este prefijo no se exponen al cliente
```

### Docker Compose no lee las variables
**Causa**: Docker Compose busca `.env` en el mismo directorio que `docker-compose.yml`

**Solución**:
```bash
# El .env debe estar en la raíz (mismo nivel que docker-compose.yml)
ls -la docker-compose.yml .env

# Ambos archivos deben estar en la raíz
```

## 📚 Referencias

- [Documentación de Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [Variables de entorno en Next.js](https://nextjs.org/docs/app/building-your-application/configuring/environment-variables)
- [Docker Compose .env file](https://docs.docker.com/compose/environment-variables/set-environment-variables/)

## 🎉 Conclusión

Esta migración simplifica significativamente la configuración del proyecto. Ahora solo necesitas un archivo `.env` en la raíz del proyecto para configurar todo: backend, frontend, Docker, APIs externas, etc.

Para cualquier duda, revisa el archivo `.env.example` que contiene comentarios detallados sobre cada variable.
