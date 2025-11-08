/**
 * Servicio de Análisis de Salud de Plantas con Gemini AI
 * 
 * Cliente para consumir los endpoints de verificación de salud del backend.
 * Proporciona métodos para analizar salud de plantas, consultar historial
 * y obtener estadísticas de salud.
 * 
 * @author Equipo Frontend
 * @date Noviembre 2025
 * @sprint Feature - Health Check AI
 * @task T-007, T-008, T-009
 */

import axios from './axios';
import { AxiosError } from 'axios';
import {
  SaludAnalisisResponse,
  HistorialSaludResponse,
  HistorialSaludParams,
  EstadisticasSaludPlanta
} from '@/models/salud';

/**
 * Opciones para la verificación de salud.
 */
export interface VerificarSaludOpciones {
  /** Notas adicionales sobre síntomas observados */
  notas_adicionales?: string;
  /** Callback para reportar progreso del upload (0-100) */
  onProgress?: (progreso: number) => void;
  /** Si se debe usar la imagen principal de la planta cuando no se proporciona imagen */
  incluir_imagen_principal?: boolean;
}

/**
 * Servicio de Análisis de Salud de Plantas.
 */
class SaludService {
  private readonly baseUrl = '/api/plantas';

  /**
   * Verifica la salud de una planta con imagen opcional.
   * 
   * Realiza un análisis completo de la salud de una planta usando Gemini AI.
   * Puede incluir análisis visual si se proporciona una imagen.
   * 
   * **Modos de uso:**
   * 1. **Con imagen nueva**: Proporciona `imagen` para análisis visual completo
   * 2. **Con imagen principal**: No proporciona imagen, `incluir_imagen_principal=true`
   * 3. **Sin imagen**: Solo análisis basado en contexto de la planta
   * 
   * @param plantaId - ID de la planta a analizar
   * @param imagen - Archivo de imagen opcional para análisis visual
   * @param opciones - Opciones adicionales para el análisis
   * @returns Promise con el análisis completo de salud
   * 
   * @throws {Error} Si la planta no existe, no pertenece al usuario, o hay error en la API
   * 
   * @example
   * ```typescript
   * // Análisis con imagen
   * const archivo = input.files[0];
   * const analisis = await saludService.verificarSalud(
   *   42,
   *   archivo,
   *   {
   *     notas_adicionales: 'Hojas amarillentas desde hace una semana',
   *     onProgress: (p) => console.log(`${p}%`)
   *   }
   * );
   * console.log(analisis.estado);
   * console.log(analisis.problemas_detectados);
   * 
   * // Análisis sin imagen (solo contexto)
   * const analisisSinImagen = await saludService.verificarSalud(42);
   * 
   * // Análisis con imagen principal de la planta
   * const analisisImagenPrincipal = await saludService.verificarSalud(
   *   42,
   *   undefined,
   *   { incluir_imagen_principal: true }
   * );
   * ```
   */
  async verificarSalud(
    plantaId: number,
    imagen?: File | Blob,
    opciones: VerificarSaludOpciones = {}
  ): Promise<SaludAnalisisResponse> {
    try {
      const formData = new FormData();

      // Agregar imagen si se proporciona
      if (imagen) {
        formData.append('imagen', imagen);
      }

      // Agregar incluir_imagen_principal
      const incluirImagenPrincipal = opciones.incluir_imagen_principal ?? false;
      formData.append('incluir_imagen_principal', String(incluirImagenPrincipal));

      // Agregar notas adicionales si existen
      if (opciones.notas_adicionales) {
        formData.append('notas_adicionales', opciones.notas_adicionales);
      }

      const response = await axios.post<SaludAnalisisResponse>(
        `${this.baseUrl}/${plantaId}/verificar-salud`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          },
          onUploadProgress: (progressEvent) => {
            if (opciones.onProgress && progressEvent.total) {
              const porcentaje = Math.round((progressEvent.loaded * 100) / progressEvent.total);
              opciones.onProgress(porcentaje);
            }
          }
        }
      );

      return response.data;
    } catch (error) {
      if (error instanceof AxiosError) {
        const mensaje = error.response?.data?.detail || 'Error al verificar la salud de la planta';
        throw new Error(mensaje);
      }
      throw error;
    }
  }

  /**
   * Verifica la salud de una planta sin imagen (solo contexto).
   * 
   * Método de conveniencia para análisis rápido sin imagen.
   * Útil cuando el usuario quiere un diagnóstico preliminar basado
   * solo en la información de la planta.
   * 
   * @param plantaId - ID de la planta a analizar
   * @param notasAdicionales - Notas opcionales sobre síntomas observados
   * @returns Promise con el análisis de salud
   * 
   * @throws {Error} Si la planta no existe o hay error en la API
   * 
   * @example
   * ```typescript
   * const analisis = await saludService.verificarSaludSinImagen(
   *   42,
   *   'La planta tiene hojas caídas desde ayer'
   * );
   * console.log(analisis.resumen);
   * console.log(analisis.recomendaciones);
   * ```
   */
  async verificarSaludSinImagen(
    plantaId: number,
    notasAdicionales?: string
  ): Promise<SaludAnalisisResponse> {
    return this.verificarSalud(plantaId, undefined, {
      notas_adicionales: notasAdicionales,
      incluir_imagen_principal: false
    });
  }

  /**
   * Verifica la salud usando la imagen principal de la planta.
   * 
   * Método de conveniencia para análisis usando la imagen principal
   * que ya está registrada en el sistema.
   * 
   * @param plantaId - ID de la planta a analizar
   * @param notasAdicionales - Notas opcionales sobre síntomas observados
   * @returns Promise con el análisis de salud
   * 
   * @throws {Error} Si la planta no tiene imagen principal o hay error en la API
   * 
   * @example
   * ```typescript
   * const analisis = await saludService.verificarSaludConImagenPrincipal(42);
   * console.log(`Estado: ${analisis.estado}`);
   * console.log(`Confianza: ${analisis.confianza}%`);
   * ```
   */
  async verificarSaludConImagenPrincipal(
    plantaId: number,
    notasAdicionales?: string
  ): Promise<SaludAnalisisResponse> {
    return this.verificarSalud(plantaId, undefined, {
      notas_adicionales: notasAdicionales,
      incluir_imagen_principal: true
    });
  }

  /**
   * Obtiene el historial de análisis de salud de una planta.
   * 
   * Retorna todos los análisis de salud realizados para una planta específica,
   * con soporte para paginación y filtros.
   * 
   * @param plantaId - ID de la planta
   * @param params - Parámetros opcionales de filtrado y paginación
   * @returns Promise con el historial de análisis
   * 
   * @throws {Error} Si la planta no existe, no pertenece al usuario, o hay error en la API
   * 
   * @example
   * ```typescript
   * // Obtener últimos 10 análisis
   * const historial = await saludService.obtenerHistorial(42, {
   *   limite: 10,
   *   offset: 0
   * });
   * console.log(`Total de análisis: ${historial.total}`);
   * historial.analisis.forEach(a => {
   *   console.log(`${a.fecha_analisis}: ${a.estado} (${a.confianza}%)`);
   * });
   * 
   * // Obtener análisis del último mes
   * const fechaDesde = new Date();
   * fechaDesde.setMonth(fechaDesde.getMonth() - 1);
   * const historialMes = await saludService.obtenerHistorial(42, {
   *   desde_fecha: fechaDesde.toISOString()
   * });
   * 
   * // Obtener solo análisis con problemas
   * const conProblemas = await saludService.obtenerHistorial(42, {
   *   solo_con_problemas: true
   * });
   * ```
   */
  async obtenerHistorial(
    plantaId: number,
    params: HistorialSaludParams = {}
  ): Promise<HistorialSaludResponse> {
    try {
      const queryParams = new URLSearchParams();

      // Agregar parámetros de paginación
      if (params.limite !== undefined) {
        queryParams.append('limite', String(params.limite));
      }
      if (params.offset !== undefined) {
        queryParams.append('offset', String(params.offset));
      }

      // Agregar filtros de fecha
      if (params.desde_fecha) {
        queryParams.append('desde_fecha', params.desde_fecha);
      }
      if (params.hasta_fecha) {
        queryParams.append('hasta_fecha', params.hasta_fecha);
      }

      // Agregar filtro de problemas
      if (params.solo_con_problemas !== undefined) {
        queryParams.append('solo_con_problemas', String(params.solo_con_problemas));
      }

      const url = `${this.baseUrl}/${plantaId}/historial-salud${
        queryParams.toString() ? `?${queryParams.toString()}` : ''
      }`;

      const response = await axios.get<HistorialSaludResponse>(url);

      return response.data;
    } catch (error) {
      if (error instanceof AxiosError) {
        const mensaje = error.response?.data?.detail || 'Error al obtener el historial de salud';
        throw new Error(mensaje);
      }
      throw error;
    }
  }

  /**
   * Obtiene el detalle completo de un análisis de salud específico.
   * 
   * Retorna toda la información de un análisis, incluyendo problemas
   * detectados, recomendaciones completas y metadatos.
   * 
   * @param plantaId - ID de la planta
   * @param analisisId - ID del análisis a consultar
   * @returns Promise con el análisis completo
   * 
   * @throws {Error} Si el análisis no existe o no pertenece a la planta del usuario
   * 
   * @example
   * ```typescript
   * const analisis = await saludService.obtenerDetalleAnalisis(42, 123);
   * console.log(analisis.diagnostico_detallado);
   * console.log(analisis.problemas_detectados);
   * analisis.recomendaciones.forEach(r => {
   *   console.log(`${r.prioridad}: ${r.descripcion}`);
   * });
   * ```
   */
  async obtenerDetalleAnalisis(
    plantaId: number,
    analisisId: number
  ): Promise<SaludAnalisisResponse> {
    try {
      const response = await axios.get<SaludAnalisisResponse>(
        `${this.baseUrl}/${plantaId}/historial-salud/${analisisId}`
      );

      return response.data;
    } catch (error) {
      if (error instanceof AxiosError) {
        const mensaje = error.response?.data?.detail || 'Error al obtener el detalle del análisis';
        throw new Error(mensaje);
      }
      throw error;
    }
  }

  /**
   * Obtiene estadísticas agregadas de salud de una planta.
   * 
   * Proporciona métricas sobre la evolución de la salud a lo largo del tiempo,
   * incluyendo tendencias y promedios.
   * 
   * @param plantaId - ID de la planta
   * @returns Promise con las estadísticas de salud
   * 
   * @throws {Error} Si la planta no existe o hay error en la API
   * 
   * @example
   * ```typescript
   * const stats = await saludService.obtenerEstadisticas(42);
   * console.log(`Total de análisis: ${stats.total_analisis}`);
   * console.log(`Último estado: ${stats.ultimo_estado}`);
   * console.log(`Tendencia: ${stats.tendencia_salud}`);
   * console.log(`Confianza promedio: ${stats.confianza_promedio}%`);
   * console.log(`Días desde último análisis: ${stats.dias_desde_ultimo_analisis}`);
   * ```
   */
  async obtenerEstadisticas(
    plantaId: number
  ): Promise<EstadisticasSaludPlanta> {
    try {
      const response = await axios.get<EstadisticasSaludPlanta>(
        `${this.baseUrl}/${plantaId}/estadisticas-salud`
      );

      return response.data;
    } catch (error) {
      if (error instanceof AxiosError) {
        const mensaje = error.response?.data?.detail || 'Error al obtener las estadísticas de salud';
        throw new Error(mensaje);
      }
      throw error;
    }
  }

  /**
   * Obtiene el último análisis de salud de una planta.
   * 
   * Método de conveniencia para obtener el análisis más reciente.
   * 
   * @param plantaId - ID de la planta
   * @returns Promise con el último análisis o null si no hay análisis
   * 
   * @example
   * ```typescript
   * const ultimoAnalisis = await saludService.obtenerUltimoAnalisis(42);
   * if (ultimoAnalisis) {
   *   console.log(`Estado actual: ${ultimoAnalisis.estado}`);
   *   console.log(`Fecha: ${ultimoAnalisis.fecha_analisis}`);
   * }
   * ```
   */
  async obtenerUltimoAnalisis(
    plantaId: number
  ): Promise<SaludAnalisisResponse | null> {
    try {
      const historial = await this.obtenerHistorial(plantaId, {
        limite: 1,
        offset: 0
      });

      if (historial.analisis.length === 0) {
        return null;
      }

      // Obtener el detalle completo del último análisis
      const ultimoItem = historial.analisis[0];
      return await this.obtenerDetalleAnalisis(plantaId, ultimoItem.id);
    } catch (error) {
      if (error instanceof AxiosError) {
        const mensaje = error.response?.data?.detail || 'Error al obtener el último análisis';
        throw new Error(mensaje);
      }
      throw error;
    }
  }

  /**
   * Compara dos análisis de salud de la misma planta.
   * 
   * Útil para mostrar evolución de la salud entre dos puntos en el tiempo.
   * 
   * @param plantaId - ID de la planta
   * @param analisisId1 - ID del primer análisis
   * @param analisisId2 - ID del segundo análisis
   * @returns Promise con ambos análisis
   * 
   * @example
   * ```typescript
   * const [anterior, actual] = await saludService.compararAnalisis(42, 100, 105);
   * console.log(`Estado anterior: ${anterior.estado}`);
   * console.log(`Estado actual: ${actual.estado}`);
   * if (actual.confianza > anterior.confianza) {
   *   console.log('La planta ha mejorado');
   * }
   * ```
   */
  async compararAnalisis(
    plantaId: number,
    analisisId1: number,
    analisisId2: number
  ): Promise<[SaludAnalisisResponse, SaludAnalisisResponse]> {
    try {
      const [analisis1, analisis2] = await Promise.all([
        this.obtenerDetalleAnalisis(plantaId, analisisId1),
        this.obtenerDetalleAnalisis(plantaId, analisisId2)
      ]);

      return [analisis1, analisis2];
    } catch (error) {
      if (error instanceof AxiosError) {
        const mensaje = error.response?.data?.detail || 'Error al comparar análisis';
        throw new Error(mensaje);
      }
      throw error;
    }
  }
}

/**
 * Instancia singleton del servicio de salud.
 */
const saludService = new SaludService();

export default saludService;

/**
 * Exportar también la clase para testing.
 */
export { SaludService };
