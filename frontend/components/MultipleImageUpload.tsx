/**
 * MultipleImageUpload.tsx - Componente de subida de múltiples imágenes con selección de órgano
 * 
 * Permite subir de 1 a 5 imágenes de plantas con especificación del tipo de órgano
 * para cada una (hoja, flor, fruto, corteza, etc.)
 * 
 * Implementación de T-024
 * 
 * @author GitHub Copilot
 * @date 2025-10-20
 */

'use client'

import React, { useState, useRef, useCallback } from 'react'
import { Camera, Upload, X } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { cn } from '@/lib/utils'
import type { OrganType } from '@/models/plant.types'
import { NOMBRES_ORGANOS } from '@/models/plant.types'

/**
 * Interfaz para una imagen con su órgano seleccionado
 */
interface ImagenConOrgano {
  id: string
  archivo: File
  previewUrl: string
  organ: OrganType
  tamano: number
}

/**
 * Props del componente MultipleImageUpload
 */
interface MultipleImageUploadProps {
  /** Callback cuando se completa la selección de imágenes */
  onImagenesSeleccionadas?: (imagenes: ImagenConOrgano[]) => void
  
  /** Número máximo de imágenes permitidas */
  maxImagenes?: number
  
  /** Clase CSS adicional */
  className?: string
  
  /** Tamaño máximo por archivo en MB */
  maxSizeMB?: number
  
  /** Órgano por defecto */
  organPorDefecto?: OrganType
}

/**
 * Componente para subir múltiples imágenes con selección de órgano
 * 
 * @example
 * ```tsx
 * <MultipleImageUpload
 *   maxImagenes={5}
 *   onImagenesSeleccionadas={(imagenes) => {
 *     console.log('Imágenes seleccionadas:', imagenes)
 *   }}
 * />
 * ```
 */
export function MultipleImageUpload({
  onImagenesSeleccionadas,
  maxImagenes = 5,
  className,
  maxSizeMB = 10,
  organPorDefecto = 'sin_especificar',
}: MultipleImageUploadProps) {
  const [imagenes, setImagenes] = useState<ImagenConOrgano[]>([])
  const [error, setError] = useState<string | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  /**
   * Genera un ID único para cada imagen
   */
  const generarId = () => `img-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`

  /**
   * Valida un archivo de imagen
   */
  const validarArchivo = (archivo: File): string | null => {
    // Validar tipo
    const tiposPermitidos = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp', 'image/heic']
    if (!tiposPermitidos.includes(archivo.type)) {
      return 'Formato no válido. Usa JPG, PNG, WEBP o HEIC'
    }

    // Validar tamaño
    const tamanoMB = archivo.size / (1024 * 1024)
    if (tamanoMB > maxSizeMB) {
      return `El archivo es muy grande (${tamanoMB.toFixed(1)}MB). Máximo ${maxSizeMB}MB`
    }

    return null
  }

  /**
   * Agrega nuevas imágenes a la lista
   */
  const agregarImagenes = useCallback(
    (archivos: FileList | null) => {
      if (!archivos || archivos.length === 0) return

      setError(null)

      // Validar límite de imágenes
      const espacioDisponible = maxImagenes - imagenes.length
      if (espacioDisponible === 0) {
        setError(`Ya has alcanzado el máximo de ${maxImagenes} imágenes`)
        return
      }

      const nuevasImagenes: ImagenConOrgano[] = []
      const archivosArray = Array.from(archivos).slice(0, espacioDisponible)

      for (const archivo of archivosArray) {
        // Validar archivo
        const errorValidacion = validarArchivo(archivo)
        if (errorValidacion) {
          setError(errorValidacion)
          continue
        }

        // Crear preview URL
        const previewUrl = URL.createObjectURL(archivo)

        nuevasImagenes.push({
          id: generarId(),
          archivo,
          previewUrl,
          organ: organPorDefecto,
          tamano: archivo.size,
        })
      }

      if (nuevasImagenes.length > 0) {
        const imagenesActualizadas = [...imagenes, ...nuevasImagenes]
        setImagenes(imagenesActualizadas)
        onImagenesSeleccionadas?.(imagenesActualizadas)
      }
    },
    [imagenes, maxImagenes, maxSizeMB, organPorDefecto, onImagenesSeleccionadas]
  )

  /**
   * Maneja el cambio del input file
   */
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    agregarImagenes(e.target.files)
    // Limpiar input para permitir seleccionar el mismo archivo de nuevo
    if (inputRef.current) {
      inputRef.current.value = ''
    }
  }

  /**
   * Elimina una imagen de la lista
   */
  const eliminarImagen = (id: string) => {
    setImagenes((prev) => {
      const nuevasImagenes = prev.filter((img) => img.id !== id)
      onImagenesSeleccionadas?.(nuevasImagenes)
      
      // Liberar URL del preview
      const imagenEliminada = prev.find((img) => img.id === id)
      if (imagenEliminada) {
        URL.revokeObjectURL(imagenEliminada.previewUrl)
      }
      
      return nuevasImagenes
    })
    setError(null)
  }

  /**
   * Actualiza el órgano de una imagen
   */
  const actualizarOrgano = (id: string, organ: OrganType) => {
    setImagenes((prev) => {
      const nuevasImagenes = prev.map((img) =>
        img.id === id ? { ...img, organ } : img
      )
      onImagenesSeleccionadas?.(nuevasImagenes)
      return nuevasImagenes
    })
  }

  /**
   * Abre el selector de archivos
   */
  const abrirSelector = () => {
    inputRef.current?.click()
  }

  /**
   * Formatea el tamaño del archivo
   */
  const formatearTamano = (bytes: number): string => {
    const kb = bytes / 1024
    if (kb < 1024) {
      return `${kb.toFixed(1)} KB`
    }
    return `${(kb / 1024).toFixed(1)} MB`
  }

  /**
   * Renderiza una tarjeta de imagen individual
   */
  const renderImagenCard = (imagen: ImagenConOrgano) => (
    <Card key={imagen.id} className="relative group">
      <CardContent className="p-3 space-y-3">
        {/* Preview de la imagen */}
        <div className="relative aspect-video bg-muted rounded-md overflow-hidden">
          <img
            src={imagen.previewUrl}
            alt={imagen.archivo.name}
            className="w-full h-full object-cover"
          />
          
          {/* Botón de eliminar */}
          <Button
            variant="destructive"
            size="icon"
            className="absolute top-2 right-2 h-8 w-8 opacity-0 group-hover:opacity-100 transition-opacity"
            onClick={() => eliminarImagen(imagen.id)}
          >
            <X className="h-4 w-4" />
          </Button>

          {/* Indicador de éxito */}
          <div className="absolute bottom-2 left-2 bg-green-500/90 text-white px-2 py-1 rounded-md text-xs font-medium flex items-center gap-1">
            <span className="text-white">✓</span>
            <span>¡Imagen subida con éxito!</span>
          </div>
        </div>

        {/* Información del archivo */}
        <div className="space-y-2">
          <div className="flex items-start justify-between gap-2">
            <p className="text-sm font-medium truncate flex-1" title={imagen.archivo.name}>
              {imagen.archivo.name}
            </p>
            <span className="text-xs text-muted-foreground whitespace-nowrap">
              {formatearTamano(imagen.tamano)}
            </span>
          </div>

          {/* Selector de órgano */}
          <Select
            value={imagen.organ}
            onValueChange={(value: string) => actualizarOrgano(imagen.id, value as OrganType)}
          >
            <SelectTrigger className="w-full">
              <SelectValue placeholder="Selecciona el órgano" />
            </SelectTrigger>
            <SelectContent>
              {Object.entries(NOMBRES_ORGANOS).map(([key, nombre]) => (
                <SelectItem key={key} value={key}>
                  {nombre}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </CardContent>
    </Card>
  )

  /**
   * Renderiza el área para agregar más imágenes
   */
  const renderAreaAgregar = () => {
    const puedeAgregarMas = imagenes.length < maxImagenes

    return (
      <Card
        className={cn(
          'border-2 border-dashed transition-colors',
          puedeAgregarMas
            ? 'hover:border-primary/50 hover:bg-accent/5 cursor-pointer'
            : 'opacity-50 cursor-not-allowed'
        )}
        onClick={puedeAgregarMas ? abrirSelector : undefined}
      >
        <CardContent className="p-6 flex flex-col items-center justify-center text-center space-y-3 min-h-[280px]">
          <div className="bg-primary/10 p-4 rounded-full">
            <Camera className="w-8 h-8 text-primary" />
          </div>
          <div>
            <p className="font-medium text-sm mb-1">
              {puedeAgregarMas
                ? `Agrega más imágenes (${imagenes.length}/${maxImagenes})`
                : `Máximo ${maxImagenes} imágenes alcanzado`}
            </p>
            <p className="text-xs text-muted-foreground">
              Soporta: JPG, PNG, HEIC
            </p>
          </div>

          {puedeAgregarMas && (
            <div className="flex flex-col gap-2 w-full">
              <Button variant="outline" size="sm" className="w-full" asChild>
                <label className="cursor-pointer">
                  <Upload className="w-4 h-4 mr-2" />
                  Subir Foto
                </label>
              </Button>
              <Button variant="outline" size="sm" className="w-full" asChild>
                <label className="cursor-pointer">
                  <Camera className="w-4 h-4 mr-2" />
                  Tomar Foto
                </label>
              </Button>
            </div>
          )}
        </CardContent>
      </Card>
    )
  }

  return (
    <div className={cn('space-y-4', className)}>
      {/* Título */}
      <div className="text-center space-y-2">
        <h2 className="text-2xl font-bold">Sube Fotos de la Planta</h2>
        <p className="text-muted-foreground">
          Toma o sube hasta {maxImagenes} fotos claras de la planta que quieres identificar
        </p>
      </div>

      {/* Input oculto para seleccionar archivos */}
      <input
        ref={inputRef}
        type="file"
        accept="image/*"
        multiple
        className="hidden"
        onChange={handleFileChange}
        aria-label="Seleccionar archivos de imagen"
      />

      {/* Grid de imágenes */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {/* Imágenes existentes */}
        {imagenes.map(renderImagenCard)}

        {/* Área para agregar más */}
        {renderAreaAgregar()}
      </div>

      {/* Mensaje de error */}
      {error && (
        <div className="bg-destructive/10 border border-destructive/30 rounded-lg p-3 text-sm text-destructive text-center">
          {error}
        </div>
      )}

      {/* Contador */}
      <div className="text-center text-sm text-muted-foreground">
        {imagenes.length === 0 ? (
          <p>No has subido ninguna imagen aún</p>
        ) : (
          <p>
            {imagenes.length} {imagenes.length === 1 ? 'imagen' : 'imágenes'} {imagenes.length === 1 ? 'seleccionada' : 'seleccionadas'}
          </p>
        )}
      </div>
    </div>
  )
}

export default MultipleImageUpload
