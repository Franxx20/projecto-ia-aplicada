/**
 * useAnalisisSalud.ts - Custom React Hook para gestión de análisis de salud
 * 
 * Hook reutilizable que encapsula toda la lógica de análisis de salud de plantas:
 * - Carga de análisis (con imagen o sin ella)
 * - Cache de últimos análisis
 * - Refetch automático
 * - Polling opcional para actualizaciones en tiempo real
 * - Historial con paginación
 * - Estadísticas agregadas
 * 
 * @author Equipo Frontend
 * @date Noviembre 2025
 * @sprint Feature - Health Check AI Extensions
 */

import { useState, useEffect, useCallback, useRef } from 'react'
import saludService from '@/lib/salud.service'
import type {
  SaludAnalisisResponse,
  HistorialSaludResponse,
  HistorialSaludParams,
  EstadisticasSaludPlanta
} from '@/models/salud'

/**
 * Opciones de configuración del hook
 */
export interface UseAnalisisSaludOptions {
  /** ID de la planta a analizar */
  plantaId: number
  
  /** Si se debe cargar el historial automáticamente */
  cargarHistorial?: boolean
  
  /** Si se debe cargar las estadísticas automáticamente */
  cargarEstadisticas?: boolean
  
  /** Intervalo de polling en milisegundos (0 = deshabilitado) */
  pollingInterval?: number
  
  /** Callback cuando se completa un análisis */
  onAnalisisCompletado?: (analisis: SaludAnalisisResponse) => void
  
  /** Callback cuando ocurre un error */
  onError?: (error: Error) => void
}

/**
 * Estado retornado por el hook
 */
export interface UseAnalisisSaludReturn {
  // Análisis actual
  analisis: SaludAnalisisResponse | null
  
  // Historial
  historial: HistorialSaludResponse | null
  
  // Estadísticas
  estadisticas: EstadisticasSaludPlanta | null
  
  // Estados de carga
  cargando: boolean
  analizando: boolean
  cargandoHistorial: boolean
  cargandoEstadisticas: boolean
  
  // Progreso de upload
  progreso: number
  
  // Error
  error: Error | null
  
  // Acciones
  verificarSalud: (imagen?: File | Blob, notas?: string) => Promise<void>
  verificarSaludSinImagen: (notas?: string) => Promise<void>
  verificarSaludConImagenPrincipal: (notas?: string) => Promise<void>
  obtenerHistorial: (params?: HistorialSaludParams) => Promise<void>
  obtenerEstadisticas: () => Promise<void>
  refetch: () => Promise<void>
  limpiar: () => void
}

/**
 * Custom hook para gestión de análisis de salud
 * 
 * @example
 * ```tsx
 * function MiComponente({ plantaId }) {
 *   const {
 *     analisis,
 *     historial,
 *     estadisticas,
 *     analizando,
 *     verificarSalud,
 *     obtenerHistorial
 *   } = useAnalisisSalud({ plantaId })
 *   
 *   return (
 *     <div>
 *       <button onClick={() => verificarSalud()}>
 *         Analizar Salud
 *       </button>
 *       {analisis && <p>{analisis.estado}</p>}
 *     </div>
 *   )
 * }
 * ```
 */
export function useAnalisisSalud(
  options: UseAnalisisSaludOptions
): UseAnalisisSaludReturn {
  const {
    plantaId,
    cargarHistorial: cargarHistorialAuto = false,
    cargarEstadisticas: cargarEstadisticasAuto = false,
    pollingInterval = 0,
    onAnalisisCompletado,
    onError
  } = options

  // Estado del análisis actual
  const [analisis, setAnalisis] = useState<SaludAnalisisResponse | null>(null)
  const [historial, setHistorial] = useState<HistorialSaludResponse | null>(null)
  const [estadisticas, setEstadisticas] = useState<EstadisticasSaludPlanta | null>(null)

  // Estados de carga
  const [cargando, setCargando] = useState(false)
  const [analizando, setAnalizando] = useState(false)
  const [cargandoHistorial, setCargandoHistorial] = useState(false)
  const [cargandoEstadisticas, setCargandoEstadisticas] = useState(false)
  const [progreso, setProgreso] = useState(0)

  // Error
  const [error, setError] = useState<Error | null>(null)

  // Referencia para polling
  const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null)

  /**
   * Limpia el intervalo de polling
   */
  const limpiarPolling = useCallback(() => {
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current)
      pollingIntervalRef.current = null
    }
  }, [])

  /**
   * Verifica la salud de la planta con imagen opcional
   */
  const verificarSalud = useCallback(async (
    imagen?: File | Blob,
    notas?: string
  ) => {
    try {
      setAnalizando(true)
      setProgreso(0)
      setError(null)

      const resultado = await saludService.verificarSalud(
        plantaId,
        imagen,
        {
          notas_adicionales: notas,
          onProgress: setProgreso
        }
      )

      setAnalisis(resultado)
      setProgreso(100)
      onAnalisisCompletado?.(resultado)
    } catch (err) {
      const errorObj = err instanceof Error ? err : new Error('Error al verificar salud')
      setError(errorObj)
      onError?.(errorObj)
    } finally {
      setAnalizando(false)
    }
  }, [plantaId, onAnalisisCompletado, onError])

  /**
   * Verifica la salud sin imagen (solo contexto)
   */
  const verificarSaludSinImagen = useCallback(async (notas?: string) => {
    try {
      setAnalizando(true)
      setError(null)

      const resultado = await saludService.verificarSaludSinImagen(plantaId, notas)
      
      setAnalisis(resultado)
      onAnalisisCompletado?.(resultado)
    } catch (err) {
      const errorObj = err instanceof Error ? err : new Error('Error al verificar salud')
      setError(errorObj)
      onError?.(errorObj)
    } finally {
      setAnalizando(false)
    }
  }, [plantaId, onAnalisisCompletado, onError])

  /**
   * Verifica la salud con la imagen principal de la planta
   */
  const verificarSaludConImagenPrincipal = useCallback(async (notas?: string) => {
    try {
      setAnalizando(true)
      setError(null)

      const resultado = await saludService.verificarSaludConImagenPrincipal(plantaId, notas)
      
      setAnalisis(resultado)
      onAnalisisCompletado?.(resultado)
    } catch (err) {
      const errorObj = err instanceof Error ? err : new Error('Error al verificar salud')
      setError(errorObj)
      onError?.(errorObj)
    } finally {
      setAnalizando(false)
    }
  }, [plantaId, onAnalisisCompletado, onError])

  /**
   * Obtiene el historial de análisis
   */
  const obtenerHistorial = useCallback(async (params?: HistorialSaludParams) => {
    try {
      setCargandoHistorial(true)
      setError(null)

      const resultado = await saludService.obtenerHistorial(plantaId, params)
      setHistorial(resultado)
    } catch (err) {
      const errorObj = err instanceof Error ? err : new Error('Error al obtener historial')
      setError(errorObj)
      onError?.(errorObj)
    } finally {
      setCargandoHistorial(false)
    }
  }, [plantaId, onError])

  /**
   * Obtiene las estadísticas de salud
   */
  const obtenerEstadisticas = useCallback(async () => {
    try {
      setCargandoEstadisticas(true)
      setError(null)

      const resultado = await saludService.obtenerEstadisticas(plantaId)
      setEstadisticas(resultado)
    } catch (err) {
      const errorObj = err instanceof Error ? err : new Error('Error al obtener estadísticas')
      setError(errorObj)
      onError?.(errorObj)
    } finally {
      setCargandoEstadisticas(false)
    }
  }, [plantaId, onError])

  /**
   * Recarga el último análisis
   */
  const refetch = useCallback(async () => {
    try {
      setCargando(true)
      setError(null)

      const ultimoAnalisis = await saludService.obtenerUltimoAnalisis(plantaId)
      setAnalisis(ultimoAnalisis)

      if (cargarHistorialAuto) {
        await obtenerHistorial()
      }

      if (cargarEstadisticasAuto) {
        await obtenerEstadisticas()
      }
    } catch (err) {
      const errorObj = err instanceof Error ? err : new Error('Error al recargar datos')
      setError(errorObj)
      onError?.(errorObj)
    } finally {
      setCargando(false)
    }
  }, [plantaId, cargarHistorialAuto, cargarEstadisticasAuto, obtenerHistorial, obtenerEstadisticas, onError])

  /**
   * Limpia el estado del hook
   */
  const limpiar = useCallback(() => {
    setAnalisis(null)
    setHistorial(null)
    setEstadisticas(null)
    setError(null)
    setProgreso(0)
    limpiarPolling()
  }, [limpiarPolling])

  // Carga inicial
  useEffect(() => {
    const cargarDatosIniciales = async () => {
      setCargando(true)

      try {
        // Obtener último análisis si existe
        const ultimoAnalisis = await saludService.obtenerUltimoAnalisis(plantaId)
        setAnalisis(ultimoAnalisis)

        // Cargar historial si está habilitado
        if (cargarHistorialAuto) {
          const historialData = await saludService.obtenerHistorial(plantaId)
          setHistorial(historialData)
        }

        // Cargar estadísticas si está habilitado
        if (cargarEstadisticasAuto) {
          const estadisticasData = await saludService.obtenerEstadisticas(plantaId)
          setEstadisticas(estadisticasData)
        }
      } catch (err) {
        // No mostrar error si simplemente no hay análisis previos
        if (err instanceof Error && !err.message.includes('no encontrad')) {
          const errorObj = err instanceof Error ? err : new Error('Error al cargar datos')
          setError(errorObj)
          onError?.(errorObj)
        }
      } finally {
        setCargando(false)
      }
    }

    cargarDatosIniciales()
  }, [plantaId, cargarHistorialAuto, cargarEstadisticasAuto, onError])

  // Setup de polling
  useEffect(() => {
    if (pollingInterval > 0) {
      pollingIntervalRef.current = setInterval(() => {
        refetch()
      }, pollingInterval)

      return () => {
        limpiarPolling()
      }
    }
  }, [pollingInterval, refetch, limpiarPolling])

  // Cleanup al desmontar
  useEffect(() => {
    return () => {
      limpiarPolling()
    }
  }, [limpiarPolling])

  return {
    // Estado
    analisis,
    historial,
    estadisticas,
    
    // Estados de carga
    cargando,
    analizando,
    cargandoHistorial,
    cargandoEstadisticas,
    progreso,
    
    // Error
    error,
    
    // Acciones
    verificarSalud,
    verificarSaludSinImagen,
    verificarSaludConImagenPrincipal,
    obtenerHistorial,
    obtenerEstadisticas,
    refetch,
    limpiar
  }
}

export default useAnalisisSalud
