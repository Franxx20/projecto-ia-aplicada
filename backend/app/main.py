"""
Aplicación principal FastAPI - Backend Básico

Servidor básico para pruebas de funcionamiento con Docker y comunicación
con frontend y base de datos.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import datetime
import os

# Importar configuración
try:
    from .core.config import obtener_configuracion
    configuracion = obtener_configuracion()
except ImportError:
    # Fallback si hay problemas con imports
    class ConfiguracionBasica:
        nombre_app = "Backend FastAPI - Proyecto IA Aplicada"
        version = "0.1.0"
        descripcion = "API backend básica para proyecto de IA aplicada"
        origenes_cors = ["*"]  # Permitir todos para pruebas
        debug = True
    
    configuracion = ConfiguracionBasica()


# Crear instancia de FastAPI
app = FastAPI(
    title=configuracion.nombre_app,
    description=configuracion.descripcion,
    version=configuracion.version,
    debug=configuracion.debug
)

# Configurar CORS para comunicación con frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=configuracion.origenes_cors,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


@app.get("/", 
         summary="Endpoint raíz",
         description="Endpoint de bienvenida del backend")
async def endpoint_raiz():
    """
    Endpoint raíz que confirma que el backend está funcionando
    
    Returns:
        dict: Información básica del backend
    """
    return {
        "mensaje": f"¡Hola desde {configuracion.nombre_app}!",
        "version": configuracion.version,
        "estado": "funcionando",
        "timestamp": datetime.datetime.now().isoformat(),
        "endpoints_disponibles": {
            "salud": "/salud",
            "info": "/info",
            "test_db": "/test-db",
            "test_frontend": "/test-frontend"
        }
    }


@app.get("/salud",
         summary="Health Check",
         description="Endpoint para verificar el estado del servidor")
async def health_check():
    """
    Health check endpoint para verificar que el servidor está funcionando
    
    Returns:
        dict: Estado del servidor
    """
    return {
        "estado": "saludable",
        "servicio": "backend-fastapi",
        "timestamp": datetime.datetime.now().isoformat(),
        "version": configuracion.version,
        "uptime": "funcionando correctamente"
    }


@app.get("/info",
         summary="Información del sistema",
         description="Información detallada del sistema y configuración")
async def info_sistema():
    """
    Información del sistema para debugging
    
    Returns:
        dict: Información del sistema
    """
    return {
        "aplicacion": {
            "nombre": configuracion.nombre_app,
            "version": configuracion.version,
            "descripcion": configuracion.descripcion,
            "debug": configuracion.debug
        },
        "sistema": {
            "python_version": f"{os.sys.version}",
            "directorio_actual": os.getcwd(),
            "variables_entorno": {
                "PATH_exists": "PATH" in os.environ,
                "HOME_exists": "HOME" in os.environ or "USERPROFILE" in os.environ
            }
        },
        "timestamp": datetime.datetime.now().isoformat()
    }


@app.get("/test-db",
         summary="Test de base de datos",
         description="Prueba básica de conexión a base de datos")
async def test_base_datos():
    """
    Test básico de base de datos
    
    Returns:
        dict: Estado de la conexión a base de datos
    """
    try:
        # Simulación de conexión a BD - en implementación real usaríamos SQLAlchemy
        estado_bd = "conectado"
        mensaje = "Base de datos SQLite funcionando correctamente"
        
        return {
            "estado": estado_bd,
            "mensaje": mensaje,
            "tipo_bd": "SQLite (desarrollo)",
            "url_bd": "sqlite:///./test_db.sqlite",
            "timestamp": datetime.datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "estado": "error",
            "mensaje": f"Error de conexión: {str(e)}",
            "timestamp": datetime.datetime.now().isoformat()
        }


@app.get("/test-frontend",
         summary="Test de comunicación con frontend",
         description="Endpoint para probar la comunicación con el frontend")
async def test_comunicacion_frontend():
    """
    Endpoint para probar la comunicación con el frontend
    
    Returns:
        dict: Datos de prueba para el frontend
    """
    return {
        "mensaje": "Comunicación exitosa con el backend",
        "datos_prueba": {
            "usuarios_activos": 5,
            "estadisticas": {
                "requests_hoy": 42,
                "uptime_horas": 1.5
            },
            "configuracion_cors": configuracion.origenes_cors
        },
        "timestamp": datetime.datetime.now().isoformat(),
        "backend_url": "http://localhost:8000"
    }


@app.get("/api/test",
         summary="Test API endpoint",
         description="Endpoint de prueba para APIs")
async def test_api():
    """
    Endpoint de prueba para verificar rutas API
    
    Returns:
        dict: Respuesta de prueba de API
    """
    return {
        "api_status": "funcionando",
        "mensaje": "API endpoint funcionando correctamente",
        "rutas_disponibles": [
            "/",
            "/salud", 
            "/info",
            "/test-db",
            "/test-frontend",
            "/api/test"
        ],
        "timestamp": datetime.datetime.now().isoformat()
    }


# Función principal para ejecutar el servidor
if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Iniciando servidor FastAPI...")
    print(f"📝 Aplicación: {configuracion.nombre_app}")
    print(f"🌐 URL: http://localhost:8000")
    print(f"📚 Documentación: http://localhost:8000/docs")
    print("🔧 Para detener: Ctrl+C")
    print("-" * 50)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )