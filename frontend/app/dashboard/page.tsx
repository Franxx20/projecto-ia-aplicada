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
import { Plus, Droplets, Sun, AlertCircle, Leaf, LogOut, Camera } from "lucide-react"
import { useAuth } from "@/hooks/useAuth"
import dashboardService from "@/lib/dashboard.service"
import plantService from "@/lib/plant.service"
import type { Planta, DashboardStats } from "@/models/dashboard.types"
import type { PlantaUsuario } from "@/models/plant.types"
import {
  estadoSaludToBadgeVariant,
  estadoSaludToLabel,
  nivelLuzToLabel,
  formatearFechaRelativa,
} from "@/models/dashboard.types"

export default function DashboardPage() {
  const router = useRouter()
  const { usuario, estaAutenticado, estaCargando: estaCargandoAuth, cerrarSesion } = useAuth()

  // Estados para datos del dashboard
  const [plantas, setPlantas] = useState<Planta[]>([])
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

      // Cargar estadísticas, plantas del dashboard y plantas del jardín en paralelo
      // Usar Promise.allSettled para que si una falla, las otras continúen
      const [statsResult, plantasResult, plantasJardinResult] = await Promise.allSettled([
        dashboardService.obtenerEstadisticas(),
        dashboardService.obtenerPlantas(100, 0, true),
        plantService.obtenerMisPlantas(),
      ])

      // Procesar resultados
      if (statsResult.status === 'fulfilled') {
        setEstadisticas(statsResult.value)
      } else {
        console.error('Error al cargar estadísticas:', statsResult.reason)
      }

      if (plantasResult.status === 'fulfilled') {
        setPlantas(plantasResult.value.plantas || [])
      } else {
        console.error('Error al cargar plantas del dashboard:', plantasResult.reason)
        setPlantas([])
      }

      if (plantasJardinResult.status === 'fulfilled') {
        setPlantasUsuario(plantasJardinResult.value || [])
      } else {
        console.error('Error al cargar plantas del jardín:', plantasJardinResult.reason)
        setPlantasUsuario([])
      }

      // DEBUG: Mostrar estado final
      console.log('🔍 Dashboard cargado:', {
        plantas: plantasResult.status === 'fulfilled' ? plantasResult.value.plantas?.length : 0,
        plantasUsuario: plantasJardinResult.status === 'fulfilled' ? plantasJardinResult.value?.length : 0,
        estadisticas: statsResult.status === 'fulfilled',
      })
    } catch (err) {
      console.error('Error al cargar datos del dashboard:', err)
      setError('Error al cargar tus plantas. Por favor, intenta de nuevo.')
      // Asegurar que los arrays estén inicializados aunque haya error
      setPlantas([])
      setPlantasUsuario([])
    } finally {
      setEstaCargando(false)
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
            {((plantas?.length ?? 0) === 0 && (plantasUsuario?.length ?? 0) === 0) && (
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
                  {plantasUsuario.map((planta) => (
                    <Card
                      key={planta.id}
                      className="overflow-hidden hover:shadow-lg transition-shadow"
                    >
                      {/* Imagen de la planta */}
                      <div className="aspect-square relative bg-muted">
                        {planta.imagen_principal?.url_blob ? (
                          <img
                            src={planta.imagen_principal.url_blob}
                            alt={planta.nombre_personalizado || 'Planta'}
                            className="w-full h-full object-cover"
                          />
                        ) : (
                          <div className="w-full h-full flex items-center justify-center">
                            <Leaf className="h-24 w-24 text-muted-foreground" />
                          </div>
                        )}
                        
                        {/* Badge con origen */}
                        <div className="absolute top-3 right-3">
                          <Badge variant="default" className="bg-green-600">
                            Identificada
                          </Badge>
                        </div>
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
                        {/* Estado de salud */}
                        <div className="flex items-center gap-2 text-sm">
                          <Badge
                            variant={estadoSaludToBadgeVariant(planta.estado_salud as any)}
                          >
                            {estadoSaludToLabel(planta.estado_salud as any)}
                          </Badge>
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
                        {planta.notas && (
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
                  ))}
                </div>
              </div>
            )}

            {/* Plants Grid */}
            {plantas.length > 0 && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {plantas.map((planta) => (
                  <Card
                    key={planta.id}
                    className="overflow-hidden hover:shadow-lg transition-shadow"
                  >
                    {/* Imagen de la planta */}
                    <div className="aspect-square relative bg-muted">
                      {planta.imagen_principal_id ? (
                        <img
                          src={`/api/imagenes/${planta.imagen_principal_id}`}
                          alt={planta.nombre_personal}
                          className="w-full h-full object-cover"
                        />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center">
                          <Leaf className="h-24 w-24 text-muted-foreground" />
                        </div>
                      )}
                      
                      {/* Badge de estado de salud */}
                      <div className="absolute top-3 right-3">
                        <Badge
                          variant={estadoSaludToBadgeVariant(planta.estado_salud)}
                        >
                          {estadoSaludToLabel(planta.estado_salud)}
                        </Badge>
                      </div>
                    </div>

                    {/* Información de la planta */}
                    <CardHeader>
                      <CardTitle className="text-xl">
                        {planta.nombre_personal}
                      </CardTitle>
                      {planta.especie_id && (
                        <CardDescription className="italic">
                          Especie ID: {planta.especie_id}
                        </CardDescription>
                      )}
                    </CardHeader>

                    <CardContent className="space-y-3">
                      {/* Último riego */}
                      <div className="flex items-center gap-2 text-sm">
                        <Droplets className="w-4 h-4 text-blue-600" />
                        <span className="text-muted-foreground">
                          Último riego:{" "}
                          {formatearFechaRelativa(planta.fecha_ultimo_riego, false)}
                        </span>
                      </div>

                      {/* Próximo riego */}
                      {planta.necesita_riego && (
                        <div className="flex items-center gap-2 text-sm">
                          <AlertCircle className="w-4 h-4 text-orange-600" />
                          <span className="text-orange-600 font-medium">
                            ¡Necesita riego hoy!
                          </span>
                        </div>
                      )}

                      {!planta.necesita_riego && planta.proxima_riego && (
                        <div className="flex items-center gap-2 text-sm">
                          <AlertCircle className="w-4 h-4 text-muted-foreground" />
                          <span className="text-muted-foreground">
                            Próximo riego:{" "}
                            {formatearFechaRelativa(planta.proxima_riego, true)}
                          </span>
                        </div>
                      )}

                      {/* Nivel de luz */}
                      <div className="flex items-center gap-2 text-sm">
                        <Sun className="w-4 h-4 text-yellow-600" />
                        <span className="text-muted-foreground">
                          {nivelLuzToLabel(planta.luz_actual)}
                        </span>
                      </div>

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
                ))}
              </div>
            )}
          </>
        )}
      </main>
    </div>
  )
}
