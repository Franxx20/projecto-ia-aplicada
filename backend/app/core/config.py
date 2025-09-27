"""
Configuración básica de la aplicación FastAPI

Siguiendo las instrucciones del proyecto con nomenclatura en español.
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Configuracion(BaseSettings):
    """
    Configuración principal de la aplicación
    """
    # Información de la aplicación
    nombre_app: str = "Backend FastAPI - Proyecto IA Aplicada"
    version: str = "0.1.0"
    descripcion: str = "API backend básica para proyecto de IA aplicada"
    debug: bool = True
    
    # Base de datos - usar SQLite por defecto para pruebas
    url_base_datos: str = "sqlite:///./test_db.sqlite"
    
    # CORS - permitir orígenes del frontend
    origenes_cors: List[str] = [
        "http://localhost:4200",
        "http://localhost:3000", 
        "http://127.0.0.1:4200",
        "http://frontend:80"  # Para Docker
    ]
    
    # Configuración de servidor
    host: str = "0.0.0.0"
    puerto: int = 8000
    
    # Logging
    nivel_log: str = "INFO"
    
    class Config:
        env_file = ".env"
        extra = "allow"  # Permitir campos extra


# Instancia global de configuración
configuracion = Configuracion()


def obtener_configuracion() -> Configuracion:
    """
    Función para obtener la configuración de la aplicación
    
    Returns:
        Configuracion: Instancia de configuración
    """
    return configuracion