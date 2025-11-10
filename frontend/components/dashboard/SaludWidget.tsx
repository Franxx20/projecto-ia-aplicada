/**
 * SaludWidget.tsx - Widget de salud para Dashboard
 * 
 * Componente que muestra un resumen de la salud de todas las plantas del usuario.
 * Incluye estadísticas agregadas, alertas críticas, y últimos análisis.
 * 
 * Features:
 * - Resumen de salud de todas las plantas
 * - Alertas de plantas críticas (banner rojo)
 * - Últimos 5 análisis realizados
 * - Estadísticas: total plantas, % saludables, necesitan atención, críticas
 * - Navegación rápida a plant detail
 * - Loading y error states
 * - Empty state si no hay análisis
 * 
 * @author Equipo Frontend
 * @date Noviembre 2025
 * @sprint Feature - Health Check AI Extensions
 */

'use client'

import React, { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import {
  Activity,
  AlertTriangle,
  ChevronRight,
  RefreshCw,
  Leaf,
  AlertCircle
} from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import saludService from '@/lib/salud.service'
import dashboardService from '@/lib/dashboard.service'
import type { HistorialSaludItem } from '@/models/salud'
import {
  ESTADO_TEXTOS,
  formatearConfianza,
  formatearDiasDesde,
  obtenerEmojiEstado
} from '@/models/salud'

/**
 * Estadísticas agregadas de salud del jardín
 */
interface SaludJardinStats {
  total_plantas: number
  total_con_analisis: number
  saludables: number  // excelente + saludable
  necesitan_atencion: number  // necesita_atencion
  criticas: number  // enfermedad + plaga + critica
  porcentaje_saludables: number
  promedio_confianza: number
  tendencia_general?: 'mejorando' | 'estable' | 'empeorando'
}

/**
 * Planta con alerta crítica
 */
interface PlantaCritica {
  planta_id: number
  analisis_id: number
  nombre: string
  estado: string
  dias_desde_analisis: number
}

/**
 * Props del componente SaludWidget
 */
interface SaludWidgetProps {
  /** Clase CSS adicional */
  readonly className?: string
}

/**
 * Widget de salud para dashboard
 */
export function SaludWidget({ className }: SaludWidgetProps) {
  const router = useRouter()

  // Estado
  const [estadisticas, setEstadisticas] = useState<SaludJardinStats | null>(null)
  const [ultimosAnalisis, setUltimosAnalisis] = useState<HistorialSaludItem[]>([])
  const [plantasCriticas, setPlantasCriticas] = useState<PlantaCritica[]>([])
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState<string | null>(null)

  /**
   * Carga datos de salud de todas las plantas
   */
  const cargarDatosSalud = async () => {
    try {
      setCargando(true)
      setError(null)

      // Obtener todas las plantas del usuario
      const plantas = await dashboardService.obtenerPlantas(100, 0)

      if (!plantas.plantas || plantas.plantas.length === 0) {
        // No hay plantas, mostrar empty state
        setEstadisticas({
          total_plantas: 0,
          total_con_analisis: 0,
          saludables: 0,
          necesitan_atencion: 0,
          criticas: 0,
          porcentaje_saludables: 0,
          promedio_confianza: 0
        })
        setUltimosAnalisis([])
        setPlantasCriticas([])
        return
      }

      // Obtener estadísticas de salud de cada planta
      const statsPromises = plantas.plantas.map(async (planta) => {
        try {
          const stats = await saludService.obtenerEstadisticas(planta.id)
          return { planta, stats }
        } catch {
          // Si no hay análisis para esta planta, retornar null
          return { planta, stats: null }
        }
      })

      const plantasConStats = await Promise.all(statsPromises)

      // Calcular estadísticas agregadas
      const plantasConAnalisis = plantasConStats.filter(p => p.stats !== null)
      
      let saludables = 0
      let necesitanAtencion = 0
      let criticas = 0
      let sumaConfianza = 0
      const analisisTodos: HistorialSaludItem[] = []
      const criticas_list: PlantaCritica[] = []

      plantasConAnalisis.forEach(({ planta, stats }) => {
        if (!stats?.ultimo_estado) return

        // Normalizar estado para comparación case-insensitive
        const estadoNormalizado = stats.ultimo_estado.toLowerCase()

        // Clasificar por estado
        if (estadoNormalizado === 'excelente' || estadoNormalizado === 'saludable' || estadoNormalizado === 'buena') {
          saludables++
        } else if (estadoNormalizado === 'necesita_atencion') {
          necesitanAtencion++
        } else {
          // enfermedad, plaga, critica
          criticas++
          
          // Agregar a lista de críticas
          criticas_list.push({
            planta_id: planta.id,
            analisis_id: stats.ultimo_analisis?.id || 0,
            nombre: planta.nombre_personal || 'Planta',
            estado: ESTADO_TEXTOS[stats.ultimo_estado] || stats.ultimo_estado,
            dias_desde_analisis: stats.dias_desde_ultimo_analisis || 0
          })
        }

        // Sumar confianza
        if (stats.confianza_promedio !== undefined) {
          sumaConfianza += stats.confianza_promedio
        }
      })

      // Obtener últimos 5 análisis de todas las plantas
      const historiales = await Promise.all(
        plantasConAnalisis.slice(0, 10).map(async ({ planta }) => {
          try {
            const historial = await saludService.obtenerHistorial({
              planta_id: planta.id,
              limite: 2,
              offset: 0
            })
            return historial.analisis.map(a => ({
              ...a,
              // Agregar nombre de la planta para mostrar
              nombre_planta: planta.nombre_personal || 'Planta'
            } as HistorialSaludItem & { nombre_planta: string }))
          } catch {
            return []
          }
        })
      )

      const todosAnalisis = historiales
        .flat()
        .sort((a, b) => 
          new Date(b.fecha_analisis).getTime() - new Date(a.fecha_analisis).getTime()
        )
        .slice(0, 5)

      setUltimosAnalisis(todosAnalisis)
      setPlantasCriticas(criticas_list)

      const porcentajeSaludables = plantasConAnalisis.length > 0
        ? (saludables / plantasConAnalisis.length) * 100
        : 0

      const promedioConfianza = plantasConAnalisis.length > 0
        ? sumaConfianza / plantasConAnalisis.length
        : 0

      setEstadisticas({
        total_plantas: plantas.plantas.length,
        total_con_analisis: plantasConAnalisis.length,
        saludables,
        necesitan_atencion: necesitanAtencion,
        criticas: criticas,
        porcentaje_saludables: porcentajeSaludables,
        promedio_confianza: promedioConfianza
      })

    } catch (err) {
      console.error('Error al cargar datos de salud:', err)
      setError('Error al cargar datos de salud')
    } finally {
      setCargando(false)
    }
  }

  // Cargar datos al montar
  useEffect(() => {
    cargarDatosSalud()
  }, [])

  /**
   * Navega a la página de detalle de un análisis de salud
   */
  const navegarAAnalisis = (analisisId: number) => {
    router.push(`/salud/analisis/${analisisId}`)
  }

  /**
   * Navega a la página de detalle de una planta
   */
  const navegarAPlanta = (plantaId: number) => {
    router.push(`/plant/${plantaId}`)
  }

  if (cargando) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="w-5 h-5 text-green-600" />
            Salud del Jardín
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600" />
          </div>
        </CardContent>
      </Card>
    )
  }

  if (error) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="w-5 h-5 text-green-600" />
            Salud del Jardín
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-start gap-3">
              <AlertCircle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
              <div className="flex-1">
                <h4 className="font-semibold text-sm text-red-900">Error</h4>
                <p className="text-sm text-red-700 mt-1">{error}</p>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={cargarDatosSalud}
                  className="mt-3"
                >
                  <RefreshCw className="w-4 h-4 mr-2" />
                  Reintentar
                </Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    )
  }

  // Empty state - no hay plantas o no hay análisis
  if (!estadisticas || estadisticas.total_plantas === 0) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="w-5 h-5 text-green-600" />
            Salud del Jardín
          </CardTitle>
          <CardDescription>
            Monitorea la salud de tus plantas
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <Leaf className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="font-semibold text-gray-900 mb-2">
              No hay plantas registradas
            </h3>
            <p className="text-sm text-muted-foreground mb-4">
              Agrega plantas a tu jardín para comenzar a monitorear su salud
            </p>
            <Button onClick={() => router.push('/identificar')}>
              Agregar Primera Planta
            </Button>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (estadisticas.total_con_analisis === 0) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="w-5 h-5 text-green-600" />
            Salud del Jardín
          </CardTitle>
          <CardDescription>
            Monitorea la salud de tus {estadisticas.total_plantas} plantas
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <Activity className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="font-semibold text-gray-900 mb-2">
              No hay análisis de salud
            </h3>
            <p className="text-sm text-muted-foreground mb-4">
              Realiza el primer análisis de salud para comenzar a monitorear
            </p>
            <Button onClick={() => router.push(`/plant/${estadisticas.total_plantas}`)}>
              Analizar Plantas
            </Button>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className={className}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Activity className="w-5 h-5 text-green-600" />
              Salud del Jardín
            </CardTitle>
            <CardDescription>
              {estadisticas.total_con_analisis} de {estadisticas.total_plantas} plantas analizadas
            </CardDescription>
          </div>
          <Button
            variant="ghost"
            size="icon"
            onClick={cargarDatosSalud}
            title="Actualizar"
          >
            <RefreshCw className="w-4 h-4" />
          </Button>
        </div>
      </CardHeader>

      <CardContent className="space-y-6">
        {/* Alertas Críticas */}
        {plantasCriticas.length > 0 && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-start gap-3">
              <AlertTriangle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
              <div className="flex-1">
                <h4 className="font-semibold text-sm text-red-900 mb-2">
                  ⚠️ {plantasCriticas.length} planta(s) crítica(s)
                </h4>
                <div className="space-y-1">
                  {plantasCriticas.map((planta) => (
                    <button
                      key={planta.planta_id}
                      onClick={() => navegarAAnalisis(planta.analisis_id)}
                      className="flex items-center justify-between w-full text-left p-2 rounded hover:bg-red-100 transition-colors"
                    >
                      <div>
                        <p className="text-sm font-medium text-red-900">{planta.nombre}</p>
                        <p className="text-xs text-red-700">{planta.estado}</p>
                      </div>
                      <ChevronRight className="w-4 h-4 text-red-600" />
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Estadísticas Resumidas */}
        <div className="grid grid-cols-3 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">
              {estadisticas.saludables}
            </div>
            <div className="text-xs text-muted-foreground mt-1">
              Saludables
            </div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-yellow-600">
              {estadisticas.necesitan_atencion}
            </div>
            <div className="text-xs text-muted-foreground mt-1">
              Atención
            </div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-red-600">
              {estadisticas.criticas}
            </div>
            <div className="text-xs text-muted-foreground mt-1">
              Críticas
            </div>
          </div>
        </div>

        {/* Porcentaje de Salud */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium">Salud General</span>
            <span className="text-sm text-muted-foreground">
              {estadisticas.porcentaje_saludables.toFixed(0)}%
            </span>
          </div>
          <Progress 
            value={estadisticas.porcentaje_saludables} 
            className="h-2"
          />
        </div>

        {/* Confianza Promedio */}
        <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
          <div className="flex items-center gap-2">
            <Activity className="w-4 h-4 text-blue-600" />
            <span className="text-sm font-medium">Confianza Promedio</span>
          </div>
          <Badge variant="outline">
            {estadisticas.promedio_confianza.toFixed(1)}%
          </Badge>
        </div>

        {/* Últimos Análisis */}
        {ultimosAnalisis.length > 0 && (
          <div>
            <h4 className="text-sm font-semibold mb-3">Análisis Recientes</h4>
            <div className="space-y-2">
              {ultimosAnalisis.map((analisis) => {
                const item = analisis as HistorialSaludItem & { nombre_planta?: string }
                return (
                  <button
                    key={`${analisis.planta_id}-${analisis.id}`}
                    onClick={() => navegarAAnalisis(analisis.id)}
                    className="flex items-center justify-between w-full p-3 rounded-lg border hover:bg-muted transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <span className="text-xl">
                        {obtenerEmojiEstado(analisis.estado)}
                      </span>
                      <div className="text-left">
                        <p className="text-sm font-medium">
                          {item.nombre_planta || 'Planta'}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          {formatearDiasDesde(analisis.fecha_analisis)}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge 
                        variant="outline" 
                        className="text-xs"
                      >
                        {formatearConfianza(analisis.confianza)}
                      </Badge>
                      <ChevronRight className="w-4 h-4 text-muted-foreground" />
                    </div>
                  </button>
                )
              })}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

export default SaludWidget
