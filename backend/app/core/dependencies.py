"""
Dependencias para autenticación y seguridad

Contiene todas las dependencias que se usan en los endpoints
para validar autenticación, rate limiting, etc.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import redis

from ..db import obtener_db
from ..db.models import Usuario
from ..services.auth import servicio_auth
from ..core.config import configuracion

# Configurar rate limiting
redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])

# Configurar esquema de seguridad Bearer
security = HTTPBearer()


async def obtener_usuario_actual(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(obtener_db)
) -> Usuario:
    """
    Dependency para obtener el usuario actual desde el token JWT
    
    Args:
        credentials: Credenciales HTTP Bearer
        db: Sesión de base de datos
        
    Returns:
        Usuario: Usuario autenticado
        
    Raises:
        HTTPException: Si el token es inválido o el usuario no existe
    """
    try:
        # Extraer token del header Authorization
        token = credentials.credentials
        
        # Obtener usuario desde token
        usuario = servicio_auth.obtener_usuario_desde_token(token, db)
        
        return usuario
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def obtener_usuario_activo(
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
) -> Usuario:
    """
    Dependency para verificar que el usuario esté activo
    
    Args:
        usuario_actual: Usuario desde token
        
    Returns:
        Usuario: Usuario activo
        
    Raises:
        HTTPException: Si el usuario está inactivo
    """
    if not usuario_actual.activo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo"
        )
    
    return usuario_actual


async def obtener_usuario_verificado(
    usuario_actual: Usuario = Depends(obtener_usuario_activo)
) -> Usuario:
    """
    Dependency para verificar que el usuario esté verificado
    
    Args:
        usuario_actual: Usuario activo
        
    Returns:
        Usuario: Usuario verificado
        
    Raises:
        HTTPException: Si el usuario no está verificado
    """
    if not usuario_actual.verificado:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario no verificado"
        )
    
    return usuario_actual


def obtener_usuario_opcional(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(obtener_db)
) -> Usuario:
    """
    Dependency opcional para obtener usuario (no falla si no hay token)
    
    Args:
        credentials: Credenciales HTTP Bearer (opcional)
        db: Sesión de base de datos
        
    Returns:
        Usuario: Usuario autenticado o None
    """
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        usuario = servicio_auth.obtener_usuario_desde_token(token, db)
        return usuario
    except:
        return None


def rate_limit_auth(limiter=Depends(lambda: limiter)):
    """
    Rate limiting específico para endpoints de autenticación
    
    Args:
        limiter: Instancia del limiter
    """
    return limiter


# Dependency para verificar si es admin (para futuras implementaciones)
async def verificar_admin(
    usuario_actual: Usuario = Depends(obtener_usuario_activo)
) -> Usuario:
    """
    Dependency para verificar permisos de administrador
    
    Args:
        usuario_actual: Usuario activo
        
    Returns:
        Usuario: Usuario admin
        
    Raises:
        HTTPException: Si no tiene permisos de admin
    """
    if not usuario_actual.es_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos de administrador"
        )
    
    return usuario_actual


# Helper para extraer token del header
def extraer_token_del_header(authorization: str) -> str:
    """
    Extraer token JWT del header Authorization
    
    Args:
        authorization: Header Authorization
        
    Returns:
        str: Token JWT
        
    Raises:
        HTTPException: Si el header es inválido
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Header Authorization requerido"
        )
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Esquema de autorización debe ser Bearer"
            )
        return token
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Formato de header Authorization inválido"
        )