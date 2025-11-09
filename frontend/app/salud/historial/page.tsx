/**
 * page.tsx - Página de historial de análisis de salud
 * 
 * Muestra el historial completo de análisis de salud con:
 * - Lista paginada de análisis
 * - Filtros por planta, estado y fechas
 * - Detalles expandibles de cada análisis
 * - Estadísticas agregadas
 * - Navegación a análisis específico
 * 
 * @author Equipo Frontend
 * @date Noviembre 2025
 * @epic Epic 3 - Sistema de verificación de Salud con Gemini AI
 * @task T-081
 */

'use client'

import React, { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { 
  ArrowLeft, 
  Filter,
  Loader2,
  FileText,
  AlertCircle,
  ChevronDown,
  ChevronUp,
  Sparkles,
  Leaf
} from 'lucide-react'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible'
import { useAuth } from '@/hooks/useAuth'
import saludService from '@/lib/salud.service'
import dashboardService from '@/lib/dashboard.service'
import type { HistorialSaludItem, HistorialSaludResponse } from '@/models/salud'
import type { Planta } from '@/models/dashboard.types'
import {
  ESTADO_TEXTOS,
  formatearConfianza,
  formatearDiasDesde,
  obtenerColorEstado,
  obtenerEmojiEstado
} from '@/models/salud'

/**
 * Props para el componente de filtros
 */
interface FiltrosHistorial {
  plantaId?: number
  estado?: string
  fechaDesde?: string
  fechaHasta?: string
}

/**
 * Componente de tarjeta de análisis individual
 */
function AnalisisCard({ 
  analisis, 
  isExpanded, 
  onToggle 
}: {
  readonly analisis: HistorialSaludItem
  readonly isExpanded: boolean
  readonly onToggle: () => void
}) {
  const router = useRouter()

  return (
    <Card 
      className="hover:shadow-md transition-shadow cursor-pointer"
      style={{ borderLeft: `4px solid ${obtenerColorEstado(analisis.estado)}` }}
    >
      <Collapsible open={isExpanded} onOpenChange={onToggle}>
        <CollapsibleTrigger asChild>
          <CardHeader className="cursor-pointer">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-2xl">{obtenerEmojiEstado(analisis.estado)}</span>
                  <CardTitle className="text-lg">
                    {analisis.planta_nombre || 'Planta'}
                  </CardTitle>
                  {analisis.es_critico && (
                    <Badge variant="destructive" className="ml-2">
                      <AlertCircle className="h-3 w-3 mr-1" />
                      Crítico
                    </Badge>
                  )}
                </div>
                <CardDescription className="flex flex-wrap items-center gap-3 text-sm">
                  <span>{formatearDiasDesde(analisis.fecha_analisis)}</span>
                  <span>•</span>
                  <Badge
                    variant="outline"
                    style={{ 
                      backgroundColor: `${obtenerColorEstado(analisis.estado)}20`,
                      borderColor: obtenerColorEstado(analisis.estado)
                    }}
                  >
                    {ESTADO_TEXTOS[analisis.estado] || analisis.estado}
                  </Badge>
                  <span>•</span>
                  <span>Confianza: {formatearConfianza(analisis.confianza)}</span>
                </CardDescription>
              </div>
              <Button variant="ghost" size="icon">
                {isExpanded ? (
                  <ChevronUp className="h-4 w-4" />
                ) : (
                  <ChevronDown className="h-4 w-4" />
                )}
              </Button>
            </div>
          </CardHeader>
        </CollapsibleTrigger>

        <CollapsibleContent>
          <CardContent className="pt-0 space-y-4">
            {/* Resumen del diagnóstico */}
            <div>
              <h4 className="font-semibold text-sm mb-2">Diagnóstico:</h4>
              <p className="text-sm text-muted-foreground">
                {analisis.resumen_diagnostico}
              </p>
            </div>

            {/* Problemas detectados */}
            {analisis.problemas_detectados && analisis.problemas_detectados.length > 0 && (
              <div>
                <h4 className="font-semibold text-sm mb-2">
                  Problemas detectados ({analisis.problemas_detectados.length}):
                </h4>
                <div className="space-y-2">
                  {analisis.problemas_detectados.slice(0, 3).map((problema: any, index: number) => (
                    <div key={index} className="flex items-start gap-2 text-sm">
                      <AlertCircle className="h-4 w-4 text-amber-500 mt-0.5 flex-shrink-0" />
                      <span className="text-muted-foreground">
                        {problema.tipo || problema.descripcion || 'Problema detectado'}
                      </span>
                    </div>
                  ))}
                  {analisis.problemas_detectados.length > 3 && (
                    <p className="text-xs text-muted-foreground">
                      +{analisis.problemas_detectados.length - 3} problema(s) más
                    </p>
                  )}
                </div>
              </div>
            )}

            {/* Metadatos */}
            <div className="grid grid-cols-3 gap-2 pt-2 border-t text-xs text-muted-foreground">
              <div>
                <span className="block font-medium">Modelo</span>
                <span>{analisis.modelo_ia_usado || 'Gemini AI'}</span>
              </div>
              <div>
                <span className="block font-medium">Tiempo</span>
                <span>{analisis.tiempo_analisis_ms}ms</span>
              </div>
              <div>
                <span className="block font-medium">Con imagen</span>
                <span>{analisis.con_imagen ? 'Sí' : 'No'}</span>
              </div>
            </div>

            {/* Botón ver detalles completos */}
            <Button
              variant="outline"
              size="sm"
              className="w-full"
              onClick={() => router.push(`/plant/${analisis.planta_id}?tab=health`)}
            >
              Ver detalles completos
            </Button>
          </CardContent>
        </CollapsibleContent>
      </Collapsible>
    </Card>
  )
}

/**
 * Página de historial de análisis de salud
 */
export default function HistorialSaludPage() {
  const router = useRouter()
  const { usuario, estaCargando: cargandoAuth } = useAuth()

  // Estados
  const [plantasDisponibles, setPlantasDisponibles] = useState<Planta[]>([])
  const [historial, setHistorial] = useState<HistorialSaludResponse | null>(null)
  const [cargandoHistorial, setCargandoHistorial] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [expandedIds, setExpandedIds] = useState<Set<number>>(new Set())

  // Filtros
  const [filtros, setFiltros] = useState<FiltrosHistorial>({})
  const [paginaActual, setPaginaActual] = useState(1)
  const itemsPorPagina = 10

  // Cargar plantas y historial inicial
  useEffect(() => {
    if (!cargandoAuth && usuario) {
      cargarDatos()
    }
  }, [usuario, cargandoAuth])

  // Recargar al cambiar filtros o página
  useEffect(() => {
    if (usuario) {
      cargarHistorial()
    }
  }, [filtros, paginaActual, usuario])

  /**
   * Carga plantas disponibles
   */
  const cargarDatos = async () => {
    try {
      const respuesta = await dashboardService.obtenerPlantas()
      setPlantasDisponibles(respuesta.plantas)
      await cargarHistorial()
    } catch (error) {
      console.error('Error al cargar datos:', error)
      setError('No se pudieron cargar los datos. Intenta de nuevo.')
    }
  }

  /**
   * Carga el historial con filtros aplicados
   */
  const cargarHistorial = async () => {
    setCargandoHistorial(true)
    setError(null)

    try {
      const offset = (paginaActual - 1) * itemsPorPagina

      const response = await saludService.obtenerHistorial({
        planta_id: filtros.plantaId,
        estado: filtros.estado as any,
        fecha_desde: filtros.fechaDesde,
        fecha_hasta: filtros.fechaHasta,
        limite: itemsPorPagina,
        offset
      })

      setHistorial(response)
    } catch (error: any) {
      console.error('Error al cargar historial:', error)
      setError(
        error.response?.data?.detail || 
        'No se pudo cargar el historial. Por favor, intenta de nuevo.'
      )
    } finally {
      setCargandoHistorial(false)
    }
  }

  /**
   * Maneja el cambio de filtros
   */
  const handleFiltroChange = (campo: keyof FiltrosHistorial, valor: any) => {
    setFiltros(prev => ({
      ...prev,
      [campo]: valor
    }))
    setPaginaActual(1) // Resetear a página 1 al cambiar filtros
  }

  /**
   * Limpia todos los filtros
   */
  const limpiarFiltros = () => {
    setFiltros({})
    setPaginaActual(1)
  }

  /**
   * Alterna la expansión de una tarjeta
   */
  const toggleExpanded = (id: number) => {
    setExpandedIds(prev => {
      const newSet = new Set(prev)
      if (newSet.has(id)) {
        newSet.delete(id)
      } else {
        newSet.add(id)
      }
      return newSet
    })
  }

  /**
   * Navega a página anterior
   */
  const paginaAnterior = () => {
    if (paginaActual > 1) {
      setPaginaActual(prev => prev - 1)
    }
  }

  /**
   * Navega a página siguiente
   */
  const paginaSiguiente = () => {
    if (historial && (paginaActual * itemsPorPagina) < historial.total) {
      setPaginaActual(prev => prev + 1)
    }
  }

  if (cargandoAuth) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  const totalPaginas = historial ? Math.ceil(historial.total / itemsPorPagina) : 0

  return (
    <div className="container mx-auto px-4 py-8 max-w-6xl">
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
              <FileText className="h-8 w-8 text-primary" />
              Historial de Salud
            </h1>
            <p className="text-muted-foreground mt-1">
              {historial ? `${historial.total} análisis realizados` : 'Cargando...'}
            </p>
          </div>
        </div>
        <Link href="/salud">
          <Button>
            <Sparkles className="h-4 w-4 mr-2" />
            Nuevo Análisis
          </Button>
        </Link>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Sidebar de Filtros */}
        <div className="lg:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <Filter className="h-5 w-5" />
                Filtros
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Filtro por Planta */}
              <div className="space-y-2">
                <Label htmlFor="planta-filter">Planta</Label>
                <Select
                  value={filtros.plantaId?.toString() || 'todas'}
                  onValueChange={(value) => 
                    handleFiltroChange('plantaId', value === 'todas' ? undefined : parseInt(value))
                  }
                >
                  <SelectTrigger id="planta-filter">
                    <SelectValue placeholder="Todas las plantas" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="todas">Todas las plantas</SelectItem>
                    {plantasDisponibles.map((planta) => (
                      <SelectItem key={planta.id} value={planta.id.toString()}>
                        <div className="flex items-center gap-2">
                          <Leaf className="h-4 w-4 text-green-600" />
                          {planta.nombre_personal}
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Filtro por Estado */}
              <div className="space-y-2">
                <Label htmlFor="estado-filter">Estado de Salud</Label>
                <Select
                  value={filtros.estado || 'todos'}
                  onValueChange={(value) => 
                    handleFiltroChange('estado', value === 'todos' ? undefined : value)
                  }
                >
                  <SelectTrigger id="estado-filter">
                    <SelectValue placeholder="Todos los estados" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="todos">Todos los estados</SelectItem>
                    <SelectItem value="excelente">🌟 Excelente</SelectItem>
                    <SelectItem value="saludable">✅ Saludable</SelectItem>
                    <SelectItem value="necesita_atencion">⚠️ Necesita atención</SelectItem>
                    <SelectItem value="enfermedad">🦠 Enfermedad</SelectItem>
                    <SelectItem value="plaga">🐛 Plaga</SelectItem>
                    <SelectItem value="critica">🚨 Crítica</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Filtro por Fecha Desde */}
              <div className="space-y-2">
                <Label htmlFor="fecha-desde">Desde</Label>
                <Input
                  id="fecha-desde"
                  type="date"
                  value={filtros.fechaDesde || ''}
                  onChange={(e) => handleFiltroChange('fechaDesde', e.target.value)}
                />
              </div>

              {/* Filtro por Fecha Hasta */}
              <div className="space-y-2">
                <Label htmlFor="fecha-hasta">Hasta</Label>
                <Input
                  id="fecha-hasta"
                  type="date"
                  value={filtros.fechaHasta || ''}
                  onChange={(e) => handleFiltroChange('fechaHasta', e.target.value)}
                />
              </div>

              {/* Botón limpiar filtros */}
              <Button
                variant="outline"
                className="w-full"
                onClick={limpiarFiltros}
              >
                Limpiar Filtros
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Lista de Análisis */}
        <div className="lg:col-span-3 space-y-4">
          {cargandoHistorial ? (
            <Card>
              <CardContent className="py-12 flex flex-col items-center justify-center">
                <Loader2 className="h-8 w-8 animate-spin text-primary mb-4" />
                <p className="text-muted-foreground">Cargando historial...</p>
              </CardContent>
            </Card>
          ) : error ? (
            <Card>
              <CardContent className="py-12 flex flex-col items-center justify-center">
                <AlertCircle className="h-8 w-8 text-destructive mb-4" />
                <p className="text-destructive font-semibold mb-2">Error al cargar historial</p>
                <p className="text-sm text-muted-foreground mb-4">{error}</p>
                <Button onClick={cargarHistorial}>Reintentar</Button>
              </CardContent>
            </Card>
          ) : !historial || historial.analisis.length === 0 ? (
            <Card>
              <CardContent className="py-12 flex flex-col items-center justify-center">
                <FileText className="h-12 w-12 text-muted-foreground mb-4" />
                <p className="text-lg font-semibold mb-2">No hay análisis</p>
                <p className="text-sm text-muted-foreground mb-4">
                  {Object.keys(filtros).length > 0
                    ? 'No se encontraron análisis con los filtros aplicados'
                    : 'Aún no has realizado análisis de salud'}
                </p>
                <Link href="/salud">
                  <Button>
                    <Sparkles className="h-4 w-4 mr-2" />
                    Realizar Primer Análisis
                  </Button>
                </Link>
              </CardContent>
            </Card>
          ) : (
            <>
              {/* Lista de análisis */}
              {historial.analisis.map((analisis) => (
                <AnalisisCard
                  key={analisis.id}
                  analisis={analisis}
                  isExpanded={expandedIds.has(analisis.id)}
                  onToggle={() => toggleExpanded(analisis.id)}
                />
              ))}

              {/* Paginación */}
              {totalPaginas > 1 && (
                <Card>
                  <CardContent className="py-4">
                    <div className="flex items-center justify-between">
                      <p className="text-sm text-muted-foreground">
                        Mostrando {((paginaActual - 1) * itemsPorPagina) + 1} - {Math.min(paginaActual * itemsPorPagina, historial.total)} de {historial.total}
                      </p>
                      <div className="flex items-center gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={paginaAnterior}
                          disabled={paginaActual === 1}
                        >
                          Anterior
                        </Button>
                        <span className="text-sm px-2">
                          Página {paginaActual} de {totalPaginas}
                        </span>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={paginaSiguiente}
                          disabled={paginaActual === totalPaginas}
                        >
                          Siguiente
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  )
}
