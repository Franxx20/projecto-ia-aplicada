"""
Schemas Pydantic para identificación de plantas con múltiples imágenes.

Modelos de validación para T-022: Soporte de hasta 5 imágenes con parámetro organ.
Basado en especificaciones de PlantNet API.
"""

from typing import List, Optional
from pydantic import BaseModel, Field, validator
from datetime import datetime


class ImagenConOrgan(BaseModel):
    """
    Schema para una imagen con su tipo de órgano especificado.
    
    Attributes:
        imagen_base64: Imagen codificada en base64
        organ: Tipo de órgano (flower, leaf, fruit, bark, habit, other, sin_especificar)
        nombre_archivo: Nombre original del archivo (opcional)
    """
    imagen_base64: str = Field(
        ...,
        description="Imagen codificada en base64",
        min_length=100,
        examples=["data:image/jpeg;base64,/9j/4AAQSkZJRg..."]
    )
    organ: str = Field(
        "sin_especificar",
        description="Tipo de órgano: flower, leaf, fruit, bark, habit, other, sin_especificar",
        examples=["flower", "leaf", "sin_especificar"]
    )
    nombre_archivo: Optional[str] = Field(
        None,
        description="Nombre original del archivo",
        max_length=255,
        examples=["mi_planta.jpg", "foto_hoja.png"]
    )
    
    @validator("organ")
    def validar_organ(cls, v):
        """
        Valida que el órgano sea un valor permitido.
        
        Valores válidos:
        - flower: Flor o inflorescencia
        - leaf: Hoja
        - fruit: Fruto o semilla
        - bark: Corteza o tronco
        - habit: Hábito o porte general
        - other: Otra parte no especificada
        - sin_especificar: No especificar (no se envía a PlantNet API)
        """
        organos_validos = ["flower", "leaf", "fruit", "bark", "habit", "other", "sin_especificar"]
        if v not in organos_validos:
            raise ValueError(
                f"Órgano '{v}' inválido. Valores válidos: {', '.join(organos_validos)}"
            )
        return v
    
    class Config:
        """Configuración del modelo Pydantic."""
        json_schema_extra = {
            "example": {
                "imagen_base64": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
                "organ": "flower",
                "nombre_archivo": "rosa_roja.jpg"
            }
        }


class IdentificacionMultipleRequest(BaseModel):
    """
    Schema para request de identificación con múltiples imágenes.
    
    Soporta de 1 a 5 imágenes en una sola petición, siguiendo
    las especificaciones de PlantNet API.
    
    Attributes:
        imagenes: Lista de imágenes con sus órganos (1-5 elementos)
        project: Proyecto de PlantNet a usar (default: 'all')
        include_related_images: Incluir imágenes similares
        nb_results: Número de resultados a retornar (1-50)
        lang: Idioma para nombres comunes
    """
    imagenes: List[ImagenConOrgan] = Field(
        ...,
        description="Lista de 1 a 5 imágenes con sus órganos",
        min_items=1,
        max_items=5,
        examples=[[
            {
                "imagen_base64": "data:image/jpeg;base64,/9j...",
                "organ": "flower",
                "nombre_archivo": "flor.jpg"
            },
            {
                "imagen_base64": "data:image/jpeg;base64,/9j...",
                "organ": "leaf",
                "nombre_archivo": "hoja.jpg"
            }
        ]]
    )
    project: str = Field(
        "all",
        description="Proyecto PlantNet: all, k-world-flora, k-western-europe, etc.",
        examples=["all", "k-world-flora"]
    )
    include_related_images: bool = Field(
        False,
        description="Incluir imágenes similares en la respuesta"
    )
    nb_results: int = Field(
        10,
        ge=1,
        le=50,
        description="Número máximo de resultados"
    )
    lang: str = Field(
        "es",
        description="Idioma: es, en, fr, pt, etc.",
        min_length=2,
        max_length=5
    )
    
    @validator("imagenes")
    def validar_cantidad_imagenes(cls, v):
        """Valida que haya entre 1 y 5 imágenes."""
        cantidad = len(v)
        if cantidad < 1:
            raise ValueError("Debe proporcionar al menos 1 imagen")
        if cantidad > 5:
            raise ValueError("No se pueden enviar más de 5 imágenes por identificación")
        return v
    
    class Config:
        """Configuración del modelo Pydantic."""
        json_schema_extra = {
            "example": {
                "imagenes": [
                    {
                        "imagen_base64": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
                        "organ": "flower",
                        "nombre_archivo": "flor_rosa.jpg"
                    },
                    {
                        "imagen_base64": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
                        "organ": "leaf",
                        "nombre_archivo": "hoja_verde.jpg"
                    }
                ],
                "project": "all",
                "include_related_images": False,
                "nb_results": 10,
                "lang": "es"
            }
        }


class IdentificacionSingleRequest(BaseModel):
    """
    Schema para request de identificación con una sola imagen (retrocompatibilidad).
    
    Mantiene compatibilidad con el endpoint anterior de imagen única.
    
    Attributes:
        imagen_base64: Imagen codificada en base64
        organ: Tipo de órgano (opcional)
        nombre_archivo: Nombre del archivo (opcional)
        project: Proyecto de PlantNet
        nb_results: Número de resultados
        lang: Idioma
    """
    imagen_base64: str = Field(
        ...,
        description="Imagen codificada en base64",
        min_length=100
    )
    organ: Optional[str] = Field(
        None,
        description="Tipo de órgano (flower, leaf, fruit, bark, habit, other)"
    )
    nombre_archivo: Optional[str] = Field(
        None,
        description="Nombre del archivo",
        max_length=255
    )
    project: str = Field(
        "all",
        description="Proyecto PlantNet"
    )
    nb_results: int = Field(
        10,
        ge=1,
        le=50
    )
    lang: str = Field(
        "es",
        min_length=2,
        max_length=5
    )
    
    @validator("organ")
    def validar_organ_opcional(cls, v):
        """Valida el órgano si se proporciona."""
        if v is not None and v != "":
            organos_validos = ["flower", "leaf", "fruit", "bark", "habit", "other"]
            if v not in organos_validos:
                raise ValueError(
                    f"Órgano '{v}' inválido. Valores válidos: {', '.join(organos_validos)}"
                )
        return v


class ImagenIdentificacionResponse(BaseModel):
    """
    Schema para información de una imagen en la respuesta.
    
    Attributes:
        id: ID de la imagen en la base de datos
        nombre_archivo: Nombre del archivo
        url_blob: URL del blob en Azure Storage
        organ: Tipo de órgano especificado
        tamano_bytes: Tamaño en bytes
    """
    id: int = Field(..., description="ID de la imagen")
    nombre_archivo: str = Field(..., description="Nombre del archivo")
    url_blob: str = Field(..., description="URL del blob")
    organ: Optional[str] = Field(None, description="Tipo de órgano")
    tamano_bytes: int = Field(..., description="Tamaño en bytes")


class IdentificacionResponse(BaseModel):
    """
    Schema para respuesta de identificación.
    
    Attributes:
        id: ID de la identificación
        usuario_id: ID del usuario
        imagenes: Lista de imágenes utilizadas
        especie_id: ID de la especie identificada
        confianza: Nivel de confianza (0-100)
        origen: Origen de la identificación (ia_plantnet)
        resultados: Lista de resultados de PlantNet
        fecha_identificacion: Fecha de la identificación
        proyecto_usado: Proyecto de PlantNet utilizado
        cantidad_imagenes: Número de imágenes usadas
    """
    id: int = Field(..., description="ID de la identificación")
    usuario_id: int = Field(..., description="ID del usuario")
    imagenes: List[ImagenIdentificacionResponse] = Field(
        ...,
        description="Lista de imágenes utilizadas"
    )
    especie_id: Optional[int] = Field(None, description="ID de la especie")
    confianza: int = Field(..., description="Confianza en porcentaje (0-100)")
    origen: str = Field(..., description="Origen de la identificación")
    resultados: dict = Field(..., description="Resultados completos de PlantNet")
    fecha_identificacion: datetime = Field(..., description="Fecha de identificación")
    proyecto_usado: str = Field(..., description="Proyecto usado")
    cantidad_imagenes: int = Field(..., description="Número de imágenes usadas")
    
    class Config:
        """Configuración del modelo Pydantic."""
        json_schema_extra = {
            "example": {
                "id": 1,
                "usuario_id": 123,
                "imagenes": [
                    {
                        "id": 456,
                        "nombre_archivo": "flor.jpg",
                        "url_blob": "https://storage.blob.core.windows.net/...",
                        "organ": "flower",
                        "tamano_bytes": 245678
                    }
                ],
                "especie_id": 789,
                "confianza": 92,
                "origen": "ia_plantnet",
                "resultados": {
                    "mejor_match": "Rosa chinensis",
                    "top_5": [...]
                },
                "fecha_identificacion": "2025-10-20T01:30:00",
                "proyecto_usado": "all",
                "cantidad_imagenes": 2
            }
        }


class EstadisticasOrganResponse(BaseModel):
    """
    Schema para estadísticas de uso de órganos.
    
    Attributes:
        total_identificaciones: Total de identificaciones realizadas
        por_organ: Diccionario con cantidad por tipo de órgano
        mas_usado: Órgano más utilizado
    """
    total_identificaciones: int
    por_organ: dict
    mas_usado: Optional[str] = None
    
    class Config:
        """Configuración del modelo Pydantic."""
        json_schema_extra = {
            "example": {
                "total_identificaciones": 150,
                "por_organ": {
                    "flower": 45,
                    "leaf": 65,
                    "fruit": 20,
                    "bark": 10,
                    "habit": 5,
                    "other": 5,
                    "sin_especificar": 0
                },
                "mas_usado": "leaf"
            }
        }
