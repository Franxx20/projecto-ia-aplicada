/**
 * Servicio de Chat API
 * 
 * Cliente para interactuar con los endpoints del chat asistente de jardinería.
 * Maneja conversaciones y mensajes con el LLM (Gemini AI).
 * 
 * @module chatService
 */

import axios from './axios';

// ==================== TIPOS ====================

export interface Conversacion {
  id: number;
  usuario_id: number;
  titulo: string;
  created_at: string;
  updated_at: string;
  is_active: boolean;
  total_mensajes: number;
}

export interface Mensaje {
  id: number;
  conversacion_id: number;
  rol: 'user' | 'assistant';
  contenido: string;
  planta_id?: number;
  tokens_usados?: number;
  created_at: string;
}

export interface ConversacionConMensajes extends Conversacion {
  mensajes: Mensaje[];
}

export interface ChatResponse {
  conversacion_id: number;
  mensaje_usuario: Mensaje;
  mensaje_asistente: Mensaje;
}

export interface ConversacionesListResponse {
  total: number;
  conversaciones: Conversacion[];
}

export interface MensajesListResponse {
  conversacion_id: number;
  total: number;
  mensajes: Mensaje[];
}

// ==================== SERVICIO ====================

const BASE_PATH = '/api/chat';

class ChatService {
  /**
   * Crea una nueva conversación de chat
   * 
   * @param titulo - Título personalizado (opcional)
   * @returns Conversación creada
   */
  async crearConversacion(titulo?: string): Promise<Conversacion> {
    try {
      const response = await axios.post<Conversacion>(
        `${BASE_PATH}/conversaciones`,
        { titulo }
      );
      return response.data;
    } catch (error) {
      console.error('Error al crear conversación:', error);
      throw error;
    }
  }

  /**
   * Obtiene todas las conversaciones del usuario
   * 
   * @param skip - Offset para paginación
   * @param limit - Límite de resultados
   * @param soloActivas - Solo conversaciones activas
   * @returns Lista de conversaciones
   */
  async obtenerConversaciones(
    skip: number = 0,
    limit: number = 20,
    soloActivas: boolean = true
  ): Promise<ConversacionesListResponse> {
    try {
      const response = await axios.get<ConversacionesListResponse>(
        `${BASE_PATH}/conversaciones`,
        {
          params: {
            skip,
            limit,
            solo_activas: soloActivas
          }
        }
      );
      return response.data;
    } catch (error) {
      console.error('Error al obtener conversaciones:', error);
      throw error;
    }
  }

  /**
   * Obtiene una conversación con todos sus mensajes
   * 
   * @param conversacionId - ID de la conversación
   * @returns Conversación con mensajes
   */
  async obtenerConversacion(conversacionId: number): Promise<ConversacionConMensajes> {
    try {
      const response = await axios.get<ConversacionConMensajes>(
        `${BASE_PATH}/conversaciones/${conversacionId}`
      );
      return response.data;
    } catch (error) {
      console.error(`Error al obtener conversación ${conversacionId}:`, error);
      throw error;
    }
  }

  /**
   * Envía un mensaje y obtiene respuesta del asistente
   * 
   * @param conversacionId - ID de la conversación
   * @param contenido - Mensaje del usuario
   * @param plantaId - ID de planta para contexto (opcional)
   * @returns Mensaje del usuario y respuesta del asistente
   */
  async enviarMensaje(
    conversacionId: number,
    contenido: string,
    plantaId?: number
  ): Promise<ChatResponse> {
    try {
      const response = await axios.post<ChatResponse>(
        `${BASE_PATH}/conversaciones/${conversacionId}/mensajes`,
        {
          contenido,
          planta_id: plantaId
        }
      );
      return response.data;
    } catch (error) {
      console.error('Error al enviar mensaje:', error);
      throw error;
    }
  }

  /**
   * Obtiene mensajes de una conversación con paginación
   * 
   * @param conversacionId - ID de la conversación
   * @param skip - Offset para paginación
   * @param limit - Límite de resultados
   * @returns Lista de mensajes
   */
  async obtenerMensajes(
    conversacionId: number,
    skip: number = 0,
    limit: number = 50
  ): Promise<MensajesListResponse> {
    try {
      const response = await axios.get<MensajesListResponse>(
        `${BASE_PATH}/conversaciones/${conversacionId}/mensajes`,
        {
          params: { skip, limit }
        }
      );
      return response.data;
    } catch (error) {
      console.error(`Error al obtener mensajes de conversación ${conversacionId}:`, error);
      throw error;
    }
  }

  /**
   * Elimina (archiva) una conversación
   * 
   * @param conversacionId - ID de la conversación
   * @param permanente - Si true, elimina permanentemente
   */
  async eliminarConversacion(
    conversacionId: number,
    permanente: boolean = false
  ): Promise<void> {
    try {
      await axios.delete(
        `${BASE_PATH}/conversaciones/${conversacionId}`,
        {
          params: { permanente }
        }
      );
    } catch (error) {
      console.error(`Error al eliminar conversación ${conversacionId}:`, error);
      throw error;
    }
  }

  /**
   * Actualiza el título de una conversación
   * 
   * @param conversacionId - ID de la conversación
   * @param titulo - Nuevo título
   * @returns Conversación actualizada
   */
  async actualizarTitulo(
    conversacionId: number,
    titulo: string
  ): Promise<Conversacion> {
    try {
      const response = await axios.patch<Conversacion>(
        `${BASE_PATH}/conversaciones/${conversacionId}`,
        { titulo }
      );
      return response.data;
    } catch (error) {
      console.error(`Error al actualizar título de conversación ${conversacionId}:`, error);
      throw error;
    }
  }

  /**
   * Archiva o restaura una conversación
   * 
   * @param conversacionId - ID de la conversación
   * @param isActive - true para restaurar, false para archivar
   * @returns Conversación actualizada
   */
  async cambiarEstadoActivo(
    conversacionId: number,
    isActive: boolean
  ): Promise<Conversacion> {
    try {
      const response = await axios.patch<Conversacion>(
        `${BASE_PATH}/conversaciones/${conversacionId}`,
        { is_active: isActive }
      );
      return response.data;
    } catch (error) {
      console.error(`Error al cambiar estado de conversación ${conversacionId}:`, error);
      throw error;
    }
  }
}

// Exportar instancia única (singleton)
const chatService = new ChatService();
export default chatService;
