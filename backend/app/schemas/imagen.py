"""
Schemas de Pydantic para validación de imágenes.

Este módulo define los schemas para la validación de requests y responses
relacionados con la gestión de imágenes en Azure Blob Storage.

Autor: Equipo Backend
Fecha: Octubre 2025
Sprint: Sprint 1 - T-004
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator


class ImagenBase(BaseModel):
    """
    Schema base para imagen con campos comunes.
    """
    descripcion: Optional[str] = Field(
        None,
        max_length=1000,
        description="Descripción opcional de la imagen"
    )


class ImagenCreate(ImagenBase):
    """
    Schema para crear una nueva imagen (usado internamente por el servicio).
    
    Los campos técnicos se generan automáticamente en el servicio de upload.
    """
    pass


class ImagenUpdate(BaseModel):
    """
    Schema para actualizar una imagen existente.
    
    Solo permite actualizar la descripción.
    """
    descripcion: Optional[str] = Field(
        None,
        max_length=1000,
        description="Nueva descripción de la imagen"
    )


class ImagenResponse(ImagenBase):
    """
    Schema de respuesta con toda la información de una imagen.
    
    Incluye todos los campos del modelo más información adicional.
    """
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(..., description="ID único de la imagen")
    usuario_id: int = Field(..., description="ID del usuario propietario")
    nombre_archivo: str = Field(..., description="Nombre original del archivo")
    nombre_blob: str = Field(..., description="Nombre del blob en Azure Storage")
    url_blob: str = Field(..., description="URL completa para acceder a la imagen")
    url_con_sas: Optional[str] = Field(None, description="URL con token SAS para acceso temporal")
    container_name: str = Field(..., description="Nombre del contenedor en Azure")
    content_type: str = Field(..., description="Tipo MIME de la imagen")
    tamano_bytes: int = Field(..., description="Tamaño del archivo en bytes")
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: datetime = Field(..., description="Fecha de última actualización")
    is_deleted: bool = Field(..., description="Indica si fue eliminada lógicamente")
    
    @property
    def tamano_mb(self) -> float:
        """
        Convierte el tamaño de bytes a megabytes.
        
        Returns:
            float: Tamaño en megabytes con 2 decimales
        """
        return round(self.tamano_bytes / (1024 * 1024), 2)
    
    @property
    def extension(self) -> str:
        """
        Extrae la extensión del archivo.
        
        Returns:
            str: Extensión del archivo (ej: 'jpg', 'png')
        """
        return self.nombre_archivo.split('.')[-1].lower() if '.' in self.nombre_archivo else ''


class ImagenListResponse(BaseModel):
    """
    Schema de respuesta para listado de imágenes con paginación.
    """
    imagenes: list[ImagenResponse] = Field(..., description="Lista de imágenes")
    total: int = Field(..., description="Total de imágenes (sin paginación)")
    pagina: int = Field(..., description="Número de página actual")
    tamano_pagina: int = Field(..., description="Tamaño de la página")
    total_paginas: int = Field(..., description="Total de páginas disponibles")


class ImagenUploadResponse(BaseModel):
    """
    Schema de respuesta después de subir una imagen.
    
    Incluye información básica de la imagen recién creada.
    """
    id: int = Field(..., description="ID de la imagen creada")
    nombre_archivo: str = Field(..., description="Nombre del archivo")
    url_blob: str = Field(..., description="URL para acceder a la imagen")
    tamano_bytes: int = Field(..., description="Tamaño del archivo en bytes")
    content_type: str = Field(..., description="Tipo MIME")
    created_at: datetime = Field(..., description="Fecha de subida")
    mensaje: str = Field(default="Imagen subida exitosamente", description="Mensaje de confirmación")


class ImagenDeleteResponse(BaseModel):
    """
    Schema de respuesta después de eliminar una imagen.
    """
    id: int = Field(..., description="ID de la imagen eliminada")
    nombre_archivo: str = Field(..., description="Nombre del archivo eliminado")
    mensaje: str = Field(default="Imagen eliminada exitosamente", description="Mensaje de confirmación")
    eliminado_de_azure: bool = Field(..., description="Indica si se eliminó físicamente de Azure")


class ImagenErrorResponse(BaseModel):
    """
    Schema de respuesta para errores relacionados con imágenes.
    """
    error: str = Field(..., description="Tipo de error")
    detalle: str = Field(..., description="Descripción detallada del error")
    codigo: int = Field(..., description="Código HTTP de error")
