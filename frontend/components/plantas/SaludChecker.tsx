/**
 * SaludChecker.tsx - Componente de verificación de salud de plantas con Gemini AI
 * 
 * Componente completo que permite analizar la salud de una planta con tres modos:
 * 1. Análisis sin imagen (solo contexto de la planta)
 * 2. Análisis con imagen nueva (upload drag-and-drop)
 * 3. Análisis con imagen principal existente
 * 
 * Incluye:
 * - Selector de modo de análisis
 * - Upload de imágenes con drag-and-drop
 * - Progress bar durante análisis
 * - Display de resultados con estado de salud
 * - Lista de problemas detectados
 * - Recomendaciones priorizadas
 * - Historial de análisis
 * 
 * @author Equipo Frontend
 * @date Noviembre 2025
 * @sprint Feature - Health Check AI
 * @task T-010
 */

'use client'

import React, { useState, useCallback } from 'react'
import {
  Leaf,
  Camera,
  FileImage,
  AlertCircle,
  CheckCircle2,
  Info,
  TrendingUp,
  AlertTriangle,
  Bug,
  Droplets,
  Sun,
  Sprout,
  Wind,
  Thermometer
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Label } from '@/components/ui/label'
import saludService from '@/lib/salud.service'
import type {
  SaludAnalisisResponse,
  TipoProblema
} from '@/models/salud'
import {
  NOMBRES_ESTADO_SALUD,
  ICONOS_ESTADO_SALUD,
  COLORES_ESTADO_SALUD,
  NOMBRES_TIPO_PROBLEMA,
  COLORES_SEVERIDAD,
  COLORES_PRIORIDAD,
  obtenerColorConfianza,
  formatearConfianza
} from '@/models/salud'
import { cn } from '@/lib/utils'

/**
 * Modos de análisis disponibles
 */
type ModoAnalisis = 'sin-imagen' | 'con-imagen' | 'imagen-principal'

/**
 * Props del componente SaludChecker
 */
interface SaludCheckerProps {
  /** ID de la planta a analizar */
  plantaId: number
  
  /** Nombre de la planta (para mostrar en UI) */
  nombrePlanta?: string
  
  /** Si la planta tiene imagen principal disponible */
  tieneImagenPrincipal?: boolean
  
  /** Callback cuando se completa un análisis exitosamente */
  onAnalisisCompletado?: (analisis: SaludAnalisisResponse) => void
  
  /** Clase CSS adicional */
  className?: string
}

/**
 * Obtiene el icono correspondiente a un tipo de problema
 */
const obtenerIconoProblema = (tipo: TipoProblema): React.ReactNode => {
  const iconos: Record<TipoProblema, React.ReactNode> = {
    riego: <Droplets className="w-4 h-4" />,
    luz: <Sun className="w-4 h-4" />,
    nutricion: <Sprout className="w-4 h-4" />,
    temperatura: <Thermometer className="w-4 h-4" />,
    humedad: <Wind className="w-4 h-4" />,
    plaga: <Bug className="w-4 h-4" />,
    enfermedad: <AlertTriangle className="w-4 h-4" />,
    fisico: <AlertCircle className="w-4 h-4" />,
    otro: <Info className="w-4 h-4" />
  }
  return iconos[tipo]
}

/**
 * Componente principal de verificación de salud
 */
export function SaludChecker({
  plantaId,
  nombrePlanta = 'Tu planta',
  tieneImagenPrincipal = false,
  onAnalisisCompletado,
  className
}: SaludCheckerProps) {
  // Estado del componente
  const [modoAnalisis, setModoAnalisis] = useState<ModoAnalisis>('sin-imagen')
  const [imagenSeleccionada, setImagenSeleccionada] = useState<File | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [notasAdicionales, setNotasAdicionales] = useState('')
  
  // Estado del análisis
  const [analizando, setAnalizando] = useState(false)
  const [progreso, setProgreso] = useState(0)
  const [resultado, setResultado] = useState<SaludAnalisisResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  /**
   * Maneja la selección de archivo de imagen
   */
  const handleImagenSeleccionada = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      // Validar tipo de archivo
      if (!file.type.startsWith('image/')) {
        setError('Por favor selecciona un archivo de imagen válido')
        return
      }
      
      // Validar tamaño (máx 10MB)
      if (file.size > 10 * 1024 * 1024) {
        setError('La imagen no debe superar los 10MB')
        return
      }
      
      setImagenSeleccionada(file)
      setError(null)
      
      // Crear preview
      const reader = new FileReader()
      reader.onloadend = () => {
        setPreviewUrl(reader.result as string)
      }
      reader.readAsDataURL(file)
    }
  }, [])

  /**
   * Maneja el drag and drop
   */
  const handleDrop = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    const file = e.dataTransfer.files?.[0]
    if (file) {
      // Validar tipo de archivo
      if (!file.type.startsWith('image/')) {
        setError('Por favor selecciona un archivo de imagen válido')
        return
      }
      
      // Validar tamaño (máx 10MB)
      if (file.size > 10 * 1024 * 1024) {
        setError('La imagen no debe superar los 10MB')
        return
      }
      
      setImagenSeleccionada(file)
      setError(null)
      
      // Crear preview
      const reader = new FileReader()
      reader.onloadend = () => {
        setPreviewUrl(reader.result as string)
      }
      reader.readAsDataURL(file)
    }
  }, [])

  /**
   * Limpia la imagen seleccionada
   */
  const limpiarImagen = useCallback(() => {
    setImagenSeleccionada(null)
    setPreviewUrl(null)
  }, [])

  /**
   * Ejecuta el análisis de salud
   */
  const ejecutarAnalisis = useCallback(async () => {
    try {
      setAnalizando(true)
      setProgreso(0)
      setError(null)
      setResultado(null)

      let analisis: SaludAnalisisResponse

      // Ejecutar según el modo seleccionado
      switch (modoAnalisis) {
        case 'sin-imagen':
          analisis = await saludService.verificarSaludSinImagen(
            plantaId,
            notasAdicionales || undefined
          )
          break

        case 'con-imagen':
          if (!imagenSeleccionada) {
            throw new Error('Debes seleccionar una imagen')
          }
          analisis = await saludService.verificarSalud(
            plantaId,
            imagenSeleccionada,
            {
              notas_adicionales: notasAdicionales || undefined,
              onProgress: setProgreso
            }
          )
          break

        case 'imagen-principal':
          analisis = await saludService.verificarSaludConImagenPrincipal(
            plantaId,
            notasAdicionales || undefined
          )
          break

        default:
          throw new Error('Modo de análisis no válido')
      }

      setResultado(analisis)
      setProgreso(100)
      onAnalisisCompletado?.(analisis)

    } catch (err) {
      const mensaje = err instanceof Error ? err.message : 'Error al analizar la salud'
      setError(mensaje)
    } finally {
      setAnalizando(false)
    }
  }, [modoAnalisis, plantaId, imagenSeleccionada, notasAdicionales, onAnalisisCompletado])

  /**
   * Reinicia el componente para un nuevo análisis
   */
  const nuevoAnalisis = useCallback(() => {
    setResultado(null)
    setError(null)
    setProgreso(0)
    limpiarImagen()
    setNotasAdicionales('')
  }, [limpiarImagen])

  return (
    <div className={cn('space-y-6', className)}>
      {/* Título y descripción */}
      <div>
        <h2 className="text-2xl font-bold flex items-center gap-2">
          <Leaf className="w-6 h-6 text-green-600" />
          Verificar Salud de {nombrePlanta}
        </h2>
        <p className="text-muted-foreground mt-1">
          Analiza la salud de tu planta con IA de Google Gemini
        </p>
      </div>

      {/* Selector de modo de análisis */}
      {!resultado && (
        <Card>
          <CardHeader>
            <CardTitle>Modo de Análisis</CardTitle>
            <CardDescription>
              Elige cómo quieres analizar la salud de tu planta
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Tabs value={modoAnalisis} onValueChange={(v) => setModoAnalisis(v as ModoAnalisis)}>
              <TabsList className="grid w-full grid-cols-3">
                <TabsTrigger value="sin-imagen" className="flex items-center gap-2">
                  <Leaf className="w-4 h-4" />
                  Sin Imagen
                </TabsTrigger>
                <TabsTrigger value="con-imagen" className="flex items-center gap-2">
                  <Camera className="w-4 h-4" />
                  Nueva Imagen
                </TabsTrigger>
                <TabsTrigger
                  value="imagen-principal"
                  disabled={!tieneImagenPrincipal}
                  className="flex items-center gap-2"
                >
                  <FileImage className="w-4 h-4" />
                  Imagen Principal
                </TabsTrigger>
              </TabsList>

              {/* Modo: Sin imagen */}
              <TabsContent value="sin-imagen" className="space-y-4 mt-4">
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <div className="flex items-start gap-3">
                    <Info className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
                    <div>
                      <h4 className="font-semibold text-sm text-blue-900">Análisis basado en contexto</h4>
                      <p className="text-sm text-blue-700 mt-1">
                        El análisis se realizará únicamente con la información registrada de tu planta
                        (especie, ubicación, cuidados). Es más rápido pero menos preciso.
                      </p>
                    </div>
                  </div>
                </div>
              </TabsContent>

              {/* Modo: Con imagen nueva */}
              <TabsContent value="con-imagen" className="space-y-4 mt-4">
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <div className="flex items-start gap-3">
                    <Camera className="h-5 w-5 text-green-600 flex-shrink-0 mt-0.5" />
                    <div>
                      <h4 className="font-semibold text-sm text-green-900">Análisis con imagen</h4>
                      <p className="text-sm text-green-700 mt-1">
                        Sube una foto reciente de tu planta para un análisis visual completo y más preciso.
                      </p>
                    </div>
                  </div>
                </div>

                {/* Área de upload */}
                <div
                  className={cn(
                    'border-2 border-dashed rounded-lg p-8 text-center transition-colors',
                    previewUrl ? 'border-green-300 bg-green-50' : 'border-gray-300 hover:border-gray-400'
                  )}
                  onDrop={handleDrop}
                  onDragOver={(e) => e.preventDefault()}
                >
                  {previewUrl ? (
                    <div className="space-y-4">
                      <img
                        src={previewUrl}
                        alt="Preview"
                        className="max-h-64 mx-auto rounded-lg shadow-md"
                      />
                      <Button
                        variant="outline"
                        onClick={limpiarImagen}
                        className="mt-2"
                      >
                        Cambiar imagen
                      </Button>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      <Camera className="w-12 h-12 mx-auto text-gray-400" />
                      <div>
                        <p className="text-sm font-medium">
                          Arrastra una imagen aquí o haz clic para seleccionar
                        </p>
                        <p className="text-xs text-muted-foreground mt-1">
                          JPG, PNG o WEBP (máx. 10MB)
                        </p>
                      </div>
                      <input
                        type="file"
                        accept="image/*"
                        onChange={handleImagenSeleccionada}
                        className="hidden"
                        id="imagen-upload"
                      />
                      <label htmlFor="imagen-upload">
                        <Button asChild variant="outline">
                          <span>Seleccionar archivo</span>
                        </Button>
                      </label>
                    </div>
                  )}
                </div>
              </TabsContent>

              {/* Modo: Imagen principal */}
              <TabsContent value="imagen-principal" className="space-y-4 mt-4">
                <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                  <div className="flex items-start gap-3">
                    <FileImage className="h-5 w-5 text-purple-600 flex-shrink-0 mt-0.5" />
                    <div>
                      <h4 className="font-semibold text-sm text-purple-900">Usar imagen principal</h4>
                      <p className="text-sm text-purple-700 mt-1">
                        Se utilizará la imagen principal registrada de tu planta para el análisis.
                      </p>
                    </div>
                  </div>
                </div>
              </TabsContent>
            </Tabs>

            {/* Notas adicionales */}
            <div className="mt-6 space-y-2">
              <Label htmlFor="notas">Notas adicionales (opcional)</Label>
              <textarea
                id="notas"
                placeholder="Describe síntomas o cambios que hayas observado..."
                value={notasAdicionales}
                onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setNotasAdicionales(e.target.value)}
                rows={3}
                className="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 resize-none"
              />
              <p className="text-xs text-muted-foreground">
                Ejemplo: "He notado hojas amarillentas desde hace una semana"
              </p>
            </div>

            {/* Botón de análisis */}
            <div className="mt-6">
              <Button
                onClick={ejecutarAnalisis}
                disabled={analizando || (modoAnalisis === 'con-imagen' && !imagenSeleccionada)}
                className="w-full"
                size="lg"
              >
                {analizando ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2" />
                    Analizando...
                  </>
                ) : (
                  <>
                    <TrendingUp className="w-4 h-4 mr-2" />
                    Analizar Salud
                  </>
                )}
              </Button>
            </div>

            {/* Barra de progreso */}
            {analizando && progreso > 0 && (
              <div className="mt-4 space-y-2">
                <Progress value={progreso} className="h-2" />
                <p className="text-xs text-center text-muted-foreground">
                  {progreso}% completado
                </p>
              </div>
            )}

            {/* Mensajes de error */}
            {error && (
              <div className="mt-4 bg-red-50 border border-red-200 rounded-lg p-4">
                <div className="flex items-start gap-3">
                  <AlertCircle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
                  <div>
                    <h4 className="font-semibold text-sm text-red-900">Error</h4>
                    <p className="text-sm text-red-700 mt-1">{error}</p>
                  </div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Resultados del análisis */}
      {resultado && (
        <div className="space-y-6">
          {/* Estado general de salud */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2">
                  {ICONOS_ESTADO_SALUD[resultado.estado]}
                  {NOMBRES_ESTADO_SALUD[resultado.estado]}
                </CardTitle>
                <Badge
                  variant="outline"
                  className={cn('text-sm', obtenerColorConfianza(resultado.confianza))}
                >
                  Confianza: {formatearConfianza(resultado.confianza)}
                </Badge>
              </div>
              <CardDescription>
                {new Date(resultado.metadata.fecha_analisis).toLocaleString('es-ES', {
                  dateStyle: 'long',
                  timeStyle: 'short'
                })}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Resumen */}
              <div
                className={cn(
                  'p-4 rounded-lg border-2',
                  COLORES_ESTADO_SALUD[resultado.estado]
                )}
              >
                <p className="text-sm leading-relaxed">{resultado.resumen}</p>
              </div>

              {/* Metadatos */}
              <div className="grid grid-cols-2 gap-4 pt-4 border-t">
                <div>
                  <p className="text-xs text-muted-foreground">Modelo IA</p>
                  <p className="text-sm font-medium">{resultado.metadata.modelo_usado}</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Tiempo de análisis</p>
                  <p className="text-sm font-medium">
                    {(resultado.metadata.tiempo_analisis_ms / 1000).toFixed(1)}s
                  </p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Con imagen</p>
                  <p className="text-sm font-medium">
                    {resultado.metadata.con_imagen ? 'Sí' : 'No'}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Problemas detectados</p>
                  <p className="text-sm font-medium">{resultado.problemas_detectados.length}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Problemas detectados */}
          {resultado.problemas_detectados.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <AlertTriangle className="w-5 h-5 text-orange-600" />
                  Problemas Detectados
                </CardTitle>
                <CardDescription>
                  {resultado.problemas_detectados.length} problema(s) identificado(s)
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {resultado.problemas_detectados.map((problema, index) => (
                  <div
                    key={`problema-${resultado.id}-${index}`}
                    className={cn(
                      'p-4 rounded-lg border-l-4',
                      COLORES_SEVERIDAD[problema.severidad]
                    )}
                  >
                    <div className="flex items-start gap-3">
                      {obtenerIconoProblema(problema.tipo)}
                      <div className="flex-1 space-y-1">
                        <div className="flex items-center justify-between">
                          <p className="font-medium text-sm">
                            {NOMBRES_TIPO_PROBLEMA[problema.tipo]}
                          </p>
                          <Badge variant="outline" className="text-xs">
                            {problema.severidad}
                          </Badge>
                        </div>
                        <p className="text-sm text-muted-foreground">
                          {problema.descripcion}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          )}

          {/* Recomendaciones */}
          {resultado.recomendaciones.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <CheckCircle2 className="w-5 h-5 text-green-600" />
                  Recomendaciones
                </CardTitle>
                <CardDescription>
                  {resultado.recomendaciones.length} acción(es) sugerida(s)
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {resultado.recomendaciones.map((recomendacion, index) => (
                  <div
                    key={`recomendacion-${resultado.id}-${index}`}
                    className={cn(
                      'p-4 rounded-lg border-l-4',
                      COLORES_PRIORIDAD[recomendacion.prioridad]
                    )}
                  >
                    <div className="flex items-start gap-3">
                      {obtenerIconoProblema(recomendacion.tipo)}
                      <div className="flex-1 space-y-1">
                        <div className="flex items-center justify-between">
                          <p className="font-medium text-sm">
                            {NOMBRES_TIPO_PROBLEMA[recomendacion.tipo]}
                          </p>
                          <div className="flex items-center gap-2">
                            <Badge variant="outline" className="text-xs">
                              {recomendacion.prioridad}
                            </Badge>
                            {recomendacion.urgencia_dias !== undefined && (
                              <Badge variant="secondary" className="text-xs">
                                {recomendacion.urgencia_dias === 0
                                  ? 'Inmediato'
                                  : `${recomendacion.urgencia_dias} días`}
                              </Badge>
                            )}
                          </div>
                        </div>
                        <p className="text-sm text-muted-foreground">
                          {recomendacion.descripcion}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          )}

          {/* Diagnóstico detallado (si existe) */}
          {resultado.diagnostico_detallado && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Info className="w-5 h-5 text-blue-600" />
                  Diagnóstico Detallado
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground leading-relaxed whitespace-pre-line">
                  {resultado.diagnostico_detallado}
                </p>
              </CardContent>
            </Card>
          )}

          {/* Botón para nuevo análisis */}
          <div className="flex justify-center">
            <Button onClick={nuevoAnalisis} variant="outline" size="lg">
              Realizar Nuevo Análisis
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}

export default SaludChecker
