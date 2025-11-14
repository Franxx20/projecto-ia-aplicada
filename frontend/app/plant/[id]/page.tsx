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
  Activity,
  Stethoscope,
} from "lucide-react"
import { useAuth } from "@/hooks/useAuth"
import dashboardService from "@/lib/dashboard.service"
import saludService from "@/lib/salud.service"
import type { Planta } from "@/models/dashboard.types"
import type { HistorialSaludItem } from "@/models/salud"
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
            <CarouselItem key={`carousel-${imagen.id}-${index}`}>
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
  const [isFertilizing, setIsFertilizing] = useState(false)
  const [isEditingName, setIsEditingName] = useState(false)
  const [nombreEditado, setNombreEditado] = useState("")
  const [isSavingName, setIsSavingName] = useState(false)
  const [isCheckingHealth, setIsCheckingHealth] = useState(false)
  const [analisisRecientes, setAnalisisRecientes] = useState<HistorialSaludItem[]>([])
  const [cargandoAnalisis, setCargandoAnalisis] = useState(false)
  const [ultimoAnalisisDetalle, setUltimoAnalisisDetalle] = useState<any>(null)
  const [imagenesPlanta, setImagenesPlanta] = useState<any[]>([])
  const [cargandoImagenes, setCargandoImagenes] = useState(false)
  const [estaAnalizando, setEstaAnalizando] = useState(false)

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

  // Cargar análisis recientes de la planta
  useEffect(() => {
    if (!estaAutenticado || !plantId || !planta) return

    const cargarAnalisis = async () => {
      try {
        setCargandoAnalisis(true)
        const historial = await saludService.obtenerHistorial({
          planta_id: parseInt(plantId),
          limite: 3,
          offset: 0
        })
        setAnalisisRecientes(historial.analisis)
        
        // Cargar detalle completo del último análisis si existe
        if (historial.analisis && historial.analisis.length > 0) {
          const detalle = await saludService.obtenerAnalisis(historial.analisis[0].id)
          setUltimoAnalisisDetalle(detalle)
        }
      } catch (err) {
        console.error("Error al cargar análisis recientes:", err)
        // No mostrar error al usuario, solo falla silenciosamente
      } finally {
        setCargandoAnalisis(false)
      }
    }

    cargarAnalisis()
  }, [estaAutenticado, plantId, planta])

  // Cargar imágenes de la planta
  useEffect(() => {
    if (!estaAutenticado || !plantId || !planta) return

    const cargarImagenes = async () => {
      try {
        setCargandoImagenes(true)
        const imagenes = await dashboardService.obtenerImagenesPlanta(parseInt(plantId))
        setImagenesPlanta(imagenes)
      } catch (err) {
        console.error("Error al cargar imágenes de la planta:", err)
        // No mostrar error al usuario, solo falla silenciosamente
      } finally {
        setCargandoImagenes(false)
      }
    }

    cargarImagenes()
  }, [estaAutenticado, plantId, planta])

  // Polling para detectar cuando termina el análisis en background
  useEffect(() => {
    if (!planta || !estaAutenticado) return
    
    // Detectar si está en estado "analizando"
    const estadoActual = planta.estado_salud?.toLowerCase()
    const enAnalisis = estadoActual === 'analizando'
    setEstaAnalizando(enAnalisis)
    
    if (!enAnalisis) return // Solo hacer polling si está analizando
    
    console.log('🔍 Planta en análisis, iniciando polling...')
    
    // Polling cada 5 segundos para detectar cambio de estado
    const intervalo = setInterval(async () => {
      try {
        const plantaActualizada = await dashboardService.obtenerPlanta(parseInt(plantId!))
        const nuevoEstado = plantaActualizada.estado_salud?.toLowerCase()
        
        if (nuevoEstado && nuevoEstado !== 'analizando') {
          console.log('✅ Análisis completado, actualizando planta...')
          setPlanta(plantaActualizada)
          setEstaAnalizando(false)
          
          // Recargar también los análisis recientes
          try {
            const historial = await saludService.obtenerHistorial({
              planta_id: parseInt(plantId!),
              limite: 3,
              offset: 0
            })
            setAnalisisRecientes(historial.analisis)
            
            if (historial.analisis && historial.analisis.length > 0) {
              const detalle = await saludService.obtenerAnalisis(historial.analisis[0].id)
              setUltimoAnalisisDetalle(detalle)
            }
          } catch (err) {
            console.error('Error recargando análisis:', err)
          }
          
          clearInterval(intervalo)
        }
      } catch (error) {
        console.error('Error en polling de planta:', error)
      }
    }, 5000)
    
    return () => clearInterval(intervalo)
  }, [planta, estaAutenticado, plantId])

  // Handler para marcar como regada
  const handleMarcarComoRegada = async () => {
    if (!planta) return

    try {
      setIsWatering(true)
      // Registrar riego y usar directamente la respuesta actualizada
      const plantaActualizada = await dashboardService.registrarRiego(planta.id)
      setPlanta(plantaActualizada)
      
      console.log('✅ Planta actualizada después de regar:', {
        fecha_ultimo_riego: plantaActualizada.fecha_ultimo_riego,
        proximo_riego: plantaActualizada.proximo_riego,
        necesita_riego: plantaActualizada.necesita_riego
      })
      
      // Recargar la planta para actualizar todas las vistas
      const plantaRefrescada = await dashboardService.obtenerPlanta(planta.id)
      setPlanta(plantaRefrescada)
    } catch (err) {
      console.error("Error al registrar riego:", err)
      alert("Error al registrar el riego")
    } finally {
      setIsWatering(false)
    }
  }

  // Handler para marcar como fertilizada
  const handleMarcarComoFertilizada = async () => {
    if (!planta) return

    try {
      setIsFertilizing(true)
      // Registrar fertilización y usar directamente la respuesta actualizada
      const plantaActualizada = await dashboardService.registrarFertilizacion(planta.id)
      setPlanta(plantaActualizada)
      
      console.log('✅ Planta actualizada después de fertilizar:', {
        fecha_ultima_fertilizacion: plantaActualizada.fecha_ultima_fertilizacion,
        proxima_fertilizacion: plantaActualizada.proxima_fertilizacion
      })
      
      // Recargar la planta para actualizar todas las vistas
      const plantaRefrescada = await dashboardService.obtenerPlanta(planta.id)
      setPlanta(plantaRefrescada)
    } catch (err) {
      console.error("Error al registrar fertilización:", err)
      alert("Error al registrar la fertilización")
    } finally {
      setIsFertilizing(false)
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

  // Handler para verificar salud
  const handleVerificarSalud = async () => {
    if (!planta) return

    try {
      setIsCheckingHealth(true)
      
      // Redirigir a la página de salud con el ID de la planta
      // Esto permitirá al usuario subir una imagen y hacer el análisis
      router.push(`/salud?planta_id=${planta.id}`)
    } catch (err) {
      console.error("Error al verificar salud:", err)
      alert("Error al iniciar verificación de salud")
    } finally {
      setIsCheckingHealth(false)
    }
  }

  // Calcular score de salud
  const calcularHealthScore = (planta: Planta): number => {
    // Normalizar estado a minúsculas para comparación
    const estadoNormalizado = planta.estado_salud.toLowerCase()
    
    let baseScore = 100
    
    // Asignar score base según estado de salud
    switch (estadoNormalizado) {
      case 'excelente':
        baseScore = 100
        break
      case 'saludable':
      case 'buena':
        baseScore = 85
        break
      case 'necesita_atencion':
        baseScore = 50
        break
      case 'critica':
      case 'enfermedad':
      case 'plaga':
        baseScore = 20
        break
      default:
        baseScore = 70
    }
    
    // Penalizar si necesita riego (hasta -15 puntos)
    if (planta.necesita_riego) {
      baseScore = Math.max(0, baseScore - 15)
    }
    
    return Math.max(0, Math.min(100, baseScore))
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

  // Determinar imágenes a mostrar (sin duplicados)
  const imagenesParaMostrar = imagenesPlanta.length > 0 
    ? (() => {
        // Crear un Map para eliminar duplicados por ID
        const imagenesUnicas = new Map()
        
        imagenesPlanta.forEach(img => {
          if (img.id && !imagenesUnicas.has(img.id)) {
            imagenesUnicas.set(img.id, {
              id: img.id,
              url_imagen: img.url_blob, // url_blob ya incluye el SAS token
              organ: img.organ,
              nombre_archivo: img.nombre_archivo,
              fecha_subida: img.created_at,
              tamano_bytes: img.tamano_bytes
            })
          }
        })
        
        return Array.from(imagenesUnicas.values())
      })()
    : planta.imagen_principal_url 
      ? [{ 
          id: `principal-${planta.id}`, // Clave única para imagen principal
          url_imagen: planta.imagen_principal_url,
          organ: undefined,
          nombre_archivo: undefined,
          fecha_subida: undefined,
          tamano_bytes: undefined
        }]
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
                      <span className="text-sm text-muted-foreground">Puntuación de Salud</span>
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

                  <Button 
                    className="w-full"
                    onClick={handleVerificarSalud}
                    disabled={isCheckingHealth || estaAnalizando}
                  >
                    {isCheckingHealth ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        Verificando...
                      </>
                    ) : estaAnalizando ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        Analizando en segundo plano...
                      </>
                    ) : (
                      <>
                        <Camera className="w-4 h-4 mr-2" />
                        Verificar Salud
                      </>
                    )}
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

            {/* Análisis Recientes Card */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Activity className="w-5 h-5 text-primary" />
                    <CardTitle className="text-lg">Análisis Recientes</CardTitle>
                  </div>
                  {analisisRecientes.length > 0 && (
                    <Link href="/salud/historial">
                      <Button variant="ghost" size="sm">
                        Ver todos
                      </Button>
                    </Link>
                  )}
                </div>
                <CardDescription>Últimos diagnósticos de salud</CardDescription>
              </CardHeader>
              <CardContent>
                {cargandoAnalisis ? (
                  <div className="flex items-center justify-center py-8">
                    <Loader2 className="w-6 h-6 animate-spin text-muted-foreground" />
                  </div>
                ) : analisisRecientes.length > 0 ? (
                  <div className="space-y-3">
                    {analisisRecientes.map((analisis) => (
                      <Link 
                        key={analisis.id}
                        href={`/salud/analisis/${analisis.id}`}
                        className="block"
                      >
                        <Card className="hover:shadow-md transition-shadow cursor-pointer border">
                          <CardContent className="p-4">
                            <div className="flex items-start gap-3">
                              {/* Estado Icon */}
                              <div className={cn(
                                "p-2 rounded-full",
                                analisis.estado === 'excelente' || analisis.estado === 'saludable' 
                                  ? "bg-green-100" 
                                  : analisis.estado === 'necesita_atencion'
                                  ? "bg-yellow-100"
                                  : "bg-red-100"
                              )}>
                                {analisis.estado === 'excelente' || analisis.estado === 'saludable' ? (
                                  <CheckCircle2 className="w-4 h-4 text-green-600" />
                                ) : analisis.estado === 'necesita_atencion' ? (
                                  <AlertCircle className="w-4 h-4 text-yellow-600" />
                                ) : (
                                  <AlertCircle className="w-4 h-4 text-red-600" />
                                )}
                              </div>

                              {/* Contenido */}
                              <div className="flex-1 min-w-0">
                                <div className="flex items-center justify-between mb-1">
                                  <Badge variant={estadoSaludToBadgeVariant(analisis.estado)}>
                                    {estadoSaludToLabel(analisis.estado)}
                                  </Badge>
                                  <span className="text-xs text-muted-foreground">
                                    {formatearFechaRelativa(analisis.fecha_analisis)}
                                  </span>
                                </div>
                                
                                <p className="text-sm font-medium text-foreground line-clamp-2 mb-1">
                                  {analisis.resumen_diagnostico}
                                </p>

                                <div className="flex items-center gap-3 text-xs text-muted-foreground">
                                  <div className="flex items-center gap-1">
                                    <Leaf className="w-3 h-3" />
                                    <span>Confianza: {Math.round(analisis.confianza)}%</span>
                                  </div>
                                  {analisis.con_imagen && (
                                    <div className="flex items-center gap-1">
                                      <Camera className="w-3 h-3" />
                                      <span>Con imagen</span>
                                    </div>
                                  )}
                                </div>
                              </div>
                            </div>
                          </CardContent>
                        </Card>
                      </Link>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    {estaAnalizando ? (
                      <>
                        <Loader2 className="w-12 h-12 mx-auto text-primary mb-3 animate-spin" />
                        <p className="text-sm font-medium text-foreground mb-1">
                          Análisis en progreso
                        </p>
                        <p className="text-xs text-muted-foreground">
                          El primer análisis de salud se está realizando en segundo plano...
                        </p>
                      </>
                    ) : (
                      <>
                        <Activity className="w-12 h-12 mx-auto text-muted-foreground mb-3" />
                        <p className="text-sm text-muted-foreground mb-4">
                          No hay análisis registrados
                        </p>
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={handleVerificarSalud}
                        >
                          <Camera className="w-4 h-4 mr-2" />
                          Realizar primer análisis
                        </Button>
                      </>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Right Column - Detailed Information */}
          <div className="lg:col-span-2">
            <Tabs defaultValue="care" className="w-full">
              <TabsList className="grid w-full grid-cols-4">
                <TabsTrigger value="care">Cuidados</TabsTrigger>
                <TabsTrigger value="environment">Ambiente</TabsTrigger>
                <TabsTrigger value="activity">Actividad</TabsTrigger>
                <TabsTrigger value="photos">Fotos</TabsTrigger>
              </TabsList>

              {/* Care Tab */}
              <TabsContent value="care" className="space-y-6 mt-6">
                {/* Watering Schedule */}
                <Card>
                  <CardHeader>
                    <div className="flex items-center gap-2">
                      <Droplets className="w-5 h-5 text-primary" />
                      <CardTitle>Calendario de Riego</CardTitle>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <p className="text-sm text-muted-foreground mb-1">Último Riego</p>
                        <p className="font-semibold">
                          {formatearFechaRelativa(planta.fecha_ultimo_riego)}
                        </p>
                      </div>
                      <div>
                        <p className="text-sm text-muted-foreground mb-1">Próximo Riego</p>
                        <p className={cn(
                          "font-semibold",
                          planta.necesita_riego ? "text-destructive" : "text-accent"
                        )}>
                          {planta.necesita_riego 
                            ? "Necesita riego ahora" 
                            : formatearFechaRelativa(planta.proximo_riego, true)
                          }
                        </p>
                      </div>
                    </div>
                    {planta.frecuencia_riego_dias && (
                      <div>
                        <p className="text-sm text-muted-foreground mb-1">Frecuencia</p>
                        <p className="font-semibold">Cada {planta.frecuencia_riego_dias} días</p>
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
                          Marcar como Regada
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
                      <CardTitle>Calendario de Fertilización</CardTitle>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <p className="text-sm text-muted-foreground mb-1">Última Fertilización</p>
                        <p className="font-semibold">
                          {formatearFechaRelativa(planta.fecha_ultima_fertilizacion, false)}
                        </p>
                      </div>
                      <div>
                        <p className="text-sm text-muted-foreground mb-1">Próxima Fertilización</p>
                        <p className="font-semibold">
                          {formatearFechaRelativa(planta.proxima_fertilizacion, true)}
                        </p>
                      </div>
                    </div>
                    <Button 
                      variant="outline" 
                      className="w-full bg-transparent"
                      onClick={handleMarcarComoFertilizada}
                      disabled={isFertilizing}
                    >
                      {isFertilizing ? (
                        <>
                          <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                          Registrando...
                        </>
                      ) : (
                        <>
                          <Sprout className="w-4 h-4 mr-2" />
                          Marcar como Fertilizada
                        </>
                      )}
                    </Button>
                  </CardContent>
                </Card>

                {/* Care Tips */}
                <Card>
                  <CardHeader>
                    <CardTitle>Consejos de Cuidado</CardTitle>
                    <CardDescription>
                      {ultimoAnalisisDetalle?.recomendaciones?.length > 0
                        ? `Recomendaciones personalizadas basadas en el último análisis (${new Date(ultimoAnalisisDetalle.fecha_analisis).toLocaleDateString('es-ES')})`
                        : "Recomendaciones personalizadas para tu planta"}
                    </CardDescription>
                  </CardHeader>
                    <CardContent>
                      {cargandoAnalisis ? (
                        <div className="space-y-3">
                          {[1, 2, 3].map((i) => (
                            <div key={i} className="flex items-start gap-3">
                              <div className="w-5 h-5 bg-muted rounded-full animate-pulse flex-shrink-0" />
                              <div className="flex-1 space-y-2">
                                <div className="h-4 bg-muted rounded animate-pulse w-3/4" />
                                <div className="h-3 bg-muted rounded animate-pulse w-1/2" />
                              </div>
                            </div>
                          ))}
                        </div>
                      ) : ultimoAnalisisDetalle?.recomendaciones?.length > 0 ? (
                        <ul className="space-y-3">
                          {ultimoAnalisisDetalle.recomendaciones.map((rec: any, index: number) => {
                            // Definir color según prioridad
                            const prioridadColor = rec.prioridad === 'alta' 
                              ? 'text-red-600' 
                              : rec.prioridad === 'media' 
                              ? 'text-yellow-600' 
                              : 'text-green-600'
                            
                            const prioridadBg = rec.prioridad === 'alta'
                              ? 'bg-red-50 border-red-200'
                              : rec.prioridad === 'media'
                              ? 'bg-yellow-50 border-yellow-200'
                              : 'bg-green-50 border-green-200'
                            
                            return (
                              <li 
                                key={index} 
                                className={cn(
                                  "flex items-start gap-3 p-3 rounded-lg border",
                                  prioridadBg
                                )}
                              >
                                <CheckCircle2 className={cn("w-5 h-5 mt-0.5 flex-shrink-0", prioridadColor)} />
                                <div className="flex-1 min-w-0">
                                  <div className="flex items-start justify-between gap-2 mb-1">
                                    <span className="text-sm font-medium">
                                      {rec.tipo}
                                    </span>
                                    {rec.prioridad && (
                                      <span className={cn(
                                        "text-xs px-2 py-0.5 rounded-full font-medium",
                                        rec.prioridad === 'alta' 
                                          ? 'bg-red-100 text-red-700'
                                          : rec.prioridad === 'media'
                                          ? 'bg-yellow-100 text-yellow-700'
                                          : 'bg-green-100 text-green-700'
                                      )}>
                                        {rec.prioridad.charAt(0).toUpperCase() + rec.prioridad.slice(1)}
                                      </span>
                                    )}
                                  </div>
                                  <p className="text-sm leading-relaxed text-muted-foreground">
                                    {rec.descripcion}
                                  </p>
                                  {rec.urgencia_dias && (
                                    <p className="text-xs mt-1 text-muted-foreground italic">
                                      ⏱ Actuar en los próximos {rec.urgencia_dias} días
                                    </p>
                                  )}
                                </div>
                              </li>
                            )
                          })}
                        </ul>
                      ) : (
                        <div className="text-center py-8">
                          <AlertCircle className="w-12 h-12 text-muted-foreground mx-auto mb-3" />
                          <p className="text-sm text-muted-foreground mb-4">
                            No hay análisis de salud disponibles todavía
                          </p>
                          <Button
                            onClick={handleVerificarSalud}
                            className="gap-2"
                            variant="outline"
                          >
                            <Stethoscope className="w-4 h-4" />
                            Realizar Análisis de Salud
                          </Button>
                        </div>
                      )}
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
                      <CardTitle>Requisitos de Luz</CardTitle>
                    </div>
                    {planta.condiciones_ambientales_recomendadas && (
                      <CardDescription>
                        Recomendaciones personalizadas para esta especie
                      </CardDescription>
                    )}
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {planta.luz_actual && (
                      <>
                        <div>
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-sm text-muted-foreground">Nivel de Luz Actual</span>
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
                          <p className="text-sm text-muted-foreground mb-1">Nivel Actual</p>
                          <p className="font-semibold capitalize">Luz {planta.luz_actual}</p>
                        </div>
                      </>
                    )}
                    <div className="bg-muted p-4 rounded-lg">
                      {planta.condiciones_ambientales_recomendadas?.luz_recomendada ? (
                        <>
                          <p className="text-sm leading-relaxed mb-2">
                            {planta.condiciones_ambientales_recomendadas.luz_recomendada}
                          </p>
                          {planta.condiciones_ambientales_recomendadas.luz_horas_diarias && (
                            <p className="text-sm text-muted-foreground">
                              ⏱ {planta.condiciones_ambientales_recomendadas.luz_horas_diarias}
                            </p>
                          )}
                        </>
                      ) : (
                        <p className="text-sm leading-relaxed">
                          La mayoría de las plantas prosperan con luz brillante indirecta. Mantenlas cerca de una ventana
                          con luz solar filtrada para un crecimiento óptimo.
                        </p>
                      )}
                    </div>
                  </CardContent>
                </Card>

                {/* Temperature */}
                <Card>
                  <CardHeader>
                    <div className="flex items-center gap-2">
                      <Thermometer className="w-5 h-5 text-accent" />
                      <CardTitle>Temperatura</CardTitle>
                    </div>
                  </CardHeader>
                  <CardContent>
                    {planta.condiciones_ambientales_recomendadas?.temperatura_ideal ? (
                      <>
                        <div>
                          <p className="text-sm text-muted-foreground mb-1">Rango Ideal</p>
                          <p className="font-semibold">{planta.condiciones_ambientales_recomendadas.temperatura_ideal}</p>
                        </div>
                        {(planta.condiciones_ambientales_recomendadas.temperatura_min || 
                          planta.condiciones_ambientales_recomendadas.temperatura_max) && (
                          <div className="mt-2">
                            <p className="text-sm text-muted-foreground">
                              Rango: {planta.condiciones_ambientales_recomendadas.temperatura_min}°C - {planta.condiciones_ambientales_recomendadas.temperatura_max}°C
                            </p>
                          </div>
                        )}
                      </>
                    ) : (
                      <div>
                        <p className="text-sm text-muted-foreground mb-1">Rango Ideal</p>
                        <p className="font-semibold">18-29°C (65-85°F)</p>
                      </div>
                    )}
                    <div className="bg-muted p-4 rounded-lg mt-4">
                      <p className="text-sm leading-relaxed">
                        Mantén temperaturas consistentes y evita colocar cerca de rejillas de calefacción 
                        o unidades de aire acondicionado.
                      </p>
                    </div>
                  </CardContent>
                </Card>

                {/* Humidity */}
                <Card>
                  <CardHeader>
                    <div className="flex items-center gap-2">
                      <Droplets className="w-5 h-5 text-primary" />
                      <CardTitle>Humedad</CardTitle>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {planta.condiciones_ambientales_recomendadas?.humedad_min && 
                     planta.condiciones_ambientales_recomendadas?.humedad_max ? (
                      <div>
                        <p className="text-sm text-muted-foreground mb-1">Rango Recomendado</p>
                        <p className="font-semibold">
                          {planta.condiciones_ambientales_recomendadas.humedad_min}% - {planta.condiciones_ambientales_recomendadas.humedad_max}%
                        </p>
                      </div>
                    ) : (
                      <div>
                        <p className="text-sm text-muted-foreground mb-1">Rango Recomendado</p>
                        <p className="font-semibold">60-80%</p>
                      </div>
                    )}
                    <div className="bg-muted p-4 rounded-lg">
                      {planta.condiciones_ambientales_recomendadas?.humedad_recomendaciones ? (
                        <p className="text-sm leading-relaxed">
                          {planta.condiciones_ambientales_recomendadas.humedad_recomendaciones}
                        </p>
                      ) : (
                        <p className="text-sm leading-relaxed">
                          Rocía las hojas regularmente o usa un humidificador para mantener 
                          niveles óptimos de humedad para plantas tropicales.
                        </p>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              {/* Activity Tab */}
              <TabsContent value="activity" className="space-y-6 mt-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Actividad Reciente</CardTitle>
                    <CardDescription>Rastrea el historial de cuidado de tu planta</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {/* Construir timeline de actividades ordenadas por fecha */}
                      {(() => {
                        const actividades: Array<{
                          tipo: string;
                          fecha: string;
                          icono: typeof Droplets;
                          texto: string;
                        }> = [];

                        // Agregar riego
                        if (planta.fecha_ultimo_riego) {
                          actividades.push({
                            tipo: 'riego',
                            fecha: planta.fecha_ultimo_riego,
                            icono: Droplets,
                            texto: 'Regada'
                          });
                        }

                        // Agregar fertilización
                        if (planta.fecha_ultima_fertilizacion) {
                          actividades.push({
                            tipo: 'fertilizacion',
                            fecha: planta.fecha_ultima_fertilizacion,
                            icono: Sprout,
                            texto: 'Fertilizada'
                          });
                        }

                        // Agregar análisis de salud
                        if (analisisRecientes && analisisRecientes.length > 0) {
                          analisisRecientes.forEach((analisis) => {
                            actividades.push({
                              tipo: 'analisis_salud',
                              fecha: analisis.fecha_analisis,
                              icono: Stethoscope,
                              texto: `Análisis de salud: ${estadoSaludToLabel(analisis.estado)}`
                            });
                          });
                        }

                        // Agregar creación de planta
                        actividades.push({
                          tipo: 'creacion',
                          fecha: planta.created_at,
                          icono: Leaf,
                          texto: 'Planta agregada'
                        });

                        // Ordenar por fecha (más reciente primero)
                        actividades.sort((a, b) => 
                          new Date(b.fecha).getTime() - new Date(a.fecha).getTime()
                        );

                        // Mostrar solo las 10 más recientes
                        return actividades.slice(0, 10).map((actividad, index) => {
                          const IconoComponente = actividad.icono;
                          return (
                            <div key={`${actividad.tipo}-${index}`} className="flex items-start gap-4">
                              <div className={cn(
                                "p-2 rounded-full",
                                actividad.tipo === 'riego' ? "bg-blue-100" :
                                actividad.tipo === 'fertilizacion' ? "bg-green-100" :
                                actividad.tipo === 'analisis_salud' ? "bg-purple-100" :
                                "bg-primary/10"
                              )}>
                                <IconoComponente className={cn(
                                  "w-4 h-4",
                                  actividad.tipo === 'riego' ? "text-blue-600" :
                                  actividad.tipo === 'fertilizacion' ? "text-green-600" :
                                  actividad.tipo === 'analisis_salud' ? "text-purple-600" :
                                  "text-primary"
                                )} />
                              </div>
                              <div className="flex-1">
                                <p className="font-semibold text-sm">{actividad.texto}</p>
                                <p className="text-sm text-muted-foreground">
                                  {formatearFechaRelativa(actividad.fecha)}
                                </p>
                              </div>
                            </div>
                          );
                        });
                      })()}
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Agregar Actividad</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <Button 
                      variant="outline" 
                      className="w-full justify-start bg-transparent"
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
                          Registrar Riego
                        </>
                      )}
                    </Button>
                    <Button 
                      variant="outline" 
                      className="w-full justify-start bg-transparent"
                      onClick={handleMarcarComoFertilizada}
                      disabled={isFertilizing}
                    >
                      {isFertilizing ? (
                        <>
                          <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                          Registrando...
                        </>
                      ) : (
                        <>
                          <Sprout className="w-4 h-4 mr-2" />
                          Registrar Fertilización
                        </>
                      )}
                    </Button>
                    <Button 
                      variant="outline" 
                      className="w-full justify-start bg-transparent"
                      onClick={handleVerificarSalud}
                      disabled={isCheckingHealth}
                    >
                      {isCheckingHealth ? (
                        <>
                          <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                          Redirigiendo...
                        </>
                      ) : (
                        <>
                          <Stethoscope className="w-4 h-4 mr-2" />
                          Verificar Salud
                        </>
                      )}
                    </Button>
                    <Button variant="outline" className="w-full justify-start bg-transparent">
                      <Camera className="w-4 h-4 mr-2" />
                      Agregar Foto
                    </Button>
                  </CardContent>
                </Card>
              </TabsContent>

              {/* Photos Tab */}
              <TabsContent value="photos" className="space-y-6 mt-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Galería de Fotos</CardTitle>
                    <CardDescription>Rastrea el crecimiento de tu planta a través del tiempo</CardDescription>
                  </CardHeader>
                  <CardContent>
                    {imagenesParaMostrar.length > 0 ? (
                      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                        {imagenesParaMostrar.map((imagen, index) => (
                          <div key={`imagen-${imagen.id}-${index}`} className="space-y-2">
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
                      Agregar Nueva Foto
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
