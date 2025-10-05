"""
Utilidades para gestión de tokens JWT

Funciones para crear, validar y decodificar tokens JWT usando python-jose.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt

from app.core.config import obtener_configuracion


def crear_token_acceso(
    datos: Dict[str, Any],
    expiracion_minutos: Optional[int] = None
) -> str:
    """
    Crear un token JWT de acceso
    
    Args:
        datos: Diccionario con los datos a codificar en el token (claims)
        expiracion_minutos: Minutos hasta que expire el token (usa config por defecto si no se especifica)
        
    Returns:
        str: Token JWT codificado
        
    Example:
        >>> token = crear_token_acceso({"sub": "usuario@ejemplo.com"})
        >>> print(token)
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
    """
    config = obtener_configuracion()
    
    # Crear copia de los datos para no modificar el original
    datos_token = datos.copy()
    
    # Calcular tiempo de expiración
    if expiracion_minutos:
        expiracion = datetime.utcnow() + timedelta(minutes=expiracion_minutos)
    else:
        expiracion = datetime.utcnow() + timedelta(minutes=config.jwt_expiracion_minutos)
    
    # Agregar claims estándar
    datos_token.update({
        "exp": expiracion,
        "iat": datetime.utcnow()
    })
    
    # Codificar el token
    token_codificado = jwt.encode(
        datos_token,
        config.jwt_secret_key,
        algorithm=config.jwt_algorithm
    )
    
    return token_codificado


def decodificar_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decodificar y validar un token JWT
    
    Args:
        token: Token JWT a decodificar
        
    Returns:
        Optional[Dict[str, Any]]: Datos decodificados del token, None si el token es inválido
        
    Example:
        >>> datos = decodificar_token(token)
        >>> print(datos["sub"])
        'usuario@ejemplo.com'
    """
    config = obtener_configuracion()
    
    try:
        payload = jwt.decode(
            token,
            config.jwt_secret_key,
            algorithms=[config.jwt_algorithm]
        )
        return payload
    except JWTError:
        return None


def verificar_token(token: str) -> bool:
    """
    Verificar si un token JWT es válido
    
    Args:
        token: Token JWT a verificar
        
    Returns:
        bool: True si el token es válido, False en caso contrario
        
    Example:
        >>> es_valido = verificar_token(token)
        >>> print(es_valido)
        True
    """
    payload = decodificar_token(token)
    return payload is not None


def extraer_email_de_token(token: str) -> Optional[str]:
    """
    Extraer el email del subject (sub) de un token JWT
    
    Args:
        token: Token JWT
        
    Returns:
        Optional[str]: Email del usuario, None si el token es inválido o no tiene subject
        
    Example:
        >>> email = extraer_email_de_token(token)
        >>> print(email)
        'usuario@ejemplo.com'
    """
    payload = decodificar_token(token)
    if payload:
        return payload.get("sub")
    return None


def calcular_expiracion(minutos: int) -> datetime:
    """
    Calcular timestamp de expiración desde ahora
    
    Args:
        minutos: Número de minutos hasta la expiración
        
    Returns:
        datetime: Timestamp de expiración
        
    Example:
        >>> expiracion = calcular_expiracion(30)
        >>> print(expiracion)
        datetime.datetime(2025, 10, 5, 15, 0, 0)
    """
    return datetime.utcnow() + timedelta(minutes=minutos)


def crear_refresh_token(
    datos: Dict[str, Any],
    expiracion_dias: Optional[int] = None
) -> str:
    """
    Crear un refresh token JWT con expiración extendida
    
    Args:
        datos: Diccionario con los datos a codificar en el token (claims)
        expiracion_dias: Días hasta que expire el token (usa config por defecto si no se especifica)
        
    Returns:
        str: Refresh token JWT codificado
        
    Example:
        >>> refresh_token = crear_refresh_token({"sub": "usuario@ejemplo.com"})
        >>> print(refresh_token)
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
    """
    config = obtener_configuracion()
    
    # Crear copia de los datos para no modificar el original
    datos_token = datos.copy()
    
    # Calcular tiempo de expiración en días
    if expiracion_dias:
        expiracion = datetime.utcnow() + timedelta(days=expiracion_dias)
    else:
        expiracion = datetime.utcnow() + timedelta(days=config.jwt_refresh_expiracion_dias)
    
    # Agregar claims estándar y tipo de token
    datos_token.update({
        "exp": expiracion,
        "iat": datetime.utcnow(),
        "type": "refresh"  # Identificar como refresh token
    })
    
    # Codificar el token
    token_codificado = jwt.encode(
        datos_token,
        config.jwt_secret_key,
        algorithm=config.jwt_algorithm
    )
    
    return token_codificado


def validar_refresh_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Validar que un token sea un refresh token válido
    
    Args:
        token: Token JWT a validar
        
    Returns:
        Optional[Dict[str, Any]]: Datos decodificados si es un refresh token válido, None en caso contrario
        
    Example:
        >>> datos = validar_refresh_token(refresh_token)
        >>> print(datos["sub"])
        'usuario@ejemplo.com'
    """
    payload = decodificar_token(token)
    
    # Verificar que sea un refresh token
    if payload and payload.get("type") == "refresh":
        return payload
    
    return None
