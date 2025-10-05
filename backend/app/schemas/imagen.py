"""
Esquemas Pydantic para manejo de imágenes

Definimos modelos de validación para requests y responses
relacionados con upload y manejo de imágenes.
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime


class ImagenUploadResponse(BaseModel):
    """Respuesta al subir una imagen"""
    filename: str = Field(..., description="Nombre único del archivo")
    original_filename: str = Field(..., description="Nombre original del archivo")
    url: str = Field(..., description="URL de acceso a la imagen")
    tamaño: int = Field(..., description="Tamaño del archivo en bytes")
    tipo_mime: str = Field(..., description="Tipo MIME del archivo")
    metadata: Dict[str, Any] = Field(..., description="Metadatos de la imagen")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ImagenInfo(BaseModel):
    """Información de una imagen almacenada"""
    filename: str = Field(..., description="Nombre del archivo")
    tamaño: int = Field(..., description="Tamaño en bytes")
    fecha_creacion: float = Field(..., description="Timestamp de creación")
    fecha_modificacion: float = Field(..., description="Timestamp de modificación")
    url: str = Field(..., description="URL de acceso")


class ErrorResponse(BaseModel):
    """Respuesta de error estándar"""
    detail: str = Field(..., description="Mensaje de error")
    error_code: Optional[str] = Field(None, description="Código de error específico")
    
    
class ImagenValidacion(BaseModel):
    """Parámetros de validación para imágenes"""
    tamaño_maximo: int = Field(default=5 * 1024 * 1024, description="Tamaño máximo en bytes (5MB)")
    tipos_permitidos: list = Field(default=["jpg", "jpeg", "png", "gif", "webp"], description="Extensiones permitidas")
    
    @validator('tamaño_maximo')
    def validar_tamaño_maximo(cls, v):
        if v <= 0:
            raise ValueError('El tamaño máximo debe ser mayor a 0')
        if v > 50 * 1024 * 1024:  # 50MB máximo absoluto
            raise ValueError('El tamaño máximo no puede exceder 50MB')
        return v
    
    @validator('tipos_permitidos')
    def validar_tipos_permitidos(cls, v):
        if not v:
            raise ValueError('Debe especificar al menos un tipo de archivo permitido')
        tipos_validos = ["jpg", "jpeg", "png", "gif", "webp", "bmp", "tiff"]
        for tipo in v:
            if tipo.lower() not in tipos_validos:
                raise ValueError(f'Tipo de archivo no válido: {tipo}')
        return [tipo.lower() for tipo in v]