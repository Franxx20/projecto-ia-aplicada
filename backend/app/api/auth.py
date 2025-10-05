"""
Router de autenticación y autorización

Endpoints para registro, login, logout y gestión de tokens JWT.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.auth import UserRegisterRequest, UserResponse, UserLoginRequest, TokenResponse
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


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Iniciar sesión",
    description="Autentica un usuario y retorna un token JWT de acceso",
    response_description="Token JWT generado exitosamente",
    responses={
        200: {
            "description": "Login exitoso - Token JWT generado",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c3VhcmlvQHBsYW50aXRhcy5jb20iLCJ1c2VyX2lkIjoxLCJub21icmUiOiJNYXLDrWEgR2FyY8OtYSIsImV4cCI6MTY5Njk1MjQwMCwiaWF0IjoxNjk2OTUwNjAwfQ.hUz5bXN3kPjS8xH9fLZc3oMj7wQdR5sYt2vK1xE4nWc",
                        "token_type": "bearer",
                        "user": {
                            "id": 1,
                            "email": "usuario@plantitas.com",
                            "nombre": "María García",
                            "is_active": True,
                            "created_at": "2025-10-05T10:30:00",
                            "updated_at": "2025-10-05T14:20:00"
                        }
                    }
                }
            }
        },
        401: {
            "description": "Credenciales inválidas",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Credenciales inválidas"
                    }
                }
            }
        },
        403: {
            "description": "Usuario desactivado",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "La cuenta de usuario está desactivada. Contacte al administrador."
                    }
                }
            }
        },
        500: {
            "description": "Error interno del servidor",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Error interno al procesar login. Por favor, intente nuevamente."
                    }
                }
            }
        }
    },
    tags=["Autenticación"]
)
async def login_usuario(
    datos_login: UserLoginRequest,
    db: Session = Depends(get_db)
):
    """
    Autenticar usuario y obtener token JWT
    
    Valida las credenciales del usuario (email y contraseña) y retorna un token JWT
    de acceso que debe ser incluido en el header Authorization de las peticiones
    subsecuentes.
    
    **Proceso de autenticación:**
    1. Valida que el email existe en el sistema
    2. Verifica que la contraseña sea correcta
    3. Verifica que la cuenta del usuario esté activa
    4. Genera un token JWT con expiración de 30 minutos
    5. Actualiza el timestamp de último acceso del usuario
    
    **Uso del token:**
    ```
    Authorization: Bearer <access_token>
    ```
    
    **Seguridad:**
    - El token expira automáticamente tras 30 minutos
    - Las contraseñas se verifican usando bcrypt
    - El token incluye el email, ID y nombre del usuario
    - Las cuentas desactivadas no pueden hacer login
    
    Args:
        datos_login: Credenciales del usuario (email y password)
        db: Sesión de base de datos (inyectada automáticamente)
        
    Returns:
        TokenResponse: Token JWT, tipo de token y datos del usuario
        
    Raises:
        HTTPException 401: Si las credenciales son inválidas
        HTTPException 403: Si la cuenta del usuario está desactivada
        HTTPException 500: Si hay un error interno al procesar el login
        
    Example:
        ```python
        # Request
        POST /auth/login
        {
            "email": "maria@plantitas.com",
            "password": "MiPassword123"
        }
        
        # Response 200 OK
        {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer",
            "user": {
                "id": 1,
                "email": "maria@plantitas.com",
                "nombre": "María García",
                "is_active": true,
                "created_at": "2025-10-05T10:30:00",
                "updated_at": "2025-10-05T14:20:00"
            }
        }
        
        # Uso del token en peticiones subsecuentes
        GET /api/plantas
        Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
        ```
    """
    # Autenticar usuario y generar token usando el servicio de autenticación
    token_response = AuthService.login_usuario(db, datos_login)
    
    return token_response
