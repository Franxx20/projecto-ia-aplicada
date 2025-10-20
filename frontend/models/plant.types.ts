/**
 * Tipos TypeScript para identificación de plantas con PlantNet API
 * 
 * Interfaces y tipos para manejar los resultados de identificación
 * de especies de plantas usando la API de PlantNet.
 * 
 * @author Equipo Frontend
 * @date Octubre 2025
 * @sprint Sprint 1-2
 * @task T-017
 */

/**
 * Información de género de la planta
 */
export interface PlantGenus {
  scientificNameWithoutAuthor: string;
  scientificNameAuthorship?: string;
  scientificName?: string;
}

/**
 * Información de familia de la planta
 */
export interface PlantFamily {
  scientificNameWithoutAuthor: string;
  scientificNameAuthorship?: string;
  scientificName?: string;
}

/**
 * Información completa de una especie
 */
export interface PlantSpecies {
  scientificNameWithoutAuthor: string;
  scientificNameAuthorship?: string;
  scientificName: string;
  genus?: PlantGenus;
  family?: PlantFamily;
  commonNames: string[];
}

/**
 * Resultado individual de identificación de PlantNet
 */
export interface PlantNetResult {
  score: number;  // Score de confianza (0.0 a 1.0)
  species: PlantSpecies;
  gbif?: {
    id?: string;
  };
  powo?: {
    id?: string;
  };
}

/**
 * Órgano detectado automáticamente por la IA
 */
export interface PredictedOrgan {
  image: string;
  filename: string;
  organ: string;
  score: number;
}

/**
 * Información del query realizado a PlantNet
 */
export interface QueryInfo {
  project: string;
  images: string[];
  organs: string[];
  includeRelatedImages: boolean;
  noReject: boolean;
  type?: string;
}

/**
 * Respuesta completa de PlantNet API
 */
export interface PlantNetResponse {
  query: QueryInfo;
  predictedOrgans: PredictedOrgan[];
  bestMatch: string;
  results: PlantNetResult[];
  version: string;
  remainingIdentificationRequests: number;
  language?: string;
  preferedReferential?: string;
}

/**
 * Resultado simplificado para uso interno
 */
export interface PlantIdentificationSimplified {
  nombre_cientifico: string;
  nombre_cientifico_sin_autor: string;
  autor: string;
  nombres_comunes: string[];
  genero: string;
  familia: string;
  score: number;
  confianza_porcentaje: number;
  gbif_id?: string;
  powo_id?: string;
}

/**
 * Request para identificar desde imagen existente
 */
export interface IdentificarRequest {
  imagen_id: number;
  organos?: string[];
  guardar_resultado?: boolean;
}

/**
 * Información de una imagen en la respuesta de identificación (T-022)
 */
export interface ImagenIdentificacionResponse {
  id: number;
  nombre_archivo: string;
  url_blob: string;
  organ?: string;
  tamano_bytes: number;
}

/**
 * Respuesta de identificación de la API (Actualizada para T-022)
 * Ahora incluye soporte para múltiples imágenes
 */
export interface IdentificarResponse {
  id: number;
  usuario_id: number;
  imagenes: ImagenIdentificacionResponse[];
  especie_id?: number;
  confianza: number;
  origen: string;
  resultados: PlantNetResponse;
  fecha_identificacion: string;
  proyecto_usado: string;
  cantidad_imagenes: number;
}

/**
 * Respuesta de identificación (versión simplificada para retrocompatibilidad)
 */
export interface IdentificarResponseSimple {
  identificacion_id?: number;
  especie: PlantIdentificationSimplified;
  confianza: number;
  confianza_porcentaje: string;
  es_confiable: boolean;
  plantnet_response: PlantNetResponse;
  mejor_resultado: PlantIdentificationSimplified;
}

/**
 * Información de cuota de PlantNet API
 */
export interface PlantNetQuota {
  requests_hoy: number;
  limite_diario: number;
  restantes: number;
  porcentaje_usado: number;
}

/**
 * Identificación en historial
 */
export interface HistorialIdentificacion {
  id: number;
  imagen_id: number;
  usuario_id: number;
  nombre_cientifico: string;
  nombres_comunes: string[];
  familia: string;
  confianza: number;
  validada: boolean;
  fecha_creacion: string;
  fecha_validacion?: string;
  plantnet_response: PlantNetResponse;
  imagen?: {
    id: number;
    url: string;
    nombre: string;
  };
}

/**
 * Respuesta de historial
 */
export interface HistorialResponse {
  total: number;
  identificaciones: HistorialIdentificacion[];
}

/**
 * Tipos de órganos de planta válidos (Actualizado T-022)
 */
export type OrganType = 'leaf' | 'flower' | 'fruit' | 'bark' | 'habit' | 'other' | 'sin_especificar' | 'auto';

/**
 * Lista de órganos válidos (Actualizado T-022)
 */
export const ORGANOS_VALIDOS: OrganType[] = ['leaf', 'flower', 'fruit', 'bark', 'habit', 'other', 'sin_especificar', 'auto'];

/**
 * Nombres en español de los órganos (Actualizado T-022)
 */
export const NOMBRES_ORGANOS: Record<OrganType, string> = {
  leaf: 'Hoja',
  flower: 'Flor',
  fruit: 'Fruto',
  bark: 'Corteza',
  habit: 'Hábito',
  other: 'Otro',
  sin_especificar: 'Sin especificar',
  auto: 'Automático'
};

/**
 * Colores para diferentes niveles de confianza
 */
export const COLORES_CONFIANZA = {
  alta: 'text-green-600',      // >= 80%
  media: 'text-yellow-600',    // 60-79%
  baja: 'text-orange-600',     // 40-59%
  muy_baja: 'text-red-600'     // < 40%
} as const;

/**
 * Obtiene el color según el nivel de confianza
 */
export function obtenerColorConfianza(confianza: number): string {
  if (confianza >= 80) return COLORES_CONFIANZA.alta;
  if (confianza >= 60) return COLORES_CONFIANZA.media;
  if (confianza >= 40) return COLORES_CONFIANZA.baja;
  return COLORES_CONFIANZA.muy_baja;
}

/**
 * Obtiene el texto de nivel de confianza
 */
export function obtenerNivelConfianza(confianza: number): string {
  if (confianza >= 80) return 'Muy Alta';
  if (confianza >= 60) return 'Alta';
  if (confianza >= 40) return 'Media';
  return 'Baja';
}

/**
 * Formatea el porcentaje de confianza
 */
export function formatearConfianza(score: number): string {
  return `${(score * 100).toFixed(2)}%`;
}

/**
 * Valida si un órgano es válido
 */
export function esOrganoValido(organo: string): organo is OrganType {
  return ORGANOS_VALIDOS.includes(organo as OrganType);
}
