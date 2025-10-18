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
import { Camera, Plus, Droplets, Sun, AlertCircle, Leaf } from "lucide-react"
import { useAuth } from "@/hooks/useAuth"
import dashboardService from "@/lib/dashboard.service"
import type { Planta, DashboardStats } from "@/models/dashboard.types"
import {
  estadoSaludToBadgeVariant,
  estadoSaludToLabel,
  nivelLuzToLabel,
  formatearFechaRelativa,
} from "@/models/dashboard.types"

export default function DashboardPage() {
  const router = useRouter()
  const { usuario, estaAutenticado, estaCargando: estaCargandoAuth } = useAuth()

  // Estados para datos del dashboard
  const [plantas, setPlantas] = useState<Planta[]>([])
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

      // Cargar estadísticas y plantas en paralelo
      const [stats, { plantas: plantasData }] = await Promise.all([
        dashboardService.obtenerEstadisticas(),
        dashboardService.obtenerPlantas(100, 0, true),
      ])

      setEstadisticas(stats)
      setPlantas(plantasData)
    } catch (err) {
      console.error('Error al cargar datos del dashboard:', err)
      setError('Error al cargar tus plantas. Por favor, intenta de nuevo.')
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
          <h1 className="text-2xl font-bold">Mi Jardín</h1>
          <div className="flex gap-2">
            <Button variant="outline" size="icon" asChild>
              <Link href="/identificar">
                <Camera className="w-5 h-5" />
              </Link>
            </Button>
            <Button asChild>
              <Link href="/identificar">
                <Camera className="w-5 h-5 mr-2" />
                Identificar Planta
              </Link>
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

            {/* Empty State */}
            {plantas.length === 0 && (
              <Card className="py-12">
                <CardContent className="text-center space-y-4">
                  <Leaf className="h-16 w-16 text-muted-foreground mx-auto" />
                  <div>
                    <h3 className="text-xl font-semibold mb-2">
                      Aún no tienes plantas
                    </h3>
                    <p className="text-muted-foreground mb-4">
                      Comienza identificando tu primera planta con la cámara
                    </p>
                    <Button asChild>
                      <Link href="/identificar">
                        <Camera className="w-4 h-4 mr-2" />
                        Identificar Primera Planta
                      </Link>
                    </Button>
                  </div>
                </CardContent>
              </Card>
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
