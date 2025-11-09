/**
 * image.service.ts - Servicio para gestión de imágenes
 * 
 * Proporciona métodos para:
 * - Subir imágenes al backend
 * - Obtener imágenes existentes
 * - Eliminar imágenes
 * - Tracking de progreso de upload
 * 
 * @author GitHub Copilot
 * @date 2025-10-12
 */

import axiosInstance from './axios'
import type {
  ImageUploadResponse,
  ImageGetResponse,
  ImageDeleteResponse,
  UploadProgress,
} from '../models/image.types'

/**
 * Servicio para gestión de imágenes
 * 
 * Maneja todas las operaciones relacionadas con imágenes:
 * - Upload con seguimiento de progreso
 * - Obtención de imágenes por ID
 * - Eliminación de imágenes
 * - Soporte para multipart/form-data
 */
class ImageService {
  private readonly BASE_PATH = '/api/imagenes'

  /**
   * Sube una imagen al servidor
   * 
   * @param file - Archivo de imagen a subir
   * @param onProgress - Callback para reportar progreso (opcional)
   * @param metadata - Metadatos adicionales (opcional)
   * @returns Promise con la respuesta del servidor
   * @throws Error si el upload falla
   */
  async subirImagen(
    file: File,
    onProgress?: (progress: UploadProgress) => void,
    metadata?: Record<string, unknown>
  ): Promise<ImageUploadResponse> {
    try {
      // Crear FormData para enviar el archivo
      const formData = new FormData()
      formData.append('archivo', file) // Backend espera 'archivo'
      
      // Agregar metadata si existe (como descripción)
      if (metadata && metadata.descripcion) {
        formData.append('descripcion', String(metadata.descripcion))
      }

      // Realizar la petición con tracking de progreso
      const response = await axiosInstance.post<ImageUploadResponse>(
        `${this.BASE_PATH}/subir`, // Endpoint correcto del backend
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
          onUploadProgress: (progressEvent) => {
            if (onProgress && progressEvent.total) {
              const loaded = progressEvent.loaded
              const total = progressEvent.total
              const percentage = Math.round((loaded * 100) / total)
              
              onProgress({
                loaded,
                total,
                percentage,
              })
            }
          },
        }
      )

      return response.data
    } catch (error) {
      console.error('Error al subir imagen:', error)
      throw this.manejarError(error)
    }
  }

  /**
   * Obtiene una imagen por su ID
   * 
   * @param imagenId - ID de la imagen a obtener
   * @returns Promise con la información de la imagen
   * @throws Error si la imagen no existe o no se puede obtener
   */
  async obtenerImagen(imagenId: string): Promise<ImageGetResponse> {
    try {
      const response = await axiosInstance.get<ImageGetResponse>(
        `${this.BASE_PATH}/${imagenId}`
      )
      return response.data
    } catch (error) {
      console.error('Error al obtener imagen:', error)
      throw this.manejarError(error)
    }
  }

  /**
   * Elimina una imagen por su ID
   * 
   * @param imagenId - ID de la imagen a eliminar
   * @returns Promise con la respuesta de eliminación
   * @throws Error si la imagen no se puede eliminar
   */
  async eliminarImagen(imagenId: string): Promise<ImageDeleteResponse> {
    try {
      const response = await axiosInstance.delete<ImageDeleteResponse>(
        `${this.BASE_PATH}/${imagenId}`
      )
      return response.data
    } catch (error) {
      console.error('Error al eliminar imagen:', error)
      throw this.manejarError(error)
    }
  }

  /**
   * Obtiene todas las imágenes asociadas a una planta específica
   * 
   * @param plantaId - ID de la planta
   * @returns Promise con la lista de imágenes de la planta
   * @throws Error si no se pueden obtener las imágenes
   */
  async obtenerImagenesPlanta(plantaId: number): Promise<{
    id: number
    nombre_archivo: string
    url_blob: string
    organ?: string
    tamano_bytes: number
  }[]> {
    try {
      const response = await axiosInstance.get<{
        imagenes: Array<{
          id: number
          usuario_id: number
          nombre_archivo: string
          nombre_blob: string
          url_blob: string
          container_name: string
          content_type: string
          tamano_bytes: number
          descripcion?: string
          organ?: string
          created_at: string
          updated_at: string
          is_deleted: boolean
        }>
        total: number
      }>(`${this.BASE_PATH}/planta/${plantaId}`)
      
      // Mapear al formato esperado
      return response.data.imagenes.map(img => ({
        id: img.id,
        nombre_archivo: img.nombre_archivo,
        url_blob: img.url_blob,
        organ: img.organ,
        tamano_bytes: img.tamano_bytes
      }))
    } catch (error) {
      console.error('Error al obtener imágenes de la planta:', error)
      // No lanzar error, devolver array vacío si falla
      return []
    }
  }

  /**
   * Obtiene la URL completa de una imagen
   * 
   * @param rutaRelativa - Ruta relativa de la imagen
   * @returns URL completa de la imagen
   */
  obtenerUrlCompleta(rutaRelativa: string): string {
    const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
    return `${baseUrl}${rutaRelativa}`
  }

  /**
   * Valida que un archivo sea una imagen válida
   * 
   * @param file - Archivo a validar
   * @returns true si el archivo es una imagen válida
   */
  esImagenValida(file: File): boolean {
    const tiposPermitidos = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp', 'image/heic']
    return tiposPermitidos.includes(file.type)
  }

  /**
   * Convierte bytes a formato legible (KB, MB)
   * 
   * @param bytes - Cantidad de bytes
   * @returns String con formato legible (ej: "2.5 MB")
   */
  formatearTamaño(bytes: number): string {
    if (bytes === 0) return '0 Bytes'
    
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`
  }

  /**
   * Maneja errores de la API y devuelve un mensaje apropiado
   * 
   * @param error - Error capturado
   * @returns Error con mensaje descriptivo
   */
  private manejarError(error: unknown): Error {
    if (typeof error === 'object' && error !== null && 'response' in error) {
      const axiosError = error as { response?: { data?: { detail?: string; message?: string } } }
      const mensaje = axiosError.response?.data?.detail || 
                      axiosError.response?.data?.message || 
                      'Error desconocido al procesar la imagen'
      return new Error(mensaje)
    }
    
    return new Error('Error de conexión con el servidor')
  }
}

/**
 * Instancia única del servicio de imágenes
 */
export const imageService = new ImageService()
