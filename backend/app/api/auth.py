"""
Endpoints de autenticación

Implementa todos los endpoints para registro, login, refresh token
y gestión de autenticación según las especificaciones del Sprint 1.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address

from ..db import obtener_db
from ..db.models import Usuario
from ..schemas.usuario import (
    UsuarioRegistro, 
    UsuarioLogin, 
    UsuarioRespuesta,
    TokenRespuesta,
    RefreshTokenRequest,
    MensajeRespuesta
)
from ..services.usuario import servicio_usuario
from ..services.auth import servicio_auth
from ..core.dependencies import obtener_usuario_actual

# Configurar router
router = APIRouter(prefix="/auth", tags=["Autenticación"])

# Rate limiting
limiter = Limiter(key_func=get_remote_address)


@router.post(
    "/registro",
    response_model=TokenRespuesta,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar nuevo usuario",
    description="Registra un nuevo usuario en el sistema y retorna tokens de autenticación"
)
@limiter.limit("5/minute")  # Limitar registros
async def registrar_usuario(
    request: Request,
    usuario_data: UsuarioRegistro,
    db: Session = Depends(obtener_db)
):
    """
    Registrar nuevo usuario
    
    Crea una nueva cuenta de usuario con los datos proporcionados.
    Retorna tokens JWT para autenticación inmediata.
    
    - **email**: Email único del usuario
    - **nombre_usuario**: Nombre de usuario único (3-50 caracteres)
    - **password**: Password segura (mín. 8 caracteres con mayúsculas, minúsculas, números y símbolos)
    - **confirmar_password**: Confirmación del password
    - **nombre_completo**: Nombre completo (opcional)
    - **bio**: Biografía del usuario (opcional)
    - **ubicacion**: Ubicación del usuario (opcional)
    """
    try:
        # Crear usuario
        usuario = servicio_usuario.crear_usuario(usuario_data, db)
        
        # Generar tokens
        tokens = servicio_auth.crear_tokens_para_usuario(usuario)
        
        # Actualizar último login
        usuario.actualizar_ultimo_login()
        db.commit()
        
        # Retornar respuesta completa
        return TokenRespuesta(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type=tokens["token_type"],
            expires_in=tokens["expires_in"],
            usuario=UsuarioRespuesta.from_orm(usuario)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno durante el registro: {str(e)}"
        )


@router.post(
    "/login",
    response_model=TokenRespuesta,
    summary="Iniciar sesión",
    description="Autentica usuario y retorna tokens de acceso"
)
@limiter.limit("10/minute")  # Limitar intentos de login
async def iniciar_sesion(
    request: Request,
    credenciales: UsuarioLogin,
    db: Session = Depends(obtener_db)
):
    """
    Iniciar sesión
    
    Autentica al usuario con email y password.
    Retorna tokens JWT para acceso a endpoints protegidos.
    
    - **email**: Email del usuario registrado
    - **password**: Password del usuario
    """
    try:
        # Autenticar usuario
        usuario = servicio_auth.autenticar_usuario(
            credenciales.email, 
            credenciales.password, 
            db
        )
        
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email o password incorrectos"
            )
        
        # Generar tokens
        tokens = servicio_auth.crear_tokens_para_usuario(usuario)
        
        # Actualizar último login
        usuario.actualizar_ultimo_login()
        db.commit()
        
        return TokenRespuesta(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"], 
            token_type=tokens["token_type"],
            expires_in=tokens["expires_in"],
            usuario=UsuarioRespuesta.from_orm(usuario)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno durante el login: {str(e)}"
        )


@router.post(
    "/refresh",
    response_model=dict,
    summary="Renovar token de acceso",
    description="Renueva el access token usando el refresh token"
)
@limiter.limit("20/minute")
async def renovar_token(
    request: Request,
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(obtener_db)
):
    """
    Renovar access token
    
    Usa el refresh token para obtener un nuevo access token
    sin necesidad de volver a hacer login.
    
    - **refresh_token**: Token de refresh válido
    """
    try:
        # Renovar token
        nuevo_token = servicio_auth.renovar_access_token(
            refresh_data.refresh_token, 
            db
        )
        
        return nuevo_token
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al renovar token: {str(e)}"
        )


@router.post(
    "/logout",
    response_model=MensajeRespuesta,
    summary="Cerrar sesión",
    description="Cierra la sesión del usuario actual"
)
async def cerrar_sesion(
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    """
    Cerrar sesión
    
    Invalida los tokens del usuario actual.
    En esta implementación básica, el cliente debe descartar los tokens.
    
    En futuras versiones se implementará blacklist de tokens.
    """
    try:
        # En una implementación completa, aquí se agregarían los tokens a una blacklist
        # Por ahora, simplemente confirmamos el logout
        
        return MensajeRespuesta(
            mensaje="Sesión cerrada exitosamente",
            detalle=f"Usuario {usuario_actual.nombre_usuario} ha cerrado sesión"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al cerrar sesión: {str(e)}"
        )


@router.get(
    "/me",
    response_model=UsuarioRespuesta,
    summary="Obtener perfil actual",
    description="Obtiene los datos del usuario autenticado actual"
)
async def obtener_perfil_actual(
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    """
    Obtener perfil del usuario actual
    
    Retorna toda la información del usuario autenticado.
    Requiere token JWT válido.
    """
    return UsuarioRespuesta.from_orm(usuario_actual)


@router.get(
    "/verificar-token",
    response_model=dict,
    summary="Verificar token",
    description="Verifica si el token actual es válido"
)
async def verificar_token(
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    """
    Verificar validez del token
    
    Endpoint para verificar si el token JWT es válido
    y el usuario está activo.
    """
    return {
        "valido": True,
        "usuario_id": usuario_actual.id,
        "email": usuario_actual.email,
        "nombre_usuario": usuario_actual.nombre_usuario,
        "activo": usuario_actual.activo,
        "verificado": usuario_actual.verificado
    }


# Endpoints adicionales para validaciones

@router.get(
    "/verificar-email/{email}",
    response_model=dict,
    summary="Verificar disponibilidad de email",
    description="Verifica si un email está disponible para registro"
)
async def verificar_disponibilidad_email(
    email: str,
    db: Session = Depends(obtener_db)
):
    """
    Verificar disponibilidad de email
    
    Útil para validación en tiempo real durante el registro.
    """
    disponible = servicio_usuario.verificar_disponibilidad_email(email, db)
    
    return {
        "email": email,
        "disponible": disponible,
        "mensaje": "Email disponible" if disponible else "Email ya está en uso"
    }


@router.get(
    "/verificar-username/{nombre_usuario}",
    response_model=dict,
    summary="Verificar disponibilidad de nombre de usuario", 
    description="Verifica si un nombre de usuario está disponible"
)
async def verificar_disponibilidad_username(
    nombre_usuario: str,
    db: Session = Depends(obtener_db)
):
    """
    Verificar disponibilidad de nombre de usuario
    
    Útil para validación en tiempo real durante el registro.
    """
    disponible = servicio_usuario.verificar_disponibilidad_nombre_usuario(nombre_usuario, db)
    
    return {
        "nombre_usuario": nombre_usuario,
        "disponible": disponible,
        "mensaje": "Nombre de usuario disponible" if disponible else "Nombre de usuario ya está en uso"
    }