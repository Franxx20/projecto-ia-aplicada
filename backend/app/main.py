"""
Punto de entrada principal de la aplicación FastAPI
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from datetime import datetime

# Configuración de la aplicación
app = FastAPI(
    title="Proyecto IA Aplicada API",
    description="API backend para el proyecto de Inteligencia Artificial Aplicada",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuración CORS
origins = os.getenv("CORS_ORIGINS", "http://localhost:4200,http://localhost:80").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rutas básicas
@app.get("/")
async def root():
    """Endpoint raíz - Health check básico"""
    return {
        "message": "Proyecto IA Aplicada API",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Health check para Docker"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "backend"
    }

# Rutas de la API
@app.get("/api/v1/")
async def api_info():
    """Información de la API"""
    return {
        "api": "Proyecto IA Aplicada",
        "version": "v1",
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/health"
        }
    }

# Manejo de errores
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Manejo personalizado de errores 404"""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Endpoint no encontrado",
            "message": f"La ruta {request.url.path} no existe",
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Manejo personalizado de errores 500"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Error interno del servidor",
            "message": "Ha ocurrido un error inesperado",
            "timestamp": datetime.now().isoformat()
        }
    )

if __name__ == "__main__":
    import uvicorn
    
    # Configuración para desarrollo
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )