"""
Módulo Schemas - Modelos Pydantic

Este módulo contiene todos los schemas de Pydantic para validación
de datos de entrada y salida.

Estructura:
- request/ - Schemas para requests (POST, PUT)
- response/ - Schemas para responses
- validators/ - Validadores personalizados
"""

from .auth import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    UserResponse
)

from .imagen import (
    ImagenResponse,
    ImagenUploadResponse
)

from .planta import (
    PlantaBase,
    PlantaCreate,
    PlantaUpdate,
    PlantaResponse,
    PlantaStats,
    PlantaListResponse,
    RegistrarRiegoRequest
)

from .plantnet import (
    PlantNetIdentificacionRequest,
    PlantNetIdentificacionResponse,
    PlantNetResultadoSimplificado,
    PlantNetRespuestaFormateada,
    PlantNetQuotaInfo,
    PlantNetResult
)

__all__ = [
    # Auth schemas
    "UserRegisterRequest",
    "UserLoginRequest",
    "TokenResponse",
    "RefreshTokenRequest",
    "UserResponse",
    # Imagen schemas
    "ImagenResponse",
    "ImagenUploadResponse",
    # Planta schemas
    "PlantaBase",
    "PlantaCreate",
    "PlantaUpdate",
    "PlantaResponse",
    "PlantaStats",
    "PlantaListResponse",
    "RegistrarRiegoRequest",
    # PlantNet schemas
    "PlantNetIdentificacionRequest",
    "PlantNetIdentificacionResponse",
    "PlantNetResultadoSimplificado",
    "PlantNetRespuestaFormateada",
    "PlantNetQuotaInfo",
    "PlantNetResult",
]
