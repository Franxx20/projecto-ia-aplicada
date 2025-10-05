"""
Router de autenticación y autorización

Endpoints para registro, login, logout y gestión de tokens JWT.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.auth import (
    UserRegisterRequest, UserResponse, UserLoginRequest, TokenResponse,
    RefreshTokenRequest, RefreshTokenResponse, LogoutRequest
)
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


@router.post(
    "/refresh",
    response_model=RefreshTokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Renovar token JWT",
    description="Renueva un token JWT existente con uno de mayor duración (7 días)",
    response_description="Nuevo token JWT con expiración extendida",
    responses={
        200: {
            "description": "Token renovado exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer",
                        "expires_in": 604800
                    }
                }
            }
        },
        401: {
            "description": "Token inválido, expirado o en blacklist",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Token inválido o expirado"
                    }
                }
            }
        },
        403: {
            "description": "Usuario desactivado",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "La cuenta de usuario está desactivada"
                    }
                }
            }
        }
    },
    tags=["Autenticación"]
)
async def refresh_token(
    datos_refresh: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Renovar un token JWT existente con uno de mayor duración
    
    Permite renovar un token JWT válido con uno nuevo que tiene una expiración
    extendida de 7 días. Útil para mantener sesiones activas sin requerir
    login frecuente del usuario.
    
    **Proceso de renovación:**
    1. Valida que el token actual sea válido y no esté expirado
    2. Verifica que el token no esté en la blacklist (logout)
    3. Verifica que el usuario existe y está activo
    4. Genera un nuevo token con expiración de 7 días
    
    **Validaciones:**
    - El token debe ser válido y no estar expirado
    - El token no debe estar en la blacklist
    - El usuario debe existir en el sistema
    - La cuenta del usuario debe estar activa
    
    Args:
        datos_refresh: Token JWT actual a renovar
        db: Sesión de base de datos (inyectada automáticamente)
        
    Returns:
        RefreshTokenResponse: Nuevo token JWT con expiración extendida y tiempo de expiración en segundos
        
    Raises:
        HTTPException 401: Si el token es inválido, expirado o está en blacklist
        HTTPException 403: Si la cuenta del usuario está desactivada
        
    Example:
        ```python
        # Request
        POST /auth/refresh
        {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        }
        
        # Response 200 OK
        {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer",
            "expires_in": 604800
        }
        ```
    """
    # Renovar token usando el servicio de autenticación
    resultado = AuthService.refresh_token(db, datos_refresh.access_token)
    
    return resultado


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Cerrar sesión (invalidar token)",
    description="Invalida un token JWT agregándolo a la blacklist",
    response_description="Token invalidado exitosamente",
    responses={
        200: {
            "description": "Logout exitoso - Token invalidado",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Logout exitoso",
                        "detail": "El token ha sido invalidado correctamente"
                    }
                }
            }
        },
        401: {
            "description": "Token inválido o ya invalidado",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "El token ya ha sido invalidado"
                    }
                }
            }
        }
    },
    tags=["Autenticación"]
)
async def logout(datos_logout: LogoutRequest):
    """
    Cerrar sesión invalidando el token JWT
    
    Invalida un token JWT agregándolo a una blacklist, previniendo su uso
    en peticiones futuras. El token no podrá ser usado nuevamente hasta
    que expire naturalmente.
    
    **Proceso de logout:**
    1. Valida que el token sea válido
    2. Verifica que el token no esté ya en la blacklist
    3. Agrega el token a la blacklist
    
    **Nota sobre blacklist:**
    - En desarrollo: Blacklist en memoria (se limpia al reiniciar servidor)
    - En producción: Se recomienda usar Redis o tabla de base de datos
    
    **Seguridad:**
    - Un token invalidado no puede ser usado nuevamente
    - Los tokens no pueden ser "reactivados" después de logout
    - La blacklist previene el uso de tokens robados después del logout
    
    Args:
        datos_logout: Token JWT a invalidar
        
    Returns:
        dict: Mensaje de confirmación del logout
        
    Raises:
        HTTPException 401: Si el token es inválido o ya está en la blacklist
        
    Example:
        ```python
        # Request
        POST /auth/logout
        {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        }
        
        # Response 200 OK
        {
            "message": "Logout exitoso",
            "detail": "El token ha sido invalidado correctamente"
        }
        
        # Intentar usar el token después del logout
        GET /api/plantas
        Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
        
        # Response 401 Unauthorized
        {
            "detail": "El token ha sido invalidado (logout)"
        }
        ```
    """
    # Invalidar token usando el servicio de autenticación
    resultado = AuthService.logout(datos_logout.access_token)
    
    return resultado
