"""
Schemas de Pydantic para validación de datos del usuario

Schemas para registro, login, respuestas y validaciones
siguiendo las especificaciones del Sprint 1.
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
import re


# === SCHEMAS BASE ===

class UsuarioBase(BaseModel):
    """Schema base para Usuario"""
    email: EmailStr = Field(..., description="Email del usuario")
    nombre_usuario: str = Field(..., min_length=3, max_length=50, description="Nombre de usuario único")
    nombre_completo: Optional[str] = Field(None, max_length=255, description="Nombre completo del usuario")
    bio: Optional[str] = Field(None, max_length=500, description="Biografía del usuario")
    ubicacion: Optional[str] = Field(None, max_length=255, description="Ubicación del usuario")
    notificaciones_activas: bool = Field(True, description="Si el usuario quiere recibir notificaciones")

    @validator('nombre_usuario')
    def validar_nombre_usuario(cls, v):
        """Validar formato de nombre de usuario"""
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', v):
            raise ValueError('Nombre de usuario debe empezar con letra y solo contener letras, números y guiones bajos')
        return v


# === SCHEMAS DE ENTRADA (REQUEST) ===

class UsuarioRegistro(UsuarioBase):
    """Schema para registro de nuevo usuario"""
    password: str = Field(..., min_length=8, description="Password del usuario")
    confirmar_password: str = Field(..., description="Confirmación del password")

    @validator('password')
    def validar_password(cls, v):
        """Validar que el password cumple con los requisitos de seguridad"""
        if len(v) < 8:
            raise ValueError('Password debe tener al menos 8 caracteres')
        
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password debe contener al menos una letra mayúscula')
        
        if not re.search(r'[a-z]', v):
            raise ValueError('Password debe contener al menos una letra minúscula')
        
        if not re.search(r'\d', v):
            raise ValueError('Password debe contener al menos un número')
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password debe contener al menos un carácter especial')
        
        return v

    @validator('confirmar_password')
    def validar_confirmacion_password(cls, v, values):
        """Validar que las passwords coincidan"""
        if 'password' in values and v != values['password']:
            raise ValueError('Las passwords no coinciden')
        return v


class UsuarioLogin(BaseModel):
    """Schema para login de usuario"""
    email: EmailStr = Field(..., description="Email del usuario")
    password: str = Field(..., description="Password del usuario")


class UsuarioActualizacion(BaseModel):
    """Schema para actualización de datos del usuario"""
    nombre_completo: Optional[str] = Field(None, max_length=255)
    bio: Optional[str] = Field(None, max_length=500)
    ubicacion: Optional[str] = Field(None, max_length=255)
    notificaciones_activas: Optional[bool] = None


class CambioPassword(BaseModel):
    """Schema para cambio de password"""
    password_actual: str = Field(..., description="Password actual")
    password_nuevo: str = Field(..., min_length=8, description="Nuevo password")
    confirmar_password_nuevo: str = Field(..., description="Confirmación del nuevo password")

    @validator('password_nuevo')
    def validar_password_nuevo(cls, v):
        """Validar nuevo password"""
        if len(v) < 8:
            raise ValueError('Password debe tener al menos 8 caracteres')
        
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password debe contener al menos una letra mayúscula')
        
        if not re.search(r'[a-z]', v):
            raise ValueError('Password debe contener al menos una letra minúscula')
        
        if not re.search(r'\d', v):
            raise ValueError('Password debe contener al menos un número')
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password debe contener al menos un carácter especial')
        
        return v

    @validator('confirmar_password_nuevo')
    def validar_confirmacion_password_nuevo(cls, v, values):
        """Validar confirmación de nuevo password"""
        if 'password_nuevo' in values and v != values['password_nuevo']:
            raise ValueError('Las passwords no coinciden')
        return v


# === SCHEMAS DE RESPUESTA (RESPONSE) ===

class UsuarioRespuesta(UsuarioBase):
    """Schema para respuesta con datos del usuario"""
    id: int
    activo: bool
    verificado: bool
    fecha_creacion: datetime
    ultimo_login: Optional[datetime] = None

    class Config:
        from_attributes = True  # Para compatibilidad con SQLAlchemy


class UsuarioPublico(BaseModel):
    """Schema para información pública del usuario (sin datos sensibles)"""
    id: int
    nombre_usuario: str
    nombre_completo: Optional[str] = None
    bio: Optional[str] = None
    ubicacion: Optional[str] = None
    fecha_creacion: datetime

    class Config:
        from_attributes = True


# === SCHEMAS DE AUTENTICACIÓN ===

class TokenRespuesta(BaseModel):
    """Schema para respuesta de token JWT"""
    access_token: str = Field(..., description="Token de acceso JWT")
    refresh_token: str = Field(..., description="Token de refresh")
    token_type: str = Field(default="bearer", description="Tipo de token")
    expires_in: int = Field(..., description="Tiempo de expiración en segundos")
    usuario: UsuarioRespuesta = Field(..., description="Datos del usuario autenticado")


class TokenData(BaseModel):
    """Schema para datos del token"""
    email: Optional[str] = None
    user_id: Optional[int] = None
    scopes: list[str] = []


class RefreshTokenRequest(BaseModel):
    """Schema para request de refresh token"""
    refresh_token: str = Field(..., description="Refresh token")


# === SCHEMAS DE RESPUESTA GENERAL ===

class MensajeRespuesta(BaseModel):
    """Schema para respuestas con mensaje"""
    mensaje: str = Field(..., description="Mensaje de respuesta")
    detalle: Optional[str] = Field(None, description="Detalle adicional")
    codigo: Optional[str] = Field(None, description="Código de respuesta")


class ErrorRespuesta(BaseModel):
    """Schema para respuestas de error"""
    error: str = Field(..., description="Mensaje de error")
    detalle: Optional[str] = Field(None, description="Detalle del error")
    codigo_error: Optional[str] = Field(None, description="Código del error")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp del error")


# === SCHEMAS DE ESTADÍSTICAS ===

class EstadisticasUsuario(BaseModel):
    """Schema para estadísticas del usuario"""
    total_plantas_identificadas: int = 0
    total_fotos_subidas: int = 0
    plantas_favoritas: int = 0
    dias_activo: int = 0
    ultimo_login: Optional[datetime] = None

    class Config:
        from_attributes = True