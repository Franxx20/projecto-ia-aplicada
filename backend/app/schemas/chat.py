"""
Schemas Pydantic para el sistema de Chat.

Define los modelos de validación para requests y responses
del sistema de chat asistente con Gemini AI.

Autor: Equipo Backend
Fecha: Noviembre 2025
Feature: Chat Asistente de Jardinería
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ==================== REQUEST SCHEMAS ====================

class ConversacionCreate(BaseModel):
    """Schema para crear una nueva conversación."""
    titulo: Optional[str] = Field(
        None,
        max_length=255,
        description="Título personalizado de la conversación (opcional, se auto-genera)"
    )


class MensajeCreate(BaseModel):
    """Schema para enviar un nuevo mensaje."""
    contenido: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Contenido del mensaje del usuario"
    )
    planta_id: Optional[int] = Field(
        None,
        description="ID de planta relacionada para agregar contexto (opcional)"
    )


class ConversacionUpdate(BaseModel):
    """Schema para actualizar una conversación."""
    titulo: Optional[str] = Field(None, max_length=255)
    is_active: Optional[bool] = None


# ==================== RESPONSE SCHEMAS ====================

class MensajeResponse(BaseModel):
    """Schema de respuesta para un mensaje."""
    id: int
    conversacion_id: int
    rol: str  # "user" o "assistant"
    contenido: str
    planta_id: Optional[int] = None
    tokens_usados: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class ConversacionResponse(BaseModel):
    """Schema de respuesta para una conversación."""
    id: int
    usuario_id: int
    titulo: str
    created_at: datetime
    updated_at: datetime
    is_active: bool
    total_mensajes: int = Field(
        default=0,
        description="Número total de mensajes en la conversación"
    )
    
    class Config:
        from_attributes = True


class ConversacionConMensajesResponse(ConversacionResponse):
    """Schema de conversación con sus mensajes incluidos."""
    mensajes: List[MensajeResponse] = []


class ChatResponse(BaseModel):
    """Schema de respuesta para envío de mensaje (incluye pregunta y respuesta)."""
    conversacion_id: int
    mensaje_usuario: MensajeResponse
    mensaje_asistente: MensajeResponse


class ConversacionesListResponse(BaseModel):
    """Schema de respuesta para lista paginada de conversaciones."""
    total: int = Field(..., description="Total de conversaciones del usuario")
    conversaciones: List[ConversacionResponse]


class MensajesListResponse(BaseModel):
    """Schema de respuesta para lista de mensajes de una conversación."""
    conversacion_id: int
    total: int = Field(..., description="Total de mensajes en la conversación")
    mensajes: List[MensajeResponse]


# ==================== SCHEMAS ADICIONALES ====================

class EstadisticasChat(BaseModel):
    """Estadísticas del uso del chat por un usuario."""
    total_conversaciones: int
    conversaciones_activas: int
    total_mensajes: int
    tokens_totales_usados: int
    promedio_mensajes_por_conversacion: float
    
    class Config:
        from_attributes = True
