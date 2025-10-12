/**
 * image.types.ts - Tipos TypeScript para manejo de imágenes
 * 
 * Define interfaces para:
 * - Upload de imágenes
 * - Preview de imágenes
 * - Validación de archivos
 * - Progreso de upload
 * - Respuestas del servidor
 * 
 * @author GitHub Copilot
 * @date 2025-10-12
 */

/**
 * Tipos de archivo de imagen permitidos
 */
export type ImageFileType = 'image/jpeg' | 'image/jpg' | 'image/png' | 'image/webp' | 'image/heic'

/**
 * Estado del upload de imagen
 */
export type UploadStatus = 'idle' | 'uploading' | 'success' | 'error'

/**
 * Interfaz para el preview de una imagen
 */
export interface ImagePreview {
  file: File
  previewUrl: string
  name: string
  size: number
  type: string
  lastModified: number
}

/**
 * Interfaz para configuración de validación de imágenes
 */
export interface ImageValidationConfig {
  maxSizeMB: number // Tamaño máximo en MB
  allowedTypes: ImageFileType[] // Tipos de archivo permitidos
  minWidth?: number // Ancho mínimo en píxeles (opcional)
  minHeight?: number // Alto mínimo en píxeles (opcional)
  maxWidth?: number // Ancho máximo en píxeles (opcional)
  maxHeight?: number // Alto máximo en píxeles (opcional)
}

/**
 * Interfaz para errores de validación
 */
export interface ImageValidationError {
  field: 'size' | 'type' | 'dimensions' | 'general'
  message: string
  details?: string
}

/**
 * Interfaz para el progreso de upload
 */
export interface UploadProgress {
  loaded: number // Bytes cargados
  total: number // Bytes totales
  percentage: number // Porcentaje (0-100)
}

/**
 * Interfaz para la respuesta de subida de imagen del backend
 */
export interface ImageUploadResponse {
  id: string
  usuario_id: number
  nombre_archivo: string
  ruta_archivo: string
  url: string
  thumbnail_url?: string
  tamaño_bytes: number
  tipo_mime: string
  ancho?: number
  alto?: number
  fecha_subida: string
  metadatos?: Record<string, unknown>
}

/**
 * Interfaz para la petición de subida de imagen
 */
export interface ImageUploadRequest {
  file: File
  metadata?: Record<string, unknown>
  generateThumbnail?: boolean
}

/**
 * Interfaz para la respuesta de eliminación de imagen
 */
export interface ImageDeleteResponse {
  success: boolean
  message: string
  deleted_image_id: string
}

/**
 * Interfaz para obtener una imagen
 */
export interface ImageGetResponse {
  id: string
  usuario_id: number
  nombre_archivo: string
  ruta_archivo: string
  url: string
  thumbnail_url?: string
  tamaño_bytes: number
  tipo_mime: string
  ancho?: number
  alto?: number
  fecha_subida: string
  metadatos?: Record<string, unknown>
}

/**
 * Interfaz para el estado del hook useImageUpload
 */
export interface ImageUploadState {
  preview: ImagePreview | null
  uploadStatus: UploadStatus
  uploadProgress: UploadProgress
  uploadedImage: ImageUploadResponse | null
  error: ImageValidationError | null
  isUploading: boolean
}

/**
 * Configuración por defecto para validación de imágenes
 */
export const DEFAULT_IMAGE_VALIDATION: ImageValidationConfig = {
  maxSizeMB: 10,
  allowedTypes: ['image/jpeg', 'image/jpg', 'image/png', 'image/webp', 'image/heic'],
  minWidth: 100,
  minHeight: 100,
  maxWidth: 8000,
  maxHeight: 8000,
}

/**
 * Mensajes de error de validación
 */
export const VALIDATION_MESSAGES = {
  FILE_TOO_LARGE: (maxSize: number) => `El archivo es demasiado grande. Tamaño máximo: ${maxSize}MB`,
  INVALID_TYPE: (allowedTypes: string[]) => `Tipo de archivo no permitido. Tipos permitidos: ${allowedTypes.join(', ')}`,
  DIMENSIONS_TOO_SMALL: (minWidth: number, minHeight: number) => 
    `La imagen es demasiado pequeña. Mínimo: ${minWidth}x${minHeight}px`,
  DIMENSIONS_TOO_LARGE: (maxWidth: number, maxHeight: number) => 
    `La imagen es demasiado grande. Máximo: ${maxWidth}x${maxHeight}px`,
  UPLOAD_FAILED: 'Error al subir la imagen. Por favor, intenta de nuevo.',
  NO_FILE_SELECTED: 'No se ha seleccionado ningún archivo',
  CAMERA_NOT_AVAILABLE: 'La cámara no está disponible en este dispositivo',
}
