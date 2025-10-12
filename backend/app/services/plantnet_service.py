"""
Servicio para integración con PlantNet API.

Este módulo proporciona funcionalidades para identificar plantas usando la API de PlantNet.
Documentación oficial: https://my.plantnet.org/doc/getting-started/introduction

Límites:
    - Máximo 500 requests por día (plan gratuito)
    - Hasta 5 imágenes por request
    - Tamaño máximo total: 50 MB
    - Formatos permitidos: JPEG, PNG
"""

import httpx
import logging
from typing import List, Optional, Dict, Any, BinaryIO, Tuple
from datetime import datetime, timedelta
from pathlib import Path

from app.core.config import settings

# Configurar logger
logger = logging.getLogger(__name__)


class PlantNetService:
    """
    Servicio para interactuar con la API de PlantNet.
    
    La API de PlantNet permite identificar especies de plantas a partir de imágenes.
    Se envían imágenes junto con el tipo de órgano (hoja, flor, fruto, corteza)
    y se recibe una lista de especies probables con scores de confianza.
    """
    
    # Contador de requests diarios (en memoria - en producción usar Redis/DB)
    _requests_today: int = 0
    _last_reset_date: datetime = datetime.now().date()
    
    # Órganos válidos según documentación de PlantNet
    ORGANOS_VALIDOS = ["leaf", "flower", "fruit", "bark", "auto"]
    
    # Proyectos disponibles (floras geográficas)
    PROYECTOS_DISPONIBLES = [
        "all",  # Todas las especies (por defecto)
        "k-world-flora",  # Flora mundial
        "k-western-europe",  # Europa occidental
        "k-southern-america",  # América del Sur
        # ... agregar más según necesidad
    ]
    
    @classmethod
    def _verificar_limite_requests(cls) -> bool:
        """
        Verifica si se ha alcanzado el límite diario de requests.
        
        Resetea el contador si es un nuevo día.
        
        Returns:
            bool: True si aún hay requests disponibles, False si se alcanzó el límite
        """
        hoy = datetime.now().date()
        
        # Resetear contador si es un nuevo día
        if hoy > cls._last_reset_date:
            cls._requests_today = 0
            cls._last_reset_date = hoy
            logger.info("Contador de requests de PlantNet reseteado para el nuevo día")
        
        # Verificar si se alcanzó el límite
        if cls._requests_today >= settings.plantnet_max_requests_per_day:
            logger.warning(
                f"Límite diario de requests alcanzado: {cls._requests_today}/{settings.plantnet_max_requests_per_day}"
            )
            return False
        
        return True
    
    @classmethod
    def _incrementar_contador_requests(cls):
        """Incrementa el contador de requests del día."""
        cls._requests_today += 1
        logger.info(
            f"Requests de PlantNet hoy: {cls._requests_today}/{settings.plantnet_max_requests_per_day}"
        )
    
    @classmethod
    def obtener_requests_restantes(cls) -> Dict[str, int]:
        """
        Obtiene información sobre los requests restantes.
        
        Returns:
            Dict con 'requests_hoy', 'limite_diario' y 'restantes'
        """
        hoy = datetime.now().date()
        if hoy > cls._last_reset_date:
            cls._requests_today = 0
            cls._last_reset_date = hoy
        
        return {
            "requests_hoy": cls._requests_today,
            "limite_diario": settings.plantnet_max_requests_per_day,
            "restantes": settings.plantnet_max_requests_per_day - cls._requests_today
        }
    
    @classmethod
    async def identificar_planta(
        cls,
        imagenes: List[Tuple[str, BinaryIO]],  # Lista de (filename, file_content)
        organos: List[str],
        project: Optional[str] = None,
        include_related_images: bool = False,
        nb_results: int = 10,
        lang: str = "es"
    ) -> Dict[str, Any]:
        """
        Identifica una planta usando la API de PlantNet.
        
        Según documentación oficial:
        - Endpoint: POST /v2/identify/{project}?api-key=YOUR_API_KEY
        - Content-Type: multipart/form-data
        - Parámetros:
            * images: Archivos binarios (JPEG/PNG, hasta 5)
            * organs: Tipo de órgano por cada imagen (leaf, flower, fruit, bark, auto)
            * include-related-images: Retornar imágenes similares (opcional)
            * nb-results: Limitar número de resultados (opcional)
            * lang: Código de idioma (opcional)
        
        Args:
            imagenes: Lista de tuplas (nombre_archivo, contenido_binario)
            organos: Lista de tipos de órgano correspondientes a cada imagen
            project: Proyecto/flora a usar (default: settings.plantnet_project)
            include_related_images: Si se incluyen imágenes relacionadas
            nb_results: Número máximo de resultados a retornar
            lang: Código de idioma para nombres comunes (es, en, fr, etc.)
        
        Returns:
            Dict con la respuesta de PlantNet incluyendo:
                - results: Lista de especies probables con scores
                - bestMatch: Nombre científico del mejor match
                - remainingIdentificationRequests: Requests restantes del día
                - version: Versión del motor de IA
        
        Raises:
            ValueError: Si los parámetros son inválidos
            RuntimeError: Si se alcanzó el límite diario de requests
            httpx.HTTPStatusError: Si la API retorna error
        """
        # Validaciones
        if not imagenes:
            raise ValueError("Debe proporcionar al menos una imagen")
        
        if len(imagenes) > 5:
            raise ValueError("Máximo 5 imágenes por request según documentación PlantNet")
        
        if len(imagenes) != len(organos):
            raise ValueError("Número de imágenes debe coincidir con número de órganos")
        
        for organo in organos:
            if organo not in cls.ORGANOS_VALIDOS:
                raise ValueError(
                    f"Órgano '{organo}' inválido. Valores válidos: {', '.join(cls.ORGANOS_VALIDOS)}"
                )
        
        # Verificar límite de requests
        if not cls._verificar_limite_requests():
            raise RuntimeError(
                f"Límite diario de requests alcanzado ({settings.plantnet_max_requests_per_day}). "
                "Intente nuevamente mañana."
            )
        
        # Usar proyecto por defecto si no se especifica
        project = project or settings.plantnet_project
        
        # Construir URL con API key como query parameter (según documentación)
        url = f"{settings.plantnet_api_url}/{project}"
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Preparar multipart/form-data según documentación oficial
                files = []
                for nombre_archivo, contenido in imagenes:
                    files.append(("images", (nombre_archivo, contenido, "image/jpeg")))
                
                # Parámetros adicionales como form data
                data = {}
                for idx, organo in enumerate(organos):
                    data["organs"] = organo  # PlantNet espera múltiples valores con mismo key
                
                # Query parameters
                params = {
                    "api-key": settings.plantnet_api_key,
                    "include-related-images": str(include_related_images).lower(),
                    "nb-results": nb_results,
                    "lang": lang
                }
                
                logger.info(f"Enviando request a PlantNet API: {url} con {len(imagenes)} imagen(es)")
                
                # Hacer request POST
                response = await client.post(
                    url,
                    params=params,
                    files=files,
                    data={"organs": organos}  # Enviar órganos como array
                )
                
                # Verificar respuesta
                response.raise_for_status()
                
                # Incrementar contador
                cls._incrementar_contador_requests()
                
                # Parsear respuesta JSON
                resultado = response.json()
                
                logger.info(
                    f"PlantNet identificó: {resultado.get('bestMatch', 'N/A')} "
                    f"(Requests restantes: {resultado.get('remainingIdentificationRequests', 'N/A')})"
                )
                
                return resultado
                
        except httpx.HTTPStatusError as e:
            logger.error(f"Error HTTP de PlantNet API: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Error de conexión con PlantNet API: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error inesperado en PlantNet API: {str(e)}")
            raise
    
    @classmethod
    async def identificar_desde_path(
        cls,
        rutas_imagenes: List[str],
        organos: List[str],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Versión simplificada que acepta rutas de archivos en lugar de contenido binario.
        
        Args:
            rutas_imagenes: Lista de rutas a archivos de imagen
            organos: Lista de tipos de órgano
            **kwargs: Argumentos adicionales para identificar_planta()
        
        Returns:
            Dict con respuesta de PlantNet
        """
        if len(rutas_imagenes) != len(organos):
            raise ValueError("Número de rutas debe coincidir con número de órganos")
        
        imagenes = []
        for ruta in rutas_imagenes:
            path = Path(ruta)
            if not path.exists():
                raise FileNotFoundError(f"Archivo no encontrado: {ruta}")
            
            with open(path, "rb") as f:
                contenido = f.read()
                imagenes.append((path.name, contenido))
        
        return await cls.identificar_planta(imagenes, organos, **kwargs)
    
    @classmethod
    def extraer_mejor_resultado(cls, respuesta: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Extrae y formatea el mejor resultado de identificación.
        
        Args:
            respuesta: Respuesta completa de PlantNet API
        
        Returns:
            Dict con información del mejor match o None si no hay resultados
        """
        results = respuesta.get("results", [])
        if not results:
            return None
        
        mejor = results[0]
        species_info = mejor.get("species", {})
        
        return {
            "nombre_cientifico": species_info.get("scientificName", ""),
            "nombre_cientifico_sin_autor": species_info.get("scientificNameWithoutAuthor", ""),
            "autor": species_info.get("scientificNameAuthorship", ""),
            "nombres_comunes": species_info.get("commonNames", []),
            "genero": species_info.get("genus", {}).get("scientificNameWithoutAuthor", ""),
            "familia": species_info.get("family", {}).get("scientificNameWithoutAuthor", ""),
            "score": mejor.get("score", 0.0),
            "confianza_porcentaje": round(mejor.get("score", 0.0) * 100, 2),
            "gbif_id": mejor.get("gbif", {}).get("id"),
            "powo_id": mejor.get("powo", {}).get("id")
        }
    
    @classmethod
    def formatear_respuesta_completa(cls, respuesta: Dict[str, Any]) -> Dict[str, Any]:
        """
        Formatea la respuesta completa de PlantNet para uso interno.
        
        Args:
            respuesta: Respuesta completa de PlantNet API
        
        Returns:
            Dict formateado con información relevante
        """
        results = respuesta.get("results", [])
        
        resultados_formateados = []
        for result in results[:10]:  # Top 10
            species_info = result.get("species", {})
            resultados_formateados.append({
                "nombre_cientifico": species_info.get("scientificName", ""),
                "nombres_comunes": species_info.get("commonNames", []),
                "familia": species_info.get("family", {}).get("scientificNameWithoutAuthor", ""),
                "score": result.get("score", 0.0),
                "confianza_porcentaje": round(result.get("score", 0.0) * 100, 2)
            })
        
        return {
            "mejor_match": respuesta.get("bestMatch", ""),
            "resultados": resultados_formateados,
            "version_ia": respuesta.get("version", ""),
            "requests_restantes_api": respuesta.get("remainingIdentificationRequests"),
            "organos_detectados": respuesta.get("predictedOrgans", []),
            "proyecto_usado": respuesta.get("query", {}).get("project", "")
        }
