/**
 * Tipos TypeScript para análisis de salud de plantas con Gemini AI
 * 
 * Interfaces y tipos para manejar los resultados de análisis de salud,
 * diagnósticos, problemas detectados y recomendaciones de cuidado.
 * 
 * @author Equipo Frontend
 * @date Noviembre 2025
 * @sprint Feature - Health Check AI
 * @task T-007
 */

/**
 * Estados de salud detallados de una planta.
 * 
 * Estos estados son retornados por el análisis de Gemini AI y permiten
 * una clasificación más granular que los estados básicos.
 */
export type EstadoSaludDetallado =
  | 'excelente'      // Planta en perfecto estado, crecimiento óptimo
  | 'saludable'      // Planta en buen estado, sin problemas significativos
  | 'necesita_atencion'  // Requiere ajustes menores en cuidados
  | 'enfermedad'     // Presenta síntomas de enfermedad
  | 'plaga'          // Infestación por plagas o parásitos
  | 'critica';       // Estado crítico, requiere intervención urgente

/**
 * Tipos de problemas que puede presentar una planta.
 */
export type TipoProblema =
  | 'riego'          // Problemas relacionados con exceso o falta de agua
  | 'luz'            // Problemas de iluminación (exceso o deficiencia)
  | 'nutricion'      // Deficiencias nutricionales o fertilización
  | 'temperatura'    // Estrés por temperatura inadecuada
  | 'humedad'        // Problemas de humedad ambiental
  | 'plaga'          // Infestación por insectos o ácaros
  | 'enfermedad'     // Infecciones fúngicas, bacterianas o virales
  | 'fisico'         // Daños físicos, mecánicos
  | 'otro';          // Otros problemas no clasificados

/**
 * Niveles de severidad de un problema detectado.
 */
export type SeveridadProblema =
  | 'leve'      // Problema menor, sin impacto significativo
  | 'moderada'  // Problema que requiere atención pronta
  | 'severa'    // Problema serio que puede afectar la supervivencia
  | 'critica';  // Problema crítico, requiere acción inmediata

/**
 * Niveles de prioridad de una recomendación.
 */
export type PrioridadRecomendacion =
  | 'baja'   // Acción opcional o de mejora
  | 'media'  // Acción recomendada en los próximos días
  | 'alta';  // Acción necesaria en las próximas 24-48 horas

/**
 * Problema detectado en el análisis de salud.
 * 
 * Representa un problema específico identificado por Gemini AI,
 * con detalles sobre su tipo, severidad y descripción.
 */
export interface ProblemaDetectado {
  tipo: TipoProblema;
  descripcion: string;
  severidad: SeveridadProblema;
}

/**
 * Recomendación de cuidado o tratamiento.
 * 
 * Representa una acción específica que el usuario debe realizar
 * para mejorar la salud de la planta.
 */
export interface RecomendacionItem {
  tipo: TipoProblema;
  descripcion: string;
  prioridad: PrioridadRecomendacion;
  urgencia_dias?: number;  // Días máximos para aplicar (0 = inmediato)
}

/**
 * Metadatos del análisis de salud.
 * 
 * Información adicional sobre el proceso de análisis.
 */
export interface SaludAnalisisMetadata {
  tiempo_analisis_ms: number;
  modelo_usado: string;
  con_imagen: boolean;
  fecha_analisis: string;  // ISO 8601 date string
  version_prompt?: string;
}

/**
 * Respuesta completa de un análisis de salud.
 * 
 * Este es el tipo principal que retorna el endpoint de verificación de salud.
 * Incluye el diagnóstico completo, problemas detectados, y recomendaciones.
 */
export interface SaludAnalisisResponse {
  id?: number;  // ID del análisis (si fue guardado en BD)
  planta_id: number;
  usuario_id: number;
  estado: EstadoSaludDetallado;
  confianza: number;  // 0-100%
  resumen: string;
  problemas_detectados: ProblemaDetectado[];
  recomendaciones: RecomendacionItem[];
  diagnostico_detallado?: string;
  imagen_analizada_url?: string;
  metadata: SaludAnalisisMetadata;
}

/**
 * Item del historial de análisis de salud.
 * 
 * Versión resumida del análisis para mostrar en listas de historial.
 */
export interface HistorialSaludItem {
  id: number;
  planta_id: number;
  estado: EstadoSaludDetallado;
  confianza: number;
  resumen: string;  // Truncado si es muy largo
  fecha_analisis: string;  // ISO 8601 date string
  con_imagen: boolean;
  imagen_analizada_url?: string;
  num_problemas: number;
  num_recomendaciones: number;
}

/**
 * Respuesta del endpoint de historial de salud.
 * 
 * Incluye lista paginada de análisis históricos.
 */
export interface HistorialSaludResponse {
  analisis: HistorialSaludItem[];
  total: number;
  planta_id: number;
}

/**
 * Parámetros opcionales para obtener historial.
 */
export interface HistorialSaludParams {
  limite?: number;    // Número máximo de resultados (default: 50)
  offset?: number;    // Desplazamiento para paginación (default: 0)
  desde_fecha?: string;  // ISO 8601 date string
  hasta_fecha?: string;  // ISO 8601 date string
  solo_con_problemas?: boolean;  // Solo análisis con problemas detectados
}

/**
 * Estadísticas agregadas de salud de una planta.
 * 
 * Proporciona métricas sobre la evolución de la salud a lo largo del tiempo.
 */
export interface EstadisticasSaludPlanta {
  planta_id: number;
  total_analisis: number;
  ultimo_estado?: EstadoSaludDetallado;
  ultimo_analisis_fecha?: string;  // ISO 8601 date string
  confianza_promedio?: number;
  tendencia_salud?: 'mejorando' | 'estable' | 'empeorando';
  dias_desde_ultimo_analisis?: number;
}

/**
 * Request para verificación de salud (metadata, sin imagen).
 * 
 * La imagen se envía por separado como archivo multipart.
 */
export interface VerificarSaludRequest {
  notas_adicionales?: string;
  incluir_imagen?: boolean;
}

// ==================== UTILIDADES Y HELPERS ====================

/**
 * Colores para diferentes estados de salud (Tailwind CSS).
 */
export const COLORES_ESTADO_SALUD: Record<EstadoSaludDetallado, string> = {
  excelente: 'text-green-600 bg-green-50 border-green-200',
  saludable: 'text-green-500 bg-green-50 border-green-200',
  necesita_atencion: 'text-yellow-600 bg-yellow-50 border-yellow-200',
  enfermedad: 'text-orange-600 bg-orange-50 border-orange-200',
  plaga: 'text-red-600 bg-red-50 border-red-200',
  critica: 'text-red-700 bg-red-100 border-red-300'
};

/**
 * Iconos para diferentes estados de salud.
 */
export const ICONOS_ESTADO_SALUD: Record<EstadoSaludDetallado, string> = {
  excelente: '🌟',
  saludable: '✅',
  necesita_atencion: '⚠️',
  enfermedad: '🤒',
  plaga: '🐛',
  critica: '🚨'
};

/**
 * Nombres en español de estados de salud.
 */
export const NOMBRES_ESTADO_SALUD: Record<EstadoSaludDetallado, string> = {
  excelente: 'Excelente',
  saludable: 'Saludable',
  necesita_atencion: 'Necesita Atención',
  enfermedad: 'Enferma',
  plaga: 'Plaga Detectada',
  critica: 'Estado Crítico'
};

/**
 * Nombres en español de tipos de problema.
 */
export const NOMBRES_TIPO_PROBLEMA: Record<TipoProblema, string> = {
  riego: 'Riego',
  luz: 'Iluminación',
  nutricion: 'Nutrición',
  temperatura: 'Temperatura',
  humedad: 'Humedad',
  plaga: 'Plaga',
  enfermedad: 'Enfermedad',
  fisico: 'Daño Físico',
  otro: 'Otro'
};

/**
 * Colores para severidad de problemas (Tailwind CSS).
 */
export const COLORES_SEVERIDAD: Record<SeveridadProblema, string> = {
  leve: 'text-yellow-600 bg-yellow-50',
  moderada: 'text-orange-600 bg-orange-50',
  severa: 'text-red-600 bg-red-50',
  critica: 'text-red-700 bg-red-100'
};

/**
 * Colores para prioridad de recomendaciones (Tailwind CSS).
 */
export const COLORES_PRIORIDAD: Record<PrioridadRecomendacion, string> = {
  baja: 'text-blue-600 bg-blue-50',
  media: 'text-yellow-600 bg-yellow-50',
  alta: 'text-red-600 bg-red-50'
};

/**
 * Obtiene el color según el nivel de confianza.
 * 
 * @param confianza - Valor de confianza (0-100)
 * @returns Clase CSS de Tailwind para el color
 */
export function obtenerColorConfianza(confianza: number): string {
  if (confianza >= 80) return 'text-green-600';
  if (confianza >= 60) return 'text-yellow-600';
  if (confianza >= 40) return 'text-orange-600';
  return 'text-red-600';
}

/**
 * Obtiene el texto de nivel de confianza.
 * 
 * @param confianza - Valor de confianza (0-100)
 * @returns Texto descriptivo del nivel
 */
export function obtenerNivelConfianza(confianza: number): string {
  if (confianza >= 80) return 'Muy Alta';
  if (confianza >= 60) return 'Alta';
  if (confianza >= 40) return 'Media';
  return 'Baja';
}

/**
 * Formatea el valor de confianza como porcentaje.
 * 
 * @param confianza - Valor de confianza (0-100)
 * @returns String formateado (ej: "85.5%")
 */
export function formatearConfianza(confianza: number): string {
  return `${confianza.toFixed(1)}%`;
}

/**
 * Determina si un análisis tiene problemas críticos.
 * 
 * @param analisis - Análisis de salud
 * @returns true si hay problemas críticos o severos
 */
export function tieneProblemasCriticos(analisis: SaludAnalisisResponse): boolean {
  return analisis.problemas_detectados.some(
    p => p.severidad === 'critica' || p.severidad === 'severa'
  );
}

/**
 * Obtiene el problema más severo de un análisis.
 * 
 * @param analisis - Análisis de salud
 * @returns El problema más severo o undefined si no hay problemas
 */
export function obtenerProblemaMasSevero(
  analisis: SaludAnalisisResponse
): ProblemaDetectado | undefined {
  if (analisis.problemas_detectados.length === 0) return undefined;
  
  const ordenSeveridad: Record<SeveridadProblema, number> = {
    critica: 4,
    severa: 3,
    moderada: 2,
    leve: 1
  };
  
  return analisis.problemas_detectados.reduce((max, problema) =>
    ordenSeveridad[problema.severidad] > ordenSeveridad[max.severidad] ? problema : max
  );
}

/**
 * Filtra recomendaciones por prioridad.
 * 
 * @param analisis - Análisis de salud
 * @param prioridad - Prioridad a filtrar
 * @returns Array de recomendaciones con la prioridad especificada
 */
export function filtrarRecomendacionesPorPrioridad(
  analisis: SaludAnalisisResponse,
  prioridad: PrioridadRecomendacion
): RecomendacionItem[] {
  return analisis.recomendaciones.filter(r => r.prioridad === prioridad);
}

/**
 * Calcula días desde el último análisis.
 * 
 * @param fechaAnalisis - Fecha del análisis en formato ISO 8601
 * @returns Número de días transcurridos
 */
export function calcularDiasDesdeAnalisis(fechaAnalisis: string): number {
  const fecha = new Date(fechaAnalisis);
  const ahora = new Date();
  const diferenciaMilisegundos = ahora.getTime() - fecha.getTime();
  return Math.floor(diferenciaMilisegundos / (1000 * 60 * 60 * 24));
}
