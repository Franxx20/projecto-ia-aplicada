"""
Configuración de la aplicación FastAPI

Gestión centralizada de configuración usando Pydantic Settings con soporte
para variables de entorno. Sigue las directrices del proyecto con nomenclatura
en español y principios de seguridad.

Ejemplo de uso:
    >>> from app.core.config import obtener_configuracion
    >>> config = obtener_configuracion()
    >>> print(config.nombre_app)
"""

from pydantic_settings import BaseSettings
from typing import List
import os
from functools import lru_cache


class Configuracion(BaseSettings):
    """
    Configuración principal de la aplicación
    
    Todas las variables pueden ser sobrescritas mediante variables de entorno
    o archivo .env en la raíz del proyecto.
    
    Attributes:
        nombre_app: Nombre de la aplicación
        version: Versión actual
        descripcion: Descripción de la API
        debug: Modo debug (desactivar en producción)
        entorno: Entorno de ejecución (desarrollo, staging, produccion)
    """
    
    # ==================== Información de la Aplicación ====================
    nombre_app: str = "Asistente Plantitas - Backend API"
    version: str = "0.1.0"
    descripcion: str = "API REST para el Asistente de Jardinería y Cuidado de Plantas"
    debug: bool = True
    entorno: str = "desarrollo"  # desarrollo, staging, produccion
    
    # ==================== Base de Datos ====================
    # URL de conexión a la base de datos
    # Desarrollo: SQLite (por defecto)
    # Producción: PostgreSQL (desde variable de entorno DATABASE_URL)
    database_url: str = "sqlite:///./plantitas_dev.db"
    
    # Pool de conexiones (solo para PostgreSQL)
    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_echo: bool = False  # Mostrar queries SQL en logs
    
    # ==================== Seguridad y Autenticación ====================
    # JWT Secret Key - DEBE ser sobrescrito en producción
    jwt_secret_key: str = "CHANGE_THIS_SECRET_KEY_IN_PRODUCTION_USE_ENV_FILE"
    jwt_algorithm: str = "HS256"
    jwt_expiracion_minutos: int = 30  # Tiempo de expiración del token
    jwt_refresh_expiracion_dias: int = 7  # Tiempo de expiración del refresh token
    
    # Password hashing
    bcrypt_rounds: int = 12  # Número de rondas para bcrypt
    
    # ==================== CORS ====================
    # Orígenes permitidos para CORS
    origenes_cors: List[str] = [
        "http://localhost:4200",       # Angular dev server
        "http://localhost:3000",       # Alternativo
        "http://127.0.0.1:4200",
        "http://frontend:80",          # Docker interno
        "http://frontend:4200",        # Docker dev
    ]
    
    # Configuración avanzada de CORS
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
    cors_allow_headers: List[str] = ["*"]
    
    # ==================== Configuración del Servidor ====================
    host: str = "0.0.0.0"
    puerto: int = 8000
    workers: int = 1  # Número de workers de Uvicorn
    
    # ==================== Logging ====================
    nivel_log: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    log_formato: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # ==================== Uploads y Archivos ====================
    directorio_uploads: str = "./uploads"
    max_tamano_archivo_mb: int = 10  # Tamaño máximo de archivo en MB
    formatos_imagen_permitidos: List[str] = ["jpg", "jpeg", "png", "webp"]
    
    # ==================== Azure Blob Storage ====================
    # Configuración para Azure Blob Storage (T-004)
    azure_storage_connection_string: str = ""
    azure_storage_account_name: str = ""
    azure_storage_account_key: str = ""
    azure_storage_container_name: str = "plantitas-imagenes"
    azure_storage_use_emulator: bool = False  # True para usar Azurite en desarrollo
    
    # ==================== APIs Externas ====================
    # PlantNet API (para Sprint 2)
    plantnet_api_key: str = ""
    plantnet_api_url: str = "https://my-api.plantnet.org/v2/identify"
    
    # Azure OpenAI / Claude API (para Sprint 3)
    azure_openai_api_key: str = ""
    azure_openai_endpoint: str = ""
    claude_api_key: str = ""
    
    # ==================== Rate Limiting ====================
    rate_limit_por_minuto: int = 60  # Número máximo de requests por minuto
    
    # ==================== Paginación ====================
    paginacion_tamano_defecto: int = 20
    paginacion_tamano_maximo: int = 100
    
    class Config:
        """Configuración de Pydantic Settings"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False  # No distinguir mayúsculas/minúsculas en vars de entorno
        extra = "allow"  # Permitir campos extra


@lru_cache()
def obtener_configuracion() -> Configuracion:
    """
    Función para obtener la configuración de la aplicación
    
    Usa @lru_cache para garantizar que solo se cree una instancia de
    configuración durante el ciclo de vida de la aplicación (patrón Singleton).
    
    Returns:
        Configuracion: Instancia única de configuración
        
    Example:
        >>> config = obtener_configuracion()
        >>> print(config.nombre_app)
        'Asistente Plantitas - Backend API'
    """
    return Configuracion()


# Instancia global de configuración (mantener compatibilidad con código existente)
configuracion = obtener_configuracion()