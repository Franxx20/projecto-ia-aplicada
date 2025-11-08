/**
 * Servicio de PlantNet para identificación de plantas
 * 
 * Cliente para consumir la API de identificación de plantas del backend.
 * Proporciona métodos para identificar plantas, consultar historial y cuotas.
 * 
 * @author Equipo Frontend
 * @date Octubre 2025
 * @sprint Sprint 1-2
 * @task T-017
 */

import axios from './axios';
import { AxiosError } from 'axios';
import {
  IdentificarRequest,
  IdentificarResponse,
  IdentificarResponseSimple,
  HistorialResponse,
  HistorialIdentificacion,
  PlantNetQuota,
  OrganType,
  AgregarPlantaRequest,
  PlantaResponse,
  PlantaUsuario
} from '@/models/plant.types';

/**
 * Servicio de PlantNet para identificación de plantas
 */
class PlantService {
  private readonly baseUrl = '/api/identificar';

  /**
   * Identifica una planta desde una imagen ya subida al sistema
   * 
   * @param imagenId - ID de la imagen en el sistema
   * @param organos - Lista de órganos de la planta (opcional, default: ['auto'])
   * @param guardarResultado - Si se debe guardar el resultado en BD (default: true)
   * @returns Promise con el resultado de la identificación
   * 
   * @throws {Error} Si la imagen no existe o la API falla
   * 
   * @example
   * ```typescript
   * const resultado = await plantService.identificarDesdeImagen(123, ['leaf']);
   * console.log(resultado.mejor_resultado.nombre_cientifico);
   * console.log(resultado.confianza_porcentaje);
   * ```
   */
  async identificarDesdeImagen(
    imagenId: number,
    organos: OrganType[] = ['auto'],
    guardarResultado: boolean = true
  ): Promise<IdentificarResponseSimple> {
    try {
      const request: IdentificarRequest = {
        imagen_id: imagenId,
        organos,
        guardar_resultado: guardarResultado
      };

      const response = await axios.post<IdentificarResponseSimple>(
        `${this.baseUrl}/desde-imagen`,
        request
      );

      return response.data;
    } catch (error) {
      if (error instanceof AxiosError) {
        const mensaje = error.response?.data?.detail || 'Error al identificar la planta';
        throw new Error(mensaje);
      }
      throw error;
    }
  }

  /**
   * Identifica una planta desde múltiples imágenes (T-022, T-023)
   * 
   * Permite enviar de 1 a 5 imágenes con especificación del órgano (parte de la planta)
   * para cada imagen.
   * 
   * @param archivos - Array de 1 a 5 archivos de imagen
   * @param organos - Array de órganos correspondiente a cada imagen
   * @param guardarResultado - Si se debe guardar el resultado en BD (default: true)
   * @param onProgress - Callback opcional para reportar progreso del upload
   * @returns Promise con el resultado de la identificación incluyendo todas las imágenes
   * 
   * @throws {Error} Si el número de imágenes no está entre 1-5 o si hay error en la API
   * 
   * @example
   * ```typescript
   * const archivos = [archivo1, archivo2, archivo3];
   * const organos = ['flower', 'leaf', 'fruit'];
   * const resultado = await plantService.identificarDesdeMultiplesImagenes(
   *   archivos,
   *   organos,
   *   true,
   *   (progreso) => console.log(`${progreso}%`)
   * );
   * console.log(`Imágenes procesadas: ${resultado.cantidad_imagenes}`);
   * console.log(`Confianza: ${resultado.confianza}%`);
   * ```
   */
  async identificarDesdeMultiplesImagenes(
    archivos: File[],
    organos: OrganType[],
    guardarResultado: boolean = true,
    onProgress?: (progreso: number) => void
  ): Promise<IdentificarResponse> {
    try {
      // Validar número de archivos
      if (archivos.length < 1 || archivos.length > 5) {
        throw new Error('Debe proporcionar entre 1 y 5 imágenes');
      }

      // Validar que haya un órgano por cada archivo
      if (organos.length !== archivos.length) {
        throw new Error('Debe proporcionar un órgano por cada imagen');
      }

      const formData = new FormData();
      
      // Agregar cada archivo
      archivos.forEach((archivo) => {
        formData.append('archivos', archivo);
      });

      // Agregar órganos separados por coma
      formData.append('organos', organos.join(','));
      formData.append('guardar_resultado', String(guardarResultado));

      const response = await axios.post<IdentificarResponse>(
        `${this.baseUrl}/multiple`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          },
          onUploadProgress: (progressEvent) => {
            if (onProgress && progressEvent.total) {
              const porcentaje = Math.round((progressEvent.loaded * 100) / progressEvent.total);
              onProgress(porcentaje);
            }
          }
        }
      );

      return response.data;
    } catch (error) {
      if (error instanceof AxiosError) {
        const mensaje = error.response?.data?.detail || 'Error al procesar las imágenes';
        throw new Error(mensaje);
      }
      throw error;
    }
  }

  /**
   * Identifica una planta subiendo un archivo directamente
   * 
   * Sube una imagen y la identifica en un solo paso.
   * 
   * @param archivo - Archivo de imagen a subir
   * @param organos - Lista de órganos de la planta
   * @param guardarImagen - Si se debe guardar la imagen en el sistema
   * @param onProgress - Callback para reportar progreso del upload
   * @returns Promise con el resultado de la identificación
   * 
   * @example
   * ```typescript
   * const archivo = input.files[0];
   * const resultado = await plantService.identificarDesdeArchivo(
   *   archivo,
   *   ['flower'],
   *   true,
   *   (progreso) => console.log(`${progreso}%`)
   * );
   * ```
   */
  async identificarDesdeArchivo(
    archivo: File,
    organos: OrganType[] = ['auto'],
    guardarImagen: boolean = true,
    onProgress?: (progreso: number) => void
  ): Promise<IdentificarResponseSimple & { imagen?: { id: number; url: string; nombre: string } }> {
    try {
      const formData = new FormData();
      formData.append('archivo', archivo);
      formData.append('organos', organos.join(','));
      formData.append('guardar_imagen', String(guardarImagen));

      const response = await axios.post(
        `${this.baseUrl}/desde-archivo`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          },
          onUploadProgress: (progressEvent) => {
            if (onProgress && progressEvent.total) {
              const porcentaje = Math.round((progressEvent.loaded * 100) / progressEvent.total);
              onProgress(porcentaje);
            }
          }
        }
      );

      return response.data;
    } catch (error) {
      if (error instanceof AxiosError) {
        const mensaje = error.response?.data?.detail || 'Error al procesar la imagen';
        throw new Error(mensaje);
      }
      throw error;
    }
  }

  /**
   * Obtiene el historial de identificaciones del usuario
   * 
   * @param limite - Número máximo de resultados (default: 50)
   * @param offset - Desplazamiento para paginación (default: 0)
   * @param soloValidadas - Si solo se deben retornar identificaciones validadas
   * @returns Promise con el historial de identificaciones
   * 
   * @example
   * ```typescript
   * const historial = await plantService.obtenerHistorial(10, 0, false);
   * console.log(`Total: ${historial.total}`);
   * historial.identificaciones.forEach(id => {
   *   console.log(id.nombre_cientifico, id.confianza);
   * });
   * ```
   */
  async obtenerHistorial(
    limite: number = 50,
    offset: number = 0,
    soloValidadas: boolean = false
  ): Promise<HistorialResponse> {
    try {
      const params = new URLSearchParams({
        limite: String(limite),
        offset: String(offset),
        solo_validadas: String(soloValidadas)
      });

      const response = await axios.get<HistorialResponse>(
        `${this.baseUrl}/historial?${params.toString()}`
      );

      return response.data;
    } catch (error) {
      if (error instanceof AxiosError) {
        const mensaje = error.response?.data?.detail || 'Error al obtener el historial';
        throw new Error(mensaje);
      }
      throw error;
    }
  }

  /**
   * Obtiene el detalle de una identificación específica
   * 
   * @param identificacionId - ID de la identificación
   * @returns Promise con el detalle completo de la identificación
   * 
   * @example
   * ```typescript
   * const detalle = await plantService.obtenerDetalleIdentificacion(42);
   * console.log(detalle.plantnet_response.results);
   * ```
   */
  async obtenerDetalleIdentificacion(
    identificacionId: number
  ): Promise<HistorialIdentificacion> {
    try {
      const response = await axios.get<HistorialIdentificacion>(
        `${this.baseUrl}/historial/${identificacionId}`
      );

      return response.data;
    } catch (error) {
      if (error instanceof AxiosError) {
        const mensaje = error.response?.data?.detail || 'Error al obtener la identificación';
        throw new Error(mensaje);
      }
      throw error;
    }
  }

  /**
   * Valida una identificación realizada por IA
   * 
   * Marca una identificación como validada por el usuario y
   * opcionalmente agrega notas.
   * 
   * @param identificacionId - ID de la identificación a validar
   * @param notas - Notas opcionales sobre la validación
   * @returns Promise con la identificación actualizada
   * 
   * @example
   * ```typescript
   * await plantService.validarIdentificacion(
   *   42,
   *   'Confirmado en mi jardín'
   * );
   * ```
   */
  async validarIdentificacion(
    identificacionId: number,
    notas?: string
  ): Promise<HistorialIdentificacion> {
    try {
      const response = await axios.post<HistorialIdentificacion>(
        `${this.baseUrl}/validar/${identificacionId}`,
        { notas }
      );

      return response.data;
    } catch (error) {
      if (error instanceof AxiosError) {
        const mensaje = error.response?.data?.detail || 'Error al validar la identificación';
        throw new Error(mensaje);
      }
      throw error;
    }
  }

  /**
   * Obtiene información sobre la cuota de requests de PlantNet
   * 
   * Retorna cuántos requests se han hecho hoy, el límite diario
   * y cuántos quedan disponibles.
   * 
   * @returns Promise con información de la cuota
   * 
   * @example
   * ```typescript
   * const quota = await plantService.obtenerQuota();
   * console.log(`Restantes: ${quota.restantes}/${quota.limite_diario}`);
   * console.log(`Usado: ${quota.porcentaje_usado}%`);
   * ```
   */
  async obtenerQuota(): Promise<PlantNetQuota> {
    try {
      const response = await axios.get<PlantNetQuota>(
        `${this.baseUrl}/quota`
      );

      return response.data;
    } catch (error) {
      if (error instanceof AxiosError) {
        const mensaje = error.response?.data?.detail || 'Error al obtener información de cuota';
        throw new Error(mensaje);
      }
      throw error;
    }
  }

  /**
   * Agrega una planta al jardín del usuario desde una identificación (T-023)
   * 
   * Permite al usuario confirmar una identificación y añadir la planta a su jardín
   * con un nombre personalizado, notas y ubicación opcionales.
   * 
   * @param request - Datos para crear la planta desde identificación
   * @returns Promise con la planta creada
   * 
   * @throws {Error} Si la identificación no existe o no pertenece al usuario
   * 
   * @example
   * ```typescript
   * const planta = await plantService.agregarPlantaAlJardin({
   *   identificacion_id: 42,
   *   nombre_personalizado: 'Mi Potus del Balcón',
   *   notas: 'Identificada el 2025-01-15',
   *   ubicacion: 'Balcón - luz indirecta'
   * });
   * console.log(`Planta agregada: ${planta.id}`);
   * ```
   */
  async agregarPlantaAlJardin(
    request: AgregarPlantaRequest
  ): Promise<PlantaResponse> {
    try {
      const response = await axios.post<PlantaResponse>(
        '/api/plantas/agregar-desde-identificacion',
        request
      );

      return response.data;
    } catch (error) {
      if (error instanceof AxiosError) {
        const mensaje = error.response?.data?.detail || 'Error al agregar la planta';
        throw new Error(mensaje);
      }
      throw error;
    }
  }

  /**
   * Obtiene todas las plantas del usuario autenticado (T-023)
   * 
   * Retorna la lista de plantas que el usuario tiene en su jardín,
   * incluyendo información de la especie e imagen principal.
   * 
   * @returns Promise con el array de plantas del usuario
   * 
   * @example
   * ```typescript
   * const plantas = await plantService.obtenerMisPlantas();
   * plantas.forEach(planta => {
   *   console.log(planta.nombre_personalizado);
   *   console.log(planta.especie?.nombre_comun);
   * });
   * ```
   */
  async obtenerMisPlantas(): Promise<PlantaUsuario[]> {
    try {
      // Usar el nuevo endpoint que incluye imágenes de identificación
      const response = await axios.get<PlantaUsuario[]>('/api/plantas/con-imagenes');
      return response.data;
    } catch (error) {
      if (error instanceof AxiosError) {
        const mensaje = error.response?.data?.detail || 'Error al obtener las plantas';
        throw new Error(mensaje);
      }
      throw error;
    }
  }

  /**
   * Actualiza una planta del usuario
   * 
   * Permite actualizar cualquier campo de una planta existente,
   * incluyendo es_favorita y es_regalo.
   * 
   * @param plantaId - ID de la planta a actualizar
   * @param datos - Campos a actualizar (parcial)
   * @returns Promise con la planta actualizada
   * 
   * @example
   * ```typescript
   * await plantService.actualizarPlanta(42, {
   *   es_favorita: true,
   *   nombre_personalizado: 'Mi Planta Favorita'
   * });
   * ```
   */
  async actualizarPlanta(
    plantaId: number,
    datos: Partial<{
      nombre_personalizado?: string;
      ubicacion?: string;
      notas?: string;
      estado_salud?: string;
      frecuencia_riego_dias?: number;
      es_favorita?: boolean;
      fue_regada_hoy?: boolean;
    }>
  ): Promise<PlantaResponse> {
    try {
      const response = await axios.put<PlantaResponse>(
        `/api/plantas/${plantaId}`,
        datos
      );
      return response.data;
    } catch (error) {
      if (error instanceof AxiosError) {
        const mensaje = error.response?.data?.detail || 'Error al actualizar la planta';
        throw new Error(mensaje);
      }
      throw error;
    }
  }
}

/**
 * Instancia singleton del servicio de PlantNet
 */
const plantService = new PlantService();

export default plantService;

/**
 * Exportar también la clase para testing
 */
export { PlantService };
