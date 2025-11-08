/**
 * Página de detalle de planta individual
 * 
 * Muestra información completa de una planta con pestañas:
 * - Care: Schedules de riego y fertilización
 * - Environment: Condiciones ambientales (luz, temperatura, humedad)
 * - Activity: Historial de actividades y cuidados
 * - Photos: Galería de fotos de la planta
 * 
 * @author GitHub Copilot
 * @date 2025-11-07
 * @sprint Sprint 3
 */

"use client"

import { useEffect, useState } from "react"
import { useRouter, useParams } from "next/navigation"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Progress } from "@/components/ui/progress"
import { Separator } from "@/components/ui/separator"
import { Input } from "@/components/ui/input"
import {
  ArrowLeft,
  Droplets,
  Sun,
  Thermometer,
  Calendar,
  Camera,
  Edit,
  Trash2,
  AlertCircle,
  CheckCircle2,
  Sprout,
  Loader2,
  MapPin,
  Leaf,
  X,
  Check,
} from "lucide-react"
import { useAuth } from "@/hooks/useAuth"
import dashboardService from "@/lib/dashboard.service"
import type { Planta } from "@/models/dashboard.types"
import { estadoSaludToBadgeVariant, estadoSaludToLabel } from "@/models/dashboard.types"
import { Carousel, CarouselContent, CarouselItem, type CarouselApi } from "@/components/ui/carousel"
import { cn } from "@/lib/utils"

/**
 * Calcula días desde una fecha
 */
function calcularDiasDesde(fecha: string | null | undefined): number {
  if (!fecha) return 0
  const fechaObj = new Date(fecha)
  const hoy = new Date()
  const diferencia = hoy.getTime() - fechaObj.getTime()
  return Math.floor(diferencia / (1000 * 60 * 60 * 24))
}

/**
 * Calcula días hasta una fecha
 */
function calcularDiasHasta(fecha: string | null | undefined): number {
  if (!fecha) return 0
  const fechaObj = new Date(fecha)
  const hoy = new Date()
  const diferencia = fechaObj.getTime() - hoy.getTime()
  return Math.floor(diferencia / (1000 * 60 * 60 * 24))
}

/**
 * Formatea fecha relativa (hace X días / en X días)
 */
function formatearFechaRelativa(fecha: string | null | undefined, esProxima: boolean = false): string {
  if (!fecha) return "No registrado"
  
  const dias = esProxima ? calcularDiasHasta(fecha) : calcularDiasDesde(fecha)
  
  if (dias === 0) return esProxima ? "Hoy" : "Hoy"
  if (dias === 1) return esProxima ? "Mañana" : "Ayer"
  if (dias < 0 && esProxima) return `Hace ${Math.abs(dias)} días`
  if (dias > 0 && !esProxima) return `Hace ${dias} días`
  if (dias > 0 && esProxima) return `En ${dias} días`
  
  return fecha
}

/**
 * Componente para el carousel de imágenes de la planta
 */
function PlantImageCarousel({ 
  images, 
  plantName 
}: Readonly<{ 
  images: Array<{id?: number; url_imagen?: string; url_blob?: string; tipo_organo?: string; organ?: string; nombre_archivo?: string; fecha_subida?: string; tamano_bytes?: number}>
  plantName: string 
}>) {
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

  const imagesToShow = Array.isArray(images) ? images : (images ? [images] : [])

  if (imagesToShow.length === 0) {
    return (
      <div className="aspect-square bg-muted flex items-center justify-center rounded-t-lg">
        <Leaf className="w-16 h-16 text-muted-foreground" />
      </div>
    )
  }

  if (imagesToShow.length === 1) {
    const imagen = imagesToShow[0]
    return (
      <div className="aspect-square relative">
        <img
          src={imagen.url_imagen || "/placeholder.svg"}
          alt={plantName}
          className="w-full h-full object-cover rounded-t-lg"
        />
        {imagen.organ && imagen.organ !== 'sin_especificar' && (
          <div className="absolute bottom-3 left-3">
            <Badge variant="secondary" className="bg-black/50 text-white backdrop-blur-sm">
              {imagen.organ}
            </Badge>
          </div>
        )}
      </div>
    )
  }

  return (
    <div className="relative">
      <Carousel setApi={setApi} className="w-full">
        <CarouselContent>
          {imagesToShow.map((imagen, index) => (
            <CarouselItem key={imagen.id || index}>
              <div className="aspect-square relative">
                <img
                  src={imagen.url_imagen || "/placeholder.svg"}
                  alt={`${plantName} - foto ${index + 1}`}
                  className="w-full h-full object-cover"
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

export default function PlantDetailPage() {
  const { estaAutenticado, estaCargando: authLoading } = useAuth()
  const router = useRouter()
  const params = useParams()
  const plantId = params?.id as string

  const [planta, setPlanta] = useState<Planta | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isWatering, setIsWatering] = useState(false)
  const [isEditingName, setIsEditingName] = useState(false)
  const [nombreEditado, setNombreEditado] = useState("")
  const [isSavingName, setIsSavingName] = useState(false)

  // Redirigir si no está autenticado
  useEffect(() => {
    if (!authLoading && !estaAutenticado) {
      router.push('/login')
    }
  }, [estaAutenticado, authLoading, router])

  // Cargar datos de la planta
  useEffect(() => {
    if (!estaAutenticado || !plantId) return

    const cargarPlanta = async () => {
      try {
        setIsLoading(true)
        setError(null)
        
        // Obtener planta específica por ID
        const plantaData = await dashboardService.obtenerPlanta(parseInt(plantId))
        setPlanta(plantaData)
      } catch (err) {
        console.error("Error al cargar planta:", err)
        setError(err instanceof Error ? err.message : "Error al cargar la planta")
      } finally {
        setIsLoading(false)
      }
    }

    cargarPlanta()
  }, [estaAutenticado, plantId])

  // Handler para marcar como regada
  const handleMarcarComoRegada = async () => {
    if (!planta) return

    try {
      setIsWatering(true)
      await dashboardService.registrarRiego(planta.id)
      
      // Recargar datos de la planta
      const plantaActualizada = await dashboardService.obtenerPlanta(planta.id)
      setPlanta(plantaActualizada)
    } catch (err) {
      console.error("Error al registrar riego:", err)
      alert("Error al registrar el riego")
    } finally {
      setIsWatering(false)
    }
  }

  // Handler para iniciar edición del nombre
  const handleStartEditName = () => {
    setNombreEditado(planta?.nombre_personal || "")
    setIsEditingName(true)
  }

  // Handler para cancelar edición del nombre
  const handleCancelEditName = () => {
    setIsEditingName(false)
    setNombreEditado("")
  }

  // Handler para guardar el nuevo nombre
  const handleSaveName = async () => {
    if (!planta || !nombreEditado.trim()) return

    try {
      setIsSavingName(true)
      await dashboardService.actualizarPlanta(planta.id, {
        nombre_personal: nombreEditado.trim()
      })
      
      // Recargar datos de la planta
      const plantaActualizada = await dashboardService.obtenerPlanta(planta.id)
      setPlanta(plantaActualizada)
      setIsEditingName(false)
      setNombreEditado("")
    } catch (err) {
      console.error("Error al actualizar nombre:", err)
      alert("Error al actualizar el nombre de la planta")
    } finally {
      setIsSavingName(false)
    }
  }

  // Calcular score de salud
  const calcularHealthScore = (planta: Planta): number => {
    let score = 100
    
    // Penalizar por estado de salud
    if (planta.estado_salud === 'necesita_atencion') score -= 20
    if (planta.estado_salud === 'critica') score -= 40
    
    // Penalizar si necesita riego
    if (planta.necesita_riego) score -= 15
    
    return Math.max(0, score)
  }

  if (authLoading || isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center space-y-4">
          <Loader2 className="w-8 h-8 animate-spin mx-auto text-primary" />
          <p className="text-muted-foreground">Cargando planta...</p>
        </div>
      </div>
    )
  }

  if (error || !planta) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center space-y-4">
          <AlertCircle className="w-16 h-16 mx-auto text-destructive" />
          <h2 className="text-2xl font-bold">Error</h2>
          <p className="text-muted-foreground">{error || "Planta no encontrada"}</p>
          <Button asChild>
            <Link href="/dashboard">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Volver al Dashboard
            </Link>
          </Button>
        </div>
      </div>
    )
  }

  const healthScore = calcularHealthScore(planta)

  // Determinar imágenes a mostrar (por ahora solo mostramos placeholder si hay URL)
  const imagenesParaMostrar: Array<{id?: number; url_imagen?: string; url_blob?: string}> = planta.imagen_principal_url 
    ? [{ url_imagen: planta.imagen_principal_url }]
    : []

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-card sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <Button variant="ghost" asChild>
              <Link href="/dashboard">
                <ArrowLeft className="w-5 h-5 mr-2" />
                Volver al Jardín
              </Link>
            </Button>
            <div className="flex gap-2">
              <Button variant="outline" size="icon">
                <Edit className="w-5 h-5" />
              </Button>
              <Button variant="outline" size="icon">
                <Trash2 className="w-5 h-5" />
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Left Column - Plant Image & Basic Info */}
          <div className="lg:col-span-1 space-y-6">
            <Card>
              <CardContent className="p-0">
                <PlantImageCarousel 
                  images={imagenesParaMostrar}
                  plantName={planta.nombre_personal || 'Planta'}
                />
                
                <div className="p-6 space-y-4">
                  <div>
                    {isEditingName ? (
                      <div className="space-y-3">
                        <Input
                          type="text"
                          value={nombreEditado}
                          onChange={(e) => setNombreEditado(e.target.value)}
                          onKeyDown={(e) => {
                            if (e.key === 'Enter') handleSaveName()
                            if (e.key === 'Escape') handleCancelEditName()
                          }}
                          placeholder="Nombre de la planta"
                          className="text-2xl font-bold"
                          autoFocus
                          disabled={isSavingName}
                        />
                        <div className="flex gap-2">
                          <Button 
                            size="sm" 
                            onClick={handleSaveName}
                            disabled={isSavingName || !nombreEditado.trim()}
                          >
                            {isSavingName ? (
                              <>
                                <Loader2 className="w-3 h-3 mr-1 animate-spin" />
                                Guardando...
                              </>
                            ) : (
                              <>
                                <Check className="w-3 h-3 mr-1" />
                                Guardar
                              </>
                            )}
                          </Button>
                          <Button 
                            size="sm" 
                            variant="outline"
                            onClick={handleCancelEditName}
                            disabled={isSavingName}
                          >
                            <X className="w-3 h-3 mr-1" />
                            Cancelar
                          </Button>
                        </div>
                      </div>
                    ) : (
                      <div className="flex items-start justify-between gap-2">
                        <div className="flex-1">
                          <h1 className="text-3xl font-bold mb-1">
                            {planta.nombre_personal || 'Mi Planta'}
                          </h1>
                          <p className="text-muted-foreground italic text-sm">
                            ID: {planta.id}
                          </p>
                        </div>
                        <Button
                          size="icon"
                          variant="ghost"
                          onClick={handleStartEditName}
                          className="shrink-0"
                        >
                          <Edit className="w-4 h-4" />
                        </Button>
                      </div>
                    )}
                  </div>

                  {/* Health Badge */}
                  <div>
                    <Badge
                      variant={estadoSaludToBadgeVariant(planta.estado_salud)}
                      className="text-sm"
                    >
                      {estadoSaludToLabel(planta.estado_salud)}
                    </Badge>
                  </div>

                  <Separator />

                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">Health Score</span>
                      <span className="text-sm font-semibold">{healthScore}%</span>
                    </div>
                    <Progress value={healthScore} className="h-2" />
                  </div>

                  <Separator />

                  <div className="space-y-2 text-sm">
                    <div className="flex items-center gap-2">
                      <Calendar className="w-4 h-4 text-muted-foreground" />
                      <span className="text-muted-foreground">
                        Agregada {new Date(planta.created_at).toLocaleDateString('es-ES', {
                          year: 'numeric',
                          month: 'long',
                          day: 'numeric'
                        })}
                      </span>
                    </div>
                    {planta.ubicacion && (
                      <div className="flex items-center gap-2">
                        <MapPin className="w-4 h-4 text-muted-foreground" />
                        <span className="text-muted-foreground">{planta.ubicacion}</span>
                      </div>
                    )}
                    {planta.luz_actual && (
                      <div className="flex items-center gap-2">
                        <Sun className="w-4 h-4 text-muted-foreground" />
                        <span className="text-muted-foreground">
                          Luz {planta.luz_actual}
                        </span>
                      </div>
                    )}
                  </div>

                  <Button className="w-full">
                    <Camera className="w-4 h-4 mr-2" />
                    Verificar Salud
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Notes Card */}
            {planta.notas && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Notas</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground leading-relaxed">{planta.notas}</p>
                </CardContent>
              </Card>
            )}
          </div>

          {/* Right Column - Detailed Information */}
          <div className="lg:col-span-2">
            <Tabs defaultValue="care" className="w-full">
              <TabsList className="grid w-full grid-cols-4">
                <TabsTrigger value="care">Care</TabsTrigger>
                <TabsTrigger value="environment">Environment</TabsTrigger>
                <TabsTrigger value="activity">Activity</TabsTrigger>
                <TabsTrigger value="photos">Photos</TabsTrigger>
              </TabsList>

              {/* Care Tab */}
              <TabsContent value="care" className="space-y-6 mt-6">
                {/* Watering Schedule */}
                <Card>
                  <CardHeader>
                    <div className="flex items-center gap-2">
                      <Droplets className="w-5 h-5 text-primary" />
                      <CardTitle>Watering Schedule</CardTitle>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <p className="text-sm text-muted-foreground mb-1">Last Watered</p>
                        <p className="font-semibold">
                          {formatearFechaRelativa(planta.fecha_ultimo_riego)}
                        </p>
                      </div>
                      <div>
                        <p className="text-sm text-muted-foreground mb-1">Next Watering</p>
                        <p className={cn(
                          "font-semibold",
                          planta.necesita_riego ? "text-destructive" : "text-accent"
                        )}>
                          {planta.necesita_riego 
                            ? "Necesita riego ahora" 
                            : formatearFechaRelativa(planta.proxima_riego, true)
                          }
                        </p>
                      </div>
                    </div>
                    {planta.frecuencia_riego_dias && (
                      <div>
                        <p className="text-sm text-muted-foreground mb-1">Frequency</p>
                        <p className="font-semibold">Every {planta.frecuencia_riego_dias} days</p>
                      </div>
                    )}
                    <Button 
                      className="w-full"
                      onClick={handleMarcarComoRegada}
                      disabled={isWatering}
                    >
                      {isWatering ? (
                        <>
                          <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                          Registrando...
                        </>
                      ) : (
                        <>
                          <Droplets className="w-4 h-4 mr-2" />
                          Mark as Watered
                        </>
                      )}
                    </Button>
                  </CardContent>
                </Card>

                {/* Fertilizing Schedule */}
                <Card>
                  <CardHeader>
                    <div className="flex items-center gap-2">
                      <Sprout className="w-5 h-5 text-primary" />
                      <CardTitle>Fertilizing Schedule</CardTitle>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <p className="text-sm text-muted-foreground mb-1">Last Fertilized</p>
                        <p className="font-semibold">2 weeks ago</p>
                      </div>
                      <div>
                        <p className="text-sm text-muted-foreground mb-1">Next Fertilizing</p>
                        <p className="font-semibold">in 2 weeks</p>
                      </div>
                    </div>
                    <Button variant="outline" className="w-full bg-transparent">
                      <Sprout className="w-4 h-4 mr-2" />
                      Mark as Fertilized
                    </Button>
                  </CardContent>
                </Card>

                {/* Care Tips */}
                <Card>
                  <CardHeader>
                    <CardTitle>Care Tips</CardTitle>
                    <CardDescription>
                      Personalized recommendations for your plant
                    </CardDescription>
                  </CardHeader>
                    <CardContent>
                      <ul className="space-y-3">
                        <li className="flex items-start gap-3">
                          <CheckCircle2 className="w-5 h-5 text-primary mt-0.5 flex-shrink-0" />
                          <span className="text-sm leading-relaxed">
                            Water when top 2 inches of soil are dry
                          </span>
                        </li>
                        <li className="flex items-start gap-3">
                          <CheckCircle2 className="w-5 h-5 text-primary mt-0.5 flex-shrink-0" />
                          <span className="text-sm leading-relaxed">
                            Wipe leaves monthly to remove dust
                          </span>
                        </li>
                        <li className="flex items-start gap-3">
                          <CheckCircle2 className="w-5 h-5 text-primary mt-0.5 flex-shrink-0" />
                          <span className="text-sm leading-relaxed">
                            Rotate plant weekly for even growth
                          </span>
                        </li>
                        <li className="flex items-start gap-3">
                          <CheckCircle2 className="w-5 h-5 text-primary mt-0.5 flex-shrink-0" />
                          <span className="text-sm leading-relaxed">
                            Provide support for climbing growth
                          </span>
                        </li>
                      </ul>
                    </CardContent>
                  </Card>
              </TabsContent>

              {/* Environment Tab */}
              <TabsContent value="environment" className="space-y-6 mt-6">
                {/* Light Requirements */}
                <Card>
                  <CardHeader>
                    <div className="flex items-center gap-2">
                      <Sun className="w-5 h-5 text-accent" />
                      <CardTitle>Light Requirements</CardTitle>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {planta.luz_actual && (
                      <>
                        <div>
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-sm text-muted-foreground">Current Light Level</span>
                            <span className="text-sm font-semibold">
                              {planta.luz_actual === 'directa' ? '100%' : 
                               planta.luz_actual === 'alta' ? '75%' : 
                               planta.luz_actual === 'media' ? '50%' : '25%'}
                            </span>
                          </div>
                          <Progress 
                            value={planta.luz_actual === 'directa' ? 100 : 
                                   planta.luz_actual === 'alta' ? 75 : 
                                   planta.luz_actual === 'media' ? 50 : 25} 
                            className="h-2" 
                          />
                        </div>
                        <div>
                          <p className="text-sm text-muted-foreground mb-1">Current Level</p>
                          <p className="font-semibold capitalize">{planta.luz_actual} light</p>
                        </div>
                      </>
                    )}
                    <div className="bg-muted p-4 rounded-lg">
                      <p className="text-sm leading-relaxed">
                        Most plants thrive with bright indirect light. Keep near a window
                        with filtered sunlight for optimal growth.
                      </p>
                    </div>
                  </CardContent>
                </Card>

                {/* Temperature */}
                <Card>
                  <CardHeader>
                    <div className="flex items-center gap-2">
                      <Thermometer className="w-5 h-5 text-accent" />
                      <CardTitle>Temperature</CardTitle>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div>
                      <p className="text-sm text-muted-foreground mb-1">Ideal Range</p>
                      <p className="font-semibold">65-85°F (18-29°C)</p>
                    </div>
                    <div className="bg-muted p-4 rounded-lg mt-4">
                      <p className="text-sm leading-relaxed">
                        Maintain consistent temperatures and avoid placing near heating vents 
                        or air conditioning units.
                      </p>
                    </div>
                  </CardContent>
                </Card>

                {/* Humidity */}
                <Card>
                  <CardHeader>
                    <div className="flex items-center gap-2">
                      <Droplets className="w-5 h-5 text-primary" />
                      <CardTitle>Humidity</CardTitle>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <p className="text-sm text-muted-foreground mb-1">Recommended Range</p>
                      <p className="font-semibold">60-80%</p>
                    </div>
                    <div className="bg-muted p-4 rounded-lg">
                      <p className="text-sm leading-relaxed">
                        Mist leaves regularly or use a humidifier to maintain optimal 
                        humidity levels for tropical plants.
                      </p>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              {/* Activity Tab */}
              <TabsContent value="activity" className="space-y-6 mt-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Recent Activity</CardTitle>
                    <CardDescription>Track your plant care history</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {planta.fecha_ultimo_riego && (
                        <div className="flex items-start gap-4">
                          <div className="bg-primary/10 p-2 rounded-full">
                            <Droplets className="w-4 h-4 text-primary" />
                          </div>
                          <div className="flex-1">
                            <p className="font-semibold text-sm">Watered</p>
                            <p className="text-sm text-muted-foreground">
                              {formatearFechaRelativa(planta.fecha_ultimo_riego)}
                            </p>
                          </div>
                        </div>
                      )}
                      <div className="flex items-start gap-4">
                        <div className="bg-primary/10 p-2 rounded-full">
                          <Sprout className="w-4 h-4 text-primary" />
                        </div>
                        <div className="flex-1">
                          <p className="font-semibold text-sm">Plant added</p>
                          <p className="text-sm text-muted-foreground">
                            {formatearFechaRelativa(planta.created_at)}
                          </p>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Add Activity</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <Button 
                      variant="outline" 
                      className="w-full justify-start bg-transparent"
                      onClick={handleMarcarComoRegada}
                      disabled={isWatering}
                    >
                      <Droplets className="w-4 h-4 mr-2" />
                      Log Watering
                    </Button>
                    <Button variant="outline" className="w-full justify-start bg-transparent">
                      <Sprout className="w-4 h-4 mr-2" />
                      Log Fertilizing
                    </Button>
                    <Button variant="outline" className="w-full justify-start bg-transparent">
                      <Camera className="w-4 h-4 mr-2" />
                      Add Photo
                    </Button>
                    <Button variant="outline" className="w-full justify-start bg-transparent">
                      <AlertCircle className="w-4 h-4 mr-2" />
                      Report Issue
                    </Button>
                  </CardContent>
                </Card>
              </TabsContent>

              {/* Photos Tab */}
              <TabsContent value="photos" className="space-y-6 mt-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Photo Gallery</CardTitle>
                    <CardDescription>Track your plant's growth over time</CardDescription>
                  </CardHeader>
                  <CardContent>
                    {imagenesParaMostrar.length > 0 ? (
                      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                        {imagenesParaMostrar.map((imagen, index) => (
                          <div key={imagen.id || index} className="space-y-2">
                            <div className="aspect-square relative rounded-lg overflow-hidden">
                              <img
                                src={imagen.url_imagen || "/placeholder.svg"}
                                alt={`Foto ${index + 1}`}
                                className="w-full h-full object-cover hover:scale-105 transition-transform"
                              />
                            </div>
                            <div>
                              <p className="text-sm font-semibold">
                                Foto {index + 1}
                              </p>
                              <p className="text-xs text-muted-foreground">
                                {planta.updated_at ? new Date(planta.updated_at).toLocaleDateString('es-ES') : ''}
                              </p>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="text-center py-8">
                        <Camera className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
                        <p className="text-muted-foreground mb-4">No hay fotos todavía</p>
                      </div>
                    )}
                    <Button variant="outline" className="w-full mt-6 bg-transparent">
                      <Camera className="w-4 h-4 mr-2" />
                      Add New Photo
                    </Button>
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          </div>
        </div>
      </main>
    </div>
  )
}
