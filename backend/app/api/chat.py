"""
Router de Chat - Endpoints para conversaciones con asistente de jardinería.

Este módulo contiene todos los endpoints REST para gestionar conversaciones
y mensajes del chat con Gemini AI.

Autor: Equipo Backend
Fecha: Noviembre 2025
Feature: Chat Asistente de Jardinería
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.chat import (
    ConversacionCreate,
    ConversacionResponse,
    ConversacionConMensajesResponse,
    MensajeCreate,
    MensajeResponse,
    ChatResponse,
    ConversacionesListResponse,
    MensajesListResponse,
    ConversacionUpdate
)
from app.services.chat_service import ChatService
from app.utils.jwt import get_current_user
from app.db.models import Usuario

# Crear router de chat
router = APIRouter()


@router.post(
    "/conversaciones",
    response_model=ConversacionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nueva conversación",
    description="Crea una nueva conversación de chat con el asistente de jardinería"
)
async def crear_conversacion(
    datos: ConversacionCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Crea una nueva conversación de chat.
    
    - **titulo**: Título personalizado (opcional, se auto-genera al primer mensaje)
    
    Returns:
        Conversación creada con ID asignado
    """
    try:
        conversacion = ChatService.crear_conversacion(
            db=db,
            usuario_id=current_user.id,
            titulo=datos.titulo
        )
        
        return ConversacionResponse(
            id=conversacion.id,
            usuario_id=conversacion.usuario_id,
            titulo=conversacion.titulo,
            created_at=conversacion.created_at,
            updated_at=conversacion.updated_at,
            is_active=conversacion.is_active,
            total_mensajes=0
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear conversación: {str(e)}"
        )


@router.get(
    "/conversaciones",
    response_model=ConversacionesListResponse,
    summary="Listar conversaciones",
    description="Obtiene todas las conversaciones del usuario autenticado"
)
async def listar_conversaciones(
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(20, ge=1, le=100, description="Máximo de registros a retornar"),
    solo_activas: bool = Query(True, description="Solo conversaciones activas"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Lista todas las conversaciones del usuario.
    
    Las conversaciones se ordenan por última actualización (más recientes primero).
    
    Query params:
    - **skip**: Offset para paginación
    - **limit**: Límite de resultados (máx 100)
    - **solo_activas**: Si True, excluye conversaciones archivadas
    
    Returns:
        Lista paginada de conversaciones con total de mensajes
    """
    try:
        conversaciones = ChatService.obtener_conversaciones(
            db=db,
            usuario_id=current_user.id,
            skip=skip,
            limit=limit,
            solo_activas=solo_activas
        )
        
        # Convertir a response models
        conversaciones_response = []
        for conv in conversaciones:
            conversaciones_response.append(
                ConversacionResponse(
                    id=conv.id,
                    usuario_id=conv.usuario_id,
                    titulo=conv.titulo,
                    created_at=conv.created_at,
                    updated_at=conv.updated_at,
                    is_active=conv.is_active,
                    total_mensajes=len(conv.mensajes) if hasattr(conv, 'mensajes') else 0
                )
            )
        
        # Contar total de conversaciones
        from app.db.models import ChatConversacion
        query = db.query(ChatConversacion).filter(
            ChatConversacion.usuario_id == current_user.id
        )
        if solo_activas:
            query = query.filter(ChatConversacion.is_active == True)
        total = query.count()
        
        return ConversacionesListResponse(
            total=total,
            conversaciones=conversaciones_response
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener conversaciones: {str(e)}"
        )


@router.get(
    "/conversaciones/{conversacion_id}",
    response_model=ConversacionConMensajesResponse,
    summary="Obtener conversación con mensajes",
    description="Obtiene una conversación específica con todos sus mensajes"
)
async def obtener_conversacion(
    conversacion_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtiene una conversación completa con su historial de mensajes.
    
    Path params:
    - **conversacion_id**: ID de la conversación
    
    Returns:
        Conversación con lista completa de mensajes ordenados cronológicamente
    """
    try:
        # Obtener conversación
        from app.db.models import ChatConversacion
        conversacion = db.query(ChatConversacion).filter(
            ChatConversacion.id == conversacion_id,
            ChatConversacion.usuario_id == current_user.id
        ).first()
        
        if not conversacion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversación {conversacion_id} no encontrada"
            )
        
        # Obtener mensajes
        mensajes = ChatService.obtener_mensajes(
            db=db,
            conversacion_id=conversacion_id,
            usuario_id=current_user.id,
            limit=1000  # Todos los mensajes
        )
        
        mensajes_response = [
            MensajeResponse(
                id=msg.id,
                conversacion_id=msg.conversacion_id,
                rol=msg.rol,
                contenido=msg.contenido,
                planta_id=msg.planta_id,
                tokens_usados=msg.tokens_usados,
                created_at=msg.created_at
            )
            for msg in mensajes
        ]
        
        return ConversacionConMensajesResponse(
            id=conversacion.id,
            usuario_id=conversacion.usuario_id,
            titulo=conversacion.titulo,
            created_at=conversacion.created_at,
            updated_at=conversacion.updated_at,
            is_active=conversacion.is_active,
            total_mensajes=len(mensajes_response),
            mensajes=mensajes_response
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener conversación: {str(e)}"
        )


@router.post(
    "/conversaciones/{conversacion_id}/mensajes",
    response_model=ChatResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Enviar mensaje",
    description="Envía un mensaje del usuario y obtiene respuesta del asistente IA"
)
async def enviar_mensaje(
    conversacion_id: int,
    datos: MensajeCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Envía un mensaje del usuario y recibe respuesta del asistente.
    
    Este endpoint:
    1. Guarda el mensaje del usuario
    2. Construye contexto (historial + datos de planta si se especifica)
    3. Llama a Gemini AI para generar respuesta
    4. Guarda la respuesta del asistente
    5. Retorna ambos mensajes
    
    Path params:
    - **conversacion_id**: ID de la conversación
    
    Body:
    - **contenido**: Mensaje del usuario (1-2000 caracteres)
    - **planta_id**: ID de planta para agregar contexto (opcional)
    
    Returns:
        Mensaje del usuario y respuesta del asistente
    """
    try:
        mensaje_usuario, mensaje_asistente = await ChatService.enviar_mensaje(
            db=db,
            conversacion_id=conversacion_id,
            usuario_id=current_user.id,
            contenido=datos.contenido,
            planta_id=datos.planta_id
        )
        
        return ChatResponse(
            conversacion_id=conversacion_id,
            mensaje_usuario=MensajeResponse(
                id=mensaje_usuario.id,
                conversacion_id=mensaje_usuario.conversacion_id,
                rol=mensaje_usuario.rol,
                contenido=mensaje_usuario.contenido,
                planta_id=mensaje_usuario.planta_id,
                tokens_usados=mensaje_usuario.tokens_usados,
                created_at=mensaje_usuario.created_at
            ),
            mensaje_asistente=MensajeResponse(
                id=mensaje_asistente.id,
                conversacion_id=mensaje_asistente.conversacion_id,
                rol=mensaje_asistente.rol,
                contenido=mensaje_asistente.contenido,
                planta_id=mensaje_asistente.planta_id,
                tokens_usados=mensaje_asistente.tokens_usados,
                created_at=mensaje_asistente.created_at
            )
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al enviar mensaje: {str(e)}"
        )


@router.get(
    "/conversaciones/{conversacion_id}/mensajes",
    response_model=MensajesListResponse,
    summary="Obtener mensajes",
    description="Obtiene los mensajes de una conversación con paginación"
)
async def obtener_mensajes(
    conversacion_id: int,
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(50, ge=1, le=200, description="Máximo de registros"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtiene mensajes de una conversación con paginación.
    
    Path params:
    - **conversacion_id**: ID de la conversación
    
    Query params:
    - **skip**: Offset para paginación
    - **limit**: Límite de resultados (máx 200)
    
    Returns:
        Lista paginada de mensajes ordenados cronológicamente
    """
    try:
        mensajes = ChatService.obtener_mensajes(
            db=db,
            conversacion_id=conversacion_id,
            usuario_id=current_user.id,
            skip=skip,
            limit=limit
        )
        
        mensajes_response = [
            MensajeResponse(
                id=msg.id,
                conversacion_id=msg.conversacion_id,
                rol=msg.rol,
                contenido=msg.contenido,
                planta_id=msg.planta_id,
                tokens_usados=msg.tokens_usados,
                created_at=msg.created_at
            )
            for msg in mensajes
        ]
        
        # Contar total de mensajes
        from app.db.models import ChatMensaje
        total = db.query(ChatMensaje).filter(
            ChatMensaje.conversacion_id == conversacion_id
        ).count()
        
        return MensajesListResponse(
            conversacion_id=conversacion_id,
            total=total,
            mensajes=mensajes_response
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener mensajes: {str(e)}"
        )


@router.delete(
    "/conversaciones/{conversacion_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar conversación",
    description="Elimina (archiva) una conversación"
)
async def eliminar_conversacion(
    conversacion_id: int,
    permanente: bool = Query(False, description="Si True, elimina permanentemente (no recomendado)"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Elimina una conversación del usuario.
    
    Por defecto hace soft delete (marca como inactiva).
    
    Path params:
    - **conversacion_id**: ID de la conversación a eliminar
    
    Query params:
    - **permanente**: Si True, elimina de BD (no recomendado). Por defecto False (soft delete)
    
    Returns:
        204 No Content
    """
    try:
        ChatService.eliminar_conversacion(
            db=db,
            conversacion_id=conversacion_id,
            usuario_id=current_user.id,
            soft_delete=not permanente
        )
        
        return None
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar conversación: {str(e)}"
        )


@router.patch(
    "/conversaciones/{conversacion_id}",
    response_model=ConversacionResponse,
    summary="Actualizar conversación",
    description="Actualiza el título o estado de una conversación"
)
async def actualizar_conversacion(
    conversacion_id: int,
    datos: ConversacionUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Actualiza propiedades de una conversación.
    
    Path params:
    - **conversacion_id**: ID de la conversación
    
    Body:
    - **titulo**: Nuevo título (opcional)
    - **is_active**: Cambiar estado activo/archivado (opcional)
    
    Returns:
        Conversación actualizada
    """
    try:
        from app.db.models import ChatConversacion
        from datetime import datetime
        
        conversacion = db.query(ChatConversacion).filter(
            ChatConversacion.id == conversacion_id,
            ChatConversacion.usuario_id == current_user.id
        ).first()
        
        if not conversacion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversación {conversacion_id} no encontrada"
            )
        
        # Actualizar campos
        if datos.titulo is not None:
            conversacion.titulo = datos.titulo
        
        if datos.is_active is not None:
            conversacion.is_active = datos.is_active
        
        conversacion.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(conversacion)
        
        return ConversacionResponse(
            id=conversacion.id,
            usuario_id=conversacion.usuario_id,
            titulo=conversacion.titulo,
            created_at=conversacion.created_at,
            updated_at=conversacion.updated_at,
            is_active=conversacion.is_active,
            total_mensajes=len(conversacion.mensajes) if hasattr(conversacion, 'mensajes') else 0
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar conversación: {str(e)}"
        )
