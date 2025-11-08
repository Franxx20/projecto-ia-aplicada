"use client"

/**
 * Página del Dashboard de Plantas
 * 
 * Dashboard principal que muestra el jardín del usuario con estadísticas,
 * grid de plantas con información de salud, riego y luz.
 * Integrado con el backend de plantas mediante dashboardService.
 * 
 * Features:
 * - Estadísticas del jardín (total plantas, saludables, necesitan atención, necesitan riego)
 * - Grid responsivo de tarjetas de plantas
 * - Información de cada planta: salud, último riego, próximo riego, luz
 * - Navegación a identificación de plantas
 * - Protección de ruta (requiere autenticación)
 * 
 * @author GitHub Copilot
 * @date 2025-10-17
 * @sprint Sprint 2 - T-017
 */

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Carousel, CarouselContent, CarouselItem, type CarouselApi } from "@/components/ui/carousel"
import { Plus, Droplets, Sun, Leaf, LogOut, Camera, Heart } from "lucide-react"
import { useAuth } from "@/hooks/useAuth"
import dashboardService from "@/lib/dashboard.service"
import plantService from "@/lib/plant.service"
import type { Planta, DashboardStats } from "@/models/dashboard.types"
import type { PlantaUsuario } from "@/models/plant.types"
import { NOMBRES_ORGANOS } from "@/models/plant.types"
import { cn } from "@/lib/utils"
import {
  estadoSaludToBadgeVariant,
  estadoSaludToLabel,
} from "@/models/dashboard.types"

/**
 * Componente para el carousel de imágenes de una planta
 */
function PlantImageCarousel({ 
  images, 
  plantName 
}: Readonly<{ 
  images: Array<{ id: number; url_blob: string; nombre_archivo: string; organ?: string; tamano_bytes: number }>;
  plantName: string;
}>) {
  const [api, setApi] = useState<CarouselApi>()
  const [current, setCurrent] = useState(0)

  useEffect(() => {
    if (!api) return

    setCurrent(api.selectedScrollSnap())

    const intervalId = setInterval(() => {
      api.scrollNext()
    }, 4000)

    api.on("select", () => {
      setCurrent(api.selectedScrollSnap())
    })

    return () => clearInterval(intervalId)
  }, [api])

  if (!images || images.length === 0) {
    return (
      <div className="aspect-square relative bg-muted flex items-center justify-center w-full h-full">
        <Leaf className="h-24 w-24 text-muted-foreground" />
      </div>
    )
  }

  if (images.length === 1) {
    return (
      <div className="aspect-square relative bg-muted w-full overflow-hidden">
        <img
          src={images[0].url_blob}
          alt={plantName}
          className="w-full h-full object-cover"
          onError={(e) => {
            console.error('Error al cargar imagen:', images[0].url_blob)
            e.currentTarget.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="400" height="400"%3E%3Crect fill="%23f0f0f0" width="400" height="400"/%3E%3Ctext fill="%23999" x="50%25" y="50%25" text-anchor="middle" dy=".3em"%3EImagen no disponible%3C/text%3E%3C/svg%3E'
          }}
        />
        {images[0].organ && images[0].organ !== 'sin_especificar' && (
          <Badge 
            className="absolute top-2 right-2 bg-black/70 text-white hover:bg-black/80"
            variant="secondary"
          >
            {NOMBRES_ORGANOS[images[0].organ as keyof typeof NOMBRES_ORGANOS] || images[0].organ}
          </Badge>
        )}
      </div>
    )
  }

  return (
    <div className="relative w-full">
      <Carousel
        setApi={setApi}
        opts={{
          align: "center",
          loop: true,
        }}
        className="w-full"
      >
        <CarouselContent>
          {images.map((imagen) => (
            <CarouselItem key={imagen.id}>
              <div className="aspect-square relative bg-muted w-full overflow-hidden">
                <img
                  src={imagen.url_blob}
                  alt={`${plantName} - ${imagen.nombre_archivo}`}
                  className="w-full h-full object-cover"
                  onError={(e) => {
                    console.error('Error al cargar imagen:', imagen.url_blob)
                    e.currentTarget.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="400" height="400"%3E%3Crect fill="%23f0f0f0" width="400" height="400"/%3E%3Ctext fill="%23999" x="50%25" y="50%25" text-anchor="middle" dy=".3em"%3EImagen no disponible%3C/text%3E%3C/svg%3E'
                  }}
                />
                {imagen.organ && imagen.organ !== 'sin_especificar' && (
                  <Badge 
                    className="absolute top-2 right-2 bg-black/70 text-white hover:bg-black/80"
                    variant="secondary"
                  >
                    {NOMBRES_ORGANOS[imagen.organ as keyof typeof NOMBRES_ORGANOS] || imagen.organ}
                  </Badge>
                )}
              </div>
            </CarouselItem>
          ))}
        </CarouselContent>
      </Carousel>
      
      {/* Indicadores de carousel */}
      {images.length > 1 && (
        <div className="absolute bottom-2 left-0 right-0 flex justify-center gap-1.5 px-2">
          {images.map((img, index) => (
            <button
              key={`indicator-${img.id}`}
              className={cn(
                "h-1.5 rounded-full transition-all",
                index === current 
                  ? "bg-white w-6 shadow-lg" 
                  : "bg-white/50 w-1.5"
              )}
              onClick={() => api?.scrollTo(index)}
              aria-label={`Ir a imagen ${index + 1}`}
            />
          ))}
        </div>
      )}
    </div>
  )
}

export default function DashboardPage() {
  const router = useRouter()
  const { usuario, estaAutenticado, estaCargando: estaCargandoAuth, cerrarSesion } = useAuth()

  // Estados para datos del dashboard
  const [plantasUsuario, setPlantasUsuario] = useState<PlantaUsuario[]>([])
  const [estadisticas, setEstadisticas] = useState<DashboardStats | null>(null)
  const [estaCargando, setEstaCargando] = useState(true)
  const [error, setError] = useState<string | null>(null)

  /**
   * Redirigir a login si no está autenticado
   */
  useEffect(() => {
    if (!estaCargandoAuth && !estaAutenticado) {
      router.push('/login')
    }
  }, [estaAutenticado, estaCargandoAuth, router])

  /**
   * Cargar datos del dashboard al montar el componente
   */
  useEffect(() => {
    if (estaAutenticado) {
      cargarDatosDashboard()
    }
  }, [estaAutenticado])

  /**
   * Función para cargar estadísticas y plantas desde el backend
   */
  const cargarDatosDashboard = async () => {
    try {
      setEstaCargando(true)
      setError(null)

      // Cargar estadísticas y plantas del jardín en paralelo
      // Usar Promise.allSettled para que si una falla, las otras continúen
      const [statsResult, plantasJardinResult] = await Promise.allSettled([
        dashboardService.obtenerEstadisticas(),
        plantService.obtenerMisPlantas(),
      ])

      // Procesar resultados
      if (statsResult.status === 'fulfilled') {
        setEstadisticas(statsResult.value)
      } else {
        console.error('Error al cargar estadísticas:', statsResult.reason)
      }

      if (plantasJardinResult.status === 'fulfilled') {
        setPlantasUsuario(plantasJardinResult.value || [])
      } else {
        console.error('Error al cargar plantas del jardín:', plantasJardinResult.reason)
        setPlantasUsuario([])
      }

      // DEBUG: Mostrar estado final
      console.log('🔍 Dashboard cargado:', {
        plantasUsuario: plantasJardinResult.status === 'fulfilled' ? plantasJardinResult.value?.length : 0,
        estadisticas: statsResult.status === 'fulfilled',
      })
    } catch (err) {
      console.error('Error al cargar datos del dashboard:', err)
      setError('Error al cargar tus plantas. Por favor, intenta de nuevo.')
      // Asegurar que los arrays estén inicializados aunque haya error
      setPlantasUsuario([])
    } finally {
      setEstaCargando(false)
    }
  }

  /**
   * Toggle favorita para una planta
   * Actualiza el estado local optimísticamente sin recargar todo
   */
  const toggleFavorita = async (plantaId: number, esFavorita: boolean) => {
    try {
      // Actualización optimista del estado local
      setPlantasUsuario(plantas => 
        plantas.map(p => 
          p.id === plantaId 
            ? { ...p, es_favorita: !esFavorita } 
            : p
        )
      )

      // Actualizar en el backend
      await plantService.actualizarPlanta(plantaId, {
        es_favorita: !esFavorita
      })
    } catch (err) {
      console.error('❌ Error al actualizar favorita:', err)
      // Revertir el cambio optimista en caso de error
      setPlantasUsuario(plantas => 
        plantas.map(p => 
          p.id === plantaId 
            ? { ...p, es_favorita: esFavorita } 
            : p
        )
      )
      alert('Error al actualizar la planta como favorita')
    }
  }

  /**
   * Toggle regada hoy para una planta
   * Actualiza el estado local optimísticamente sin recargar todo
   */
  const toggleRegadaHoy = async (plantaId: number, fueRegadaHoy: boolean) => {
    try {
      // Actualización optimista del estado local
      setPlantasUsuario(plantas => 
        plantas.map(p => 
          p.id === plantaId 
            ? { ...p, fue_regada_hoy: !fueRegadaHoy } 
            : p
        )
      )

      // Actualizar en el backend
      await plantService.actualizarPlanta(plantaId, {
        fue_regada_hoy: !fueRegadaHoy
      })
    } catch (err) {
      console.error('❌ Error al actualizar regada hoy:', err)
      // Revertir el cambio optimista en caso de error
      setPlantasUsuario(plantas => 
        plantas.map(p => 
          p.id === plantaId 
            ? { ...p, fue_regada_hoy: fueRegadaHoy } 
            : p
        )
      )
      alert('Error al marcar la planta como regada')
    }
  }

  // Mostrar loading mientras se verifica la autenticación
  if (estaCargandoAuth) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <Leaf className="h-12 w-12 text-primary animate-pulse mx-auto mb-4" />
          <p className="text-muted-foreground">Cargando...</p>
        </div>
      </div>
    )
  }

  // No mostrar nada si no está autenticado (se está redirigiendo)
  if (!estaAutenticado || !usuario) {
    return null
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-card">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">Mi Jardín</h1>
            <p className="text-sm text-muted-foreground">Bienvenido, {usuario?.nombre}</p>
          </div>
          <div className="flex gap-2">
            <Button asChild>
              <Link href="/identificar">
                <Camera className="w-5 h-5 mr-2" />
                Identificar Planta
              </Link>
            </Button>
            <Button 
              variant="ghost" 
              size="icon"
              onClick={async () => {
                await cerrarSesion()
              }}
              title="Cerrar sesión"
            >
              <LogOut className="w-5 h-5" />
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Loading State */}
        {estaCargando && (
          <div className="flex flex-col items-center justify-center py-12">
            <Leaf className="h-12 w-12 text-primary animate-pulse mb-4" />
            <p className="text-muted-foreground">Cargando tu jardín...</p>
          </div>
        )}

        {/* Error State */}
        {error && !estaCargando && (
          <Card className="border-destructive">
            <CardHeader>
              <CardTitle className="text-destructive">Error</CardTitle>
              <CardDescription>{error}</CardDescription>
            </CardHeader>
            <CardContent>
              <Button onClick={cargarDatosDashboard}>Reintentar</Button>
            </CardContent>
          </Card>
        )}

        {/* Dashboard Content */}
        {!estaCargando && !error && (
          <>
            {/* Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
              <Card>
                <CardHeader className="pb-3">
                  <CardDescription>Total de Plantas</CardDescription>
                  <CardTitle className="text-3xl">
                    {estadisticas?.total_plantas || 0}
                  </CardTitle>
                </CardHeader>
              </Card>

              <Card>
                <CardHeader className="pb-3">
                  <CardDescription>Necesitan Riego Hoy</CardDescription>
                  <CardTitle className="text-3xl text-blue-600">
                    {estadisticas?.plantas_necesitan_riego || 0}
                  </CardTitle>
                </CardHeader>
              </Card>

              <Card>
                <CardHeader className="pb-3">
                  <CardDescription>Plantas Saludables</CardDescription>
                  <CardTitle className="text-3xl text-green-600">
                    {estadisticas?.plantas_saludables || 0}
                  </CardTitle>
                </CardHeader>
              </Card>

              <Card>
                <CardHeader className="pb-3">
                  <CardDescription>Necesitan Atención</CardDescription>
                  <CardTitle className="text-3xl text-orange-600">
                    {estadisticas?.plantas_necesitan_atencion || 0}
                  </CardTitle>
                </CardHeader>
              </Card>
            </div>

            {/* Plants Grid */}
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-semibold">Tus Plantas</h2>
              <Button variant="outline" asChild>
                <Link href="/identificar">
                  <Plus className="w-4 h-4 mr-2" />
                  Agregar Planta
                </Link>
              </Button>
            </div>
          </>
        )}

        {/* Empty State - Mostrar SIEMPRE que no haya plantas */}
        {!estaCargando && !error && (
          <>
            {(plantasUsuario?.length ?? 0) === 0 && (
              <div className="py-16 px-8 border-2 border-dashed border-green-200 bg-gradient-to-br from-green-50/50 to-emerald-50/50 rounded-lg">
                <div className="text-center space-y-6 max-w-3xl mx-auto">
              {/* Icono más grande con efecto visual */}
              <div className="relative mx-auto w-24 h-24">
                <Leaf className="h-24 w-24 text-green-600/80 mx-auto animate-pulse" />
                <div className="absolute inset-0 bg-green-500/10 rounded-full blur-xl" />
              </div>
              
              <div className="space-y-3">
                <h3 className="text-2xl font-bold text-gray-900">
                  ¡Tu jardín está esperando! 🌱
                </h3>
                <p className="text-lg text-gray-600 max-w-md mx-auto leading-relaxed">
                  Comienza identificando tu primera planta con ayuda de la IA. 
                  Toma una foto y descubre todo sobre ella en segundos.
                </p>
              </div>

              {/* Botón principal más llamativo */}
              <div className="pt-2">
                <Button 
                  asChild 
                  size="lg" 
                  className="bg-green-600 hover:bg-green-700 text-white shadow-lg hover:shadow-xl transition-all"
                >
                  <Link href="/identificar">
                    <Camera className="w-5 h-5 mr-2" />
                    Identificar Mi Primera Planta
                  </Link>
                </Button>
              </div>

              {/* Características motivacionales */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-6">
                <div className="flex flex-col items-center space-y-2">
                  <div className="bg-green-100 p-3 rounded-full">
                    <Camera className="w-5 h-5 text-green-600" />
                  </div>
                  <p className="text-sm font-medium text-gray-700">Identificación rápida</p>
                  <p className="text-xs text-gray-500">Con IA avanzada</p>
                </div>
                <div className="flex flex-col items-center space-y-2">
                  <div className="bg-blue-100 p-3 rounded-full">
                    <Droplets className="w-5 h-5 text-blue-600" />
                  </div>
                  <p className="text-sm font-medium text-gray-700">Recordatorios de riego</p>
                  <p className="text-xs text-gray-500">Nunca olvides regarlas</p>
                </div>
                <div className="flex flex-col items-center space-y-2">
                  <div className="bg-yellow-100 p-3 rounded-full">
                    <Sun className="w-5 h-5 text-yellow-600" />
                  </div>
                  <p className="text-sm font-medium text-gray-700">Consejos de cuidado</p>
                  <p className="text-xs text-gray-500">Personalizados para ti</p>
                </div>
              </div>

              {/* Texto motivacional adicional */}
              <p className="text-sm text-gray-500 pt-4">
                Únete a miles de jardineros que cuidan mejor sus plantas con Asistente Plantitas 🌿
              </p>
            </div>
          </div>
            )}
          </>
        )}

        {/* Dashboard Content - Continuar con plantas */}
        {!estaCargando && !error && (
          <>

            {/* Sección: Plantas agregadas desde identificaciones (T-023) */}
            {plantasUsuario && plantasUsuario.length > 0 && (
              <div className="mb-12">
                <div className="flex items-center justify-between mb-6">
                  <div>
                    <h2 className="text-2xl font-semibold">Mis Plantas Identificadas</h2>
                    <p className="text-muted-foreground mt-1">
                      Plantas agregadas desde identificaciones
                    </p>
                  </div>
                  <Badge variant="secondary" className="text-lg px-4 py-1">
                    {plantasUsuario.length}
                  </Badge>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {plantasUsuario
                    .sort((a, b) => {
                      // Ordenar: favoritas primero, luego por fecha de creación
                      if (a.es_favorita && !b.es_favorita) return -1
                      if (!a.es_favorita && b.es_favorita) return 1
                      return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
                    })
                    .map((planta) => {
                    // Determinar qué imágenes mostrar
                    const imagenesParaMostrar = (() => {
                      if (planta.imagenes_identificacion && planta.imagenes_identificacion.length > 0) {
                        return planta.imagenes_identificacion
                      }
                      if (planta.imagen_principal) {
                        return [planta.imagen_principal]
                      }
                      return []
                    })()

                    return (
                    <Card
                      key={planta.id}
                      className="overflow-hidden hover:shadow-lg transition-shadow relative"
                    >
                      <div className="relative">
                        {/* Carousel de imágenes de la planta */}
                        <PlantImageCarousel 
                          images={imagenesParaMostrar}
                          plantName={planta.nombre_personalizado || 'Planta'}
                        />

                        {/* Badge de estado de salud - superior izquierda */}
                        <div className="absolute top-3 left-3 z-10">
                          <Badge
                            variant={estadoSaludToBadgeVariant(planta.estado_salud)}
                            className="shadow-lg"
                          >
                            {estadoSaludToLabel(planta.estado_salud)}
                          </Badge>
                        </div>

                        {/* Botón de favorita (corazón) en esquina superior derecha */}
                        <div className="absolute top-3 right-3 z-20">
                          <Button
                            size="icon"
                            variant="ghost"
                            className={cn(
                              "h-10 w-10 rounded-full shadow-lg backdrop-blur-sm transition-all duration-300 ease-in-out",
                              "hover:shadow-2xl hover:scale-125 hover:-translate-y-0.5 hover:z-30",
                              planta.es_favorita
                                ? "bg-red-100/95 hover:bg-red-200 ring-2 ring-red-200"
                                : "bg-white/95 hover:bg-red-100 hover:ring-2 hover:ring-red-300"
                            )}
                            onClick={(e) => {
                              e.preventDefault()
                              e.stopPropagation()
                              toggleFavorita(planta.id, planta.es_favorita)
                            }}
                          >
                            <Heart 
                              className={cn(
                                "w-5 h-5 transition-all duration-300",
                                planta.es_favorita 
                                  ? "fill-red-500 text-red-500 drop-shadow-sm" 
                                  : "text-gray-400 hover:text-red-500 hover:scale-110 hover:drop-shadow-md"
                              )} 
                            />
                          </Button>
                        </div>

                        {/* Badge de regada hoy si está marcado - inferior izquierda */}
                        {planta.fue_regada_hoy && (
                          <div className="absolute bottom-3 left-3 z-10">
                            <Badge 
                              variant="secondary" 
                              className="bg-blue-500 text-white shadow-lg"
                            >
                              <Droplets className="w-3 h-3 mr-1" />
                              Regada Hoy
                            </Badge>
                          </div>
                        )}
                      </div>

                      {/* Información de la planta */}
                      <CardHeader>
                        <CardTitle className="text-xl">
                          {planta.nombre_personalizado || 'Sin nombre'}
                        </CardTitle>
                        {planta.especie && (
                          <CardDescription className="space-y-1">
                            <p className="italic text-primary font-medium">
                              {planta.especie.nombre_cientifico}
                            </p>
                            {planta.especie.nombre_comun && (
                              <p className="text-sm">
                                {planta.especie.nombre_comun}
                              </p>
                            )}
                            {planta.especie.familia && (
                              <p className="text-xs text-muted-foreground">
                                Familia: {planta.especie.familia}
                              </p>
                            )}
                          </CardDescription>
                        )}
                      </CardHeader>

                      <CardContent className="space-y-3">
                        {/* Botón para marcar como regada hoy */}
                        <div className="flex justify-start">
                          <Button
                            variant="outline"
                            size="icon"
                            className={cn(
                              "h-10 w-10 rounded-full transition-all duration-200",
                              planta.fue_regada_hoy 
                                ? "bg-blue-50 border-blue-500 hover:bg-blue-100 hover:border-blue-600 hover:shadow-lg hover:scale-110" 
                                : "hover:bg-blue-50 hover:border-blue-400 hover:shadow-lg hover:scale-110"
                            )}
                            onClick={(e) => {
                              e.preventDefault()
                              toggleRegadaHoy(planta.id, planta.fue_regada_hoy)
                            }}
                          >
                            <Droplets 
                              className={cn(
                                "w-5 h-5 transition-all duration-200", 
                                planta.fue_regada_hoy ? "text-blue-500" : "text-gray-400 hover:text-blue-500"
                              )} 
                            />
                          </Button>
                        </div>

                        {/* Ubicación */}
                        {planta.ubicacion && (
                          <div className="flex items-center gap-2 text-sm">
                            <Sun className="w-4 h-4 text-yellow-600" />
                            <span className="text-muted-foreground">
                              {planta.ubicacion}
                            </span>
                          </div>
                        )}

                        {/* Frecuencia de riego */}
                        {planta.frecuencia_riego_dias && (
                          <div className="flex items-center gap-2 text-sm">
                            <Droplets className="w-4 h-4 text-blue-600" />
                            <span className="text-muted-foreground">
                              Riego cada {planta.frecuencia_riego_dias} días
                            </span>
                          </div>
                        )}

                        {/* Notas */}
                        {planta.notas && !planta.notas.includes('Identificación confirmada con') && (
                          <div className="text-sm text-muted-foreground italic pt-2 border-t">
                            {planta.notas}
                          </div>
                        )}

                        {/* Botón ver detalles */}
                        <Button
                          variant="outline"
                          className="w-full mt-4 bg-transparent"
                          asChild
                        >
                          <Link href={`/plant/${planta.id}`}>
                            Ver Detalles
                          </Link>
                        </Button>
                      </CardContent>
                    </Card>
                  )
                  })}
                </div>
              </div>
            )}
          </>
        )}
      </main>
    </div>
  )
}
