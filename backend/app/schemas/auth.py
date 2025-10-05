"""
Schemas de autenticación y autorización
Modelos Pydantic para validación de requests/responses de autenticación
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
from typing import Optional
import re


class UserRegisterRequest(BaseModel):
    """
    Schema para request de registro de usuario
    
    Attributes:
        email: Email único del usuario (validado por EmailStr)
        password: Contraseña (mínimo 8 caracteres, debe incluir mayúscula, minúscula y número)
        nombre: Nombre completo del usuario (opcional)
    """
    email: EmailStr = Field(
        ...,
        description="Email del usuario, debe ser único en el sistema",
        examples=["usuario@ejemplo.com"]
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="Contraseña segura con al menos 8 caracteres",
        examples=["MiPassword123"]
    )
    nombre: Optional[str] = Field(
        None,
        min_length=2,
        max_length=100,
        description="Nombre completo del usuario",
        examples=["Juan Pérez"]
    )

    @field_validator('password')
    @classmethod
    def validar_password_segura(cls, v: str) -> str:
        """
        Validar que la contraseña cumple con los requisitos de seguridad:
        - Al menos una letra mayúscula
        - Al menos una letra minúscula
        - Al menos un número
        
        Args:
            v: Contraseña a validar
            
        Returns:
            str: Contraseña validada
            
        Raises:
            ValueError: Si la contraseña no cumple los requisitos
        """
        if not re.search(r'[A-Z]', v):
            raise ValueError('La contraseña debe contener al menos una letra mayúscula')
        if not re.search(r'[a-z]', v):
            raise ValueError('La contraseña debe contener al menos una letra minúscula')
        if not re.search(r'\d', v):
            raise ValueError('La contraseña debe contener al menos un número')
        return v

    @field_validator('nombre')
    @classmethod
    def validar_nombre(cls, v: Optional[str]) -> Optional[str]:
        """
        Validar que el nombre no contenga caracteres especiales peligrosos
        
        Args:
            v: Nombre a validar
            
        Returns:
            Optional[str]: Nombre validado o None
            
        Raises:
            ValueError: Si el nombre contiene caracteres no permitidos
        """
        if v is None:
            return v
        
        # Eliminar espacios en blanco al inicio y final
        v = v.strip()
        
        # Validar que solo contenga letras, espacios, acentos y algunos caracteres especiales comunes
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s\'-]+$', v):
            raise ValueError('El nombre solo puede contener letras, espacios, guiones y apóstrofes')
        
        return v

    class Config:
        """Configuración del schema"""
        json_schema_extra = {
            "example": {
                "email": "nuevo.usuario@plantitas.com",
                "password": "MiPassword123",
                "nombre": "María García"
            }
        }


class UserResponse(BaseModel):
    """
    Schema para response de datos de usuario
    
    No incluye información sensible como password_hash
    
    Attributes:
        id: ID único del usuario
        email: Email del usuario
        nombre: Nombre del usuario
        is_active: Estado de activación de la cuenta
        created_at: Fecha de creación de la cuenta
        updated_at: Última actualización del usuario
    """
    id: int = Field(..., description="ID único del usuario")
    email: EmailStr = Field(..., description="Email del usuario")
    nombre: Optional[str] = Field(None, description="Nombre completo del usuario")
    is_active: bool = Field(..., description="Estado de activación de la cuenta")
    created_at: datetime = Field(..., description="Fecha de creación del usuario")
    updated_at: datetime = Field(..., description="Fecha de última actualización")

    class Config:
        """Configuración del schema"""
        from_attributes = True  # Permite crear desde modelos SQLAlchemy
        json_schema_extra = {
            "example": {
                "id": 1,
                "email": "usuario@plantitas.com",
                "nombre": "María García",
                "is_active": True,
                "created_at": "2025-10-05T10:30:00",
                "updated_at": "2025-10-05T10:30:00"
            }
        }


class UserLoginRequest(BaseModel):
    """
    Schema para request de login de usuario
    
    Attributes:
        email: Email del usuario
        password: Contraseña del usuario
    """
    email: EmailStr = Field(
        ...,
        description="Email del usuario",
        examples=["usuario@ejemplo.com"]
    )
    password: str = Field(
        ...,
        description="Contraseña del usuario",
        examples=["MiPassword123"]
    )

    class Config:
        """Configuración del schema"""
        json_schema_extra = {
            "example": {
                "email": "usuario@plantitas.com",
                "password": "MiPassword123"
            }
        }


class TokenResponse(BaseModel):
    """
    Schema para response de token JWT
    
    Attributes:
        access_token: Token JWT para autenticación
        token_type: Tipo de token (siempre "bearer")
        user: Datos del usuario autenticado
    """
    access_token: str = Field(..., description="Token JWT de acceso")
    token_type: str = Field(default="bearer", description="Tipo de token")
    user: UserResponse = Field(..., description="Datos del usuario autenticado")

    class Config:
        """Configuración del schema"""
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "user": {
                    "id": 1,
                    "email": "usuario@plantitas.com",
                    "nombre": "María García",
                    "es_activo": True,
                    "fecha_registro": "2025-10-05T10:30:00",
                    "ultimo_acceso": "2025-10-05T14:20:00"
                }
            }
        }


class RefreshTokenRequest(BaseModel):
    """
    Schema para request de refresh token
    
    Attributes:
        access_token: Token JWT actual que se desea renovar
    """
    access_token: str = Field(
        ...,
        description="Token JWT actual que se desea renovar",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."]
    )

    class Config:
        """Configuración del schema"""
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }


class RefreshTokenResponse(BaseModel):
    """
    Schema para response de refresh token
    
    Attributes:
        access_token: Nuevo token JWT con expiración extendida
        token_type: Tipo de token (siempre "bearer")
        expires_in: Tiempo de expiración en segundos
    """
    access_token: str = Field(..., description="Nuevo token JWT de acceso")
    token_type: str = Field(default="bearer", description="Tipo de token")
    expires_in: int = Field(..., description="Tiempo de expiración en segundos")

    class Config:
        """Configuración del schema"""
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 604800
            }
        }


class LogoutRequest(BaseModel):
    """
    Schema para request de logout
    
    Attributes:
        access_token: Token JWT que se desea invalidar
    """
    access_token: str = Field(
        ...,
        description="Token JWT que se desea invalidar",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."]
    )

    class Config:
        """Configuración del schema"""
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }
