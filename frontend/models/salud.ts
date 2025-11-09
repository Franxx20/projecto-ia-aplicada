/**
 * Tipos y modelos para el sistema de Health Check
 * 
 * Define las interfaces y tipos necesarios para el análisis de salud de plantas:
 * - Estados de salud
 * - Análisis de salud
 * - Estadísticas
 * - Historial
 * - Utilidades
 * 
 * @author Equipo Frontend
 * @date Noviembre 2025
 * @sprint Sprint Health Check
 */

/**
 * Estados posibles de salud de una planta
 */
export type EstadoSalud =
  | 'excelente'
  | 'saludable'
  | 'necesita_atencion'
  | 'enfermedad'
  | 'plaga'
  | 'critica'
  | 'desconocido'

/**
 * Tendencia de salud de la planta
 */
export type TendenciaSalud = 'mejorando' | 'estable' | 'empeorando'

/**
 * Request para crear un análisis de salud
 */
export interface AnalisisSaludRequest {
  planta_id: number
  imagen_id?: number | null
  sintomas_observados?: string
  notas_adicionales?: string
}

/**
 * Resultado de un análisis de salud
 */
export interface AnalisisSalud {
  id: number
  planta_id: number
  usuario_id?: number
  imagen_id?: number | null
  estado: EstadoSalud
  confianza: number // 0-100
  resumen_diagnostico: string
  diagnostico_detallado?: string | null
  problemas_detectados: Array<{
    tipo: string
    severidad: string
    descripcion: string
    recomendacion?: string
  }>
  recomendaciones: Array<{
    categoria: string
    prioridad: string
    accion: string
    descripcion: string
  }>
  modelo_ia_usado: string
  tiempo_analisis_ms: number
  version_prompt: string
  con_imagen: boolean
  notas_usuario?: string | null
  imagen_analisis_url: string | null
  fecha_analisis: string // ISO datetime
  created_at: string
  updated_at?: string
  // Legacy fields (para backward compatibility)
  diagnostico?: string
  recomendaciones_legacy?: string[]
}

/**
 * Response del análisis de salud con planta info
 */
export interface AnalisisSaludResponse extends AnalisisSalud {
  planta_nombre?: string
  planta_especie?: string
}

/**
 * Estadísticas de salud de una planta
 */
export interface EstadisticasSalud {
  planta_id: number
  ultimo_estado: EstadoSalud
  total_analisis: number
  confianza_promedio: number
  dias_desde_ultimo_analisis: number
  tendencia: TendenciaSalud
}

/**
 * Item del historial de salud (coincide con backend HistorialSaludItem + campos extras del endpoint)
 */
export interface HistorialSaludItem {
  id: number
  planta_id: number
  estado: EstadoSalud
  confianza: number
  resumen: string
  fecha_analisis: string
  con_imagen: boolean
  imagen_analizada_url: string | null
  num_problemas: number
  num_recomendaciones: number
  // Campos adicionales agregados por el endpoint
  planta_nombre?: string
  es_critico?: boolean
  color_estado?: string
  modelo_ia_usado?: string
  tiempo_analisis_ms?: number
  problemas_detectados?: Array<{
    tipo: string
    severidad: string
    descripcion: string
  }>
  recomendaciones?: Array<{
    prioridad: string
    accion: string
    descripcion: string
  }>
  resumen_diagnostico?: string
  diagnostico_detallado?: string
}

/**
 * Response del historial de análisis de salud
 */
export interface HistorialSaludResponse {
  analisis: HistorialSaludItem[]
  total: number
  planta_id?: number
  limite?: number
  offset?: number
}

/**
 * Parámetros de consulta para el historial
 */
export interface HistorialSaludParams {
  planta_id?: number
  limite?: number
  offset?: number
  estado?: EstadoSalud
  fecha_desde?: string
  fecha_hasta?: string
}

/**
 * Estadísticas agregadas de salud del jardín (dashboard)
 */
export interface SaludJardinStats {
  total_plantas: number
  total_con_analisis: number
  saludables: number // excelente + saludable
  necesitan_atencion: number
  criticas: number // enfermedad + plaga + critica
  porcentaje_saludables: number
  promedio_confianza: number
  tendencia_general?: TendenciaSalud
}

/**
 * Información de planta crítica
 */
export interface PlantaCritica {
  planta_id: number
  nombre: string
  estado: string
  dias_desde_analisis: number
}

// ============================================================
// UTILIDADES
// ============================================================

/**
 * Mapeo de estados a emojis
 */
export const ESTADO_EMOJIS: Record<EstadoSalud, string> = {
  excelente: '🌟',
  saludable: '✅',
  necesita_atencion: '⚠️',
  enfermedad: '🦠',
  plaga: '🐛',
  critica: '🚨',
  desconocido: '❓',
}

/**
 * Mapeo de estados a colores (Tailwind classes)
 */
export const ESTADO_COLORES: Record<EstadoSalud, string> = {
  excelente: 'text-green-600',
  saludable: 'text-green-500',
  necesita_atencion: 'text-yellow-600',
  enfermedad: 'text-red-600',
  plaga: 'text-orange-600',
  critica: 'text-red-700',
  desconocido: 'text-gray-500',
}

/**
 * Mapeo de estados a colores de fondo (Tailwind classes)
 */
export const ESTADO_BG_COLORES: Record<EstadoSalud, string> = {
  excelente: 'bg-green-50 border-green-200',
  saludable: 'bg-green-50 border-green-200',
  necesita_atencion: 'bg-yellow-50 border-yellow-200',
  enfermedad: 'bg-red-50 border-red-200',
  plaga: 'bg-orange-50 border-orange-200',
  critica: 'bg-red-50 border-red-200',
  desconocido: 'bg-gray-50 border-gray-200',
}

/**
 * Mapeo de estados a textos legibles en español
 */
export const ESTADO_TEXTOS: Record<EstadoSalud, string> = {
  excelente: 'Excelente',
  saludable: 'Saludable',
  necesita_atencion: 'Necesita Atención',
  enfermedad: 'Enfermedad Detectada',
  plaga: 'Plaga Detectada',
  critica: 'Estado Crítico',
  desconocido: 'Estado Desconocido',
}

/**
 * Obtiene el emoji correspondiente a un estado de salud
 */
export function obtenerEmojiEstado(estado: EstadoSalud): string {
  return ESTADO_EMOJIS[estado] || ESTADO_EMOJIS.desconocido
}

/**
 * Obtiene el color correspondiente a un estado de salud
 */
export function obtenerColorEstado(estado: EstadoSalud): string {
  return ESTADO_COLORES[estado] || ESTADO_COLORES.desconocido
}

/**
 * Obtiene el color de fondo correspondiente a un estado de salud
 */
export function obtenerBgColorEstado(estado: EstadoSalud): string {
  return ESTADO_BG_COLORES[estado] || ESTADO_BG_COLORES.desconocido
}

/**
 * Obtiene el texto legible correspondiente a un estado de salud
 */
export function obtenerTextoEstado(estado: EstadoSalud): string {
  return ESTADO_TEXTOS[estado] || ESTADO_TEXTOS.desconocido
}

/**
 * Determina si un estado es considerado saludable
 */
export function esSaludable(estado: EstadoSalud): boolean {
  return estado === 'excelente' || estado === 'saludable'
}

/**
 * Determina si un estado es considerado crítico
 */
export function esCritico(estado: EstadoSalud): boolean {
  return estado === 'enfermedad' || estado === 'plaga' || estado === 'critica'
}

/**
 * Determina si un estado necesita atención
 */
export function necesitaAtencion(estado: EstadoSalud): boolean {
  return estado === 'necesita_atencion' || esCritico(estado)
}

/**
 * Formatea la confianza como porcentaje
 */
export function formatearConfianza(confianza: number): string {
  return `${confianza.toFixed(1)}%`
}

/**
 * Calcula los días desde un análisis
 */
export function calcularDiasDesde(fecha: string): number {
  const fechaAnalisis = new Date(fecha)
  const ahora = new Date()
  const diff = ahora.getTime() - fechaAnalisis.getTime()
  return Math.floor(diff / (1000 * 60 * 60 * 24))
}

/**
 * Formatea los días desde un análisis para mostrar al usuario
 */
export function formatearDiasDesde(fecha: string): string {
  const dias = calcularDiasDesde(fecha)
  if (dias === 0) return 'Hoy'
  if (dias === 1) return 'Hace 1 día'
  return `Hace ${dias} días`
}

/**
 * Obtiene el color de badge según el nivel de confianza
 */
export function obtenerColorConfianza(confianza: number): string {
  if (confianza >= 85) return 'text-green-700 bg-green-100 border-green-200'
  if (confianza >= 70) return 'text-blue-700 bg-blue-100 border-blue-200'
  if (confianza >= 50) return 'text-yellow-700 bg-yellow-100 border-yellow-200'
  return 'text-red-700 bg-red-100 border-red-200'
}

/**
 * Valida que un estado de salud sea válido
 */
export function esEstadoValido(estado: string): estado is EstadoSalud {
  return [
    'excelente',
    'saludable',
    'necesita_atencion',
    'enfermedad',
    'plaga',
    'critica',
    'desconocido',
  ].includes(estado)
}
