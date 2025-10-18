/**
 * Servicio de API para el Dashboard de Plantas
 * 
 * Proporciona métodos para interactuar con los endpoints de plantas del backend.
 * Maneja la autenticación mediante axios instance que incluye el JWT token.
 * 
 * @module dashboard.service
 */

import axios from './axios';
import type {
  Planta,
  PlantaCreate,
  PlantaUpdate,
  DashboardStats,
  PlantaListResponse,
  RegistrarRiegoRequest,
} from '@/models/dashboard.types';

const BASE_PATH = '/api/plantas';

/**
 * Servicio para gestionar las plantas del usuario
 */
class DashboardService {
  /**
   * Obtiene estadísticas del jardín del usuario actual
   * 
   * @returns {Promise<DashboardStats>} Estadísticas del dashboard
   * @throws {Error} Si hay error en la petición
   * 
   * @example
   * ```typescript
   * const stats = await dashboardService.obtenerEstadisticas();
   * console.log(`Total de plantas: ${stats.total_plantas}`);
   * ```
   */
  async obtenerEstadisticas(): Promise<DashboardStats> {
    try {
      const response = await axios.get<DashboardStats>(`${BASE_PATH}/stats`);
      return response.data;
    } catch (error) {
      console.error('Error al obtener estadísticas del dashboard:', error);
      throw error;
    }
  }

  /**
   * Obtiene todas las plantas del usuario actual con paginación opcional
   * 
   * @param {number} limite - Número máximo de plantas a retornar (default: 100)
   * @param {number} offset - Número de plantas a saltar (default: 0)
   * @param {boolean} soloActivas - Si true, solo retorna plantas activas (default: true)
   * @returns {Promise<PlantaListResponse>} Lista de plantas y total
   * @throws {Error} Si hay error en la petición
   * 
   * @example
   * ```typescript
   * const { plantas, total } = await dashboardService.obtenerPlantas(10, 0);
   * console.log(`Mostrando ${plantas.length} de ${total} plantas`);
   * ```
   */
  async obtenerPlantas(
    limite: number = 100,
    offset: number = 0,
    soloActivas: boolean = true
  ): Promise<PlantaListResponse> {
    try {
      const params = new URLSearchParams({
        limite: limite.toString(),
        offset: offset.toString(),
        ...(soloActivas && { solo_activas: 'true' })
      });

      const response = await axios.get<PlantaListResponse>(
        `${BASE_PATH}?${params.toString()}`
      );
      
      return response.data;
    } catch (error) {
      console.error('Error al obtener plantas:', error);
      throw error;
    }
  }

  /**
   * Obtiene una planta específica por su ID
   * 
   * @param {number} plantaId - ID de la planta a obtener
   * @returns {Promise<Planta>} Datos de la planta
   * @throws {Error} Si hay error en la petición o la planta no existe
   * 
   * @example
   * ```typescript
   * const planta = await dashboardService.obtenerPlanta(123);
   * console.log(`Planta: ${planta.nombre_personal}`);
   * ```
   */
  async obtenerPlanta(plantaId: number): Promise<Planta> {
    try {
      const response = await axios.get<Planta>(`${BASE_PATH}/${plantaId}`);
      return response.data;
    } catch (error) {
      console.error(`Error al obtener planta ${plantaId}:`, error);
      throw error;
    }
  }

  /**
   * Crea una nueva planta para el usuario actual
   * 
   * @param {PlantaCreate} datos - Datos de la nueva planta
   * @returns {Promise<Planta>} Planta creada con su ID asignado
   * @throws {Error} Si hay error en la validación o creación
   * 
   * @example
   * ```typescript
   * const nuevaPlanta = await dashboardService.crearPlanta({
   *   nombre_personal: 'Mi Monstera',
   *   estado_salud: 'buena',
   *   ubicacion: 'Sala',
   *   frecuencia_riego_dias: 7
   * });
   * ```
   */
  async crearPlanta(datos: PlantaCreate): Promise<Planta> {
    try {
      const response = await axios.post<Planta>(BASE_PATH, datos);
      return response.data;
    } catch (error) {
      console.error('Error al crear planta:', error);
      throw error;
    }
  }

  /**
   * Actualiza una planta existente
   * 
   * @param {number} plantaId - ID de la planta a actualizar
   * @param {PlantaUpdate} datos - Campos a actualizar (parcial)
   * @returns {Promise<Planta>} Planta actualizada
   * @throws {Error} Si hay error en la validación o actualización
   * 
   * @example
   * ```typescript
   * const plantaActualizada = await dashboardService.actualizarPlanta(123, {
   *   estado_salud: 'necesita_atencion',
   *   notas: 'Hojas amarillentas'
   * });
   * ```
   */
  async actualizarPlanta(plantaId: number, datos: PlantaUpdate): Promise<Planta> {
    try {
      const response = await axios.put<Planta>(`${BASE_PATH}/${plantaId}`, datos);
      return response.data;
    } catch (error) {
      console.error(`Error al actualizar planta ${plantaId}:`, error);
      throw error;
    }
  }

  /**
   * Elimina (desactiva) una planta
   * 
   * @param {number} plantaId - ID de la planta a eliminar
   * @returns {Promise<void>}
   * @throws {Error} Si hay error en la eliminación
   * 
   * @example
   * ```typescript
   * await dashboardService.eliminarPlanta(123);
   * console.log('Planta eliminada exitosamente');
   * ```
   */
  async eliminarPlanta(plantaId: number): Promise<void> {
    try {
      await axios.delete(`${BASE_PATH}/${plantaId}`);
    } catch (error) {
      console.error(`Error al eliminar planta ${plantaId}:`, error);
      throw error;
    }
  }

  /**
   * Registra un nuevo riego para una planta
   * 
   * @param {number} plantaId - ID de la planta regada
   * @param {RegistrarRiegoRequest} datos - Datos del riego (opcional fecha)
   * @returns {Promise<Planta>} Planta actualizada con nueva fecha de riego
   * @throws {Error} Si hay error al registrar el riego
   * 
   * @example
   * ```typescript
   * // Registrar riego ahora
   * const planta = await dashboardService.registrarRiego(123, {});
   * 
   * // Registrar riego en fecha específica
   * const planta = await dashboardService.registrarRiego(123, {
   *   fecha_riego: '2025-10-15T10:00:00Z'
   * });
   * ```
   */
  async registrarRiego(
    plantaId: number,
    datos: RegistrarRiegoRequest = {}
  ): Promise<Planta> {
    try {
      const response = await axios.post<Planta>(
        `${BASE_PATH}/${plantaId}/riego`,
        datos
      );
      return response.data;
    } catch (error) {
      console.error(`Error al registrar riego para planta ${plantaId}:`, error);
      throw error;
    }
  }

  /**
   * Obtiene plantas que necesitan riego hoy
   * 
   * @returns {Promise<Planta[]>} Lista de plantas que necesitan riego
   * @throws {Error} Si hay error en la petición
   * 
   * @example
   * ```typescript
   * const plantasSedentas = await dashboardService.obtenerPlantasNecesitanRiego();
   * console.log(`${plantasSedentas.length} plantas necesitan riego hoy`);
   * ```
   */
  async obtenerPlantasNecesitanRiego(): Promise<Planta[]> {
    try {
      const response = await axios.get<Planta[]>(`${BASE_PATH}/necesitan-riego`);
      return response.data;
    } catch (error) {
      console.error('Error al obtener plantas que necesitan riego:', error);
      throw error;
    }
  }
}

// Exportar instancia única del servicio (Singleton)
const dashboardService = new DashboardService();
export default dashboardService;

// También exportar la clase para testing
export { DashboardService };
