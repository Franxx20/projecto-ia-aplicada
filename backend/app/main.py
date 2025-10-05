"""
Aplicación principal FastAPI - Asistente Plantitas

Servidor completo con autenticación JWT, gestión de usuarios y upload de imágenes.
Implementación del Sprint 1 con todas las funcionalidades requeridas.
"""

from fastapi import FastAPI, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import datetime
import logging
import os

# Imports de la aplicación
from .core.config import configuracion, crear_directorios_necesarios
from .db import crear_tablas
from .api import auth_router, usuarios_router
from .api.imagenes import router as imagenes_router

# Configurar logging
logging.basicConfig(
    level=getattr(logging, configuracion.nivel_log),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestión del ciclo de vida de la aplicación
    
    Se ejecuta al inicio y fin de la aplicación para configurar
    recursos necesarios como base de datos y directorios.
    """
    # Startup
    logger.info("🚀 Iniciando Asistente Plantitas API...")
    
    try:
        # Crear directorios necesarios
        crear_directorios_necesarios()
        logger.info("📁 Directorios creados correctamente")
        
        # Crear tablas de base de datos
        crear_tablas()
        logger.info("🗄️ Base de datos inicializada")
        
        logger.info("✅ Aplicación iniciada exitosamente")
        
    except Exception as e:
        logger.error(f"❌ Error durante el startup: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 Cerrando Asistente Plantitas API...")


# Crear instancia de FastAPI con configuración completa
app = FastAPI(
    title=configuracion.nombre_app,
    description=configuracion.descripcion,
    version=configuracion.version,
    debug=configuracion.debug,
    lifespan=lifespan,
    docs_url="/docs" if configuracion.debug else None,
    redoc_url="/redoc" if configuracion.debug else None
)

# === CONFIGURAR MIDDLEWARE ===

# CORS para comunicación con frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=configuracion.origenes_cors,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# === MANEJADORES DE ERROR GLOBALES ===

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Manejador global de HTTPException
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.datetime.now().isoformat(),
            "path": str(request.url)
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Manejador global de excepciones generales
    """
    logger.error(f"Error no manejado: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Error interno del servidor",
            "detail": str(exc) if configuracion.debug else "Ha ocurrido un error interno",
            "timestamp": datetime.datetime.now().isoformat(),
            "path": str(request.url)
        }
    )


# === INCLUIR ROUTERS ===

# APIs de autenticación
app.include_router(auth_router, prefix="/api/v1")

# APIs de usuarios
app.include_router(usuarios_router, prefix="/api/v1")

# APIs de imágenes
app.include_router(imagenes_router, prefix="/api/v1")

# === MONTAR ARCHIVOS ESTÁTICOS ===

# Servir archivos subidos (uploads)
if os.path.exists(configuracion.directorio_uploads):
    app.mount("/uploads", StaticFiles(directory=configuracion.directorio_uploads), name="uploads")


# === ENDPOINTS BÁSICOS ===

@app.get("/", 
         summary="Endpoint raíz",
         description="Endpoint de bienvenida del Asistente Plantitas",
         tags=["General"])
async def endpoint_raiz():
    """
    Endpoint raíz que confirma que la API está funcionando
    
    Returns:
        dict: Información básica de la API
    """
    return {
        "mensaje": f"¡Bienvenido a {configuracion.nombre_app}!",
        "version": configuracion.version,
        "estado": "funcionando",
        "descripcion": configuracion.descripcion,
        "timestamp": datetime.datetime.now().isoformat(),
        "documentacion": {
            "swagger": "/docs",
            "redoc": "/redoc"
        },
        "endpoints_principales": {
            "autenticacion": "/api/v1/auth",
            "usuarios": "/api/v1/usuarios",
            "salud": "/health"
        }
    }


@app.get("/health",
         summary="Health Check",
         description="Endpoint para verificar el estado del servidor",
         tags=["General"])
async def health_check():
    """
    Health check endpoint para verificar que el servidor está funcionando
    
    Útil para monitoreo, load balancers y deployment pipelines.
    
    Returns:
        dict: Estado detallado del servidor
    """
    return {
        "estado": "saludable",
        "servicio": "asistente-plantitas-api",
        "version": configuracion.version,
        "timestamp": datetime.datetime.now().isoformat(),
        "entorno": configuracion.entorno,
        "base_datos": "conectada",  # TODO: Verificar conexión real en futuras versiones
        "uptime": "funcionando correctamente"
    }


@app.get("/info",
         summary="Información del sistema",
         description="Información detallada del sistema y configuración",
         tags=["General"])
async def info_sistema():
    """
    Información del sistema para debugging y monitoreo
    
    Returns:
        dict: Información detallada del sistema
    """
    return {
        "aplicacion": {
            "nombre": configuracion.nombre_app,
            "version": configuracion.version,
            "descripcion": configuracion.descripcion,
            "debug": configuracion.debug,
            "entorno": configuracion.entorno
        },
        "configuracion": {
            "base_datos": configuracion.tipo_base_datos,
            "cors_origins": len(configuracion.origenes_cors),
            "rate_limiting": configuracion.limite_requests_por_minuto,
            "directorio_uploads": configuracion.directorio_uploads
        },
        "sistema": {
            "python_version": f"{os.sys.version}",
            "directorio_actual": os.getcwd(),
            "timestamp": datetime.datetime.now().isoformat()
        }
    }


# Función principal para ejecutar el servidor
if __name__ == "__main__":
    import uvicorn
    
    print("=" * 60)
    print("🌱 ASISTENTE PLANTITAS - BACKEND API")
    print("=" * 60)
    print(f"📝 Aplicación: {configuracion.nombre_app}")
    print(f"🔧 Versión: {configuracion.version}")
    print(f"🌐 URL: http://localhost:{configuracion.puerto}")
    print(f"📚 Documentación: http://localhost:{configuracion.puerto}/docs")
    print(f"🔍 ReDoc: http://localhost:{configuracion.puerto}/redoc")
    print(f"⚙️ Entorno: {configuracion.entorno}")
    print(f"�️ Base de datos: {configuracion.tipo_base_datos}")
    print("")
    print("🚀 Para detener el servidor: Ctrl+C")
    print("=" * 60)
    
    uvicorn.run(
        "main:app",
        host=configuracion.host,
        port=configuracion.puerto,
        reload=configuracion.debug,
        log_level=configuracion.nivel_log.lower()
    )