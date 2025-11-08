"""
Schemas Pydantic para el modelo Planta.

Este módulo define los schemas de validación de datos para las operaciones
CRUD de plantas y estadísticas del jardín del usuario.

Autor: Equipo Backend
Fecha: Octubre 2025
Sprint: Sprint 2 - T-014
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator


class PlantaBase(BaseModel):
    """
    Schema base para Planta con campos comunes.
    """
    nombre_personal: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Nombre personalizado de la planta",
        examples=["Mi Monstera", "Suculenta del balcón"]
    )
    especie_id: Optional[int] = Field(
        None,
        description="ID de la especie de la planta",
        ge=1
    )
    estado_salud: str = Field(
        default="buena",
        description="Estado de salud de la planta",
        examples=["excelente", "buena", "necesita_atencion", "critica"]
    )
    ubicacion: Optional[str] = Field(
        None,
        max_length=255,
        description="Ubicación física de la planta",
        examples=["Sala", "Balcón", "Jardín trasero"]
    )
    notas: Optional[str] = Field(
        None,
        description="Notas adicionales sobre la planta"
    )
    imagen_principal_id: Optional[int] = Field(
        None,
        description="ID de la imagen principal",
        ge=1
    )
    fecha_ultimo_riego: Optional[datetime] = Field(
        None,
        description="Fecha y hora del último riego"
    )
    frecuencia_riego_dias: Optional[int] = Field(
        7,
        description="Frecuencia de riego en días",
        ge=1,
        le=365
    )
    luz_actual: Optional[str] = Field(
        None,
        description="Nivel de luz que recibe",
        examples=["baja", "media", "alta", "directa"]
    )
    fecha_adquisicion: Optional[datetime] = Field(
        None,
        description="Fecha de adquisición de la planta"
    )
    
    @field_validator('estado_salud')
    @classmethod
    def validar_estado_salud(cls, v: str) -> str:
        """Valida que el estado de salud sea uno de los valores permitidos."""
        estados_validos = ['excelente', 'buena', 'necesita_atencion', 'critica']
        if v not in estados_validos:
            raise ValueError(f'Estado de salud debe ser uno de: {", ".join(estados_validos)}')
        return v
    
    @field_validator('luz_actual')
    @classmethod
    def validar_luz_actual(cls, v: Optional[str]) -> Optional[str]:
        """Valida que el nivel de luz sea uno de los valores permitidos."""
        if v is None:
            return v
        niveles_validos = ['baja', 'media', 'alta', 'directa']
        if v not in niveles_validos:
            raise ValueError(f'Nivel de luz debe ser uno de: {", ".join(niveles_validos)}')
        return v


class PlantaCreate(PlantaBase):
    """
    Schema para crear una nueva planta.
    
    Hereda todos los campos de PlantaBase.
    El usuario_id se obtiene del token JWT, no del request body.
    """
    pass


class PlantaUpdate(BaseModel):
    """
    Schema para actualizar una planta existente.
    
    Todos los campos son opcionales para permitir actualizaciones parciales.
    """
    nombre_personal: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="Nombre personalizado de la planta"
    )
    especie_id: Optional[int] = Field(
        None,
        description="ID de la especie de la planta",
        ge=1
    )
    estado_salud: Optional[str] = Field(
        None,
        description="Estado de salud de la planta"
    )
    ubicacion: Optional[str] = Field(
        None,
        max_length=255,
        description="Ubicación física de la planta"
    )
    notas: Optional[str] = Field(
        None,
        description="Notas adicionales sobre la planta"
    )
    imagen_principal_id: Optional[int] = Field(
        None,
        description="ID de la imagen principal",
        ge=1
    )
    fecha_ultimo_riego: Optional[datetime] = Field(
        None,
        description="Fecha y hora del último riego"
    )
    frecuencia_riego_dias: Optional[int] = Field(
        None,
        description="Frecuencia de riego en días",
        ge=1,
        le=365
    )
    luz_actual: Optional[str] = Field(
        None,
        description="Nivel de luz que recibe"
    )
    fecha_adquisicion: Optional[datetime] = Field(
        None,
        description="Fecha de adquisición de la planta"
    )
    
    @field_validator('estado_salud')
    @classmethod
    def validar_estado_salud(cls, v: Optional[str]) -> Optional[str]:
        """Valida que el estado de salud sea uno de los valores permitidos."""
        if v is None:
            return v
        estados_validos = ['excelente', 'buena', 'necesita_atencion', 'critica']
        if v not in estados_validos:
            raise ValueError(f'Estado de salud debe ser uno de: {", ".join(estados_validos)}')
        return v
    
    @field_validator('luz_actual')
    @classmethod
    def validar_luz_actual(cls, v: Optional[str]) -> Optional[str]:
        """Valida que el nivel de luz sea uno de los valores permitidos."""
        if v is None:
            return v
        niveles_validos = ['baja', 'media', 'alta', 'directa']
        if v not in niveles_validos:
            raise ValueError(f'Nivel de luz debe ser uno de: {", ".join(niveles_validos)}')
        return v


class PlantaResponse(PlantaBase):
    """
    Schema para la respuesta de una planta.
    
    Incluye todos los campos del modelo, incluyendo IDs y timestamps.
    """
    id: int = Field(
        ...,
        description="ID único de la planta"
    )
    usuario_id: int = Field(
        ...,
        description="ID del usuario propietario"
    )
    proxima_riego: Optional[datetime] = Field(
        None,
        description="Fecha y hora del próximo riego"
    )
    created_at: datetime = Field(
        ...,
        description="Fecha de creación del registro"
    )
    updated_at: datetime = Field(
        ...,
        description="Fecha de última actualización"
    )
    is_active: bool = Field(
        default=True,
        description="Indica si la planta está activa"
    )
    necesita_riego: bool = Field(
        default=False,
        description="Indica si la planta necesita riego ahora"
    )
    imagen_principal_url: Optional[str] = Field(
        None,
        description="URL de la imagen principal de la planta"
    )
    
    class Config:
        """Configuración del schema."""
        from_attributes = True


class PlantaStats(BaseModel):
    """
    Schema para estadísticas del jardín del usuario.
    
    Proporciona un resumen del estado de todas las plantas.
    """
    total_plantas: int = Field(
        ...,
        description="Número total de plantas activas",
        ge=0
    )
    plantas_saludables: int = Field(
        ...,
        description="Plantas en estado excelente o bueno",
        ge=0
    )
    plantas_necesitan_atencion: int = Field(
        ...,
        description="Plantas que necesitan atención o están en estado crítico",
        ge=0
    )
    plantas_necesitan_riego: int = Field(
        ...,
        description="Plantas que necesitan riego hoy",
        ge=0
    )
    porcentaje_salud: float = Field(
        ...,
        description="Porcentaje de plantas saludables",
        ge=0.0,
        le=100.0
    )
    
    class Config:
        """Configuración del schema."""
        from_attributes = True


class AgregarPlantaDesdeIdentificacionRequest(BaseModel):
    """
    Schema para agregar una planta al jardín desde una identificación.
    
    Este schema se usa cuando el usuario confirma una identificación
    y quiere agregar la planta a su colección personal.
    """
    identificacion_id: int = Field(
        ...,
        description="ID de la identificación de la planta",
        ge=1
    )
    nombre_personalizado: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="Nombre personalizado (opcional, si no se provee usa el nombre común)"
    )
    notas: Optional[str] = Field(
        None,
        description="Notas adicionales sobre la planta"
    )
    ubicacion: Optional[str] = Field(
        None,
        max_length=255,
        description="Ubicación física de la planta"
    )


class RegistrarRiegoRequest(BaseModel):
    """
    Schema para registrar un nuevo riego en una planta.
    """
    fecha_riego: Optional[datetime] = Field(
        None,
        description="Fecha y hora del riego. Si no se provee, usa la fecha actual"
    )


class PlantaListResponse(BaseModel):
    """
    Schema para la respuesta de lista de plantas con paginación.
    """
    plantas: list[PlantaResponse] = Field(
        ...,
        description="Lista de plantas"
    )
    total: int = Field(
        ...,
        description="Número total de plantas",
        ge=0
    )
    
    class Config:
        """Configuración del schema."""
        from_attributes = True


class ImagenIdentificacionSchema(BaseModel):
    """
    Schema para información básica de una imagen en una identificación.
    """
    id: int = Field(
        ...,
        description="ID único de la imagen"
    )
    nombre_archivo: str = Field(
        ...,
        description="Nombre del archivo de imagen"
    )
    url_blob: str = Field(
        ...,
        description="URL del blob en Azure Storage"
    )
    organ: Optional[str] = Field(
        None,
        description="Órgano de la planta (flower, leaf, fruit, etc.)"
    )
    tamano_bytes: int = Field(
        ...,
        description="Tamaño del archivo en bytes"
    )
    
    class Config:
        """Configuración del schema."""
        from_attributes = True


class EspecieBasicSchema(BaseModel):
    """
    Schema para información básica de una especie.
    """
    id: int = Field(
        ...,
        description="ID único de la especie"
    )
    nombre_cientifico: str = Field(
        ...,
        description="Nombre científico de la especie"
    )
    nombre_comun: Optional[str] = Field(
        None,
        description="Nombre común de la especie"
    )
    familia: Optional[str] = Field(
        None,
        description="Familia taxonómica"
    )
    
    class Config:
        """Configuración del schema."""
        from_attributes = True


class PlantaUsuarioResponse(BaseModel):
    """
    Schema para la respuesta de una planta del usuario con información completa.
    
    Incluye:
    - Todos los datos de la planta
    - Información de la especie (si está identificada)
    - Imagen principal
    - TODAS las imágenes de identificación (si fue agregada desde identificación)
    """
    id: int = Field(
        ...,
        description="ID único de la planta"
    )
    usuario_id: int = Field(
        ...,
        description="ID del usuario propietario"
    )
    especie_id: Optional[int] = Field(
        None,
        description="ID de la especie"
    )
    nombre_personalizado: Optional[str] = Field(
        None,
        description="Nombre personalizado de la planta"
    )
    fecha_adquisicion: Optional[datetime] = Field(
        None,
        description="Fecha de adquisición"
    )
    ubicacion: Optional[str] = Field(
        None,
        description="Ubicación física"
    )
    estado_salud: str = Field(
        ...,
        description="Estado de salud"
    )
    frecuencia_riego_dias: Optional[int] = Field(
        None,
        description="Frecuencia de riego en días"
    )
    notas: Optional[str] = Field(
        None,
        description="Notas del usuario"
    )
    imagen_principal_id: Optional[int] = Field(
        None,
        description="ID de la imagen principal"
    )
    activa: bool = Field(
        default=True,
        description="Si la planta está activa"
    )
    fecha_creacion: datetime = Field(
        ...,
        description="Fecha de creación"
    )
    fecha_actualizacion: datetime = Field(
        ...,
        description="Fecha de última actualización"
    )
    # Información adicional
    especie: Optional[EspecieBasicSchema] = Field(
        None,
        description="Información de la especie"
    )
    imagen_principal: Optional[ImagenIdentificacionSchema] = Field(
        None,
        description="Imagen principal de la planta"
    )
    imagenes_identificacion: List[ImagenIdentificacionSchema] = Field(
        default_factory=list,
        description="Todas las imágenes usadas para identificar esta planta"
    )
    
    class Config:
        """Configuración del schema."""
        from_attributes = True
