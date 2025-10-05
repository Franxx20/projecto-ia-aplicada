"""
Configuración principal de la aplicación FastAPI

Siguiendo las convenciones del proyecto con nomenclatura en español.
Configuración para autenticación JWT, base de datos PostgreSQL y Azure.
"""

from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from typing import List, Optional, Union
import os
from pathlib import Path


class Configuracion(BaseSettings):
    """
    Configuración principal de la aplicación con todas las settings necesarias
    para el Sprint 1: autenticación, base de datos, upload de imágenes.
    """
    
    # === INFORMACIÓN DE LA APLICACIÓN ===
    nombre_app: str = Field(default="Asistente Plantitas API", alias="app_name")
    version: str = Field(default="1.0.0", alias="app_version")
    descripcion: str = "API backend para el asistente inteligente de jardinería"
    debug: bool = True
    
    # === CONFIGURACIÓN DE SERVIDOR ===
    host: str = "0.0.0.0"
    puerto: int = Field(default=8000, alias="port")
    
    # === CONFIGURACIÓN DE BASE DE DATOS ===
    # PostgreSQL para producción, SQLite para desarrollo
    tipo_base_datos: str = "postgresql"  # postgresql | sqlite
    
    # Campo para recibir DATABASE_URL del entorno (Docker, etc.)
    database_url: Optional[str] = Field(default=None, alias="DATABASE_URL")
    
    # PostgreSQL settings
    postgres_usuario: str = "plantitas_user"
    postgres_password: str = "plantitas_password"
    postgres_servidor: str = "localhost"
    postgres_puerto: str = "5432"
    postgres_base_datos: str = "plantitas_db"
    
    @property
    def url_base_datos(self) -> str:
        """
        Construye la URL de conexión a la base de datos
        """
        # Si se proporciona DATABASE_URL del entorno, usarla
        if self.database_url:
            return self.database_url
            
        if self.tipo_base_datos == "postgresql":
            return f"postgresql://{self.postgres_usuario}:{self.postgres_password}@{self.postgres_servidor}:{self.postgres_puerto}/{self.postgres_base_datos}"
        else:
            # SQLite para desarrollo
            return "sqlite:///./plantitas_dev.db"
    
    # === CONFIGURACIÓN JWT Y SEGURIDAD ===
    clave_secreta_jwt: str = Field(default="tu-clave-secreta-super-segura-cambiar-en-produccion", alias="SECRET_KEY")
    algoritmo_jwt: str = Field(default="HS256", alias="ALGORITHM")
    tiempo_expiracion_token: int = Field(default=30, alias="ACCESS_TOKEN_EXPIRE_MINUTES")  # minutos
    tiempo_expiracion_refresh: int = 7  # días
    
    # === CONFIGURACIÓN CORS ===
    origenes_cors: Union[List[str], str] = Field(
        default=[
            "http://localhost:4200",  # Angular dev
            "http://localhost:3000",  # React dev (si aplica)
            "http://127.0.0.1:4200",
            "http://frontend:80",     # Docker
            "https://plantitas-frontend.azurewebsites.net"  # Producción
        ],
        alias="CORS_ORIGINS"
    )
    
    @field_validator('origenes_cors')
    @classmethod
    def validate_cors_origins(cls, v):
        """Convierte string separado por comas en lista"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',') if origin.strip()]
        return v
    
    # === CONFIGURACIÓN DE AZURE BLOB STORAGE ===
    azure_storage_account: Optional[str] = None
    azure_storage_key: Optional[str] = None
    azure_storage_container: str = "imagenes-plantas"
    azure_storage_connection_string: Optional[str] = None
    usar_azure_storage: bool = False  # True para usar Azure, False para almacenamiento local
    
    # === CONFIGURACIÓN DE UPLOAD DE ARCHIVOS ===
    directorio_uploads: str = "./uploads"
    tamaño_maximo_archivo: int = 10 * 1024 * 1024  # 10MB
    tipos_archivos_permitidos: List[str] = ["jpg", "jpeg", "png", "webp"]
    
    # === CONFIGURACIÓN DE RATE LIMITING ===
    limite_requests_por_minuto: int = 60
    limite_login_por_minuto: int = 5
    
    # === CONFIGURACIÓN DE LOGGING ===
    nivel_log: str = "INFO"
    directorio_logs: str = "./logs"
    
    # === CONFIGURACIÓN DE DESARROLLO ===
    # Para activar middleware de desarrollo, logging detallado, etc.
    entorno: str = "desarrollo"  # desarrollo | produccion
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore"  # Ignorar campos extra en lugar de fallar
    }


# Configuración para diferentes entornos
class ConfiguracionDesarrollo(Configuracion):
    """Configuración específica para desarrollo"""
    debug: bool = True
    tipo_base_datos: str = "sqlite"
    nivel_log: str = "DEBUG"
    entorno: str = "desarrollo"


class ConfiguracionProduccion(Configuracion):
    """Configuración específica para producción"""
    debug: bool = False
    tipo_base_datos: str = "postgresql"
    nivel_log: str = "WARNING"
    entorno: str = "produccion"
    
    # En producción, estas variables DEBEN venir del entorno
    clave_secreta_jwt: str
    postgres_password: str
    azure_storage_connection_string: str


def obtener_configuracion() -> Configuracion:
    """
    Factory function para obtener la configuración según el entorno
    
    Returns:
        Configuracion: Instancia de configuración apropiada
    """
    entorno = os.getenv("ENTORNO", "desarrollo").lower()
    
    if entorno == "produccion":
        return ConfiguracionProduccion()
    else:
        return ConfiguracionDesarrollo()


# Instancia global de configuración
configuracion = obtener_configuracion()


# Función helper para crear directorios necesarios
def crear_directorios_necesarios():
    """
    Crea los directorios necesarios para uploads y logs
    """
    Path(configuracion.directorio_uploads).mkdir(parents=True, exist_ok=True)
    Path(configuracion.directorio_logs).mkdir(parents=True, exist_ok=True)