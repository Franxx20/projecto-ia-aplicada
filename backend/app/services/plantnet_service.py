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
import asyncio
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
        
        Nota T-022:
            Si un órgano es "sin_especificar", se omite del request a PlantNet.
            Las imágenes sin órgano especificado se envían sin el parámetro organs correspondiente.
        
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
        
        # T-022: Filtrar órganos válidos
        # Si el órgano es "sin_especificar", NO lo enviamos a PlantNet (detección automática)
        # Solo enviamos órganos explícitamente especificados
        organos_para_plantnet = []
        for organo in organos:
            if organo == "sin_especificar":
                # No agregar nada - PlantNet hará detección automática
                continue
            elif organo not in cls.ORGANOS_VALIDOS:
                raise ValueError(
                    f"Órgano '{organo}' inválido. Valores válidos: {', '.join(cls.ORGANOS_VALIDOS)}"
                )
            else:
                # Agregar órgano válido especificado
                organos_para_plantnet.append(organo)
        
        logger.info(
            f"Preparando request: {len(imagenes)} imágenes, "
            f"{len(organos_para_plantnet)} órganos especificados: {organos_para_plantnet}"
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
        
        # Query parameters
        params = {
            "api-key": settings.plantnet_api_key,
            "include-related-images": str(include_related_images).lower(),
            "nb-results": nb_results,
            "lang": lang
        }
        
        try:
            # Preparar archivos - convertir a bytes si es necesario
            archivos_preparados = []
            for nombre_archivo, contenido in imagenes:
                # Si contenido es BytesIO u otro stream, leerlo completamente
                if hasattr(contenido, 'read'):
                    if hasattr(contenido, 'seek'):
                        contenido.seek(0)  # Asegurar posición inicial
                    imagen_bytes = contenido.read()
                else:
                    imagen_bytes = contenido
                
                archivos_preparados.append((nombre_archivo, imagen_bytes))
            
            logger.info(
                f"Enviando request a PlantNet API: {url} con {len(imagenes)} imagen(es) "
                f"y órganos especificados: {organos_para_plantnet}"
            )
            
            # Debug: verificar estructura de archivos_preparados
            logger.debug(f"Archivos preparados: {[(nombre, type(contenido).__name__, len(contenido) if isinstance(contenido, bytes) else 'N/A') for nombre, contenido in archivos_preparados]}")
            
            # Función síncrona para hacer el request con httpx.Client
            def _hacer_request_sincrono():
                try:
                    with httpx.Client(timeout=30.0) as client:
                        # Construir data como lista de tuplas para órganos repetidos
                        # Solo enviamos organs si hay órganos especificados (no "sin_especificar")
                        data_list = []
                        for organo in organos_para_plantnet:
                            data_list.append(("organs", organo))
                        
                        # Construir files para multipart/form-data
                        # httpx espera: lista de tuplas (field_name, file_tuple)
                        # file_tuple puede ser: (filename, content, content_type)
                        files_to_upload = []
                        for nombre, img_bytes in archivos_preparados:
                            if not isinstance(img_bytes, bytes):
                                logger.error(f"Error: contenido no es bytes, es {type(img_bytes)}")
                                raise ValueError(f"El contenido de la imagen debe ser bytes, no {type(img_bytes)}")
                            
                            # Formato: (field_name, (filename, bytes, content_type))
                            files_to_upload.append(("images", (nombre, img_bytes, "image/jpeg")))
                        
                        logger.debug(f"Files list construida con {len(files_to_upload)} archivos")
                        
                        # Hacer request POST con multipart/form-data
                        response = client.post(
                            url,
                            params=params,
                            files=files_to_upload,
                            data=data_list if data_list else None  # Solo enviar data si hay órganos
                        )
                        
                        # Verificar respuesta
                        response.raise_for_status()
                        
                        return response.json()
                except Exception as e:
                    import traceback
                    logger.error(f"Error en _hacer_request_sincrono: {str(e)}")
                    logger.error(f"Traceback completo:\n{traceback.format_exc()}")
                    raise
            
            # Ejecutar el request síncrono en un thread separado
            resultado = await asyncio.to_thread(_hacer_request_sincrono)
            
            # Incrementar contador
            cls._incrementar_contador_requests()
            
            # Parsear respuesta JSON
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
