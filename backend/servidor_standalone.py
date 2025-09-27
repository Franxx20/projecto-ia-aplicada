#!/usr/bin/env python3
"""
Servidor FastAPI Básico Standalone

Este archivo funciona de forma independiente para pruebas.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import datetime
import uvicorn
import os

# Crear aplicación FastAPI
app = FastAPI(
    title="Backend FastAPI - Proyecto IA Aplicada",
    description="API backend básica para proyecto de IA aplicada - STANDALONE",
    version="0.1.0",
    debug=True
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",
        "http://localhost:3000",
        "http://127.0.0.1:4200",
        "http://frontend:80",
        "*"  # Para pruebas
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Endpoints básicos
@app.get("/")
async def endpoint_raiz():
    return {
        "mensaje": "¡Hola desde el Backend FastAPI!",
        "version": "0.1.0",
        "estado": "funcionando",
        "timestamp": datetime.datetime.now().isoformat(),
        "endpoints": {
            "salud": "/salud",
            "info": "/info", 
            "docs": "/docs",
            "test_frontend": "/test-frontend"
        }
    }

@app.get("/salud")
async def health_check():
    return {
        "estado": "saludable",
        "servicio": "backend-fastapi-standalone",
        "timestamp": datetime.datetime.now().isoformat(),
        "version": "0.1.0",
        "mensaje": "Backend funcionando correctamente"
    }

@app.get("/info")
async def info_sistema():
    return {
        "aplicacion": "Backend FastAPI - Proyecto IA Aplicada",
        "version": "0.1.0",
        "python_version": f"{os.sys.version}",
        "directorio_actual": os.getcwd(),
        "timestamp": datetime.datetime.now().isoformat()
    }

@app.get("/test-frontend")
async def test_comunicacion_frontend():
    return {
        "mensaje": "Comunicación exitosa con el backend",
        "backend_funcionando": True,
        "datos_prueba": {
            "usuarios_activos": 5,
            "estadisticas": {
                "requests_hoy": 42,
                "uptime_horas": 1.5
            }
        },
        "timestamp": datetime.datetime.now().isoformat(),
        "backend_url": "http://localhost:8001"
    }

@app.get("/test-db")
async def test_base_datos():
    return {
        "estado": "simulado",
        "mensaje": "Base de datos SQLite simulada funcionando correctamente",
        "tipo_bd": "SQLite (desarrollo)",
        "timestamp": datetime.datetime.now().isoformat()
    }

if __name__ == "__main__":
    print("🚀 Iniciando Backend FastAPI Standalone...")
    print("📝 Aplicación: Backend FastAPI - Proyecto IA Aplicada")
    print("🌐 URL: http://localhost:8001")
    print("📚 Documentación: http://localhost:8001/docs")
    print("🔧 Health Check: http://localhost:8001/salud")
    print("")
    print("Para detener el servidor, presiona Ctrl+C")
    print("-" * 50)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        reload=False,
        access_log=True
    )