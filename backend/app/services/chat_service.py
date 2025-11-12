"""
Servicio de Chat con Gemini AI para asistencia de jardinería.

Este servicio maneja la lógica de conversación con el LLM, incluyendo:
- Construcción de contexto inteligente (historial + datos de plantas)
- Manejo de límites de tokens para evitar overflow
- Generación de títulos de conversación
- Integración con base de datos

Autor: Equipo Backend
Fecha: Noviembre 2025
Feature: Chat Asistente de Jardinería
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc

try:
    import google.generativeai as genai
    from google.generativeai.types import HarmCategory, HarmBlockThreshold
except ImportError:
    raise ImportError(
        "google-generativeai no está instalado. "
        "Ejecuta: pip install google-generativeai"
    )

from app.core.config import obtener_configuracion
from app.db.models import ChatConversacion, ChatMensaje, Planta, AnalisisSalud, Usuario

# Configuración
config = obtener_configuracion()
logger = logging.getLogger(__name__)

# Configurar Gemini API
if config.gemini_api_key:
    genai.configure(api_key=config.gemini_api_key)
else:
    logger.warning("⚠️  GEMINI_API_KEY no configurada. El servicio de chat no funcionará.")


class ChatService:
    """Servicio para gestionar conversaciones de chat con Gemini AI."""
    
    # Límites de contexto para evitar overflow
    MAX_MENSAJES_HISTORIAL = 10  # Últimos N mensajes a incluir
    MAX_TOKENS_CONTEXTO = 4000   # Tokens máximos para contexto de planta
    
    # Configuración de seguridad (permitir contenido sobre plantas)
    SAFETY_SETTINGS = {
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    }
    
    @staticmethod
    def crear_conversacion(
        db: Session,
        usuario_id: int,
        titulo: Optional[str] = None
    ) -> ChatConversacion:
        """
        Crea una nueva conversación de chat.
        
        Args:
            db: Sesión de base de datos
            usuario_id: ID del usuario
            titulo: Título personalizado (opcional, se genera automáticamente)
        
        Returns:
            ChatConversacion: Nueva conversación creada
        """
        nueva_conversacion = ChatConversacion(
            usuario_id=usuario_id,
            titulo=titulo or "Nueva conversación",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            is_active=True
        )
        
        db.add(nueva_conversacion)
        db.commit()
        db.refresh(nueva_conversacion)
        
        logger.info(f"✅ Conversación {nueva_conversacion.id} creada para usuario {usuario_id}")
        return nueva_conversacion
    
    @staticmethod
    def obtener_conversaciones(
        db: Session,
        usuario_id: int,
        skip: int = 0,
        limit: int = 20,
        solo_activas: bool = True
    ) -> List[ChatConversacion]:
        """
        Obtiene las conversaciones de un usuario.
        
        Args:
            db: Sesión de base de datos
            usuario_id: ID del usuario
            skip: Número de registros a saltar (paginación)
            limit: Máximo de registros a retornar
            solo_activas: Si True, solo retorna conversaciones activas
        
        Returns:
            Lista de conversaciones ordenadas por última actualización
        """
        query = db.query(ChatConversacion).filter(
            ChatConversacion.usuario_id == usuario_id
        )
        
        if solo_activas:
            query = query.filter(ChatConversacion.is_active == True)
        
        conversaciones = query.order_by(
            desc(ChatConversacion.updated_at)
        ).offset(skip).limit(limit).all()
        
        return conversaciones
    
    @staticmethod
    def obtener_mensajes(
        db: Session,
        conversacion_id: int,
        usuario_id: int,
        skip: int = 0,
        limit: int = 50
    ) -> List[ChatMensaje]:
        """
        Obtiene los mensajes de una conversación.
        
        Args:
            db: Sesión de base de datos
            conversacion_id: ID de la conversación
            usuario_id: ID del usuario (para validar permisos)
            skip: Número de registros a saltar
            limit: Máximo de registros a retornar
        
        Returns:
            Lista de mensajes ordenados cronológicamente
        
        Raises:
            ValueError: Si la conversación no existe o no pertenece al usuario
        """
        # Validar que la conversación existe y pertenece al usuario
        conversacion = db.query(ChatConversacion).filter(
            ChatConversacion.id == conversacion_id,
            ChatConversacion.usuario_id == usuario_id
        ).first()
        
        if not conversacion:
            raise ValueError(f"Conversación {conversacion_id} no encontrada o no pertenece al usuario")
        
        mensajes = db.query(ChatMensaje).filter(
            ChatMensaje.conversacion_id == conversacion_id
        ).order_by(ChatMensaje.created_at).offset(skip).limit(limit).all()
        
        return mensajes
    
    @staticmethod
    def _construir_contexto_planta(
        db: Session,
        planta_id: int,
        usuario_id: int
    ) -> str:
        """
        Construye contexto sobre una planta específica.
        
        Args:
            db: Sesión de base de datos
            planta_id: ID de la planta
            usuario_id: ID del usuario (para validar permisos)
        
        Returns:
            String con información contextual de la planta
        """
        planta = db.query(Planta).filter(
            Planta.id == planta_id,
            Planta.usuario_id == usuario_id
        ).first()
        
        if not planta:
            return ""
        
        # Obtener último análisis de salud
        ultimo_analisis = db.query(AnalisisSalud).filter(
            AnalisisSalud.planta_id == planta_id
        ).order_by(desc(AnalisisSalud.created_at)).first()
        
        # Construir contexto
        contexto = f"""
INFORMACIÓN DE LA PLANTA:
- Nombre: {planta.nombre_personal}
- Especie: {planta.especie.nombre_cientifico if planta.especie else 'No especificada'}
- Ubicación: {planta.ubicacion or 'No especificada'}
- Estado de salud: {planta.estado_salud}
- Frecuencia de riego: Cada {planta.frecuencia_riego_dias} días
- Luz actual: {planta.luz_actual}
- Último riego: {planta.fecha_ultimo_riego.strftime('%Y-%m-%d') if planta.fecha_ultimo_riego else 'Sin registro'}
"""
        
        if ultimo_analisis:
            contexto += f"""
- Último análisis de salud: {ultimo_analisis.estado} ({ultimo_analisis.confianza}% confianza)
- Diagnóstico: {ultimo_analisis.diagnostico_resumido}
"""
        
        if planta.notas:
            contexto += f"- Notas del usuario: {planta.notas}\n"
        
        return contexto
    
    @staticmethod
    def _construir_historial_mensajes(
        mensajes: List[ChatMensaje],
        max_mensajes: int = 10
    ) -> List[Dict[str, str]]:
        """
        Construye historial de mensajes para el LLM.
        
        Args:
            mensajes: Lista completa de mensajes de la conversación
            max_mensajes: Máximo de mensajes a incluir (para evitar overflow)
        
        Returns:
            Lista de mensajes en formato para Gemini
        """
        # Tomar solo los últimos N mensajes
        mensajes_recientes = mensajes[-max_mensajes:] if len(mensajes) > max_mensajes else mensajes
        
        historial = []
        for mensaje in mensajes_recientes:
            historial.append({
                "role": "user" if mensaje.rol == "user" else "model",
                "parts": [mensaje.contenido]
            })
        
        return historial
    
    @staticmethod
    def _generar_prompt_sistema(
        usuario: Optional[Usuario] = None,
        contexto_planta: Optional[str] = None
    ) -> str:
        """
        Genera el prompt del sistema con contexto.
        
        Args:
            usuario: Usuario actual (opcional)
            contexto_planta: Contexto de planta específica (opcional)
        
        Returns:
            Prompt del sistema
        """
        prompt = """Eres un experto jardinero y botánico con años de experiencia en el cuidado de plantas.

Tu objetivo es ayudar a los usuarios a cuidar mejor sus plantas, respondiendo preguntas sobre:
- Identificación y características de plantas
- Diagnóstico de problemas (plagas, enfermedades, deficiencias)
- Consejos de riego, luz, fertilización y trasplante
- Cuidados específicos según especie y condiciones ambientales
- Prevención de problemas comunes

INSTRUCCIONES:
1. Responde de forma clara, amigable y práctica
2. Da consejos específicos y accionables
3. Si no tienes información suficiente, pide más detalles
4. Menciona posibles riesgos y precauciones
5. Sé conciso pero completo (máximo 3 párrafos por respuesta)
6. Usa emojis relevantes para hacer la respuesta más amigable 🌱

"""
        
        if usuario and usuario.nombre:
            prompt += f"Estás asistiendo a {usuario.nombre}.\n\n"
        
        if contexto_planta:
            prompt += f"{contexto_planta}\n"
        
        return prompt
    
    @staticmethod
    async def enviar_mensaje(
        db: Session,
        conversacion_id: int,
        usuario_id: int,
        contenido: str,
        planta_id: Optional[int] = None
    ) -> Tuple[ChatMensaje, ChatMensaje]:
        """
        Envía un mensaje del usuario y obtiene respuesta del asistente.
        
        Args:
            db: Sesión de base de datos
            conversacion_id: ID de la conversación
            usuario_id: ID del usuario
            contenido: Contenido del mensaje del usuario
            planta_id: ID de planta relacionada (opcional)
        
        Returns:
            Tuple con (mensaje_usuario, mensaje_asistente)
        
        Raises:
            ValueError: Si la conversación no existe o no pertenece al usuario
            Exception: Si hay error al comunicarse con Gemini
        """
        # Validar conversación
        conversacion = db.query(ChatConversacion).filter(
            ChatConversacion.id == conversacion_id,
            ChatConversacion.usuario_id == usuario_id
        ).first()
        
        if not conversacion:
            raise ValueError(f"Conversación {conversacion_id} no encontrada")
        
        # Obtener usuario para contexto
        usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
        
        # 1. Guardar mensaje del usuario
        mensaje_usuario = ChatMensaje(
            conversacion_id=conversacion_id,
            rol="user",
            contenido=contenido,
            planta_id=planta_id,
            created_at=datetime.utcnow()
        )
        db.add(mensaje_usuario)
        db.flush()
        
        try:
            # 2. Construir contexto
            contexto_planta = None
            if planta_id:
                contexto_planta = ChatService._construir_contexto_planta(db, planta_id, usuario_id)
            
            # 3. Obtener historial de mensajes (excluyendo el mensaje actual)
            mensajes_previos = db.query(ChatMensaje).filter(
                ChatMensaje.conversacion_id == conversacion_id,
                ChatMensaje.id != mensaje_usuario.id
            ).order_by(ChatMensaje.created_at).all()
            
            historial = ChatService._construir_historial_mensajes(
                mensajes_previos,
                max_mensajes=ChatService.MAX_MENSAJES_HISTORIAL
            )
            
            # 4. Generar prompt del sistema
            prompt_sistema = ChatService._generar_prompt_sistema(usuario, contexto_planta)
            
            # 5. Llamar a Gemini
            logger.info(f"🤖 Llamando a Gemini para conversación {conversacion_id}")
            
            modelo = genai.GenerativeModel(
                model_name=config.gemini_model,
                safety_settings=ChatService.SAFETY_SETTINGS
            )
            
            # Agregar instrucción del sistema como primer mensaje del historial
            historial_completo = [
                {
                    "role": "user",
                    "parts": [prompt_sistema]
                },
                {
                    "role": "model",
                    "parts": ["Entendido. Estoy listo para ayudarte con tus plantas. ¿En qué puedo asistirte? 🌱"]
                }
            ] + historial
            
            # Iniciar chat con historial
            chat = modelo.start_chat(history=historial_completo)
            
            # Enviar mensaje y obtener respuesta
            respuesta = chat.send_message(contenido)
            
            # 6. Guardar respuesta del asistente
            mensaje_asistente = ChatMensaje(
                conversacion_id=conversacion_id,
                rol="assistant",
                contenido=respuesta.text,
                planta_id=planta_id,
                tokens_usados=respuesta.usage_metadata.total_token_count if hasattr(respuesta, 'usage_metadata') else 0,
                metadata_json=json.dumps({
                    "modelo": config.gemini_model,
                    "prompt_tokens": respuesta.usage_metadata.prompt_token_count if hasattr(respuesta, 'usage_metadata') else 0,
                    "completion_tokens": respuesta.usage_metadata.candidates_token_count if hasattr(respuesta, 'usage_metadata') else 0,
                    "timestamp": datetime.utcnow().isoformat()
                }),
                created_at=datetime.utcnow()
            )
            db.add(mensaje_asistente)
            
            # 7. Actualizar conversación
            conversacion.updated_at = datetime.utcnow()
            
            # 8. Auto-generar título si es la primera interacción
            if len(mensajes_previos) == 0 and conversacion.titulo == "Nueva conversación":
                titulo_generado = ChatService._generar_titulo_conversacion(contenido, respuesta.text)
                conversacion.titulo = titulo_generado
            
            db.commit()
            db.refresh(mensaje_usuario)
            db.refresh(mensaje_asistente)
            
            logger.info(f"✅ Respuesta generada para conversación {conversacion_id}")
            
            return mensaje_usuario, mensaje_asistente
        
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Error al generar respuesta: {str(e)}")
            raise Exception(f"Error al comunicarse con el asistente: {str(e)}")
    
    @staticmethod
    def _generar_titulo_conversacion(pregunta: str, respuesta: str) -> str:
        """
        Genera un título descriptivo basado en el primer mensaje.
        
        Args:
            pregunta: Primera pregunta del usuario
            respuesta: Primera respuesta del asistente
        
        Returns:
            Título generado (máximo 50 caracteres)
        """
        # Extraer palabras clave de la pregunta
        pregunta_lower = pregunta.lower()
        
        # Palabras clave comunes en jardinería
        keywords = {
            'riego': '💧 Riego',
            'agua': '💧 Riego',
            'enfermedad': '🩺 Enfermedad',
            'plaga': '🐛 Plagas',
            'amarill': '🍂 Hojas amarillas',
            'marron': '🍂 Hojas marrones',
            'luz': '☀️ Luz',
            'sol': '☀️ Sol',
            'tierra': '🌱 Sustrato',
            'fertiliz': '🌿 Fertilización',
            'trasplant': '🪴 Trasplante',
            'poda': '✂️ Poda',
            'identificar': '🔍 Identificación',
        }
        
        for keyword, titulo in keywords.items():
            if keyword in pregunta_lower:
                return titulo[:50]
        
        # Si no hay keyword, usar las primeras palabras de la pregunta
        palabras = pregunta.split()[:5]
        titulo = ' '.join(palabras)
        
        if len(titulo) > 50:
            titulo = titulo[:47] + "..."
        
        return titulo or "Consulta de jardinería"
    
    @staticmethod
    def eliminar_conversacion(
        db: Session,
        conversacion_id: int,
        usuario_id: int,
        soft_delete: bool = True
    ) -> bool:
        """
        Elimina una conversación (soft o hard delete).
        
        Args:
            db: Sesión de base de datos
            conversacion_id: ID de la conversación
            usuario_id: ID del usuario (para validar permisos)
            soft_delete: Si True, solo marca como inactiva. Si False, elimina de BD
        
        Returns:
            True si se eliminó exitosamente
        
        Raises:
            ValueError: Si la conversación no existe o no pertenece al usuario
        """
        conversacion = db.query(ChatConversacion).filter(
            ChatConversacion.id == conversacion_id,
            ChatConversacion.usuario_id == usuario_id
        ).first()
        
        if not conversacion:
            raise ValueError(f"Conversación {conversacion_id} no encontrada")
        
        if soft_delete:
            conversacion.is_active = False
            conversacion.updated_at = datetime.utcnow()
            db.commit()
            logger.info(f"🗑️ Conversación {conversacion_id} archivada (soft delete)")
        else:
            db.delete(conversacion)
            db.commit()
            logger.info(f"🗑️ Conversación {conversacion_id} eliminada permanentemente")
        
        return True
