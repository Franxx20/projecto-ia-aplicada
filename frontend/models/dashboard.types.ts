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
 */
export type EstadoSalud = 'excelente' | 'buena' | 'necesita_atencion' | 'critica';

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
  switch (estado) {
    case 'excelente':
    case 'buena':
      return 'default'; // Verde
    case 'necesita_atencion':
      return 'secondary'; // Amarillo/Warning
    case 'critica':
      return 'destructive'; // Rojo
    default:
      return 'default';
  }
};

/**
 * Mapeo de estados de salud a texto legible
 */
export const estadoSaludToLabel = (estado: EstadoSalud): string => {
  switch (estado) {
    case 'excelente':
      return 'Excelente';
    case 'buena':
      return 'Saludable';
    case 'necesita_atencion':
      return 'Necesita Atención';
    case 'critica':
      return 'Estado Crítico';
    default:
      return estado;
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
