"""
Router de autenticación y autorización

Endpoints para registro, login, logout y gestión de tokens JWT.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.auth import UserRegisterRequest, UserResponse
from app.services.auth_service import AuthService

# Crear router de autenticación
router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar nuevo usuario",
    description="Crea una nueva cuenta de usuario en el sistema",
    response_description="Usuario creado exitosamente",
    responses={
        201: {
            "description": "Usuario registrado exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "email": "nuevo.usuario@plantitas.com",
                        "nombre": "María García",
                        "es_activo": True,
                        "fecha_registro": "2025-10-05T10:30:00",
                        "ultimo_acceso": None
                    }
                }
            }
        },
        409: {
            "description": "Email ya registrado",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "El email usuario@ejemplo.com ya está registrado en el sistema"
                    }
                }
            }
        },
        422: {
            "description": "Datos de validación incorrectos",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["body", "password"],
                                "msg": "La contraseña debe contener al menos una letra mayúscula",
                                "type": "value_error"
                            }
                        ]
                    }
                }
            }
        },
        500: {
            "description": "Error interno del servidor",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Error interno al registrar usuario. Por favor, intente nuevamente."
                    }
                }
            }
        }
    },
    tags=["Autenticación"]
)
async def registrar_usuario(
    datos_registro: UserRegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Registrar un nuevo usuario en el sistema
    
    Crea una cuenta de usuario con los datos proporcionados. El email debe ser único
    en el sistema y la contraseña debe cumplir con los requisitos de seguridad.
    
    **Requisitos de contraseña:**
    - Mínimo 8 caracteres
    - Al menos una letra mayúscula
    - Al menos una letra minúscula
    - Al menos un número
    
    **Validaciones:**
    - Email debe ser válido y único en el sistema
    - Nombre solo puede contener letras, espacios, guiones y apóstrofes
    - Contraseña se hashea automáticamente usando bcrypt
    
    Args:
        datos_registro: Datos del usuario a registrar (email, password, nombre)
        db: Sesión de base de datos (inyectada automáticamente)
        
    Returns:
        UserResponse: Datos del usuario creado (sin información sensible)
        
    Raises:
        HTTPException 409: Si el email ya está registrado
        HTTPException 422: Si los datos de validación son incorrectos
        HTTPException 500: Si hay un error interno al crear el usuario
        
    Example:
        ```python
        # Request
        POST /auth/register
        {
            "email": "maria@plantitas.com",
            "password": "MiPassword123",
            "nombre": "María García"
        }
        
        # Response 201 Created
        {
            "id": 1,
            "email": "maria@plantitas.com",
            "nombre": "María García",
            "es_activo": true,
            "fecha_registro": "2025-10-05T10:30:00",
            "ultimo_acceso": null
        }
        ```
    """
    # Registrar usuario usando el servicio de autenticación
    nuevo_usuario = AuthService.registrar_usuario(db, datos_registro)
    
    # Retornar respuesta con datos del usuario (UserResponse se crea automáticamente
    # desde el modelo Usuario gracias a from_attributes=True)
    return nuevo_usuario
