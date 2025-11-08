/**
 * Servicio de Health Check para análisis de salud de plantas
 * 
 * Cliente para consumir los endpoints de análisis de salud del backend.
 * Proporciona métodos para:
 * - Crear análisis de salud
 * - Consultar estadísticas de salud
 * - Obtener historial de análisis
 * 
 * @author Equipo Frontend
 * @date Noviembre 2025
 * @sprint Sprint Health Check
 */

import axios from './axios'
import { AxiosError } from 'axios'
import {
  AnalisisSaludRequest,
  AnalisisSaludResponse,
  EstadisticasSalud,
  HistorialSaludResponse,
  HistorialSaludParams,
} from '@/models/salud'

/**
 * Servicio de Health Check para análisis de salud
 */
class SaludService {
  private readonly baseUrl = '/api/salud'

  /**
   * Crea un nuevo análisis de salud para una planta
   * 
   * @param request - Datos del análisis (planta_id, imagen_id, notas)
   * @returns Promise con el resultado del análisis
   * 
   * @throws {Error} Si la planta o imagen no existen, o si falla el análisis
   * 
   * @example
   * ```typescript
   * const analisis = await saludService.crearAnalisis({
   *   planta_id: 123,
   *   imagen_id: 456,
   *   notas: 'Hojas amarillentas'
   * })
   * console.log(analisis.estado) // 'necesita_atencion'
   * console.log(analisis.diagnostico)
   * console.log(analisis.recomendaciones)
   * ```
   */
  async crearAnalisis(request: AnalisisSaludRequest): Promise<AnalisisSaludResponse> {
    try {
      const response = await axios.post<AnalisisSaludResponse>(
        `${this.baseUrl}/analisis`,
        request
      )
      return response.data
    } catch (error) {
      if (error instanceof AxiosError) {
        const mensaje = error.response?.data?.detail || 'Error al crear análisis de salud'
        throw new Error(mensaje)
      }
      throw new Error('Error al crear análisis de salud')
    }
  }

  /**
   * Obtiene las estadísticas de salud de una planta
   * 
   * Incluye:
   * - Último estado de salud
   * - Total de análisis realizados
   * - Confianza promedio
   * - Días desde último análisis
   * - Tendencia (mejorando, estable, empeorando)
   * 
   * @param plantaId - ID de la planta
   * @returns Promise con las estadísticas de salud
   * 
   * @throws {Error} Si la planta no existe o no tiene análisis
   * 
   * @example
   * ```typescript
   * const stats = await saludService.obtenerEstadisticas(123)
   * console.log(stats.ultimo_estado) // 'saludable'
   * console.log(stats.confianza_promedio) // 85.5
   * console.log(stats.tendencia) // 'estable'
   * ```
   */
  async obtenerEstadisticas(plantaId: number): Promise<EstadisticasSalud> {
    try {
      const response = await axios.get<EstadisticasSalud>(
        `${this.baseUrl}/estadisticas/${plantaId}`
      )
      return response.data
    } catch (error) {
      if (error instanceof AxiosError) {
        const mensaje = error.response?.data?.detail || 'Error al obtener estadísticas de salud'
        throw new Error(mensaje)
      }
      throw new Error('Error al obtener estadísticas de salud')
    }
  }

  /**
   * Obtiene el historial de análisis de salud de una planta
   * 
   * Soporta:
   * - Paginación (limite, offset)
   * - Filtrado por estado
   * - Filtrado por rango de fechas
   * 
   * @param plantaId - ID de la planta
   * @param params - Parámetros de consulta (opcional)
   * @returns Promise con el historial de análisis
   * 
   * @throws {Error} Si la planta no existe
   * 
   * @example
   * ```typescript
   * // Obtener últimos 10 análisis
   * const historial = await saludService.obtenerHistorial(123, {
   *   limite: 10,
   *   offset: 0
   * })
   * 
   * // Filtrar por estado
   * const criticos = await saludService.obtenerHistorial(123, {
   *   estado: 'enfermedad',
   *   limite: 20
   * })
   * 
   * // Filtrar por fechas
   * const recientes = await saludService.obtenerHistorial(123, {
   *   fecha_desde: '2025-11-01T00:00:00Z',
   *   fecha_hasta: '2025-11-08T23:59:59Z'
   * })
   * ```
   */
  async obtenerHistorial(
    plantaId: number,
    params?: HistorialSaludParams
  ): Promise<HistorialSaludResponse> {
    try {
      const response = await axios.get<HistorialSaludResponse>(
        `${this.baseUrl}/historial/${plantaId}`,
        { params }
      )
      return response.data
    } catch (error) {
      if (error instanceof AxiosError) {
        const mensaje = error.response?.data?.detail || 'Error al obtener historial de salud'
        throw new Error(mensaje)
      }
      throw new Error('Error al obtener historial de salud')
    }
  }

  /**
   * Obtiene un análisis específico por su ID
   * 
   * @param analisisId - ID del análisis
   * @returns Promise con los detalles del análisis
   * 
   * @throws {Error} Si el análisis no existe
   * 
   * @example
   * ```typescript
   * const analisis = await saludService.obtenerAnalisis(789)
   * console.log(analisis.estado)
   * console.log(analisis.diagnostico)
   * console.log(analisis.recomendaciones)
   * ```
   */
  async obtenerAnalisis(analisisId: number): Promise<AnalisisSaludResponse> {
    try {
      const response = await axios.get<AnalisisSaludResponse>(
        `${this.baseUrl}/analisis/${analisisId}`
      )
      return response.data
    } catch (error) {
      if (error instanceof AxiosError) {
        const mensaje = error.response?.data?.detail || 'Error al obtener análisis'
        throw new Error(mensaje)
      }
      throw new Error('Error al obtener análisis')
    }
  }

  /**
   * Elimina un análisis de salud
   * 
   * @param analisisId - ID del análisis a eliminar
   * @returns Promise que se resuelve cuando se elimina
   * 
   * @throws {Error} Si el análisis no existe o no se puede eliminar
   * 
   * @example
   * ```typescript
   * await saludService.eliminarAnalisis(789)
   * console.log('Análisis eliminado')
   * ```
   */
  async eliminarAnalisis(analisisId: number): Promise<void> {
    try {
      await axios.delete(`${this.baseUrl}/analisis/${analisisId}`)
    } catch (error) {
      if (error instanceof AxiosError) {
        const mensaje = error.response?.data?.detail || 'Error al eliminar análisis'
        throw new Error(mensaje)
      }
      throw new Error('Error al eliminar análisis')
    }
  }

  /**
   * Verifica la disponibilidad del servicio de Health Check
   * 
   * @returns Promise con el estado del servicio
   * 
   * @example
   * ```typescript
   * const disponible = await saludService.verificarServicio()
   * if (disponible) {
   *   console.log('Servicio disponible')
   * }
   * ```
   */
  async verificarServicio(): Promise<boolean> {
    try {
      const response = await axios.get(`${this.baseUrl}/health`)
      return response.status === 200
    } catch (error) {
      return false
    }
  }
}

// Exportar instancia singleton
const saludService = new SaludService()
export default saludService
