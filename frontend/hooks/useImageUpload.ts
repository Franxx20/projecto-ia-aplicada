/**
 * useImageUpload.ts - Custom Hook para gestión de upload de imágenes
 * 
 * Hook reutilizable que maneja:
 * - Selección de archivos
 * - Validación de imágenes
 * - Preview de imágenes
 * - Upload con progreso
 * - Manejo de errores
 * - Captura desde cámara
 * 
 * @author GitHub Copilot
 * @date 2025-10-12
 */

import { useState, useCallback, useRef } from 'react'
import { imageService } from '@/lib/image.service'
import type {
  ImagePreview,
  ImageUploadState,
  ImageValidationConfig,
  ImageValidationError,
  UploadProgress,
  ImageUploadResponse,
} from '@/models/image.types'
import {
  DEFAULT_IMAGE_VALIDATION,
  VALIDATION_MESSAGES,
} from '@/models/image.types'

/**
 * Opciones de configuración para el hook
 */
interface UseImageUploadOptions {
  validationConfig?: Partial<ImageValidationConfig>
  autoUpload?: boolean
  onUploadSuccess?: (response: ImageUploadResponse) => void
  onUploadError?: (error: Error) => void
}

/**
 * Custom Hook para gestión de upload de imágenes
 * 
 * @param options - Opciones de configuración
 * @returns Estado y métodos para gestionar el upload de imágenes
 * 
 * @example
 * ```tsx
 * const {
 *   preview,
 *   uploadStatus,
 *   uploadProgress,
 *   seleccionarArchivo,
 *   subirImagen,
 *   limpiar,
 * } = useImageUpload({
 *   autoUpload: false,
 *   onUploadSuccess: (response) => console.log('Imagen subida:', response)
 * })
 * ```
 */
export function useImageUpload(options: UseImageUploadOptions = {}) {
  const {
    validationConfig = {},
    autoUpload = false,
    onUploadSuccess,
    onUploadError,
  } = options

  // Combinar configuración por defecto con la personalizada
  const config: ImageValidationConfig = {
    ...DEFAULT_IMAGE_VALIDATION,
    ...validationConfig,
  }

  // Estado del hook
  const [state, setState] = useState<ImageUploadState>({
    preview: null,
    uploadStatus: 'idle',
    uploadProgress: { loaded: 0, total: 0, percentage: 0 },
    uploadedImage: null,
    error: null,
    isUploading: false,
  })

  // Ref para el input file (útil para resetear)
  const inputRef = useRef<HTMLInputElement>(null)

  /**
   * Valida el tamaño del archivo
   */
  const validarTamaño = useCallback((file: File): ImageValidationError | null => {
    const maxSizeBytes = config.maxSizeMB * 1024 * 1024
    
    if (file.size > maxSizeBytes) {
      return {
        field: 'size',
        message: VALIDATION_MESSAGES.FILE_TOO_LARGE(config.maxSizeMB),
        details: `Tamaño del archivo: ${imageService.formatearTamaño(file.size)}`,
      }
    }
    
    return null
  }, [config.maxSizeMB])

  /**
   * Valida el tipo de archivo
   */
  const validarTipo = useCallback((file: File): ImageValidationError | null => {
    if (!config.allowedTypes.includes(file.type as any)) {
      return {
        field: 'type',
        message: VALIDATION_MESSAGES.INVALID_TYPE(config.allowedTypes),
        details: `Tipo recibido: ${file.type}`,
      }
    }
    
    return null
  }, [config.allowedTypes])

  /**
   * Valida las dimensiones de la imagen
   */
  const validarDimensiones = useCallback(
    (file: File): Promise<ImageValidationError | null> => {
      return new Promise((resolve) => {
        const img = new Image()
        const url = URL.createObjectURL(file)

        img.onload = () => {
          URL.revokeObjectURL(url)

          // Validar dimensiones mínimas
          if (config.minWidth && img.width < config.minWidth) {
            resolve({
              field: 'dimensions',
              message: VALIDATION_MESSAGES.DIMENSIONS_TOO_SMALL(
                config.minWidth,
                config.minHeight || 0
              ),
              details: `Dimensiones: ${img.width}x${img.height}px`,
            })
            return
          }

          if (config.minHeight && img.height < config.minHeight) {
            resolve({
              field: 'dimensions',
              message: VALIDATION_MESSAGES.DIMENSIONS_TOO_SMALL(
                config.minWidth || 0,
                config.minHeight
              ),
              details: `Dimensiones: ${img.width}x${img.height}px`,
            })
            return
          }

          // Validar dimensiones máximas
          if (config.maxWidth && img.width > config.maxWidth) {
            resolve({
              field: 'dimensions',
              message: VALIDATION_MESSAGES.DIMENSIONS_TOO_LARGE(
                config.maxWidth,
                config.maxHeight || 0
              ),
              details: `Dimensiones: ${img.width}x${img.height}px`,
            })
            return
          }

          if (config.maxHeight && img.height > config.maxHeight) {
            resolve({
              field: 'dimensions',
              message: VALIDATION_MESSAGES.DIMENSIONS_TOO_LARGE(
                config.maxWidth || 0,
                config.maxHeight
              ),
              details: `Dimensiones: ${img.width}x${img.height}px`,
            })
            return
          }

          resolve(null)
        }

        img.onerror = () => {
          URL.revokeObjectURL(url)
          resolve({
            field: 'general',
            message: 'No se pudo cargar la imagen para validar dimensiones',
          })
        }

        img.src = url
      })
    },
    [config.minWidth, config.minHeight, config.maxWidth, config.maxHeight]
  )

  /**
   * Valida un archivo completo
   */
  const validarArchivo = useCallback(
    async (file: File): Promise<ImageValidationError | null> => {
      // Validar tamaño
      const errorTamaño = validarTamaño(file)
      if (errorTamaño) return errorTamaño

      // Validar tipo
      const errorTipo = validarTipo(file)
      if (errorTipo) return errorTipo

      // Validar dimensiones (asíncrono)
      const errorDimensiones = await validarDimensiones(file)
      if (errorDimensiones) return errorDimensiones

      return null
    },
    [validarTamaño, validarTipo, validarDimensiones]
  )

  /**
   * Crea el preview de una imagen
   */
  const crearPreview = useCallback((file: File): ImagePreview => {
    const previewUrl = URL.createObjectURL(file)
    
    return {
      file,
      previewUrl,
      name: file.name,
      size: file.size,
      type: file.type,
      lastModified: file.lastModified,
    }
  }, [])

  /**
   * Selecciona un archivo y crea su preview
   */
  const seleccionarArchivo = useCallback(
    async (file: File) => {
      // Resetear estado anterior
      setState((prev) => ({
        ...prev,
        error: null,
        uploadStatus: 'idle',
        uploadProgress: { loaded: 0, total: 0, percentage: 0 },
      }))

      // Validar archivo
      const error = await validarArchivo(file)
      
      if (error) {
        setState((prev) => ({
          ...prev,
          error,
          preview: null,
        }))
        return
      }

      // Crear preview
      const preview = crearPreview(file)
      
      setState((prev) => ({
        ...prev,
        preview,
        error: null,
      }))

      // Auto-upload si está habilitado
      if (autoUpload) {
        await subirImagen(file)
      }
    },
    [validarArchivo, crearPreview, autoUpload]
  )

  /**
   * Sube la imagen al servidor
   */
  const subirImagen = useCallback(
    async (file?: File) => {
      const archivoASubir = file || state.preview?.file

      if (!archivoASubir) {
        setState((prev) => ({
          ...prev,
          error: {
            field: 'general',
            message: VALIDATION_MESSAGES.NO_FILE_SELECTED,
          },
        }))
        return
      }

      // Actualizar estado: iniciando upload
      setState((prev) => ({
        ...prev,
        uploadStatus: 'uploading',
        isUploading: true,
        error: null,
      }))

      try {
        // Callback para actualizar progreso
        const onProgress = (progress: UploadProgress) => {
          setState((prev) => ({
            ...prev,
            uploadProgress: progress,
          }))
        }

        // Subir imagen
        const response = await imageService.subirImagen(
          archivoASubir,
          onProgress
        )

        // Actualizar estado: upload exitoso
        setState((prev) => ({
          ...prev,
          uploadStatus: 'success',
          isUploading: false,
          uploadedImage: response,
        }))

        // Callback de éxito
        if (onUploadSuccess) {
          onUploadSuccess(response)
        }
      } catch (error) {
        const errorMessage = error instanceof Error 
          ? error.message 
          : VALIDATION_MESSAGES.UPLOAD_FAILED

        // Actualizar estado: error en upload
        setState((prev) => ({
          ...prev,
          uploadStatus: 'error',
          isUploading: false,
          error: {
            field: 'general',
            message: errorMessage,
          },
        }))

        // Callback de error
        if (onUploadError) {
          onUploadError(error instanceof Error ? error : new Error(errorMessage))
        }
      }
    },
    [state.preview, onUploadSuccess, onUploadError]
  )

  /**
   * Limpia el estado y el preview
   */
  const limpiar = useCallback(() => {
    // Liberar URL del preview
    if (state.preview?.previewUrl) {
      URL.revokeObjectURL(state.preview.previewUrl)
    }

    // Resetear input file
    if (inputRef.current) {
      inputRef.current.value = ''
    }

    // Resetear estado
    setState({
      preview: null,
      uploadStatus: 'idle',
      uploadProgress: { loaded: 0, total: 0, percentage: 0 },
      uploadedImage: null,
      error: null,
      isUploading: false,
    })
  }, [state.preview])

  /**
   * Elimina la imagen subida
   */
  const eliminarImagen = useCallback(
    async (imagenId: string) => {
      try {
        await imageService.eliminarImagen(imagenId)
        limpiar()
      } catch (error) {
        setState((prev) => ({
          ...prev,
          error: {
            field: 'general',
            message: error instanceof Error ? error.message : 'Error al eliminar imagen',
          },
        }))
      }
    },
    [limpiar]
  )

  return {
    // Estado
    preview: state.preview,
    uploadStatus: state.uploadStatus,
    uploadProgress: state.uploadProgress,
    uploadedImage: state.uploadedImage,
    error: state.error,
    isUploading: state.isUploading,
    
    // Métodos
    seleccionarArchivo,
    subirImagen,
    limpiar,
    eliminarImagen,
    
    // Ref
    inputRef,
  }
}
