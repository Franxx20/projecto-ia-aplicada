"""
Schemas Pydantic para PlantNet API.

Modelos de validación para requests y responses de identificación de plantas.
Basados en la documentación oficial de PlantNet:
https://my.plantnet.org/doc/api/identify
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator


class PlantNetIdentificacionRequest(BaseModel):
    """
    Schema para request de identificación de PlantNet.
    
    Attributes:
        organos: Lista de tipos de órgano por cada imagen
        project: Proyecto/flora a usar (default: 'all')
        include_related_images: Incluir imágenes relacionadas
        nb_results: Número máximo de resultados
        lang: Código de idioma para nombres comunes
    """
    organos: List[str] = Field(
        ...,
        description="Tipo de órgano por cada imagen: leaf, flower, fruit, bark, auto",
        min_items=1,
        max_items=5,
        examples=[["leaf"], ["flower", "leaf"]]
    )
    project: Optional[str] = Field(
        "all",
        description="Proyecto/flora: all, k-world-flora, k-western-europe, etc.",
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
        description="Número máximo de resultados a retornar"
    )
    lang: str = Field(
        "es",
        description="Código de idioma para nombres comunes (default: español). Valores: es, en, fr, pt, de, it, ar, cs, etc.",
        min_length=2,
        max_length=5,
        examples=["es", "en", "fr"]
    )
    
    @validator("organos")
    def validar_organos(cls, v):
        """Valida que los órganos sean valores permitidos."""
        organos_validos = ["leaf", "flower", "fruit", "bark", "auto"]
        for organo in v:
            if organo not in organos_validos:
                raise ValueError(
                    f"Órgano '{organo}' inválido. Valores válidos: {', '.join(organos_validos)}"
                )
        return v


class PlantNetGenusInfo(BaseModel):
    """Información del género de la planta."""
    scientificNameWithoutAuthor: str
    scientificNameAuthorship: Optional[str] = ""
    scientificName: Optional[str]


class PlantNetFamilyInfo(BaseModel):
    """Información de la familia de la planta."""
    scientificNameWithoutAuthor: str
    scientificNameAuthorship: Optional[str] = ""
    scientificName: Optional[str]


class PlantNetSpeciesInfo(BaseModel):
    """Información detallada de la especie."""
    scientificNameWithoutAuthor: str
    scientificNameAuthorship: Optional[str] = ""
    scientificName: str
    genus: Optional[PlantNetGenusInfo] = None
    family: Optional[PlantNetFamilyInfo] = None
    commonNames: List[str] = Field(default_factory=list)


class PlantNetGBIFInfo(BaseModel):
    """Información de GBIF (Global Biodiversity Information Facility)."""
    id: Optional[str] = None


class PlantNetPOWOInfo(BaseModel):
    """Información de POWO (Plants of the World Online)."""
    id: Optional[str] = None


class PlantNetResult(BaseModel):
    """
    Un resultado individual de identificación.
    
    Representa una posible especie identificada con su score de confianza.
    """
    score: float = Field(..., description="Score de confianza (0.0 a 1.0)")
    species: PlantNetSpeciesInfo
    gbif: Optional[PlantNetGBIFInfo] = None
    powo: Optional[PlantNetPOWOInfo] = None
    
    @property
    def confianza_porcentaje(self) -> float:
        """Retorna el score como porcentaje."""
        return round(self.score * 100, 2)


class PlantNetPredictedOrgan(BaseModel):
    """Órgano detectado automáticamente por la IA."""
    image: str = Field(..., description="ID/hash de la imagen")
    filename: str = Field(..., description="Nombre del archivo")
    organ: str = Field(..., description="Órgano detectado")
    score: float = Field(..., description="Confianza de la detección")


class PlantNetQueryInfo(BaseModel):
    """Información del query realizado."""
    project: str
    images: List[str]
    organs: List[str]
    includeRelatedImages: bool = False
    noReject: bool = False
    type: Optional[str] = None


class PlantNetIdentificacionResponse(BaseModel):
    """
    Schema para response completa de PlantNet API.
    
    Estructura basada en la documentación oficial:
    https://my.plantnet.org/doc/api/identify
    """
    query: PlantNetQueryInfo
    predictedOrgans: List[PlantNetPredictedOrgan] = Field(default_factory=list)
    bestMatch: str = Field(..., description="Nombre científico del mejor match")
    results: List[PlantNetResult] = Field(..., description="Lista de especies probables")
    version: str = Field(..., description="Versión del motor de IA")
    remainingIdentificationRequests: int = Field(
        ...,
        description="Requests restantes del día en la API"
    )
    language: Optional[str] = "en"
    preferedReferential: Optional[str] = None
    
    class Config:
        """Configuración del modelo Pydantic."""
        json_schema_extra = {
            "example": {
                "query": {
                    "project": "all",
                    "images": ["abc123"],
                    "organs": ["flower"],
                    "includeRelatedImages": False,
                    "noReject": False
                },
                "bestMatch": "Monstera deliciosa Liebm.",
                "results": [
                    {
                        "score": 0.9234,
                        "species": {
                            "scientificNameWithoutAuthor": "Monstera deliciosa",
                            "scientificNameAuthorship": "Liebm.",
                            "scientificName": "Monstera deliciosa Liebm.",
                            "genus": {
                                "scientificNameWithoutAuthor": "Monstera",
                                "scientificName": "Monstera"
                            },
                            "family": {
                                "scientificNameWithoutAuthor": "Araceae",
                                "scientificName": "Araceae"
                            },
                            "commonNames": ["Costilla de Adán", "Monstera"]
                        }
                    }
                ],
                "version": "2025-01-17 (7.3)",
                "remainingIdentificationRequests": 498
            }
        }


class PlantNetResultadoSimplificado(BaseModel):
    """
    Resultado simplificado para uso interno de la aplicación.
    
    Extrae solo la información más relevante del response de PlantNet.
    """
    nombre_cientifico: str = Field(..., description="Nombre científico completo")
    nombre_cientifico_sin_autor: str = Field(..., description="Nombre sin autor")
    autor: str = Field(default="", description="Autor del nombre científico")
    nombres_comunes: List[str] = Field(
        default_factory=list,
        description="Lista de nombres comunes"
    )
    genero: str = Field(default="", description="Género de la planta")
    familia: str = Field(default="", description="Familia taxonómica")
    score: float = Field(..., ge=0.0, le=1.0, description="Score de confianza (0.0 a 1.0)")
    confianza_porcentaje: float = Field(..., description="Confianza en porcentaje")
    gbif_id: Optional[str] = Field(None, description="ID en GBIF")
    powo_id: Optional[str] = Field(None, description="ID en POWO")
    
    class Config:
        """Configuración del modelo Pydantic."""
        json_schema_extra = {
            "example": {
                "nombre_cientifico": "Monstera deliciosa Liebm.",
                "nombre_cientifico_sin_autor": "Monstera deliciosa",
                "autor": "Liebm.",
                "nombres_comunes": ["Costilla de Adán", "Monstera"],
                "genero": "Monstera",
                "familia": "Araceae",
                "score": 0.9234,
                "confianza_porcentaje": 92.34,
                "gbif_id": "2768247",
                "powo_id": "712345-1"
            }
        }


class PlantNetRespuestaFormateada(BaseModel):
    """
    Respuesta formateada de identificación para la aplicación.
    
    Estructura simplificada y traducida al español.
    """
    mejor_match: str = Field(..., description="Mejor coincidencia (nombre científico)")
    resultados: List[Dict[str, Any]] = Field(
        ...,
        description="Lista de resultados con score y nombres"
    )
    version_ia: str = Field(..., description="Versión del motor de IA de PlantNet")
    requests_restantes_api: int = Field(
        ...,
        description="Requests restantes en PlantNet API hoy"
    )
    requests_restantes_app: int = Field(
        ...,
        description="Requests restantes en nuestra aplicación hoy"
    )
    organos_detectados: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Órganos detectados automáticamente"
    )
    proyecto_usado: str = Field(..., description="Proyecto/flora utilizado")
    
    class Config:
        """Configuración del modelo Pydantic."""
        json_schema_extra = {
            "example": {
                "mejor_match": "Monstera deliciosa Liebm.",
                "resultados": [
                    {
                        "nombre_cientifico": "Monstera deliciosa Liebm.",
                        "nombres_comunes": ["Costilla de Adán", "Monstera"],
                        "familia": "Araceae",
                        "score": 0.9234,
                        "confianza_porcentaje": 92.34
                    }
                ],
                "version_ia": "2025-01-17 (7.3)",
                "requests_restantes_api": 498,
                "requests_restantes_app": 485,
                "organos_detectados": [
                    {
                        "filename": "planta.jpg",
                        "organ": "leaf",
                        "score": 0.95
                    }
                ],
                "proyecto_usado": "all"
            }
        }


class PlantNetQuotaInfo(BaseModel):
    """Información sobre el uso de la API."""
    requests_hoy: int = Field(..., description="Requests realizados hoy")
    limite_diario: int = Field(..., description="Límite diario de requests")
    restantes: int = Field(..., description="Requests restantes hoy")
    porcentaje_usado: float = Field(..., description="Porcentaje del cupo usado")
    
    @validator("porcentaje_usado", pre=True, always=True)
    def calcular_porcentaje(cls, v, values):
        """Calcula el porcentaje usado automáticamente."""
        if "requests_hoy" in values and "limite_diario" in values:
            if values["limite_diario"] > 0:
                return round((values["requests_hoy"] / values["limite_diario"]) * 100, 2)
        return 0.0
