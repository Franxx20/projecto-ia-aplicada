"""
Servicio de Identificación de Plantas.

Coordina la integración entre PlantNetService y los modelos de base de datos.
Gestiona el flujo completo de identificación: llamar PlantNet API, guardar especies
y registrar identificaciones con sus metadatos.
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from pathlib import Path
from io import BytesIO
from sqlalchemy.orm import Session
import json
import logging

from app.db.models import Especie, Identificacion, Usuario, Imagen
from app.services.plantnet_service import PlantNetService
from app.services.imagen_service import AzureBlobService, ImagenService

logger = logging.getLogger(__name__)


class IdentificacionService:
    """Servicio para coordinar la identificación de plantas con PlantNet."""
    
    @staticmethod
    async def identificar_desde_imagen(
        db: Session,
        imagen_id: int,
        usuario_id: int,
        organos: Optional[List[str]] = None,
        guardar_resultado: bool = True
    ) -> Dict[str, Any]:
        """
        Identifica una planta desde una imagen ya subida al sistema.
        
        Args:
            db: Sesión de base de datos
            imagen_id: ID de la imagen en la base de datos
            usuario_id: ID del usuario que solicita la identificación
            organos: Lista de órganos de la planta en las imágenes
            guardar_resultado: Si True, guarda el resultado en la BD
            
        Returns:
            Dict con la respuesta de PlantNet y el ID de la identificación creada
            
        Raises:
            ValueError: Si la imagen o usuario no existen
            Exception: Si hay error en la API de PlantNet
        """
        # Verificar que la imagen existe y pertenece al usuario
        imagen = db.query(Imagen).filter(
            Imagen.id == imagen_id,
            Imagen.usuario_id == usuario_id
        ).first()
        
        if not imagen:
            raise ValueError(f"Imagen {imagen_id} no encontrada o no pertenece al usuario")
        
        # Descargar la imagen desde Azure Blob Storage
        try:
            azure_service = AzureBlobService()
            imagen_bytes_content = azure_service.descargar_blob(imagen.nombre_blob)
            imagen_bytes = BytesIO(imagen_bytes_content)
            imagen_bytes.name = imagen.nombre_archivo
        except Exception as e:
            raise ValueError(f"Error al descargar imagen desde Azure: {str(e)}")
        
        # Llamar a PlantNet con la imagen descargada
        if organos is None:
            organos = ["auto"]  # Detección automática
            
        respuesta = await PlantNetService.identificar_planta(
            imagenes=[(imagen.nombre_archivo, imagen_bytes)],
            organos=organos,
            include_related_images=True  # Incluir imágenes de referencia para mostrar en UI
        )
        
        # Si no hay que guardar, retornar solo la respuesta
        if not guardar_resultado:
            return {
                "plantnet_response": respuesta,
                "identificacion_id": None
            }
        
        # Obtener el mejor resultado
        mejor_resultado = PlantNetService.extraer_mejor_resultado(respuesta)
        
        # Buscar o crear la especie en la base de datos
        especie = await IdentificacionService._buscar_o_crear_especie(
            db=db,
            resultado=mejor_resultado,
            respuesta_completa=respuesta
        )
        
        # Crear el registro de identificación
        identificacion = Identificacion(
            usuario_id=usuario_id,
            imagen_id=imagen_id,
            especie_id=especie.id,
            confianza=int(mejor_resultado["score"] * 100),  # Convertir 0.0-1.0 a 0-100
            origen="plantnet",
            validado=False,
            metadatos_ia=json.dumps({  # Serializar a JSON string
                "plantnet_response": respuesta,
                "mejor_resultado": mejor_resultado,
                "organos_detectados": [
                    {
                        "organ": img.get("organ"),
                        "score": img.get("score")
                    }
                    for img in respuesta.get("images", [])
                ]
            }, default=str)  # default=str maneja objetos datetime
        )
        
        db.add(identificacion)
        db.commit()
        db.refresh(identificacion)
        
        return {
            "identificacion_id": identificacion.id,
            "especie": especie.to_dict(),
            "confianza": identificacion.confianza,
            "confianza_porcentaje": identificacion.confianza_porcentaje,
            "es_confiable": identificacion.es_confiable,
            "plantnet_response": respuesta,
            "mejor_resultado": mejor_resultado
        }
    
    @staticmethod
    async def identificar_desde_archivo(
        db: Session,
        ruta_archivo: str,
        usuario_id: int,
        organos: Optional[List[str]] = None,
        guardar_imagen: bool = True
    ) -> Dict[str, Any]:
        """
        Identifica una planta desde un archivo (sin registro previo de Imagen).
        
        Args:
            db: Sesión de base de datos
            ruta_archivo: Ruta al archivo de imagen
            usuario_id: ID del usuario
            organos: Lista de órganos de la planta
            guardar_imagen: Si True, crea un registro de Imagen
            
        Returns:
            Dict con la respuesta de PlantNet y datos de identificación
        """
        # Verificar que el archivo existe
        ruta_completa = Path(ruta_archivo)
        if not ruta_completa.exists():
            raise ValueError(f"Archivo no encontrado: {ruta_archivo}")
        
        # Llamar a PlantNet
        if organos is None:
            organos = ["auto"]
            
        respuesta = await PlantNetService.identificar_desde_path(
            rutas_imagenes=[str(ruta_completa)],
            organos=organos
        )
        
        # Obtener el mejor resultado
        mejor_resultado = PlantNetService.extraer_mejor_resultado(respuesta)
        
        # Buscar o crear la especie
        especie = await IdentificacionService._buscar_o_crear_especie(
            db=db,
            resultado=mejor_resultado,
            respuesta_completa=respuesta
        )
        
        # Si se solicita guardar la imagen, crear el registro
        imagen_id = None
        if guardar_imagen:
            # Crear registro de imagen básico
            imagen = Imagen(
                usuario_id=usuario_id,
                ruta_archivo=str(ruta_archivo),
                nombre_archivo=ruta_completa.name,
                tipo_mime="image/jpeg",  # Asumiendo JPEG, debería detectarse
                tamano_bytes=ruta_completa.stat().st_size
            )
            db.add(imagen)
            db.commit()
            db.refresh(imagen)
            imagen_id = imagen.id
            
            # Crear identificación
            identificacion = Identificacion(
                usuario_id=usuario_id,
                imagen_id=imagen_id,
                especie_id=especie.id,
                confianza=int(mejor_resultado["score"] * 100),  # Convertir 0.0-1.0 a 0-100
                origen="plantnet",
                validado=False,
                metadatos_ia=json.dumps({  # Serializar a JSON string
                    "plantnet_response": respuesta,
                    "mejor_resultado": mejor_resultado
                }, default=str)  # default=str maneja objetos datetime
            )
            db.add(identificacion)
            db.commit()
            db.refresh(identificacion)
        
        return {
            "imagen_id": imagen_id,
            "especie": especie.to_dict(),
            "confianza": mejor_resultado["score"],
            "plantnet_response": respuesta,
            "mejor_resultado": mejor_resultado
        }
    
    @staticmethod
    async def _buscar_o_crear_especie(
        db: Session,
        resultado: Dict[str, Any],
        respuesta_completa: Dict[str, Any]
    ) -> Especie:
        """
        Busca una especie en la BD por nombre científico o la crea si no existe.
        
        Args:
            db: Sesión de base de datos
            resultado: Resultado simplificado de PlantNet
            respuesta_completa: Respuesta completa de PlantNet para metadatos
            
        Returns:
            Instancia de Especie (existente o nueva)
        """
        nombre_cientifico = resultado["nombre_cientifico"]
        
        # Buscar especie existente
        especie = db.query(Especie).filter(
            Especie.nombre_cientifico == nombre_cientifico
        ).first()
        
        if especie:
            return especie
        
        # Crear nueva especie
        # Extraer nombre común del resultado
        nombres_comunes = resultado.get("nombres_comunes", [])
        nombre_comun = nombres_comunes[0] if nombres_comunes else nombre_cientifico
        
        # Buscar imagen de referencia
        imagen_referencia_url = None
        results = respuesta_completa.get("results", [])
        if results:
            primer_resultado = results[0]
            images = primer_resultado.get("images", [])
            if images:
                # Tomar la primera imagen con mejor score
                mejor_imagen = max(
                    images,
                    key=lambda img: img.get("score", 0)
                )
                url_obj = mejor_imagen.get("url", {})
                if url_obj:
                    imagen_referencia_url = url_obj.get("o")  # Original
        
        especie = Especie(
            nombre_comun=nombre_comun,
            nombre_cientifico=nombre_cientifico,
            familia=resultado.get("familia", "Desconocida"),
            descripcion=f"Especie identificada automáticamente por PlantNet. {resultado.get('familia', '')}",
            # Valores por defecto conservadores
            nivel_dificultad="medio",
            luz_requerida="luz_indirecta",
            riego_frecuencia="semanal",
            temperatura_min=15.0,
            temperatura_max=30.0,
            humedad_requerida=50.0,
            imagen_referencia_url=imagen_referencia_url,
            is_active=True
        )
        
        db.add(especie)
        db.commit()
        db.refresh(especie)
        
        return especie
    
    @staticmethod
    def obtener_historial_usuario(
        db: Session,
        usuario_id: int,
        limite: int = 50,
        offset: int = 0,
        solo_validadas: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Obtiene el historial de identificaciones de un usuario.
        
        Args:
            db: Sesión de base de datos
            usuario_id: ID del usuario
            limite: Número máximo de resultados
            offset: Desplazamiento para paginación
            solo_validadas: Si True, solo retorna identificaciones validadas
            
        Returns:
            Lista de identificaciones con información de especie e imagen
        """
        query = db.query(Identificacion).filter(
            Identificacion.usuario_id == usuario_id
        )
        
        if solo_validadas:
            query = query.filter(Identificacion.validado == True)
        
        identificaciones = query.order_by(
            Identificacion.fecha_identificacion.desc()
        ).limit(limite).offset(offset).all()
        
        resultados = []
        for ident in identificaciones:
            resultado = {
                "id": ident.id,
                "fecha": ident.fecha_identificacion.isoformat(),
                "confianza": ident.confianza,
                "confianza_porcentaje": ident.confianza_porcentaje,
                "es_confiable": ident.es_confiable,
                "validado": ident.validado,
                "origen": ident.origen,
                "especie": {
                    "id": ident.especie.id,
                    "nombre_comun": ident.especie.nombre_comun,
                    "nombre_cientifico": ident.especie.nombre_cientifico,
                    "familia": ident.especie.familia,
                    "imagen_url": ident.especie.imagen_referencia_url
                },
                "imagen": {
                    "id": ident.imagen.id,
                    "url": ident.imagen.url_blob,
                    "nombre": ident.imagen.nombre_archivo
                }
            }
            resultados.append(resultado)
        
        return resultados
    
    @staticmethod
    def validar_identificacion(
        db: Session,
        identificacion_id: int,
        usuario_id: int,
        notas: Optional[str] = None
    ) -> Identificacion:
        """
        Valida una identificación realizada por IA.
        
        Args:
            db: Sesión de base de datos
            identificacion_id: ID de la identificación
            usuario_id: ID del usuario (debe ser el propietario)
            notas: Notas opcionales sobre la validación
            
        Returns:
            Identificación actualizada
            
        Raises:
            ValueError: Si la identificación no existe o no pertenece al usuario
        """
        identificacion = db.query(Identificacion).filter(
            Identificacion.id == identificacion_id,
            Identificacion.usuario_id == usuario_id
        ).first()
        
        if not identificacion:
            raise ValueError(
                f"Identificación {identificacion_id} no encontrada o no pertenece al usuario"
            )
        
        identificacion.validar(notas)
        db.commit()
        db.refresh(identificacion)
        
        return identificacion
    
    @staticmethod
    async def obtener_quota_info() -> Dict[str, Any]:
        """
        Obtiene información sobre la cuota de requests de PlantNet.
        
        Returns:
            Dict con información de cuota (requests realizados, restantes, límite)
        """
        return PlantNetService.obtener_requests_restantes()
    
    @staticmethod
    async def identificar_desde_multiples_imagenes(
        db: Session,
        imagenes: List[tuple],  # Lista de (UploadFile, organ: str)
        usuario_id: int,
        guardar_resultado: bool = True
    ) -> Dict[str, Any]:
        """
        Identifica una planta desde múltiples imágenes (T-022).
        
        Procesa de 1 a 5 imágenes con sus respectivos órganos, las sube a Azure,
        llama a PlantNet API y guarda los resultados en la base de datos.
        
        Args:
            db: Sesión de base de datos
            imagenes: Lista de tuplas (UploadFile, organ_str)
            usuario_id: ID del usuario que solicita la identificación
            guardar_resultado: Si True, guarda el resultado en la BD
            
        Returns:
            Dict con la respuesta de PlantNet formateada según IdentificacionResponse
            
        Raises:
            ValueError: Si el número de imágenes es inválido o hay errores de validación
            Exception: Si hay error en la API de PlantNet
        """
        # Validar número de imágenes (1-5 según T-022)
        if len(imagenes) < 1 or len(imagenes) > 5:
            raise ValueError("Debe proporcionar entre 1 y 5 imágenes")
        
        # Crear instancia de ImagenService
        imagen_service = ImagenService(db)
        
        # Guardar todas las imágenes en Azure y crear registros en DB
        imagenes_guardadas = []
        for upload_file, organ in imagenes:
            imagen_guardada = await imagen_service.subir_imagen(
                archivo=upload_file,
                usuario_id=usuario_id
            )
            imagenes_guardadas.append({
                "imagen_db": imagen_guardada,
                "organ": organ,
                "url": imagen_guardada.url_blob
            })
        
        # Preparar imágenes para PlantNet
        azure_service = AzureBlobService()
        imagenes_para_plantnet = []
        organos_para_plantnet = []
        
        for img_data in imagenes_guardadas:
            # Descargar contenido desde Azure
            try:
                imagen_bytes_content = azure_service.descargar_blob(
                    img_data["imagen_db"].nombre_blob
                )
                # NO usar BytesIO, pasar bytes directamente
                # BytesIO causa problemas con httpx AsyncClient porque tiene operaciones síncronas
                imagenes_para_plantnet.append(
                    (img_data["imagen_db"].nombre_archivo, imagen_bytes_content)
                )
                organos_para_plantnet.append(img_data["organ"])
            except Exception as e:
                raise ValueError(
                    f"Error al descargar imagen desde Azure: {str(e)}"
                )
        
        # Llamar a PlantNet con múltiples imágenes
        respuesta = await PlantNetService.identificar_planta(
            imagenes=imagenes_para_plantnet,
            organos=organos_para_plantnet,
            include_related_images=True  # Incluir imágenes de referencia para mostrar en UI
        )
        
        # Si no hay que guardar, retornar solo la respuesta
        if not guardar_resultado:
            return {
                "plantnet_response": respuesta,
                "identificacion_id": None,
                "imagenes": imagenes_guardadas
            }
        
        # Obtener el mejor resultado
        mejor_resultado = PlantNetService.extraer_mejor_resultado(respuesta)
        
        # Buscar o crear la especie en la base de datos
        especie = await IdentificacionService._buscar_o_crear_especie(
            db=db,
            resultado=mejor_resultado,
            respuesta_completa=respuesta
        )
        
        # Crear el registro de identificación (sin imagen_id inicialmente)
        identificacion = Identificacion(
            usuario_id=usuario_id,
            imagen_id=None,  # Para múltiples imágenes, no usamos imagen_id
            especie_id=especie.id,
            confianza=int(mejor_resultado["score"] * 100),
            origen="plantnet",
            validado=False,
            metadatos_ia=json.dumps({
                "mejor_resultado": {
                    "nombre_cientifico": mejor_resultado["nombre_cientifico"],
                    "nombres_comunes": mejor_resultado["nombres_comunes"][:3],  # Solo primeros 3 nombres
                    "familia": mejor_resultado["familia"],
                    "score": mejor_resultado["score"]
                },
                "organos_detectados": [
                    {
                        "organ": img.get("organ"),
                        "score": img.get("score")
                    }
                    for img in respuesta.get("images", [])
                ],
                "num_imagenes": len(imagenes_guardadas),
                "resultados_alternativos": len(respuesta.get("results", [])),
                "requests_restantes": respuesta.get("remainingIdentificationRequests")
            }, default=str)
        )
        
        db.add(identificacion)
        db.commit()
        db.refresh(identificacion)
        
        # Actualizar todas las imágenes con el identificacion_id
        for img_data in imagenes_guardadas:
            img_db = img_data["imagen_db"]
            img_db.identificacion_id = identificacion.id
            img_db.organ = img_data["organ"]
            db.add(img_db)
        
        db.commit()
        
        # Formatear respuesta según IdentificacionResponse schema
        # IMPORTANTE: Incluir plantnet_response para que el frontend pueda mostrar
        # resultados alternativos y permitir al usuario elegir la especie correcta
        respuesta_formateada = {
            "id": identificacion.id,
            "identificacion_id": identificacion.id,
            "especie": {
                "nombre_cientifico": mejor_resultado["nombre_cientifico"],
                "nombre_comun": mejor_resultado["nombres_comunes"][0] if mejor_resultado["nombres_comunes"] else mejor_resultado["nombre_cientifico"],
                "familia": mejor_resultado["familia"],
            },
            "confianza": identificacion.confianza,
            "confianza_porcentaje": f"{identificacion.confianza}%",
            "es_confiable": identificacion.es_confiable,
            "imagenes": [
                {
                    "id": img_data["imagen_db"].id,
                    "url": img_data["url"],
                    "organ": img_data["organ"],
                    "nombre_archivo": img_data["imagen_db"].nombre_archivo
                }
                for img_data in imagenes_guardadas
            ],
            "fecha_identificacion": identificacion.fecha_identificacion.isoformat(),
            "validado": identificacion.validado,
            "origen": identificacion.origen,
            "plantnet_response": respuesta,  # Respuesta completa para mostrar alternativas
            "metadatos_plantnet": {
                "version": respuesta.get("version", ""),
                "proyecto": respuesta.get("query", {}).get("project", ""),
                "resultados_alternativos": len(respuesta.get("results", [])),
                "requests_restantes": respuesta.get("remainingIdentificationRequests")
            }
        }
        
        logger.info(f"Respuesta formateada para múltiples imágenes: id={respuesta_formateada['id']}, identificacion_id={respuesta_formateada['identificacion_id']}")
        
        return respuesta_formateada
