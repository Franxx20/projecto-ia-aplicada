"""
Schemas Pydantic para el análisis de salud de plantas con Gemini AI.

Este módulo define los schemas de validación de datos para las operaciones
de verificación de salud de plantas, análisis con IA, y historial de diagnósticos.

Autor: Equipo Backend
Fecha: Noviembre 2025
Sprint: Feature - Health Check AI
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, field_validator


class EstadoSaludDetallado(str, Enum):
    """
    Enum para los estados de salud detallados de una planta.
    
    Estos estados son retornados por el análisis de Gemini AI y permiten
    una clasificación más granular que los estados básicos.
    
    Attributes:
        EXCELENTE: Planta en perfecto estado, crecimiento óptimo
        SALUDABLE: Planta en buen estado, sin problemas significativos
        NECESITA_ATENCION: Requiere ajustes menores en cuidados
        ENFERMEDAD: Presenta síntomas de enfermedad
        PLAGA: Infestación por plagas o parásitos
        CRITICA: Estado crítico, requiere intervención urgente
    """
    EXCELENTE = "excelente"
    SALUDABLE = "saludable"
    NECESITA_ATENCION = "necesita_atencion"
    ENFERMEDAD = "enfermedad"
    PLAGA = "plaga"
    CRITICA = "critica"


class TipoProblema(str, Enum):
    """
    Enum para los tipos de problemas que puede presentar una planta.
    
    Attributes:
        RIEGO: Problemas relacionados con exceso o falta de agua
        LUZ: Problemas de iluminación (exceso o deficiencia)
        NUTRICION: Deficiencias nutricionales o fertilización
        TEMPERATURA: Estrés por temperatura inadecuada
        HUMEDAD: Problemas de humedad ambiental
        PLAGA: Infestación por insectos o ácaros
        ENFERMEDAD: Infecciones fúngicas, bacterianas o virales
        FISICO: Daños físicos, mecánicos
        OTRO: Otros problemas no clasificados
    """
    RIEGO = "riego"
    LUZ = "luz"
    NUTRICION = "nutricion"
    TEMPERATURA = "temperatura"
    HUMEDAD = "humedad"
    PLAGA = "plaga"
    ENFERMEDAD = "enfermedad"
    FISICO = "fisico"
    OTRO = "otro"


class SeveridadProblema(str, Enum):
    """
    Enum para la severidad de un problema detectado.
    
    Attributes:
        LEVE: Problema menor, sin impacto significativo
        MODERADA: Problema que requiere atención pronta
        SEVERA: Problema serio que puede afectar la supervivencia
        CRITICA: Problema crítico, requiere acción inmediata
    """
    LEVE = "leve"
    MODERADA = "moderada"
    SEVERA = "severa"
    CRITICA = "critica"


class PrioridadRecomendacion(str, Enum):
    """
    Enum para la prioridad de una recomendación.
    
    Attributes:
        BAJA: Acción opcional o de mejora
        MEDIA: Acción recomendada en los próximos días
        ALTA: Acción necesaria en las próximas 24-48 horas
    """
    BAJA = "baja"
    MEDIA = "media"
    ALTA = "alta"


class ProblemaDetectado(BaseModel):
    """
    Schema para un problema detectado en el análisis de salud.
    
    Representa un problema específico identificado por Gemini AI,
    con detalles sobre su tipo, severidad y descripción.
    """
    tipo: TipoProblema = Field(
        ...,
        description="Tipo de problema detectado",
        examples=["riego", "plaga", "luz"]
    )
    descripcion: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Descripción detallada del problema",
        examples=["Hojas amarillentas en los bordes, posible exceso de riego"]
    )
    severidad: SeveridadProblema = Field(
        ...,
        description="Severidad del problema",
        examples=["moderada", "severa"]
    )
    
    class Config:
        """Configuración del schema."""
        from_attributes = True
        use_enum_values = True


class RecomendacionItem(BaseModel):
    """
    Schema para una recomendación de cuidado o tratamiento.
    
    Representa una acción específica que el usuario debe realizar
    para mejorar la salud de la planta.
    """
    tipo: TipoProblema = Field(
        ...,
        description="Tipo de recomendación (relacionado con el problema)",
        examples=["riego", "luz", "nutricion"]
    )
    descripcion: str = Field(
        ...,
        min_length=1,
        max_length=800,
        description="Descripción detallada de la acción a realizar",
        examples=["Reduce la frecuencia de riego a una vez cada 10 días"]
    )
    prioridad: PrioridadRecomendacion = Field(
        ...,
        description="Prioridad de la recomendación",
        examples=["alta", "media", "baja"]
    )
    urgencia_dias: Optional[int] = Field(
        None,
        ge=0,
        le=365,
        description="Días máximos para aplicar la recomendación (0 = inmediato)",
        examples=[0, 1, 7, 14]
    )
    
    class Config:
        """Configuración del schema."""
        from_attributes = True
        use_enum_values = True


class VerificarSaludRequest(BaseModel):
    """
    Schema para solicitud de verificación de salud de una planta.
    
    Este schema NO incluye la imagen ya que se envía como archivo multipart.
    Solo incluye metadatos adicionales opcionales para el análisis.
    """
    notas_adicionales: Optional[str] = Field(
        None,
        max_length=1000,
        description="Notas adicionales del usuario sobre síntomas observados",
        examples=["He notado manchas marrones en las hojas desde hace una semana"]
    )
    incluir_imagen: bool = Field(
        default=True,
        description="Indica si se incluye imagen en el análisis"
    )
    
    class Config:
        """Configuración del schema."""
        from_attributes = True


class SaludAnalisisMetadata(BaseModel):
    """
    Schema para metadatos del análisis de salud.
    
    Información adicional sobre el proceso de análisis.
    """
    tiempo_analisis_ms: int = Field(
        ...,
        ge=0,
        description="Tiempo de análisis en milisegundos",
        examples=[5000, 8500]
    )
    modelo_usado: str = Field(
        ...,
        description="Modelo de IA usado para el análisis",
        examples=["gemini-2.5-flash", "gemini-2.5-pro"]
    )
    con_imagen: bool = Field(
        ...,
        description="Indica si el análisis incluyó imagen"
    )
    fecha_analisis: datetime = Field(
        ...,
        description="Fecha y hora del análisis"
    )
    version_prompt: str = Field(
        default="v1",
        description="Versión del prompt usado",
        examples=["v1", "v2"]
    )
    
    class Config:
        """Configuración del schema."""
        from_attributes = True


class SaludAnalisisResponse(BaseModel):
    """
    Schema para la respuesta completa de un análisis de salud.
    
    Este es el schema principal que retorna el endpoint de verificación de salud.
    Incluye el diagnóstico completo, problemas detectados, y recomendaciones.
    """
    id: Optional[int] = Field(
        None,
        description="ID del análisis (si fue guardado en BD)",
        ge=1
    )
    planta_id: int = Field(
        ...,
        description="ID de la planta analizada",
        ge=1
    )
    usuario_id: int = Field(
        ...,
        description="ID del usuario que solicitó el análisis",
        ge=1
    )
    imagen_id: Optional[int] = Field(
        None,
        description="ID de la imagen analizada",
        ge=1
    )
    estado: EstadoSaludDetallado = Field(
        ...,
        description="Estado de salud determinado por el análisis",
        examples=["excelente", "necesita_atencion", "enfermedad"]
    )
    confianza: int = Field(
        ...,
        ge=0,
        le=100,
        description="Nivel de confianza del diagnóstico (0-100)",
        examples=[85, 92]
    )
    resumen_diagnostico: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Resumen del diagnóstico en lenguaje natural",
        examples=["La planta presenta un estado saludable con crecimiento vigoroso..."]
    )
    diagnostico_detallado: Optional[str] = Field(
        None,
        max_length=3000,
        description="Diagnóstico técnico detallado (opcional)"
    )
    problemas_detectados: List[dict] = Field(
        default_factory=list,
        description="Lista de problemas detectados (vacía si no hay problemas)"
    )
    recomendaciones: List[dict] = Field(
        default_factory=list,
        description="Lista de recomendaciones para mejorar la salud"
    )
    modelo_ia_usado: str = Field(
        ...,
        description="Modelo de IA usado para el análisis"
    )
    tiempo_analisis_ms: int = Field(
        ...,
        ge=0,
        description="Tiempo de análisis en milisegundos"
    )
    version_prompt: str = Field(
        ...,
        description="Versión del prompt usado"
    )
    con_imagen: bool = Field(
        ...,
        description="Indica si el análisis incluyó imagen"
    )
    notas_usuario: Optional[str] = Field(
        None,
        description="Notas adicionales del usuario"
    )
    fecha_analisis: datetime = Field(
        ...,
        description="Fecha y hora del análisis"
    )
    created_at: datetime = Field(
        ...,
        description="Fecha de creación del registro"
    )
    updated_at: datetime = Field(
        ...,
        description="Fecha de última actualización"
    )
    
    class Config:
        """Configuración del schema."""
        from_attributes = True


# Alias para compatibilidad
AnalisisSaludResponse = SaludAnalisisResponse


class DetalleAnalisisSaludResponse(SaludAnalisisResponse):
    """
    Schema extendido para respuesta con detalles adicionales.
    
    Incluye toda la información de SaludAnalisisResponse más:
    - Información de tendencia
    - Indicador si es crítico
    - Color del estado para UI
    - Información de planta asociada
    """
    tendencia: Optional[str] = Field(
        None,
        description="Tendencia de salud (mejorando/estable/empeorando)"
    )
    es_critico: Optional[bool] = Field(
        None,
        description="Indica si el estado requiere atención urgente"
    )
    color_estado: Optional[str] = Field(
        None,
        description="Color hexadecimal para UI según estado"
    )
    planta: Optional[dict] = Field(
        None,
        description="Información básica de la planta"
    )
    imagen_url: Optional[str] = Field(
        None,
        description="URL de la imagen analizada"
    )
    
    class Config:
        """Configuración del schema."""
        from_attributes = True


class EstadisticasSaludResponse(BaseModel):
    """
    Schema para respuesta de estadísticas de salud.
    """
    planta_id: int = Field(..., description="ID de la planta")
    nombre_planta: str = Field(..., description="Nombre de la planta")
    periodo_dias: int = Field(..., description="Periodo de días analizado")
    total_analisis: int = Field(..., ge=0, description="Total de análisis realizados")
    estado_actual: str = Field(..., description="Estado de salud actual")
    confianza_actual: int = Field(..., ge=0, le=100, description="Confianza del último análisis")
    tendencia_general: str = Field(..., description="Tendencia general de salud")
    confianza_promedio: float = Field(..., ge=0, le=100, description="Confianza promedio")
    distribucion_estados: dict = Field(..., description="Distribución de estados")
    problemas_frecuentes: List[dict] = Field(default_factory=list, description="Problemas más frecuentes")
    ultimo_analisis: Optional[dict] = Field(None, description="Último análisis realizado")
    requiere_atencion: bool = Field(..., description="Si requiere atención")
    
    # Campos adicionales para compatibilidad con frontend
    ultimo_estado: Optional[str] = Field(None, description="Alias de estado_actual para compatibilidad")
    tendencia: Optional[str] = Field(None, description="Alias de tendencia_general para compatibilidad")
    dias_desde_ultimo_analisis: Optional[int] = Field(None, ge=0, description="Días desde el último análisis")
    
    class Config:
        """Configuración del schema."""
        from_attributes = True


# Alias para compatibilidad con el endpoint
AnalisisSaludResponse = SaludAnalisisResponse


class HistorialSaludItem(BaseModel):
    """
    Schema para un item del historial de análisis de salud.
    
    Versión resumida del análisis para mostrar en listas de historial.
    """
    id: int = Field(
        ...,
        description="ID del análisis",
        ge=1
    )
    planta_id: int = Field(
        ...,
        description="ID de la planta",
        ge=1
    )
    estado: EstadoSaludDetallado = Field(
        ...,
        description="Estado de salud determinado"
    )
    confianza: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Nivel de confianza del diagnóstico"
    )
    resumen: str = Field(
        ...,
        description="Resumen breve del diagnóstico (truncado si es muy largo)",
        max_length=200
    )
    fecha_analisis: datetime = Field(
        ...,
        description="Fecha y hora del análisis"
    )
    con_imagen: bool = Field(
        ...,
        description="Indica si el análisis incluyó imagen"
    )
    imagen_analizada_url: Optional[str] = Field(
        None,
        description="URL de la imagen (si existe)"
    )
    num_problemas: int = Field(
        ...,
        ge=0,
        description="Número de problemas detectados"
    )
    num_recomendaciones: int = Field(
        ...,
        ge=0,
        description="Número de recomendaciones generadas"
    )
    planta_nombre: Optional[str] = Field(
        None,
        description="Nombre personalizado de la planta"
    )
    
    class Config:
        """Configuración del schema."""
        from_attributes = True
        use_enum_values = True


class HistorialSaludResponse(BaseModel):
    """
    Schema para la respuesta del endpoint de historial de salud.
    
    Incluye lista paginada de análisis históricos.
    """
    analisis: List[HistorialSaludItem] = Field(
        ...,
        description="Lista de análisis históricos"
    )
    total: int = Field(
        ...,
        ge=0,
        description="Número total de análisis en la BD"
    )
    planta_id: Optional[int] = Field(
        None,
        ge=1,
        description="ID de la planta (si se filtró por planta)"
    )
    limite: Optional[int] = Field(
        None,
        ge=1,
        description="Límite de resultados por página"
    )
    offset: Optional[int] = Field(
        None,
        ge=0,
        description="Desplazamiento para paginación"
    )
    
    class Config:
        """Configuración del schema."""
        from_attributes = True


class EstadisticasSaludPlanta(BaseModel):
    """
    Schema para estadísticas agregadas de salud de una planta.
    
    Proporciona métricas sobre la evolución de la salud a lo largo del tiempo.
    """
    planta_id: int = Field(
        ...,
        ge=1,
        description="ID de la planta"
    )
    total_analisis: int = Field(
        ...,
        ge=0,
        description="Número total de análisis realizados"
    )
    ultimo_estado: Optional[EstadoSaludDetallado] = Field(
        None,
        description="Último estado de salud registrado"
    )
    ultimo_analisis_fecha: Optional[datetime] = Field(
        None,
        description="Fecha del último análisis"
    )
    confianza_promedio: Optional[float] = Field(
        None,
        ge=0.0,
        le=100.0,
        description="Confianza promedio de todos los análisis"
    )
    tendencia_salud: Optional[str] = Field(
        None,
        description="Tendencia general (mejorando, estable, empeorando)",
        examples=["mejorando", "estable", "empeorando"]
    )
    dias_desde_ultimo_analisis: Optional[int] = Field(
        None,
        ge=0,
        description="Días desde el último análisis"
    )
    
    class Config:
        """Configuración del schema."""
        from_attributes = True


class SolicitudAnalisisSalud(BaseModel):
    """
    Schema para solicitud de análisis de salud de una planta.
    
    Este schema se usa en el endpoint POST /api/salud/analisis
    para crear un nuevo análisis de salud.
    """
    planta_id: int = Field(
        ...,
        ge=1,
        description="ID de la planta a analizar"
    )
    imagen_id: Optional[int] = Field(
        None,
        ge=1,
        description="ID de la imagen para análisis visual (opcional)"
    )
    sintomas_observados: Optional[str] = Field(
        None,
        max_length=1000,
        description="Síntomas observados por el usuario"
    )
    notas_adicionales: Optional[str] = Field(
        None,
        max_length=1000,
        description="Notas adicionales del usuario"
    )
    
    class Config:
        """Configuración del schema."""
        from_attributes = True


class AnalisisRapidoRequest(BaseModel):
    """
    Schema para solicitud de análisis rápido sin guardar en BD.
    
    Este schema se usa cuando el usuario solo quiere un análisis
    preliminar sin guardarlo en el historial.
    """
    datos_planta: Dict[str, Any] = Field(
        ...,
        description="Datos de la planta para contexto del análisis"
    )
    incluir_imagen: bool = Field(
        default=False,
        description="Indica si se incluye imagen"
    )
    
    class Config:
        """Configuración del schema."""
        from_attributes = True
