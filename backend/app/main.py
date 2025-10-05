"""
Aplicación principal FastAPI - Asistente Plantitas

Backend API REST para el sistema de gestión y cuidado de plantas con IA.
Implementa arquitectura MVC con FastAPI, SQLAlchemy y Pydantic.

Estructura del proyecto:
    /api - Endpoints REST organizados por recursos
    /core - Configuración y componentes centrales
    /db - Modelos de base de datos (SQLAlchemy)
    /schemas - Modelos de validación (Pydantic)
    /services - Lógica de negocio
    /utils - Utilidades y helpers

Author: Equipo Plantitas
Date: Octubre 2025
Version: 0.1.0 (Sprint 1 - T-001)
"""

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import datetime
import os
import sys

# Importar configuración
from .core.config import obtener_configuracion

# Obtener configuración de la aplicación
configuracion = obtener_configuracion()


def crear_aplicacion() -> FastAPI:
    """
    Factory function para crear y configurar la aplicación FastAPI
    
    Crea la instancia de FastAPI con toda la configuración necesaria,
    middleware, y routers. Sigue el patrón de Application Factory.
    
    Returns:
        FastAPI: Instancia configurada de la aplicación
        
    Example:
        >>> app = crear_aplicacion()
        >>> # Usar con uvicorn: uvicorn app.main:app
    """
    
    # Crear instancia de FastAPI con metadata
    aplicacion = FastAPI(
        title=configuracion.nombre_app,
        description=configuracion.descripcion,
        version=configuracion.version,
        debug=configuracion.debug,
        docs_url="/docs" if configuracion.debug else None,  # Deshabilitar docs en prod
        redoc_url="/redoc" if configuracion.debug else None,
        openapi_url="/openapi.json" if configuracion.debug else None,
    )
    
    # ==================== Configurar CORS ====================
    aplicacion.add_middleware(
        CORSMiddleware,
        allow_origins=configuracion.origenes_cors,
        allow_credentials=configuracion.cors_allow_credentials,
        allow_methods=configuracion.cors_allow_methods,
        allow_headers=configuracion.cors_allow_headers,
    )
    
    # ==================== Registrar Routers ====================
    # TODO: Agregar routers de la carpeta /api cuando se implementen
    # from .api import auth_router, usuarios_router, plantas_router
    # aplicacion.include_router(auth_router, prefix="/api/auth", tags=["Autenticación"])
    # aplicacion.include_router(usuarios_router, prefix="/api/usuarios", tags=["Usuarios"])
    # aplicacion.include_router(plantas_router, prefix="/api/plantas", tags=["Plantas"])
    
    return aplicacion


# Crear instancia de la aplicación
app = crear_aplicacion()


# ==================== Endpoints Base ====================

@app.get(
    "/",
    summary="Endpoint raíz",
    description="Endpoint de bienvenida que confirma que la API está funcionando",
    response_description="Información básica de la API",
    status_code=status.HTTP_200_OK,
    tags=["Sistema"]
)
async def endpoint_raiz():
    """
    Endpoint raíz de bienvenida
    
    Retorna información básica sobre la API y enlaces a recursos importantes.
    
    Returns:
        dict: Información de bienvenida y enlaces útiles
    """
    return {
        "mensaje": f"¡Bienvenido a {configuracion.nombre_app}!",
        "version": configuracion.version,
        "estado": "funcionando",
        "entorno": configuracion.entorno,
        "timestamp": datetime.datetime.now().isoformat(),
        "documentacion": {
            "swagger_ui": "/docs",
            "redoc": "/redoc",
            "openapi_json": "/openapi.json"
        },
        "endpoints_disponibles": {
            "salud": "/salud",
            "info": "/info",
            "metricas": "/metricas"
        }
    }


@app.get(
    "/salud",
    summary="Health Check",
    description="Endpoint de health check para verificar el estado del servicio",
    response_description="Estado del servicio y sus dependencias",
    status_code=status.HTTP_200_OK,
    tags=["Sistema"]
)
async def health_check():
    """
    Health check endpoint
    
    Verifica el estado del servicio y sus dependencias (base de datos, APIs externas).
    Usado por sistemas de monitoreo, orchestradores (Kubernetes), y load balancers.
    
    Returns:
        dict: Estado detallado del servicio
        
    Status Codes:
        200: Servicio funcionando correctamente
        503: Servicio no disponible
    """
    
    # TODO: Agregar checks de base de datos cuando se implemente en T-002
    # db_status = await verificar_conexion_base_datos()
    
    estado_servicio = {
        "estado": "saludable",
        "servicio": "asistente-plantitas-api",
        "version": configuracion.version,
        "entorno": configuracion.entorno,
        "timestamp": datetime.datetime.now().isoformat(),
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
                "mensaje": f"Directorio uploads: {configuracion.directorio_uploads}"
            }
        }
    }
    
    # Verificar si todos los componentes están operacionales
    todos_operacionales = all(
        comp["estado"] in ["operacional", "pendiente"]
        for comp in estado_servicio["componentes"].values()
    )
    
    if not todos_operacionales:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=estado_servicio
        )
    
    return estado_servicio


@app.get(
    "/info",
    summary="Información del sistema",
    description="Información detallada del sistema, configuración y ambiente",
    response_description="Información técnica del sistema",
    status_code=status.HTTP_200_OK,
    tags=["Sistema"]
)
async def info_sistema():
    """
    Información detallada del sistema
    
    Proporciona información técnica sobre la configuración, ambiente y
    dependencias del sistema. Útil para debugging y monitoreo.
    
    Returns:
        dict: Información completa del sistema
        
    Note:
        Este endpoint puede exponer información sensible. 
        Considerar restringir acceso en producción.
    """
    return {
        "aplicacion": {
            "nombre": configuracion.nombre_app,
            "version": configuracion.version,
            "descripcion": configuracion.descripcion,
            "entorno": configuracion.entorno,
            "debug": configuracion.debug
        },
        "sistema": {
            "python_version": f"{sys.version}",
            "plataforma": sys.platform,
            "directorio_actual": os.getcwd(),
            "directorio_uploads": configuracion.directorio_uploads,
        },
        "base_datos": {
            "url": configuracion.url_base_datos.split("://")[0] + "://*****",  # Ocultar credenciales
            "pool_size": configuracion.db_pool_size,
            "echo": configuracion.db_echo
        },
        "seguridad": {
            "jwt_algorithm": configuracion.jwt_algorithm,
            "jwt_expiracion_minutos": configuracion.jwt_expiracion_minutos,
            "cors_origins": configuracion.origenes_cors
        },
        "timestamp": datetime.datetime.now().isoformat()
    }


@app.get(
    "/metricas",
    summary="Métricas del sistema",
    description="Métricas básicas de uso y rendimiento",
    response_description="Métricas de la aplicación",
    status_code=status.HTTP_200_OK,
    tags=["Sistema"]
)
async def metricas_sistema():
    """
    Métricas del sistema
    
    Retorna métricas básicas de uso y rendimiento de la aplicación.
    En una implementación completa, esto se integraría con herramientas
    como Prometheus o Application Insights.
    
    Returns:
        dict: Métricas del sistema
        
    Note:
        Implementación básica para Sprint 1. 
        Expandir con métricas reales en sprints futuros.
    """
    return {
        "aplicacion": configuracion.nombre_app,
        "version": configuracion.version,
        "metricas": {
            "uptime": "calculado_en_tiempo_real",  # TODO: Implementar uptime real
            "requests_totales": "N/A",  # TODO: Implementar contador de requests
            "requests_exitosas": "N/A",
            "requests_fallidas": "N/A",
            "tiempo_respuesta_promedio_ms": "N/A"
        },
        "recursos": {
            "memoria_uso": "N/A",  # TODO: Implementar con psutil
            "cpu_uso": "N/A"
        },
        "timestamp": datetime.datetime.now().isoformat(),
        "nota": "Métricas básicas - Sprint 1. Expandir en siguientes sprints."
    }


# ==================== Event Handlers ====================

@app.on_event("startup")
async def startup_event():
    """
    Evento ejecutado al iniciar la aplicación
    
    Inicializa recursos necesarios como:
    - Conexión a base de datos
    - Creación de directorios necesarios
    - Inicialización de servicios externos
    """
    print("=" * 60)
    print(f"🚀 Iniciando {configuracion.nombre_app}")
    print(f"📝 Versión: {configuracion.version}")
    print(f"🌍 Entorno: {configuracion.entorno}")
    print(f"🔧 Debug: {configuracion.debug}")
    print(f"🌐 Host: {configuracion.host}:{configuracion.puerto}")
    print(f"📚 Documentación: http://{configuracion.host}:{configuracion.puerto}/docs")
    print("=" * 60)
    
    # Crear directorio de uploads si no existe
    if not os.path.exists(configuracion.directorio_uploads):
        os.makedirs(configuracion.directorio_uploads)
        print(f"✅ Directorio de uploads creado: {configuracion.directorio_uploads}")
    
    # TODO: Inicializar conexión a base de datos (T-002)
    # TODO: Verificar APIs externas (T-012 en Sprint 2)


@app.on_event("shutdown")
async def shutdown_event():
    """
    Evento ejecutado al cerrar la aplicación
    
    Limpia recursos y cierra conexiones:
    - Cierre de conexiones a base de datos
    - Limpieza de archivos temporales
    - Guardado de métricas
    """
    print("=" * 60)
    print(f"� Cerrando {configuracion.nombre_app}")
    print("👋 Hasta pronto!")
    print("=" * 60)
    
    # TODO: Cerrar conexión a base de datos
    # TODO: Guardar métricas finales