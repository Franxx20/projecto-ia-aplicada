/**
 * ImageUpload.tsx - Componente de subida de imágenes
 * 
 * Componente completo que incluye:
 * - Drag and drop de archivos
 * - Selección de archivos con click
 * - Captura desde cámara (móvil/desktop)
 * - Preview de imagen antes de subir
 * - Barra de progreso de upload
 * - Validación de formato y tamaño
 * - Mensajes de error personalizados
 * 
 * @author GitHub Copilot
 * @date 2025-10-12
 */

'use client'

import React, { useCallback, useState, DragEvent } from 'react'
import { Camera, Upload, X, Loader2, CheckCircle2, AlertCircle, Image as ImageIcon } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { useImageUpload } from '@/hooks/useImageUpload'
import type { ImageUploadResponse, ImageValidationConfig } from '@/models/image.types'
import { cn } from '@/lib/utils'

/**
 * Props del componente ImageUpload
 */
interface ImageUploadProps {
  /** Callback cuando se sube exitosamente una imagen */
  onUploadSuccess?: (response: ImageUploadResponse) => void
  
  /** Callback cuando ocurre un error */
  onUploadError?: (error: Error) => void
  
  /** Si se debe subir automáticamente al seleccionar */
  autoUpload?: boolean
  
  /** Configuración de validación personalizada */
  validationConfig?: Partial<ImageValidationConfig>
  
  /** Clase CSS adicional para el contenedor */
  className?: string
  
  /** Mostrar botón de captura de cámara */
  showCameraCapture?: boolean
  
  /** Texto personalizado para el área de drop */
  dropText?: string
  
  /** Mostrar tips de uso */
  showTips?: boolean
}

/**
 * Componente de subida de imágenes con drag-and-drop
 * 
 * @example
 * ```tsx
 * <ImageUpload
 *   autoUpload={false}
 *   onUploadSuccess={(response) => {
 *     console.log('Imagen subida:', response)
 *   }}
 *   showCameraCapture={true}
 * />
 * ```
 */
export function ImageUpload({
  onUploadSuccess,
  onUploadError,
  autoUpload = false,
  validationConfig,
  className,
  showCameraCapture = true,
  dropText = 'Arrastra tu imagen aquí, o haz click para seleccionar',
  showTips = true,
}: ImageUploadProps) {
  // Estado del drag and drop
  const [isDragging, setIsDragging] = useState(false)

  // Hook de upload de imágenes
  const {
    preview,
    uploadStatus,
    uploadProgress,
    error,
    isUploading,
    seleccionarArchivo,
    subirImagen,
    limpiar,
    inputRef,
  } = useImageUpload({
    autoUpload,
    validationConfig,
    onUploadSuccess,
    onUploadError,
  })

  /**
   * Maneja el evento de cambio del input file
   */
  const handleFileChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0]
      if (file) {
        seleccionarArchivo(file)
      }
    },
    [seleccionarArchivo]
  )

  /**
   * Maneja el evento de drop
   */
  const handleDrop = useCallback(
    (e: DragEvent<HTMLDivElement>) => {
      e.preventDefault()
      setIsDragging(false)

      const file = e.dataTransfer.files?.[0]
      if (file) {
        seleccionarArchivo(file)
      }
    },
    [seleccionarArchivo]
  )

  /**
   * Maneja el evento de drag over
   */
  const handleDragOver = useCallback((e: DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  /**
   * Maneja el evento de drag leave
   */
  const handleDragLeave = useCallback((e: DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    setIsDragging(false)
  }, [])

  /**
   * Renderiza el área de upload cuando no hay preview
   */
  const renderUploadArea = () => (
    <div
      className={cn(
        'border-2 border-dashed rounded-lg p-8 text-center transition-colors duration-200',
        isDragging
          ? 'border-primary bg-primary/5'
          : 'border-border hover:border-primary/50 hover:bg-accent/5',
        className
      )}
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
    >
      <div className="space-y-4">
        {/* Icono */}
        <div className="flex justify-center">
          <div className="bg-primary/10 p-4 rounded-full">
            <ImageIcon className="w-10 h-10 text-primary" />
          </div>
        </div>

        {/* Texto */}
        <div>
          <p className="text-base font-medium mb-1">{dropText}</p>
          <p className="text-sm text-muted-foreground">
            Soporta: JPG, PNG, WEBP, HEIC (máx. {validationConfig?.maxSizeMB || 10}MB)
          </p>
        </div>

        {/* Botones */}
        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          <Button asChild variant="default">
            <label className="cursor-pointer">
              <Upload className="w-4 h-4 mr-2" />
              Seleccionar Archivo
              <input
                ref={inputRef}
                type="file"
                accept="image/*"
                className="hidden"
                onChange={handleFileChange}
              />
            </label>
          </Button>

          {showCameraCapture && (
            <Button asChild variant="outline">
              <label className="cursor-pointer">
                <Camera className="w-4 h-4 mr-2" />
                Tomar Foto
                <input
                  type="file"
                  accept="image/*"
                  capture="environment"
                  className="hidden"
                  onChange={handleFileChange}
                />
              </label>
            </Button>
          )}
        </div>
      </div>
    </div>
  )

  /**
   * Renderiza el preview de la imagen seleccionada
   */
  const renderPreview = () => {
    if (!preview) return null

    return (
      <Card>
        <CardContent className="p-4 space-y-4">
          {/* Imagen Preview */}
          <div className="relative">
            <img
              src={preview.previewUrl}
              alt={preview.name}
              className="w-full h-auto max-h-96 object-contain rounded-lg"
            />
            
            {/* Botón de eliminar */}
            {!isUploading && (
              <Button
                variant="destructive"
                size="icon"
                className="absolute top-2 right-2"
                onClick={limpiar}
              >
                <X className="w-4 h-4" />
              </Button>
            )}

            {/* Overlay de éxito */}
            {uploadStatus === 'success' && (
              <div className="absolute inset-0 bg-black/50 rounded-lg flex items-center justify-center">
                <div className="text-center text-white">
                  <CheckCircle2 className="w-16 h-16 mx-auto mb-2" />
                  <p className="text-lg font-semibold">¡Imagen subida con éxito!</p>
                </div>
              </div>
            )}
          </div>

          {/* Información del archivo */}
          <div className="space-y-2">
            <div className="flex justify-between items-center text-sm">
              <span className="font-medium truncate flex-1">{preview.name}</span>
              <span className="text-muted-foreground ml-2">
                {(preview.size / (1024 * 1024)).toFixed(2)} MB
              </span>
            </div>

            {/* Barra de progreso */}
            {isUploading && (
              <div className="space-y-1">
                <Progress value={uploadProgress.percentage} className="h-2" />
                <p className="text-xs text-center text-muted-foreground">
                  Subiendo... {uploadProgress.percentage}%
                </p>
              </div>
            )}
          </div>

          {/* Botón de subir (si no es auto-upload) */}
          {!autoUpload && uploadStatus === 'idle' && (
            <Button
              className="w-full"
              onClick={() => subirImagen()}
              disabled={isUploading}
            >
              {isUploading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Subiendo...
                </>
              ) : (
                <>
                  <Upload className="w-4 h-4 mr-2" />
                  Subir Imagen
                </>
              )}
            </Button>
          )}

          {/* Botón de nueva imagen después de éxito */}
          {uploadStatus === 'success' && (
            <Button variant="outline" className="w-full" onClick={limpiar}>
              Subir Otra Imagen
            </Button>
          )}
        </CardContent>
      </Card>
    )
  }

  /**
   * Renderiza mensajes de error
   */
  const renderError = () => {
    if (!error) return null

    return (
      <div className="bg-destructive/10 border border-destructive/30 rounded-lg p-4 flex items-start gap-3">
        <AlertCircle className="w-5 h-5 text-destructive flex-shrink-0 mt-0.5" />
        <div className="flex-1">
          <p className="font-medium text-destructive">{error.message}</p>
          {error.details && (
            <p className="text-sm text-muted-foreground mt-1">{error.details}</p>
          )}
        </div>
      </div>
    )
  }

  /**
   * Renderiza tips de uso
   */
  const renderTips = () => {
    if (!showTips) return null

    return (
      <div className="bg-muted/50 rounded-lg p-4 space-y-2">
        <h4 className="font-semibold text-sm">💡 Tips para mejores resultados:</h4>
        <ul className="space-y-1 text-sm text-muted-foreground">
          <li className="flex gap-2">
            <span className="text-primary">•</span>
            <span>Toma fotos con buena iluminación natural</span>
          </li>
          <li className="flex gap-2">
            <span className="text-primary">•</span>
            <span>Captura la planta completa o características distintivas</span>
          </li>
          <li className="flex gap-2">
            <span className="text-primary">•</span>
            <span>Evita imágenes borrosas o muy oscuras</span>
          </li>
          <li className="flex gap-2">
            <span className="text-primary">•</span>
            <span>Incluye detalles como hojas, flores o frutos</span>
          </li>
        </ul>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Área de upload o preview */}
      {preview ? renderPreview() : renderUploadArea()}

      {/* Mensajes de error */}
      {renderError()}

      {/* Tips */}
      {!preview && renderTips()}
    </div>
  )
}

export default ImageUpload
