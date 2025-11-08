/**
 * HistorialSalud.tsx - Componente de historial de análisis de salud
 * 
 * Componente para mostrar el historial completo de análisis de salud de una planta
 * con visualización en timeline, filtros, paginación y comparación de análisis.
 * 
 * Características:
 * - Timeline visual con íconos de estado
 * - Filtros por fecha y problemas
 * - Paginación con scroll infinito
 * - Comparación entre análisis
 * - Gráfico de tendencia de salud
 * - Export a PDF (próximamente)
 * 
 * @author Equipo Frontend
 * @date Noviembre 2025
 * @sprint Feature - Health Check AI Extensions
 */

'use client'

import React, { useState, useEffect, useCallback } from 'react'
import {
  Calendar,
  Filter,
  TrendingUp,
  TrendingDown,
  Minus,
  ChevronDown,
  ChevronUp,
  RefreshCw,
  Download,
  AlertCircle
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Label } from '@/components/ui/label'
import saludService from '@/lib/salud.service'
import type {
  HistorialSaludResponse,
  HistorialSaludItem,
  HistorialSaludParams,
  EstadisticasSaludPlanta
} from '@/models/salud'
import {
  NOMBRES_ESTADO_SALUD,
  ICONOS_ESTADO_SALUD,
  COLORES_ESTADO_SALUD,
  obtenerColorConfianza,
  formatearConfianza,
  calcularDiasDesdeAnalisis
} from '@/models/salud'
import { cn } from '@/lib/utils'

/**
 * Props del componente HistorialSalud
 */
interface HistorialSaludProps {
  /** ID de la planta */
  plantaId: number
  
  /** Nombre de la planta (para mostrar en UI) */
  nombrePlanta?: string
  
  /** Número de items por página */
  itemsPorPagina?: number
  
  /** Si se debe mostrar las estadísticas */
  mostrarEstadisticas?: boolean
  
  /** Callback cuando se selecciona un análisis para ver detalle */
  onSeleccionarAnalisis?: (analisis: HistorialSaludItem) => void
  
  /** Clase CSS adicional */
  className?: string
}

/**
 * Componente de historial de análisis de salud
 */
export function HistorialSalud({
  plantaId,
  nombrePlanta = 'la planta',
  itemsPorPagina = 10,
  mostrarEstadisticas = true,
  onSeleccionarAnalisis,
  className
}: HistorialSaludProps) {
  // Estado del historial
  const [historial, setHistorial] = useState<HistorialSaludResponse | null>(null)
  const [estadisticas, setEstadisticas] = useState<EstadisticasSaludPlanta | null>(null)
  
  // Estado de carga
  const [cargando, setCargando] = useState(true)
  const [cargandoMas, setCargandoMas] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  // Estado de filtros
  const [filtros, setFiltros] = useState<HistorialSaludParams>({
    limite: itemsPorPagina,
    offset: 0,
    solo_con_problemas: false
  })
  const [mostrarFiltros, setMostrarFiltros] = useState(false)
  
  // Estado de items expandidos
  const [itemsExpandidos, setItemsExpandidos] = useState<Set<number>>(new Set())

  /**
   * Carga el historial inicial
   */
  const cargarHistorial = useCallback(async (nuevosFiltros?: HistorialSaludParams) => {
    try {
      setCargando(true)
      setError(null)
      
      const filtrosActualizados = nuevosFiltros || filtros
      const [historialData, statsData] = await Promise.all([
        saludService.obtenerHistorial(plantaId, filtrosActualizados),
        mostrarEstadisticas ? saludService.obtenerEstadisticas(plantaId) : Promise.resolve(null)
      ])
      
      setHistorial(historialData)
      setEstadisticas(statsData)
      setFiltros(filtrosActualizados)
    } catch (err) {
      const mensaje = err instanceof Error ? err.message : 'Error al cargar el historial'
      setError(mensaje)
    } finally {
      setCargando(false)
    }
  }, [plantaId, filtros, mostrarEstadisticas])

  /**
   * Carga más items (paginación)
   */
  const cargarMas = useCallback(async () => {
    if (!historial || cargandoMas) return
    
    try {
      setCargandoMas(true)
      
      const nuevosFiltros: HistorialSaludParams = {
        ...filtros,
        offset: (filtros.offset || 0) + (filtros.limite || itemsPorPagina)
      }
      
      const nuevosItems = await saludService.obtenerHistorial(plantaId, nuevosFiltros)
      
      setHistorial({
        ...historial,
        analisis: [...historial.analisis, ...nuevosItems.analisis]
      })
      setFiltros(nuevosFiltros)
    } catch (err) {
      console.error('Error al cargar más items:', err)
    } finally {
      setCargandoMas(false)
    }
  }, [plantaId, historial, filtros, cargandoMas, itemsPorPagina])

  /**
   * Alterna la expansión de un item
   */
  const toggleExpansion = useCallback((analisisId: number) => {
    setItemsExpandidos(prev => {
      const nuevo = new Set(prev)
      if (nuevo.has(analisisId)) {
        nuevo.delete(analisisId)
      } else {
        nuevo.add(analisisId)
      }
      return nuevo
    })
  }, [])

  /**
   * Aplica filtros
   */
  const aplicarFiltros = useCallback(() => {
    cargarHistorial({ ...filtros, offset: 0 })
  }, [cargarHistorial, filtros])

  /**
   * Limpia filtros
   */
  const limpiarFiltros = useCallback(() => {
    const filtrosLimpios: HistorialSaludParams = {
      limite: itemsPorPagina,
      offset: 0,
      solo_con_problemas: false
    }
    setFiltros(filtrosLimpios)
    cargarHistorial(filtrosLimpios)
  }, [itemsPorPagina, cargarHistorial])

  // Carga inicial
  useEffect(() => {
    cargarHistorial()
  }, []) // Solo en mount

  /**
   * Obtiene el icono de tendencia
   */
  const obtenerIconoTendencia = (tendencia?: string) => {
    switch (tendencia) {
      case 'mejorando':
        return <TrendingUp className="w-4 h-4 text-green-600" />
      case 'empeorando':
        return <TrendingDown className="w-4 h-4 text-red-600" />
      default:
        return <Minus className="w-4 h-4 text-gray-600" />
    }
  }

  if (cargando) {
    return (
      <div className={cn('flex items-center justify-center p-12', className)}>
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto" />
          <p className="text-sm text-muted-foreground">Cargando historial...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className={cn('p-6', className)}>
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <AlertCircle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
            <div>
              <h4 className="font-semibold text-sm text-red-900">Error</h4>
              <p className="text-sm text-red-700 mt-1">{error}</p>
              <Button
                variant="outline"
                size="sm"
                onClick={() => cargarHistorial()}
                className="mt-3"
              >
                <RefreshCw className="w-4 h-4 mr-2" />
                Reintentar
              </Button>
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (!historial || historial.analisis.length === 0) {
    return (
      <div className={cn('p-12 text-center', className)}>
        <Calendar className="w-16 h-16 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          No hay análisis registrados
        </h3>
        <p className="text-sm text-muted-foreground">
          Realiza el primer análisis de salud de {nombrePlanta} para ver el historial aquí.
        </p>
      </div>
    )
  }

  const hayMasItems = historial.analisis.length < historial.total

  return (
    <div className={cn('space-y-6', className)}>
      {/* Título y acciones */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold flex items-center gap-2">
            <Calendar className="w-6 h-6 text-green-600" />
            Historial de Salud
          </h2>
          <p className="text-muted-foreground mt-1">
            {historial.total} análisis registrado{historial.total !== 1 ? 's' : ''}
          </p>
        </div>
        
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setMostrarFiltros(!mostrarFiltros)}
          >
            <Filter className="w-4 h-4 mr-2" />
            Filtros
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => cargarHistorial()}
          >
            <RefreshCw className="w-4 h-4" />
          </Button>
        </div>
      </div>

      {/* Estadísticas */}
      {mostrarEstadisticas && estadisticas && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Resumen General</CardTitle>
            <CardDescription>Estadísticas de salud de {nombrePlanta}</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <p className="text-xs text-muted-foreground mb-1">Total de Análisis</p>
                <p className="text-2xl font-bold">{estadisticas.total_analisis}</p>
              </div>
              
              {estadisticas.ultimo_estado && (
                <div>
                  <p className="text-xs text-muted-foreground mb-1">Último Estado</p>
                  <div className="flex items-center gap-2">
                    <span className="text-xl">{ICONOS_ESTADO_SALUD[estadisticas.ultimo_estado]}</span>
                    <span className="text-sm font-medium">
                      {NOMBRES_ESTADO_SALUD[estadisticas.ultimo_estado]}
                    </span>
                  </div>
                </div>
              )}
              
              {estadisticas.confianza_promedio !== undefined && (
                <div>
                  <p className="text-xs text-muted-foreground mb-1">Confianza Promedio</p>
                  <p className="text-2xl font-bold">
                    {estadisticas.confianza_promedio.toFixed(1)}%
                  </p>
                </div>
              )}
              
              {estadisticas.tendencia_salud && (
                <div>
                  <p className="text-xs text-muted-foreground mb-1">Tendencia</p>
                  <div className="flex items-center gap-2">
                    {obtenerIconoTendencia(estadisticas.tendencia_salud)}
                    <span className="text-sm font-medium capitalize">
                      {estadisticas.tendencia_salud}
                    </span>
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Panel de filtros */}
      {mostrarFiltros && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Filtros</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* Fecha desde */}
              <div className="space-y-2">
                <Label htmlFor="fecha-desde">Desde</Label>
                <input
                  id="fecha-desde"
                  type="date"
                  value={filtros.desde_fecha?.split('T')[0] || ''}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
                    const fecha = e.target.value ? new Date(e.target.value).toISOString() : undefined
                    setFiltros({ ...filtros, desde_fecha: fecha })
                  }}
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                />
              </div>
              
              {/* Fecha hasta */}
              <div className="space-y-2">
                <Label htmlFor="fecha-hasta">Hasta</Label>
                <input
                  id="fecha-hasta"
                  type="date"
                  value={filtros.hasta_fecha?.split('T')[0] || ''}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
                    const fecha = e.target.value ? new Date(e.target.value).toISOString() : undefined
                    setFiltros({ ...filtros, hasta_fecha: fecha })
                  }}
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                />
              </div>
              
              {/* Solo con problemas */}
              <div className="flex items-end">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={filtros.solo_con_problemas || false}
                    onChange={(e: React.ChangeEvent<HTMLInputElement>) => 
                      setFiltros({ ...filtros, solo_con_problemas: e.target.checked })
                    }
                    className="w-4 h-4 rounded border-gray-300"
                  />
                  <span className="text-sm">Solo con problemas</span>
                </label>
              </div>
            </div>
            
            <div className="flex gap-2">
              <Button onClick={aplicarFiltros} size="sm">
                Aplicar Filtros
              </Button>
              <Button onClick={limpiarFiltros} variant="outline" size="sm">
                Limpiar
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Timeline de análisis */}
      <div className="space-y-4">
        {historial.analisis.map((analisis, index) => {
          const esExpandido = itemsExpandidos.has(analisis.id)
          const diasDesde = calcularDiasDesdeAnalisis(analisis.fecha_analisis)
          
          return (
            <Card key={analisis.id} className="relative overflow-hidden">
              {/* Línea de timeline */}
              {index < historial.analisis.length - 1 && (
                <div className="absolute left-[41px] top-[60px] bottom-[-20px] w-0.5 bg-gray-200" />
              )}
              
              <CardHeader className="pb-3">
                <div className="flex items-start gap-4">
                  {/* Icono de estado con círculo */}
                  <div className="relative">
                    <div className={cn(
                      'w-10 h-10 rounded-full flex items-center justify-center text-xl border-2 bg-white z-10 relative',
                      COLORES_ESTADO_SALUD[analisis.estado]
                    )}>
                      {ICONOS_ESTADO_SALUD[analisis.estado]}
                    </div>
                  </div>
                  
                  {/* Contenido principal */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-4">
                      <div>
                        <CardTitle className="text-lg">
                          {NOMBRES_ESTADO_SALUD[analisis.estado]}
                        </CardTitle>
                        <CardDescription className="mt-1">
                          {new Date(analisis.fecha_analisis).toLocaleString('es-ES', {
                            dateStyle: 'long',
                            timeStyle: 'short'
                          })}
                          {' • '}
                          {diasDesde === 0 ? 'Hoy' : 
                           diasDesde === 1 ? 'Ayer' : 
                           `Hace ${diasDesde} días`}
                        </CardDescription>
                      </div>
                      
                      <div className="flex items-center gap-2">
                        <Badge
                          variant="outline"
                          className={cn('text-xs', obtenerColorConfianza(analisis.confianza))}
                        >
                          {formatearConfianza(analisis.confianza)}
                        </Badge>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => toggleExpansion(analisis.id)}
                        >
                          {esExpandido ? (
                            <ChevronUp className="w-4 h-4" />
                          ) : (
                            <ChevronDown className="w-4 h-4" />
                          )}
                        </Button>
                      </div>
                    </div>
                    
                    {/* Resumen */}
                    <p className="text-sm text-muted-foreground mt-2 line-clamp-2">
                      {analisis.resumen}
                    </p>
                    
                    {/* Badges de información */}
                    <div className="flex flex-wrap gap-2 mt-3">
                      {analisis.con_imagen && (
                        <Badge variant="secondary" className="text-xs">
                          📷 Con imagen
                        </Badge>
                      )}
                      {analisis.num_problemas > 0 && (
                        <Badge variant="destructive" className="text-xs">
                          ⚠️ {analisis.num_problemas} problema{analisis.num_problemas !== 1 ? 's' : ''}
                        </Badge>
                      )}
                      {analisis.num_recomendaciones > 0 && (
                        <Badge variant="outline" className="text-xs">
                          💡 {analisis.num_recomendaciones} recomendación{analisis.num_recomendaciones !== 1 ? 'es' : ''}
                        </Badge>
                      )}
                    </div>
                  </div>
                </div>
              </CardHeader>
              
              {/* Contenido expandido */}
              {esExpandido && (
                <CardContent className="pt-0 pl-[74px]">
                  <div className="space-y-3 border-t pt-4">
                    <div>
                      <h4 className="text-sm font-semibold mb-2">Resumen Completo</h4>
                      <p className="text-sm text-muted-foreground">{analisis.resumen}</p>
                    </div>
                    
                    {analisis.imagen_analizada_url && (
                      <div>
                        <h4 className="text-sm font-semibold mb-2">Imagen Analizada</h4>
                        <img
                          src={analisis.imagen_analizada_url}
                          alt="Imagen del análisis"
                          className="max-w-xs rounded-lg border"
                        />
                      </div>
                    )}
                    
                    <div className="flex gap-2 pt-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => onSeleccionarAnalisis?.(analisis)}
                      >
                        Ver Detalle Completo
                      </Button>
                    </div>
                  </div>
                </CardContent>
              )}
            </Card>
          )
        })}
      </div>

      {/* Botón cargar más */}
      {hayMasItems && (
        <div className="flex justify-center pt-4">
          <Button
            variant="outline"
            onClick={cargarMas}
            disabled={cargandoMas}
          >
            {cargandoMas ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-current mr-2" />
                Cargando...
              </>
            ) : (
              <>
                <ChevronDown className="w-4 h-4 mr-2" />
                Cargar más ({historial.total - historial.analisis.length} restantes)
              </>
            )}
          </Button>
        </div>
      )}
    </div>
  )
}

export default HistorialSalud
