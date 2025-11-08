"""
Servicio de Google Gemini para análisis de salud de plantas.

Este módulo implementa la integración con Google Gemini API para analizar
el estado de salud de plantas mediante visión por computadora y procesamiento
de lenguaje natural.

Características:
- Análisis de imágenes de plantas
- Diagnóstico basado en contexto (datos históricos, cuidados)
- Generación de recomendaciones personalizadas
- Rate limiting y manejo de errores
- Soporte para análisis sin imagen

Autor: Equipo Backend
Fecha: Noviembre 2025
Sprint: Feature - Health Check AI
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
import base64

try:
    import google.generativeai as genai
    from google.generativeai.types import HarmCategory, HarmBlockThreshold
except ImportError:
    raise ImportError(
        "google-generativeai no está instalado. "
        "Ejecuta: pip install google-generativeai"
    )

from app.core.config import obtener_configuracion

# Configuración
config = obtener_configuracion()
logger = logging.getLogger(__name__)

# Configurar Gemini API
if config.gemini_api_key:
    genai.configure(api_key=config.gemini_api_key)
else:
    logger.warning("⚠️  GEMINI_API_KEY no configurada. El servicio no funcionará.")


class GeminiServiceError(Exception):
    """Excepción base para errores del servicio Gemini"""
    pass


class GeminiAPIError(GeminiServiceError):
    """Error al comunicarse con la API de Gemini"""
    pass


class GeminiRateLimitError(GeminiServiceError):
    """Error de límite de requests alcanzado"""
    pass


class GeminiInvalidResponseError(GeminiServiceError):
    """Error al parsear respuesta de Gemini"""
    pass


class RateLimiter:
    """
    Controlador simple de rate limiting en memoria.
    
    En producción, usar Redis o similar para persistencia.
    """
    
    def __init__(self):
        self._requests: Dict[str, List[datetime]] = {}
        self._daily_count: Dict[str, int] = {}
        self._last_reset: datetime = datetime.now()
    
    def _reset_if_needed(self):
        """Resetear contadores si es un nuevo día"""
        now = datetime.now()
        if now.date() > self._last_reset.date():
            logger.info("🔄 Reseteando contadores diarios de Gemini")
            self._daily_count = {}
            self._last_reset = now
    
    def check_rate_limit(
        self, 
        user_id: Optional[int] = None,
        per_minute: int = 60,
        per_day: int = 1500,
        per_user_per_day: int = 10
    ) -> bool:
        """
        Verificar si se puede hacer un request.
        
        Args:
            user_id: ID del usuario (opcional, para límite por usuario)
            per_minute: Límite de requests por minuto (global)
            per_day: Límite de requests por día (global)
            per_user_per_day: Límite de requests por día por usuario
            
        Returns:
            True si puede hacer el request, False si excede límite
            
        Raises:
            GeminiRateLimitError: Si se excede el límite
        """
        self._reset_if_needed()
        
        now = datetime.now()
        key_global = "global"
        key_user = f"user_{user_id}" if user_id else None
        
        # Verificar límite por minuto (global)
        if key_global not in self._requests:
            self._requests[key_global] = []
        
        # Limpiar requests antiguos (más de 1 minuto)
        one_minute_ago = now - timedelta(minutes=1)
        self._requests[key_global] = [
            ts for ts in self._requests[key_global] 
            if ts > one_minute_ago
        ]
        
        if len(self._requests[key_global]) >= per_minute:
            raise GeminiRateLimitError(
                f"Límite de {per_minute} requests por minuto alcanzado. "
                f"Intenta nuevamente en unos momentos."
            )
        
        # Verificar límite diario (global)
        daily_count = self._daily_count.get(key_global, 0)
        if daily_count >= per_day:
            raise GeminiRateLimitError(
                f"Límite diario de {per_day} requests alcanzado. "
                f"Intenta mañana."
            )
        
        # Verificar límite por usuario por día
        if key_user:
            user_daily_count = self._daily_count.get(key_user, 0)
            if user_daily_count >= per_user_per_day:
                raise GeminiRateLimitError(
                    f"Has alcanzado tu límite diario de {per_user_per_day} análisis. "
                    f"Intenta mañana."
                )
        
        # Registrar request
        self._requests[key_global].append(now)
        self._daily_count[key_global] = daily_count + 1
        
        if key_user:
            self._daily_count[key_user] = user_daily_count + 1
        
        return True
    
    def get_remaining_today(self, user_id: Optional[int] = None) -> Dict[str, int]:
        """Obtener requests restantes hoy"""
        self._reset_if_needed()
        
        global_used = self._daily_count.get("global", 0)
        global_remaining = max(0, config.gemini_max_requests_per_day - global_used)
        
        result = {
            "global_remaining": global_remaining,
            "global_limit": config.gemini_max_requests_per_day
        }
        
        if user_id:
            user_key = f"user_{user_id}"
            user_used = self._daily_count.get(user_key, 0)
            user_remaining = max(
                0, 
                config.gemini_max_requests_per_user_per_day - user_used
            )
            result["user_remaining"] = user_remaining
            result["user_limit"] = config.gemini_max_requests_per_user_per_day
        
        return result


# Instancia global del rate limiter
_rate_limiter = RateLimiter()


class GeminiService:
    """
    Servicio para interactuar con Google Gemini AI.
    
    Proporciona métodos para analizar la salud de plantas usando
    visión por computadora y procesamiento de lenguaje natural.
    """
    
    # Plantilla del prompt principal (versión 1.0)
    PROMPT_TEMPLATE_V1 = """
Eres un experto botánico especializado en diagnóstico fitosanitario de plantas de interior y exterior.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                  INFORMACIÓN DE LA PLANTA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 IDENTIFICACIÓN:
   • Nombre: {nombre_personalizado}
   • Especie: {nombre_cientifico} ({nombre_comun})
   • Familia: {familia}
   • Edad en colección: {dias_desde_adquisicion} días

📍 UBICACIÓN Y AMBIENTE:
   • Ubicación: {ubicacion}
   • Nivel de luz: {luz_actual}

💧 HISTORIAL DE CUIDADOS:
   • Último riego: hace {dias_desde_riego} días
   • Frecuencia óptima: cada {frecuencia_riego} días
   • Estado del riego: {estado_riego}

📊 ESTADO PREVIO:
   • Estado anterior: {estado_salud_anterior}
   • Último análisis: {fecha_ultimo_analisis}

📝 NOTAS DEL USUARIO:
{notas_usuario}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                     INSTRUCCIONES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 TAREA:
Analiza {tiene_imagen} y toda la información contextual para proporcionar
un diagnóstico profesional del estado de salud de esta planta.

🔍 FACTORES A EVALUAR:

1. ANÁLISIS VISUAL {si_tiene_imagen}:
   • Color de hojas (verde intenso, amarillento, marrón, manchas)
   • Textura y turgencia (firmes, marchitas, blandas)
   • Crecimiento (nuevo crecimiento, hojas secas)
   • Plagas visibles (insectos, ácaros, cochinillas)
   • Enfermedades (hongos, manchas, pudrición)
   • Estado general (vigor, tamaño, forma)

2. ANÁLISIS CONTEXTUAL:
   • ¿La frecuencia de riego es apropiada?
   • ¿Los días desde el último riego son excesivos o insuficientes?
   • ¿La ubicación y luz son adecuadas para esta especie?
   • ¿Hay coherencia entre síntomas visuales y cuidados?

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                  FORMATO DE RESPUESTA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Responde ÚNICAMENTE con un objeto JSON válido con esta estructura exacta:

{{
  "estado": "<uno de: excelente|saludable|necesita_atencion|enfermedad|plaga|critica>",
  "confianza": <número entre 0 y 100>,
  "resumen": "<2-3 oraciones describiendo el estado general>",
  "diagnostico_completo": "<análisis detallado de todos los síntomas>",
  "problemas_detectados": [
    {{
      "tipo": "<exceso_riego|falta_riego|plaga_insectos|hongo|bacteria|falta_luz|exceso_luz|nutrientes|otro>",
      "severidad": "<leve|moderada|severa>",
      "ubicacion": "<descripción de dónde se observa>",
      "descripcion": "<explicación específica>"
    }}
  ],
  "recomendaciones": [
    {{
      "tipo": "<riego|poda|fertilizante|tratamiento|ubicacion|luz|drenaje|sustrato|otro>",
      "descripcion": "<instrucción específica y accionable>",
      "prioridad": "<alta|media|baja>",
      "urgencia_dias": <número de días antes de actuar, o null>
    }}
  ]
}}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                    CRITERIOS DE ESTADO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🟢 EXCELENTE (90-100%): Hojas verde intenso, brillantes, nuevo crecimiento activo
🟢 SALUDABLE (70-89%): Hojas verdes, algunas imperfecciones menores
🟡 NECESITA_ATENCION (50-69%): Hojas con manchas o amarillamiento leve, problemas corregibles
🟠 ENFERMEDAD (30-49%): Infección fúngica o bacteriana evidente, requiere tratamiento
🟠 PLAGA (30-49%): Presencia visible de insectos/ácaros, requiere tratamiento
🔴 CRITICA (0-29%): Múltiples problemas simultáneos, alto riesgo de pérdida

⚠️  IMPORTANTE:
   • Sé específico en las recomendaciones
   • Prioriza las acciones más urgentes
   • Considera la especie al hacer recomendaciones
   • Si no tienes imagen, reduce el nivel de confianza (máx 70%)
   • Responde SOLO con JSON, sin texto adicional antes o después
"""
    
    @classmethod
    def _construir_prompt(
        cls,
        datos_planta: Dict[str, Any],
        tiene_imagen: bool = True
    ) -> str:
        """
        Construir el prompt personalizado con los datos de la planta.
        
        Args:
            datos_planta: Diccionario con información de la planta
            tiene_imagen: Si se incluye imagen en el análisis
            
        Returns:
            Prompt formateado listo para Gemini
        """
        # Valores por defecto
        defaults = {
            "nombre_personalizado": datos_planta.get("nombre_personal", "Mi planta"),
            "nombre_cientifico": datos_planta.get("nombre_cientifico", "Desconocida"),
            "nombre_comun": datos_planta.get("nombre_comun", "Planta"),
            "familia": datos_planta.get("familia", "Desconocida"),
            "dias_desde_adquisicion": datos_planta.get("dias_desde_adquisicion", "N/A"),
            "ubicacion": datos_planta.get("ubicacion", "No especificada"),
            "luz_actual": datos_planta.get("luz_actual", "No especificada"),
            "dias_desde_riego": datos_planta.get("dias_desde_riego", "N/A"),
            "frecuencia_riego": datos_planta.get("frecuencia_riego_dias", "N/A"),
            "estado_riego": datos_planta.get("estado_riego", "normal"),
            "estado_salud_anterior": datos_planta.get("estado_salud", "desconocido"),
            "fecha_ultimo_analisis": datos_planta.get("fecha_ultimo_analisis", "Nunca"),
            "notas_usuario": datos_planta.get("notas", "Sin notas adicionales"),
            "tiene_imagen": "la imagen adjunta" if tiene_imagen else "solo la información contextual",
            "si_tiene_imagen": "(Imagen disponible)" if tiene_imagen else "(Sin imagen - análisis predictivo)"
        }
        
        return cls.PROMPT_TEMPLATE_V1.format(**defaults)
    
    @classmethod
    def _preparar_imagen(
        cls,
        imagen_path: Optional[Union[str, Path]] = None,
        imagen_bytes: Optional[bytes] = None
    ) -> Optional[Any]:
        """
        Preparar imagen para enviar a Gemini.
        
        Args:
            imagen_path: Ruta a la imagen en disco
            imagen_bytes: Bytes de la imagen
            
        Returns:
            Objeto de imagen compatible con Gemini o None
        """
        if imagen_bytes:
            # Usar bytes directamente
            return imagen_bytes
        
        if imagen_path:
            # Leer desde archivo
            path = Path(imagen_path)
            if not path.exists():
                raise FileNotFoundError(f"Imagen no encontrada: {imagen_path}")
            
            with open(path, "rb") as f:
                return f.read()
        
        return None
    
    @classmethod
    def _parsear_respuesta_json(cls, texto: str) -> Dict[str, Any]:
        """
        Parsear respuesta de Gemini eliminando markdown si existe.
        
        Args:
            texto: Texto de respuesta de Gemini
            
        Returns:
            Diccionario con la respuesta parseada
            
        Raises:
            GeminiInvalidResponseError: Si no se puede parsear el JSON
        """
        texto = texto.strip()
        
        # Limpiar markdown si existe
        if "```json" in texto:
            texto = texto.split("```json")[1].split("```")[0].strip()
        elif "```" in texto:
            # Intentar extraer cualquier bloque de código
            partes = texto.split("```")
            if len(partes) >= 2:
                texto = partes[1].strip()
        
        try:
            data = json.loads(texto)
            return data
        except json.JSONDecodeError as e:
            logger.error(f"Error parseando JSON: {e}")
            logger.error(f"Texto recibido: {texto[:500]}...")
            raise GeminiInvalidResponseError(
                f"La respuesta de Gemini no es JSON válido: {str(e)}"
            )
    
    @classmethod
    def _validar_respuesta(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validar que la respuesta tenga la estructura esperada.
        
        Args:
            data: Diccionario con la respuesta
            
        Returns:
            Diccionario validado (con valores por defecto si faltan campos)
            
        Raises:
            GeminiInvalidResponseError: Si faltan campos críticos
        """
        # Campos requeridos
        campos_requeridos = ["estado", "confianza", "resumen", "recomendaciones"]
        
        for campo in campos_requeridos:
            if campo not in data:
                raise GeminiInvalidResponseError(
                    f"Campo requerido '{campo}' no encontrado en respuesta"
                )
        
        # Validar estado
        estados_validos = [
            "excelente", "saludable", "necesita_atencion", 
            "enfermedad", "plaga", "critica"
        ]
        if data["estado"] not in estados_validos:
            logger.warning(
                f"Estado inválido: {data['estado']}. Usando 'saludable'"
            )
            data["estado"] = "saludable"
        
        # Validar confianza
        try:
            confianza = float(data["confianza"])
            if not (0 <= confianza <= 100):
                confianza = max(0, min(100, confianza))
            data["confianza"] = confianza
        except (ValueError, TypeError):
            logger.warning("Confianza inválida. Usando 50.0")
            data["confianza"] = 50.0
        
        # Campos opcionales con defaults
        if "diagnostico_completo" not in data:
            data["diagnostico_completo"] = data["resumen"]
        
        if "problemas_detectados" not in data:
            data["problemas_detectados"] = []
        
        # Validar recomendaciones
        if not isinstance(data["recomendaciones"], list):
            data["recomendaciones"] = []
        
        return data
    
    @classmethod
    def analizar_salud_planta(
        cls,
        datos_planta: Dict[str, Any],
        imagen_path: Optional[Union[str, Path]] = None,
        imagen_bytes: Optional[bytes] = None,
        usuario_id: Optional[int] = None,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Analizar la salud de una planta usando Gemini.
        
        Args:
            datos_planta: Información contextual de la planta
            imagen_path: Ruta a la imagen (opcional)
            imagen_bytes: Bytes de la imagen (opcional)
            usuario_id: ID del usuario para rate limiting
            timeout: Timeout en segundos (default: config.gemini_timeout_seconds)
            
        Returns:
            Diccionario con el análisis completo:
            {
                "estado": str,
                "confianza": float,
                "resumen": str,
                "diagnostico_completo": str,
                "problemas_detectados": List[Dict],
                "recomendaciones": List[Dict],
                "metadata": Dict
            }
            
        Raises:
            GeminiServiceError: Error general del servicio
            GeminiAPIError: Error de comunicación con API
            GeminiRateLimitError: Límite de requests alcanzado
            GeminiInvalidResponseError: Respuesta inválida de Gemini
        """
        inicio = datetime.now()
        
        # Verificar API key
        if not config.gemini_api_key:
            raise GeminiServiceError(
                "GEMINI_API_KEY no configurada. "
                "Agrega tu API key en el archivo .env"
            )
        
        # Verificar rate limit
        try:
            _rate_limiter.check_rate_limit(
                user_id=usuario_id,
                per_minute=60,
                per_day=config.gemini_max_requests_per_day,
                per_user_per_day=config.gemini_max_requests_per_user_per_day
            )
        except GeminiRateLimitError as e:
            logger.warning(f"Rate limit alcanzado: {e}")
            raise
        
        # Preparar imagen si existe
        tiene_imagen = imagen_path is not None or imagen_bytes is not None
        imagen_data = None
        
        if tiene_imagen:
            try:
                imagen_data = cls._preparar_imagen(imagen_path, imagen_bytes)
                logger.info("✅ Imagen preparada para análisis")
            except Exception as e:
                logger.error(f"Error preparando imagen: {e}")
                raise GeminiAPIError(f"Error al procesar la imagen: {str(e)}")
        
        # Construir prompt
        prompt = cls._construir_prompt(datos_planta, tiene_imagen)
        
        # Configurar modelo
        try:
            model = genai.GenerativeModel(
                model_name=config.gemini_model,
                generation_config={
                    "temperature": config.gemini_temperature,
                    "max_output_tokens": config.gemini_max_output_tokens,
                }
            )
            logger.info(f"📡 Usando modelo: {config.gemini_model}")
        except Exception as e:
            logger.error(f"Error configurando modelo: {e}")
            raise GeminiAPIError(f"Error al configurar Gemini: {str(e)}")
        
        # Hacer request a Gemini
        try:
            if imagen_data:
                # Análisis con imagen
                logger.info("🖼️  Enviando análisis con imagen...")
                response = model.generate_content(
                    [prompt, {"mime_type": "image/jpeg", "data": imagen_data}]
                )
            else:
                # Análisis solo con contexto
                logger.info("📝 Enviando análisis sin imagen...")
                response = model.generate_content(
                    prompt
                )
            
            logger.info("✅ Respuesta recibida de Gemini")
            
        except Exception as e:
            logger.error(f"Error en llamada a Gemini: {e}")
            raise GeminiAPIError(f"Error comunicándose con Gemini: {str(e)}")
        
        # Parsear respuesta
        try:
            texto_respuesta = response.text
            data = cls._parsear_respuesta_json(texto_respuesta)
            data = cls._validar_respuesta(data)
            
        except GeminiInvalidResponseError:
            raise
        except Exception as e:
            logger.error(f"Error procesando respuesta: {e}")
            raise GeminiInvalidResponseError(
                f"Error al procesar respuesta de Gemini: {str(e)}"
            )
        
        # Calcular tiempo de análisis
        tiempo_ms = int((datetime.now() - inicio).total_seconds() * 1000)
        
        # Agregar metadata
        data["metadata"] = {
            "modelo": config.gemini_model,
            "version_prompt": "v1.0",
            "tiempo_analisis_ms": tiempo_ms,
            "con_imagen": tiene_imagen,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(
            f"✅ Análisis completado: {data['estado']} "
            f"({data['confianza']:.1f}% confianza) en {tiempo_ms}ms"
        )
        
        return data
    
    @classmethod
    def get_remaining_quota(cls, usuario_id: Optional[int] = None) -> Dict[str, int]:
        """
        Obtener cuota restante de análisis.
        
        Args:
            usuario_id: ID del usuario (opcional)
            
        Returns:
            Diccionario con cuotas restantes
        """
        return _rate_limiter.get_remaining_today(usuario_id)
    
    @classmethod
    def verificar_disponibilidad(cls) -> Dict[str, Any]:
        """
        Verificar que el servicio está disponible y configurado.
        
        Returns:
            Diccionario con estado del servicio
        """
        resultado = {
            "disponible": False,
            "configurado": False,
            "modelo": config.gemini_model,
            "errores": []
        }
        
        # Verificar API key
        if not config.gemini_api_key:
            resultado["errores"].append("GEMINI_API_KEY no configurada")
            return resultado
        
        resultado["configurado"] = True
        
        # Intentar un test simple
        try:
            model = genai.GenerativeModel(config.gemini_model)
            response = model.generate_content(
                "Responde solo 'OK'"
            )
            
            if "ok" in response.text.lower():
                resultado["disponible"] = True
                logger.info("✅ Servicio Gemini disponible y funcionando")
            else:
                resultado["errores"].append("Respuesta inesperada del modelo")
                
        except Exception as e:
            resultado["errores"].append(f"Error de conectividad: {str(e)}")
            logger.error(f"Error verificando Gemini: {e}")
        
        return resultado
