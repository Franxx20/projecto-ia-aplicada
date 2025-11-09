/**
 * page.tsx - Página de análisis de salud de plantas
 * 
 * Permite a los usuarios:
 * - Seleccionar una planta de su jardín
 * - Subir foto opcional de la planta
 * - Describir síntomas observados
 * - Analizar salud usando Gemini AI
 * - Ver diagnóstico completo con recomendaciones
 * 
 * @author Equipo Frontend
 * @date Noviembre 2025
 * @epic Epic 3 - Sistema de verificación de Salud con Gemini AI
 * @task T-080
 */

'use client'

import React, { useState, useEffect, Suspense } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { ArrowLeft, Sparkles, AlertCircle, Loader2, Stethoscope, Camera, FileText, Leaf, Upload, Image as ImageIcon } from 'lucide-react'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { useAuth } from '@/hooks/useAuth'
import saludService from '@/lib/salud.service'
import dashboardService from '@/lib/dashboard.service'
import type { AnalisisSalud } from '@/models/salud'
import type { Planta } from '@/models/dashboard.types'
import {
  ESTADO_TEXTOS,
  ESTADO_COLORES,
  ESTADO_EMOJIS,
  formatearConfianza,
  obtenerColorEstado,
  obtenerEmojiEstado
} from '@/models/salud'

/**
 * Resultado del análisis de salud
 */
interface ResultadoAnalisis extends AnalisisSalud {
  planta_nombre?: string
}

/**
 * Componente interno que usa searchParams
 * Separado para poder envolverlo en Suspense
 */
function SaludPageContent() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const { usuario, estaCargando: cargandoAuth } = useAuth()
  
  // Estados del formulario
  const [plantasDisponibles, setPlantasDisponibles] = useState<Planta[]>([])
  const [plantaSeleccionada, setPlantaSeleccionada] = useState<string>('')
  const [imagenSeleccionada, setImagenSeleccionada] = useState<File | null>(null)
  const [imagenPreview, setImagenPreview] = useState<string | null>(null)
  const [sintomasObservados, setSintomasObservados] = useState('')
  const [notasAdicionales, setNotasAdicionales] = useState('')
  
  // Estados del proceso
  const [estaAnalizando, setEstaAnalizando] = useState(false)
  const [progresoAnalisis, setProgresoAnalisis] = useState(0)
  const [errorAnalisis, setErrorAnalisis] = useState<string | null>(null)
  const [resultadoAnalisis, setResultadoAnalisis] = useState<ResultadoAnalisis | null>(null)
  
  // Cargar plantas del usuario y pre-seleccionar si viene de URL
  useEffect(() => {
    if (!cargandoAuth && usuario) {
      cargarPlantas()
    }
  }, [usuario, cargandoAuth])

  // Pre-seleccionar planta si viene desde parámetro URL
  useEffect(() => {
    const plantaId = searchParams?.get('planta_id')
    if (plantaId && plantasDisponibles.length > 0) {
      setPlantaSeleccionada(plantaId)
    }
  }, [searchParams, plantasDisponibles])

  /**
   * Carga las plantas del jardín del usuario
   */
  const cargarPlantas = async () => {
    try {
      const respuesta = await dashboardService.obtenerPlantas()
      setPlantasDisponibles(respuesta.plantas)
    } catch (error) {
      console.error('Error al cargar plantas:', error)
      setErrorAnalisis('No se pudieron cargar tus plantas. Por favor, intenta de nuevo.')
    }
  }

  /**
   * Maneja la selección de imagen
   */
  const handleImagenSeleccionada = (archivo: File, preview: string) => {
    setImagenSeleccionada(archivo)
    setImagenPreview(preview)
    setErrorAnalisis(null)
  }

  /**
   * Elimina la imagen seleccionada
   */
  const handleEliminarImagen = () => {
    setImagenSeleccionada(null)
    setImagenPreview(null)
  }

  /**
   * Valida el formulario antes de enviar
   */
  const validarFormulario = (): boolean => {
    if (!plantaSeleccionada) {
      setErrorAnalisis('Debes seleccionar una planta para analizar')
      return false
    }

    if (!imagenSeleccionada && !sintomasObservados.trim()) {
      setErrorAnalisis('Debes proporcionar una imagen o describir los síntomas observados')
      return false
    }

    return true
  }

  /**
   * Inicia el análisis de salud con Gemini AI
   */
  const analizarSalud = async () => {
    if (!validarFormulario()) return

    setEstaAnalizando(true)
    setErrorAnalisis(null)
    setResultadoAnalisis(null)
    setProgresoAnalisis(0)

    try {
      const plantaId = parseInt(plantaSeleccionada)
      const plantaInfo = plantasDisponibles.find(p => p.id === plantaId)

      console.log('Analizando salud de planta:', {
        plantaId,
        conImagen: !!imagenSeleccionada,
        conSintomas: !!sintomasObservados.trim()
      })

      // Simular progreso
      const intervaloProgreso = setInterval(() => {
        setProgresoAnalisis(prev => {
          if (prev >= 90) {
            clearInterval(intervaloProgreso)
            return 90
          }
          return prev + 10
        })
      }, 300)

      // Subir imagen si existe
      let imagenId: number | null = null
      if (imagenSeleccionada) {
        try {
          console.log('Subiendo imagen...')
          const { imageService } = await import('@/lib/image.service')
          const resultadoImagen = await imageService.subirImagen(
            imagenSeleccionada,
            (progreso: { percentage: number }) => {
              console.log(`Progreso subida imagen: ${progreso.percentage}%`)
            },
            { descripcion: 'Imagen para análisis de salud' }
          )
          console.log('Respuesta de subida de imagen:', resultadoImagen)
          
          // El backend devuelve 'id' como number, pero el tipo frontend lo define como string
          imagenId = typeof resultadoImagen.id === 'string' 
            ? parseInt(resultadoImagen.id, 10) 
            : resultadoImagen.id as number
          console.log('Imagen subida exitosamente. ID:', imagenId)
        } catch (errorImagen) {
          console.error('Error al subir imagen:', errorImagen)
          throw new Error(`Error al subir imagen: ${errorImagen instanceof Error ? errorImagen.message : 'Error desconocido'}`)
        }
      }

      console.log('Llamando a saludService.crearAnalisis con:', {
        planta_id: plantaId,
        imagen_id: imagenId,
        sintomas_observados: sintomasObservados.trim() || undefined,
        notas_adicionales: notasAdicionales.trim() || undefined
      })

      // Llamar al servicio de análisis
      const resultado = await saludService.crearAnalisis({
        planta_id: plantaId,
        imagen_id: imagenId,
        sintomas_observados: sintomasObservados.trim() || undefined,
        notas_adicionales: notasAdicionales.trim() || undefined
      })

      clearInterval(intervaloProgreso)
      setProgresoAnalisis(100)

      console.log('Análisis completado:', resultado)

      // Agregar nombre de planta al resultado
      const resultadoConNombre: ResultadoAnalisis = {
        ...resultado,
        planta_nombre: plantaInfo?.nombre_personal || 'Planta'
      }

      setResultadoAnalisis(resultadoConNombre)

      // Scroll al resultado
      setTimeout(() => {
        document.getElementById('resultado-analisis')?.scrollIntoView({ 
          behavior: 'smooth',
          block: 'start'
        })
      }, 100)

    } catch (error: any) {
      console.error('Error al analizar salud:', error)
      setErrorAnalisis(
        error.response?.data?.detail || 
        error.message || 
        'Ocurrió un error al analizar la salud de la planta. Por favor, intenta de nuevo.'
      )
    } finally {
      setEstaAnalizando(false)
    }
  }

  /**
   * Reinicia el formulario para un nuevo análisis
   */
  const nuevoAnalisis = () => {
    setPlantaSeleccionada('')
    setImagenSeleccionada(null)
    setImagenPreview(null)
    setSintomasObservados('')
    setNotasAdicionales('')
    setResultadoAnalisis(null)
    setErrorAnalisis(null)
    setProgresoAnalisis(0)
  }

  /**
   * Navega a la página de historial
   */
  const verHistorial = () => {
    router.push('/salud/historial')
  }

  if (cargandoAuth) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-4">
          <Link href="/dashboard">
            <Button variant="ghost" size="icon">
              <ArrowLeft className="h-5 w-5" />
            </Button>
          </Link>
          <div>
            <h1 className="text-3xl font-bold flex items-center gap-2">
              <Stethoscope className="h-8 w-8 text-primary" />
              Análisis de Salud
            </h1>
            <p className="text-muted-foreground mt-1">
              Diagnóstico inteligente con Gemini AI
            </p>
          </div>
        </div>
        <Button
          variant="outline"
          onClick={verHistorial}
          className="hidden sm:flex"
        >
          <FileText className="h-4 w-4 mr-2" />
          Ver Historial
        </Button>
      </div>

      {/* Formulario de Análisis */}
      {!resultadoAnalisis && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-primary" />
              Nuevo Análisis
            </CardTitle>
            <CardDescription>
              Selecciona una planta y proporciona información sobre su estado
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Selección de Planta */}
            <div className="space-y-2">
              <Label htmlFor="planta-select">
                Planta a analizar <span className="text-destructive">*</span>
              </Label>
              <Select
                value={plantaSeleccionada}
                onValueChange={setPlantaSeleccionada}
                disabled={estaAnalizando}
              >
                <SelectTrigger id="planta-select">
                  <SelectValue placeholder="Selecciona una planta de tu jardín" />
                </SelectTrigger>
                <SelectContent>
                  {plantasDisponibles.length === 0 ? (
                    <SelectItem value="none" disabled>
                      No tienes plantas registradas
                    </SelectItem>
                  ) : (
                    plantasDisponibles.map((planta) => (
                      <SelectItem key={planta.id} value={planta.id.toString()}>
                        <div className="flex items-center gap-2">
                          <Leaf className="h-4 w-4 text-green-600" />
                          <span>{planta.nombre_personal}</span>
                          {(planta as any).especie?.nombre_comun && (
                            <span className="text-muted-foreground text-sm">
                              ({(planta as any).especie.nombre_comun})
                            </span>
                          )}
                        </div>
                      </SelectItem>
                    ))
                  )}
                </SelectContent>
              </Select>
            </div>

            {/* Upload de Imagen */}
            <div className="space-y-2">
              <Label htmlFor="imagen-upload">
                Foto de la planta <span className="text-muted-foreground">(opcional)</span>
              </Label>
              <p className="text-sm text-muted-foreground">
                Una imagen ayuda a Gemini AI a hacer un diagnóstico más preciso
              </p>
              {!imagenPreview ? (
                <div className="border-2 border-dashed rounded-lg p-8 text-center">
                  <div className="space-y-4">
                    <div className="flex justify-center">
                      <div className="bg-primary/10 p-4 rounded-full">
                        <ImageIcon className="w-10 h-10 text-primary" />
                      </div>
                    </div>
                    <p className="text-base font-medium mb-1">Selecciona una imagen de la planta</p>
                    <p className="text-sm text-muted-foreground">JPG, PNG, WEBP (máx. 10MB)</p>
                    <Button asChild variant="default" disabled={estaAnalizando}>
                      <label className="cursor-pointer">
                        <Upload className="w-4 h-4 mr-2" />
                        Seleccionar Archivo
                        <input
                          type="file"
                          accept="image/*"
                          className="hidden"
                          onChange={(e) => {
                            const file = e.target.files?.[0]
                            if (file) {
                              const preview = URL.createObjectURL(file)
                              handleImagenSeleccionada(file, preview)
                            }
                          }}
                          disabled={estaAnalizando}
                        />
                      </label>
                    </Button>
                  </div>
                </div>
              ) : (
                <div className="relative">
                  <img
                    src={imagenPreview}
                    alt="Vista previa"
                    className="w-full h-64 object-cover rounded-lg border"
                  />
                  <Button
                    variant="destructive"
                    size="icon"
                    className="absolute top-2 right-2"
                    onClick={handleEliminarImagen}
                    disabled={estaAnalizando}
                  >
                    <AlertCircle className="h-4 w-4" />
                  </Button>
                  <Badge className="absolute bottom-2 left-2 bg-black/70 text-white">
                    <Camera className="h-3 w-3 mr-1" />
                    Imagen cargada
                  </Badge>
                </div>
              )}
            </div>

            {/* Síntomas Observados */}
            <div className="space-y-2">
              <Label htmlFor="sintomas">
                Síntomas observados <span className="text-muted-foreground">(opcional)</span>
              </Label>
              <p className="text-sm text-muted-foreground">
                Describe qué has notado en tu planta: manchas, hojas amarillas, etc.
              </p>
              <Textarea
                id="sintomas"
                placeholder="Ejemplo: He notado manchas marrones en las hojas inferiores y algunos bordes secos..."
                value={sintomasObservados}
                onChange={(e) => setSintomasObservados(e.target.value)}
                disabled={estaAnalizando}
                rows={4}
                className="resize-none"
              />
              <p className="text-xs text-muted-foreground text-right">
                {sintomasObservados.length} / 1000 caracteres
              </p>
            </div>

            {/* Notas Adicionales */}
            <div className="space-y-2">
              <Label htmlFor="notas">
                Notas adicionales <span className="text-muted-foreground">(opcional)</span>
              </Label>
              <p className="text-sm text-muted-foreground">
                Cualquier información adicional que pueda ayudar al diagnóstico
              </p>
              <Textarea
                id="notas"
                placeholder="Ejemplo: La planta está cerca de una ventana con mucha luz directa..."
                value={notasAdicionales}
                onChange={(e) => setNotasAdicionales(e.target.value)}
                disabled={estaAnalizando}
                rows={3}
                className="resize-none"
              />
            </div>

            {/* Error */}
            {errorAnalisis && (
              <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertTitle>Error</AlertTitle>
                <AlertDescription>{errorAnalisis}</AlertDescription>
              </Alert>
            )}

            {/* Progreso */}
            {estaAnalizando && (
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Analizando con Gemini AI...</span>
                  <span className="font-medium">{progresoAnalisis}%</span>
                </div>
                <div className="w-full bg-secondary rounded-full h-2">
                  <div
                    className="bg-primary h-2 rounded-full transition-all duration-300"
                    style={{ width: `${progresoAnalisis}%` }}
                  />
                </div>
              </div>
            )}

            {/* Botón de Análisis */}
            <Button
              onClick={analizarSalud}
              disabled={estaAnalizando || !plantaSeleccionada}
              className="w-full"
              size="lg"
            >
              {estaAnalizando ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Analizando...
                </>
              ) : (
                <>
                  <Sparkles className="mr-2 h-4 w-4" />
                  Analizar Salud
                </>
              )}
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Resultado del Análisis */}
      {resultadoAnalisis && (
        <div id="resultado-analisis" className="space-y-6">
          {/* Header del Resultado */}
          <Card className="border-2" style={{ borderColor: obtenerColorEstado(resultadoAnalisis.estado) }}>
            <CardHeader>
              <div className="flex items-start justify-between">
                <div>
                  <CardTitle className="text-2xl flex items-center gap-2">
                    <span className="text-3xl">{obtenerEmojiEstado(resultadoAnalisis.estado)}</span>
                    Estado: {ESTADO_TEXTOS[resultadoAnalisis.estado] || resultadoAnalisis.estado}
                  </CardTitle>
                  <CardDescription className="mt-2">
                    Planta: <span className="font-semibold">{resultadoAnalisis.planta_nombre}</span>
                  </CardDescription>
                </div>
                <Badge
                  variant="outline"
                  className="text-lg px-4 py-2"
                  style={{ 
                    backgroundColor: `${obtenerColorEstado(resultadoAnalisis.estado)}20`,
                    borderColor: obtenerColorEstado(resultadoAnalisis.estado)
                  }}
                >
                  Confianza: {formatearConfianza(resultadoAnalisis.confianza)}
                </Badge>
              </div>
            </CardHeader>
          </Card>

          {/* Diagnóstico */}
          <Card>
            <CardHeader>
              <CardTitle>Diagnóstico</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <h4 className="font-semibold mb-2">Resumen:</h4>
                <p className="text-muted-foreground">{resultadoAnalisis.resumen_diagnostico}</p>
              </div>
              {resultadoAnalisis.diagnostico_detallado && (
                <div>
                  <h4 className="font-semibold mb-2">Diagnóstico Detallado:</h4>
                  <p className="text-sm text-muted-foreground whitespace-pre-wrap">
                    {resultadoAnalisis.diagnostico_detallado}
                  </p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Problemas Detectados */}
          {resultadoAnalisis.problemas_detectados && resultadoAnalisis.problemas_detectados.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <AlertCircle className="h-5 w-5 text-amber-500" />
                  Problemas Detectados
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {resultadoAnalisis.problemas_detectados.map((problema: any, index: number) => (
                    <div key={index} className="flex items-start gap-3 p-3 border rounded-lg">
                      <div className="flex-1">
                        <h4 className="font-semibold">{problema.tipo || 'Problema'}</h4>
                        <p className="text-sm text-muted-foreground mt-1">
                          {problema.descripcion || problema.detalle || 'Sin descripción'}
                        </p>
                      </div>
                      {problema.severidad && (
                        <Badge
                          variant={
                            problema.severidad === 'critica' ? 'destructive' :
                            problema.severidad === 'severa' ? 'destructive' :
                            problema.severidad === 'moderada' ? 'default' :
                            'secondary'
                          }
                        >
                          {problema.severidad}
                        </Badge>
                      )}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Recomendaciones */}
          {resultadoAnalisis.recomendaciones && resultadoAnalisis.recomendaciones.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Sparkles className="h-5 w-5 text-primary" />
                  Recomendaciones
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {resultadoAnalisis.recomendaciones.map((recomendacion: any, index: number) => (
                    <div key={index} className="flex items-start gap-3">
                      <div className="mt-1 h-2 w-2 rounded-full bg-primary flex-shrink-0" />
                      <div className="flex-1">
                        <p className="text-sm">
                          {typeof recomendacion === 'string' 
                            ? recomendacion 
                            : recomendacion.accion || recomendacion.descripcion || 'Sin descripción'
                          }
                        </p>
                        {typeof recomendacion === 'object' && recomendacion.prioridad && (
                          <Badge variant="outline" className="mt-1">
                            Prioridad: {recomendacion.prioridad}
                          </Badge>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Metadatos del Análisis */}
          <Card>
            <CardContent className="pt-6">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <p className="text-muted-foreground">Modelo IA</p>
                  <p className="font-medium">{resultadoAnalisis.modelo_ia_usado || 'Gemini AI'}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Tiempo de análisis</p>
                  <p className="font-medium">{resultadoAnalisis.tiempo_analisis_ms}ms</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Con imagen</p>
                  <p className="font-medium">{resultadoAnalisis.con_imagen ? 'Sí' : 'No'}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Versión</p>
                  <p className="font-medium">{resultadoAnalisis.version_prompt || 'v1'}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Acciones */}
          <div className="flex flex-col sm:flex-row gap-3">
            <Button onClick={nuevoAnalisis} variant="outline" className="flex-1">
              Nuevo Análisis
            </Button>
            <Button onClick={verHistorial} className="flex-1">
              <FileText className="mr-2 h-4 w-4" />
              Ver Historial Completo
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}

/**
 * Página de análisis de salud de plantas
 * 
 * Wrapper con Suspense para manejar useSearchParams correctamente
 * durante la pre-renderización de Next.js
 */
export default function SaludPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center space-y-4">
          <Loader2 className="w-8 h-8 animate-spin mx-auto text-primary" />
          <p className="text-muted-foreground">Cargando análisis de salud...</p>
        </div>
      </div>
    }>
      <SaludPageContent />
    </Suspense>
  )
}
