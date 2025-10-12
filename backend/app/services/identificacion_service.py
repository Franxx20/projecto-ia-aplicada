"""
Servicio de Identificación de Plantas.

Coordina la integración entre PlantNetService y los modelos de base de datos.
Gestiona el flujo completo de identificación: llamar PlantNet API, guardar especies
y registrar identificaciones con sus metadatos.
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from pathlib import Path
from sqlalchemy.orm import Session

from app.db.models import Especie, Identificacion, Usuario, Imagen
from app.services.plantnet_service import PlantNetService
from app.schemas.plantnet import (
    PlantNetIdentificacionResponse,
    PlantNetResultadoSimplificado
)


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
        
        # Obtener la ruta absoluta de la imagen
        # Asumiendo que imagen.ruta_archivo contiene la ruta relativa desde uploads/
        ruta_completa = Path(imagen.ruta_archivo)
        if not ruta_completa.exists():
            raise ValueError(f"Archivo de imagen no encontrado: {imagen.ruta_archivo}")
        
        # Llamar a PlantNet
        if organos is None:
            organos = ["auto"]  # Detección automática
            
        respuesta = await PlantNetService.identificar_desde_path(
            rutas_imagenes=[str(ruta_completa)],
            organos=organos
        )
        
        # Si no hay que guardar, retornar solo la respuesta
        if not guardar_resultado:
            return {
                "plantnet_response": respuesta.dict(),
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
            confianza=mejor_resultado["confianza"],
            origen="plantnet",
            validado=False,
            metadatos_ia={
                "plantnet_response": respuesta.dict(),
                "mejor_resultado": mejor_resultado,
                "organos_detectados": [
                    {
                        "organ": img.get("organ"),
                        "score": img.get("score")
                    }
                    for img in respuesta.dict().get("images", [])
                ]
            }
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
            "plantnet_response": respuesta.dict(),
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
                confianza=mejor_resultado["confianza"],
                origen="plantnet",
                validado=False,
                metadatos_ia={
                    "plantnet_response": respuesta.dict(),
                    "mejor_resultado": mejor_resultado
                }
            )
            db.add(identificacion)
            db.commit()
            db.refresh(identificacion)
        
        return {
            "imagen_id": imagen_id,
            "especie": especie.to_dict(),
            "confianza": mejor_resultado["confianza"],
            "plantnet_response": respuesta.dict(),
            "mejor_resultado": mejor_resultado
        }
    
    @staticmethod
    async def _buscar_o_crear_especie(
        db: Session,
        resultado: Dict[str, Any],
        respuesta_completa: PlantNetIdentificacionResponse
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
        if respuesta_completa.results:
            primer_resultado = respuesta_completa.results[0]
            if primer_resultado.images:
                # Tomar la primera imagen con mejor score
                mejor_imagen = max(
                    primer_resultado.images,
                    key=lambda img: img.score or 0
                )
                if hasattr(mejor_imagen, 'url') and mejor_imagen.url:
                    imagen_referencia_url = str(mejor_imagen.url.get('o'))  # Original
        
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
                    "url": ident.imagen.ruta_archivo,
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
