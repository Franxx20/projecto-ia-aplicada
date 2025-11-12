/**
 * page.tsx - Página de detalle de análisis de salud
 * 
 * Muestra los detalles completos de un análisis de salud realizado previamente.
 * Similar a la vista de resultados de /salud, pero para análisis históricos.
 * 
 * @author Equipo Frontend
 * @date Noviembre 2025
 */

'use client'

import React, { useState, useEffect } from 'react'
import { useRouter, useParams } from 'next/navigation'
import { ArrowLeft, Sparkles, AlertCircle, Loader2, FileText, Leaf } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Carousel, CarouselContent, CarouselItem, CarouselApi } from '@/components/ui/carousel'
import { useAuth } from '@/hooks/useAuth'
import saludService from '@/lib/salud.service'
import type { DetalleAnalisisSaludResponse } from '@/models/salud'
import {
  ESTADO_TEXTOS,
  formatearConfianza,
  obtenerColorEstado,
  obtenerEmojiEstado
} from '@/models/salud'

/**
 * Componente para mostrar carrusel de imágenes
 */
interface ImageCarouselProps {
  imagenes: Array<{
    id: number
    url: string
    nombre_archivo: string
    organ?: string | null
  }>
}

function ImageCarousel({ imagenes }: ImageCarouselProps) {
  const [api, setApi] = useState<CarouselApi>()
  const [current, setCurrent] = useState(0)
  const [count, setCount] = useState(0)

  useEffect(() => {
    if (!api) return

    setCount(api.scrollSnapList().length)
    setCurrent(api.selectedScrollSnap() + 1)

    api.on("select", () => {
      setCurrent(api.selectedScrollSnap() + 1)
    })
  }, [api])

  return (
    <div className="relative">
      <Carousel setApi={setApi} className="w-full">
        <CarouselContent>
          {imagenes.map((imagen, index) => (
            <CarouselItem key={`analisis-img-${imagen.id}-${index}`}>
              <div className="relative">
                <img
                  src={imagen.url}
                  alt={imagen.nombre_archivo}
                  className="w-full max-h-96 object-contain rounded-lg border"
                />
                {imagen.organ && imagen.organ !== 'sin_especificar' && (
                  <div className="absolute bottom-3 left-3">
                    <Badge variant="secondary" className="bg-black/50 text-white backdrop-blur-sm">
                      {imagen.organ}
                    </Badge>
                  </div>
                )}
              </div>
            </CarouselItem>
          ))}
        </CarouselContent>
      </Carousel>

      {/* Indicador de posición */}
      {count > 1 && (
        <div className="absolute bottom-4 right-4">
          <Badge variant="secondary" className="bg-black/50 text-white backdrop-blur-sm">
            {current} / {count}
          </Badge>
        </div>
      )}
    </div>
  )
}

/**
 * Formatea una fecha a texto legible
 */
function formatearFecha(fecha: string): string {
  const date = new Date(fecha)
  return date.toLocaleDateString('es-ES', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

export default function DetalleAnalisisPage() {
  const router = useRouter()
  const params = useParams()
  const { usuario, estaCargando: authLoading } = useAuth()
  
  const [analisis, setAnalisis] = useState<DetalleAnalisisSaludResponse | null>(null)
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (authLoading) return

    if (!usuario) {
      router.push('/login')
      return
    }

    cargarAnalisis()
  }, [usuario, authLoading, params.id])

  const cargarAnalisis = async () => {
    try {
      setCargando(true)
      setError(null)
      
      const analisisId = Number(params.id)
      if (isNaN(analisisId)) {
        setError('ID de análisis inválido')
        return
      }

      const data = await saludService.obtenerAnalisis(analisisId)
      setAnalisis(data)
    } catch (err) {
      console.error('Error al cargar análisis:', err)
      setError(err instanceof Error ? err.message : 'Error al cargar el análisis')
    } finally {
      setCargando(false)
    }
  }

  const verHistorial = () => {
    router.push('/salud/historial')
  }

  const verPlanta = () => {
    if (analisis?.planta_id) {
      router.push(`/plant/${analisis.planta_id}`)
    }
  }

  const nuevoAnalisis = () => {
    if (analisis?.planta_id) {
      router.push(`/salud?planta_id=${analisis.planta_id}`)
    } else {
      router.push('/salud')
    }
  }

  // Loading state
  if (authLoading || cargando) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center space-y-4">
          <Loader2 className="w-8 h-8 animate-spin mx-auto text-primary" />
          <p className="text-muted-foreground">Cargando análisis...</p>
        </div>
      </div>
    )
  }

  // Error state
  if (error) {
    return (
      <div className="container max-w-4xl mx-auto px-4 py-8">
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
        <div className="mt-4">
          <Button onClick={() => router.back()} variant="outline">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Volver
          </Button>
        </div>
      </div>
    )
  }

  // No data state
  if (!analisis) {
    return (
      <div className="container max-w-4xl mx-auto px-4 py-8">
        <Alert>
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>No encontrado</AlertTitle>
          <AlertDescription>No se encontró el análisis solicitado.</AlertDescription>
        </Alert>
        <div className="mt-4">
          <Button onClick={() => router.back()} variant="outline">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Volver
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="container max-w-4xl mx-auto px-4 py-8 space-y-6">
      {/* Header con navegación */}
      <div className="flex items-center justify-between">
        <Button variant="ghost" onClick={() => router.back()}>
          <ArrowLeft className="mr-2 h-4 w-4" />
          Volver
        </Button>
        <div className="flex gap-2">
          {analisis.planta && (
            <Button variant="outline" onClick={verPlanta}>
              <Leaf className="mr-2 h-4 w-4" />
              Ver Planta
            </Button>
          )}
        </div>
      </div>

      {/* Resultado del Análisis - Igual que /salud */}
      <div id="resultado-analisis" className="space-y-6">
        {/* Header del Resultado */}
        <Card className="border-2" style={{ borderColor: obtenerColorEstado(analisis.estado) }}>
          <CardHeader>
            <div className="flex items-start justify-between">
              <div className="space-y-2">
                <CardTitle className="text-2xl flex items-center gap-2">
                  <span className="text-3xl">{obtenerEmojiEstado(analisis.estado)}</span>
                  Estado: {ESTADO_TEXTOS[analisis.estado] || analisis.estado}
                </CardTitle>
                <CardDescription className="space-y-1">
                  {analisis.planta && (
                    <div>
                      Planta: <span className="font-semibold">{analisis.planta.nombre_personal}</span>
                      {analisis.planta.especie && (
                        <span className="text-muted-foreground"> ({analisis.planta.especie})</span>
                      )}
                    </div>
                  )}
                  <div className="text-xs text-muted-foreground">
                    Analizado el {formatearFecha(analisis.fecha_analisis)}
                  </div>
                </CardDescription>
              </div>
              <div className="flex flex-col items-end gap-2">
                <Badge
                  variant="outline"
                  className="text-lg px-4 py-2"
                  style={{ 
                    backgroundColor: `${obtenerColorEstado(analisis.estado)}20`,
                    borderColor: obtenerColorEstado(analisis.estado)
                  }}
                >
                  Confianza: {formatearConfianza(analisis.confianza)}
                </Badge>
                {analisis.tendencia && (
                  <Badge variant="secondary" className="text-xs">
                    Tendencia: {analisis.tendencia}
                  </Badge>
                )}
              </div>
            </div>
          </CardHeader>
        </Card>

        {/* Imágenes analizadas */}
        {((analisis.imagenes && analisis.imagenes.length > 0) || analisis.imagen_url) && (
          <Card>
            <CardHeader>
              <CardTitle>
                {analisis.imagenes && analisis.imagenes.length > 1 
                  ? `Imágenes Analizadas (${analisis.imagenes.length})`
                  : 'Imagen Analizada'
                }
              </CardTitle>
            </CardHeader>
            <CardContent>
              {analisis.imagenes && analisis.imagenes.length > 0 ? (
                // Múltiples imágenes - Mostrar carrusel
                analisis.imagenes.length === 1 ? (
                  // Una sola imagen - Mostrar sin carrusel
                  <div className="relative">
                    <img
                      src={analisis.imagenes[0].url}
                      alt={analisis.imagenes[0].nombre_archivo}
                      className="w-full max-h-96 object-contain rounded-lg border"
                    />
                    {analisis.imagenes[0].organ && analisis.imagenes[0].organ !== 'sin_especificar' && (
                      <div className="absolute bottom-3 left-3">
                        <Badge variant="secondary" className="bg-black/50 text-white backdrop-blur-sm">
                          {analisis.imagenes[0].organ}
                        </Badge>
                      </div>
                    )}
                  </div>
                ) : (
                  // Múltiples imágenes - Mostrar carrusel
                  <ImageCarousel imagenes={analisis.imagenes} />
                )
              ) : analisis.imagen_url ? (
                // Fallback para análisis antiguos con imagen_url
                <img
                  src={analisis.imagen_url}
                  alt="Imagen analizada"
                  className="w-full max-h-96 object-contain rounded-lg border"
                />
              ) : null}
            </CardContent>
          </Card>
        )}

        {/* Diagnóstico */}
        <Card>
          <CardHeader>
            <CardTitle>Diagnóstico</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <h4 className="font-semibold mb-2">Resumen:</h4>
              <p className="text-muted-foreground">{analisis.resumen_diagnostico}</p>
            </div>
            {analisis.diagnostico_detallado && (
              <div>
                <h4 className="font-semibold mb-2">Diagnóstico Detallado:</h4>
                <p className="text-sm text-muted-foreground whitespace-pre-wrap">
                  {analisis.diagnostico_detallado}
                </p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Problemas Detectados */}
        {analisis.problemas_detectados && analisis.problemas_detectados.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <AlertCircle className="h-5 w-5 text-amber-500" />
                Problemas Detectados
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {analisis.problemas_detectados.map((problema: any, index: number) => (
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
        {analisis.recomendaciones && analisis.recomendaciones.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Sparkles className="h-5 w-5 text-primary" />
                Recomendaciones
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {analisis.recomendaciones.map((recomendacion: any, index: number) => (
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
                <p className="font-medium">{analisis.modelo_ia_usado || 'Gemini AI'}</p>
              </div>
              <div>
                <p className="text-muted-foreground">Tiempo de análisis</p>
                <p className="font-medium">{analisis.tiempo_analisis_ms}ms</p>
              </div>
              <div>
                <p className="text-muted-foreground">Con imagen</p>
                <p className="font-medium">{analisis.con_imagen ? 'Sí' : 'No'}</p>
              </div>
              <div>
                <p className="text-muted-foreground">Versión</p>
                <p className="font-medium">{analisis.version_prompt || 'v1'}</p>
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
    </div>
  )
}
