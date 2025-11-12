/**
 * Tipos TypeScript para el Dashboard de Plantas
 * 
 * Estos tipos están sincronizados con los schemas del backend (planta.py)
 * para garantizar consistencia en la comunicación API.
 * 
 * @module dashboard.types
 */

/**
 * Tipo para el estado de salud de una planta
 * Sincronizado con el backend y el módulo de salud
 */
export type EstadoSalud = 
  | 'excelente' 
  | 'saludable' 
  | 'necesita_atencion' 
  | 'enfermedad' 
  | 'plaga' 
  | 'critica' 
  | 'desconocido';

/**
 * Tipo para el nivel de luz que recibe una planta
 */
export type NivelLuz = 'baja' | 'media' | 'alta' | 'directa';

/**
 * Interfaz para una Planta individual
 * Corresponde al schema PlantaResponse del backend
 */
export interface Planta {
  id: number;
  usuario_id: number;
  nombre_personal: string;
  especie_id: number | null;
  estado_salud: EstadoSalud;
  ubicacion: string | null;
  notas: string | null;
  imagen_principal_id: number | null;
  imagen_principal_url: string | null;
  fecha_ultimo_riego: string | null; // ISO datetime string
  frecuencia_riego_dias: number;
  luz_actual: NivelLuz | null;
  fecha_adquisicion: string | null; // ISO datetime string
  proxima_riego: string | null; // ISO datetime string
  created_at: string; // ISO datetime string
  updated_at: string; // ISO datetime string
  is_active: boolean;
  necesita_riego: boolean;
  es_favorita: boolean;
  fue_regada_hoy: boolean;
  condiciones_ambientales_recomendadas?: {
    luz_recomendada: string;
    luz_horas_diarias?: string;
    temperatura_min?: number;
    temperatura_max?: number;
    temperatura_ideal?: string;
    humedad_min?: number;
    humedad_max?: number;
    humedad_recomendaciones?: string;
    frecuencia_riego_dias?: number;
    descripcion_riego?: string;
  } | null;
}

/**
 * Interfaz para crear una nueva planta
 * Corresponde al schema PlantaCreate del backend
 */
export interface PlantaCreate {
  nombre_personal: string;
  especie_id?: number | null;
  estado_salud?: EstadoSalud;
  ubicacion?: string | null;
  notas?: string | null;
  imagen_principal_id?: number | null;
  fecha_ultimo_riego?: string | null;
  frecuencia_riego_dias?: number;
  luz_actual?: NivelLuz | null;
  fecha_adquisicion?: string | null;
}

/**
 * Interfaz para actualizar una planta existente
 * Corresponde al schema PlantaUpdate del backend
 */
export interface PlantaUpdate {
  nombre_personal?: string;
  especie_id?: number | null;
  estado_salud?: EstadoSalud;
  ubicacion?: string | null;
  notas?: string | null;
  imagen_principal_id?: number | null;
  fecha_ultimo_riego?: string | null;
  frecuencia_riego_dias?: number;
  luz_actual?: NivelLuz | null;
  fecha_adquisicion?: string | null;
  es_favorita?: boolean;
  fue_regada_hoy?: boolean;
}

/**
 * Interfaz para estadísticas del Dashboard
 * Corresponde al schema PlantaStats del backend
 */
export interface DashboardStats {
  total_plantas: number;
  plantas_saludables: number;
  plantas_necesitan_atencion: number;
  plantas_necesitan_riego: number;
  porcentaje_salud: number;
}

/**
 * Interfaz para la respuesta de lista de plantas
 * Corresponde al schema PlantaListResponse del backend
 */
export interface PlantaListResponse {
  plantas: Planta[];
  total: number;
}

/**
 * Interfaz para registrar un riego
 * Corresponde al schema RegistrarRiegoRequest del backend
 */
export interface RegistrarRiegoRequest {
  fecha_riego?: string | null; // ISO datetime string
}

/**
 * Interfaz para imagen de planta
 * Representa una imagen asociada a una planta (principal, identificación, o análisis)
 */
export interface ImagenPlanta {
  id: number;
  nombre_archivo: string;
  url_blob: string; // URL con SAS token incluido
  tamano_bytes: number;
  content_type: string;
  descripcion?: string | null;
  organ?: string | null;
  created_at?: string | null; // ISO datetime string
}

/**
 * Interfaz para datos de una tarjeta de planta en el UI
 * Extensión de Planta con información computada para mostrar
 */
export interface PlantaCard extends Planta {
  // Campos computados para el UI
  diasDesdeUltimoRiego?: number;
  diasHastaProximoRiego?: number;
  urlImagen?: string;
  nombreEspecie?: string;
  descripcionLuz?: string;
}

/**
 * Mapeo de estados de salud a variantes de Badge
 */
export const estadoSaludToBadgeVariant = (estado: EstadoSalud): 'default' | 'destructive' | 'secondary' => {
  // Normalizar a minúsculas para comparación case-insensitive
  const estadoNormalizado = estado.toLowerCase() as EstadoSalud
  
  switch (estadoNormalizado) {
    case 'excelente':
    case 'saludable':
      return 'default'; // Verde
    case 'necesita_atencion':
      return 'secondary'; // Amarillo/Warning
    case 'enfermedad':
    case 'plaga':
    case 'critica':
      return 'destructive'; // Rojo
    case 'desconocido':
      return 'secondary'; // Gris/Unknown
    default:
      return 'default';
  }
};

/**
 * Mapeo de estados de salud a texto legible
 * Sincronizado con el módulo de salud para consistencia
 */
export const estadoSaludToLabel = (estado: EstadoSalud): string => {
  // Normalizar a minúsculas para comparación case-insensitive
  const estadoNormalizado = estado.toLowerCase() as EstadoSalud
  
  switch (estadoNormalizado) {
    case 'excelente':
      return 'Excelente';
    case 'saludable':
      return 'Saludable';
    case 'necesita_atencion':
      return 'Necesita Atención';
    case 'enfermedad':
      return 'Enfermedad Detectada';
    case 'plaga':
      return 'Plaga Detectada';
    case 'critica':
      return 'Estado Crítico';
    case 'desconocido':
      return 'Estado Desconocido';
    default:
      // Si viene capitalizado, devolverlo tal cual
      return estado.charAt(0).toUpperCase() + estado.slice(1).toLowerCase();
  }
};

/**
 * Mapeo de estados de salud a emojis
 */
export const estadoSaludToEmoji = (estado: EstadoSalud): string => {
  const estadoNormalizado = estado.toLowerCase() as EstadoSalud
  
  switch (estadoNormalizado) {
    case 'excelente':
      return '🌟';
    case 'saludable':
      return '✅';
    case 'necesita_atencion':
      return '⚠️';
    case 'enfermedad':
      return '🦠';
    case 'plaga':
      return '🐛';
    case 'critica':
      return '🚨';
    case 'desconocido':
      return '❓';
    default:
      return '🌱';
  }
};

/**
 * Mapeo de estados de salud a clases CSS personalizadas para badges
 * Con fondos opacos y sombras para mejor legibilidad sobre cualquier imagen
 */
export const estadoSaludToBadgeClasses = (estado: EstadoSalud): string => {
  const estadoNormalizado = estado.toLowerCase() as EstadoSalud
  
  switch (estadoNormalizado) {
    case 'excelente':
      return 'bg-green-600 hover:bg-green-700 text-white border-2 border-green-700 font-semibold backdrop-blur-sm shadow-md';
    case 'saludable':
      return 'bg-green-500 hover:bg-green-600 text-white border-2 border-green-600 font-semibold backdrop-blur-sm shadow-md';
    case 'necesita_atencion':
      return 'bg-yellow-600 hover:bg-yellow-700 text-white border-2 border-yellow-700 font-semibold backdrop-blur-sm shadow-md';
    case 'enfermedad':
      return 'bg-red-600 hover:bg-red-700 text-white border-2 border-red-700 font-semibold backdrop-blur-sm shadow-md';
    case 'plaga':
      return 'bg-orange-600 hover:bg-orange-700 text-white border-2 border-orange-700 font-semibold backdrop-blur-sm shadow-md';
    case 'critica':
      return 'bg-red-700 hover:bg-red-800 text-white border-2 border-red-800 font-semibold backdrop-blur-sm shadow-md';
    case 'desconocido':
      return 'bg-gray-600 hover:bg-gray-700 text-white border-2 border-gray-700 font-semibold backdrop-blur-sm shadow-md';
    default:
      return 'bg-gray-600 hover:bg-gray-700 text-white border-2 border-gray-700 font-semibold backdrop-blur-sm shadow-md';
  }
};

/**
 * Mapeo de estados de salud a estilos inline para garantizar colores consistentes
 */
export const estadoSaludToBadgeStyle = (estado: EstadoSalud): React.CSSProperties => {
  const estadoNormalizado = estado.toLowerCase() as EstadoSalud
  
  switch (estadoNormalizado) {
    case 'excelente':
      return { backgroundColor: 'rgb(22 163 74)', borderColor: 'rgb(21 128 61)' }; // green-600/green-700
    case 'saludable':
      return { backgroundColor: 'rgb(34 197 94)', borderColor: 'rgb(22 163 74)' }; // green-500/green-600
    case 'necesita_atencion':
      return { backgroundColor: 'rgb(202 138 4)', borderColor: 'rgb(161 98 7)' }; // yellow-600/yellow-700
    case 'enfermedad':
      return { backgroundColor: 'rgb(220 38 38)', borderColor: 'rgb(185 28 28)' }; // red-600/red-700
    case 'plaga':
      return { backgroundColor: 'rgb(234 88 12)', borderColor: 'rgb(194 65 12)' }; // orange-600/orange-700
    case 'critica':
      return { backgroundColor: 'rgb(185 28 28)', borderColor: 'rgb(153 27 27)' }; // red-700/red-800
    case 'desconocido':
      return { backgroundColor: 'rgb(75 85 99)', borderColor: 'rgb(55 65 81)' }; // gray-600/gray-700
    default:
      return { backgroundColor: 'rgb(75 85 99)', borderColor: 'rgb(55 65 81)' }; // gray-600/gray-700
  }
};

/**
 * Mapeo de niveles de luz a descripciones legibles
 */
export const nivelLuzToLabel = (nivel: NivelLuz | null): string => {
  if (!nivel) return 'No especificado';
  
  switch (nivel) {
    case 'baja':
      return 'Luz Baja';
    case 'media':
      return 'Luz Media';
    case 'alta':
      return 'Luz Alta / Indirecta';
    case 'directa':
      return 'Luz Directa';
    default:
      return nivel;
  }
};

/**
 * Calcula los días desde la última fecha hasta ahora
 */
export const calcularDiasDesde = (fecha: string | null): number | undefined => {
  if (!fecha) return undefined;
  
  const fechaRiego = new Date(fecha);
  const ahora = new Date();
  const diferencia = ahora.getTime() - fechaRiego.getTime();
  const dias = Math.floor(diferencia / (1000 * 60 * 60 * 24));
  
  return dias;
};

/**
 * Calcula los días hasta una fecha futura desde ahora
 */
export const calcularDiasHasta = (fecha: string | null): number | undefined => {
  if (!fecha) return undefined;
  
  const fechaFutura = new Date(fecha);
  const ahora = new Date();
  const diferencia = fechaFutura.getTime() - ahora.getTime();
  const dias = Math.ceil(diferencia / (1000 * 60 * 60 * 24));
  
  return dias;
};

/**
 * Formatea una fecha relativa (ej: "hace 2 días", "en 3 días")
 */
export const formatearFechaRelativa = (fecha: string | null, esFutura: boolean = false): string => {
  if (!fecha) return 'No especificado';
  
  const dias = esFutura ? calcularDiasHasta(fecha) : calcularDiasDesde(fecha);
  
  if (dias === undefined) return 'No especificado';
  
  if (dias === 0) {
    return esFutura ? 'Hoy' : 'Hoy';
  } else if (dias === 1) {
    return esFutura ? 'Mañana' : 'Ayer';
  } else if (dias < 0 && esFutura) {
    return `Hace ${Math.abs(dias)} día${Math.abs(dias) > 1 ? 's' : ''}`;
  } else {
    return esFutura 
      ? `En ${dias} día${dias > 1 ? 's' : ''}`
      : `Hace ${dias} día${dias > 1 ? 's' : ''}`;
  }
};
