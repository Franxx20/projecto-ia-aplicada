"""
Router de plantas - Endpoints para gestión del jardín del usuario.

Este módulo contiene todos los endpoints REST para el CRUD de plantas
y consulta de estadísticas del jardín personal del usuario.

Autor: Equipo Backend
Fecha: Octubre 2025
Sprint: Sprint 2 - T-014
"""

from datetime import datetime
from typing import List, Optional
import logging
import threading
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.db.session import get_db
from app.db.models import Planta, Usuario, Imagen
from app.schemas.planta import (
    PlantaCreate,
    PlantaUpdate,
    PlantaResponse,
    PlantaStats,
    PlantaListResponse,
    RegistrarRiegoRequest,
    RegistrarFertilizacionRequest,
    AgregarPlantaDesdeIdentificacionRequest,
    PlantaUsuarioResponse
)
from app.services.planta_service import PlantaService
from app.utils.jwt import get_current_user
from app.db.models import Usuario, Imagen

# Configurar logger
logger = logging.getLogger(__name__)

# Crear router de plantas
router = APIRouter()


# ==================== FUNCIÓN DE ANÁLISIS EN BACKGROUND ====================

def ejecutar_analisis_inicial_background(
    planta_id: int,
    usuario_id: int,
    identificacion_id: int,
    db_url: str
):
    """
    Ejecuta el análisis inicial de Gemini en segundo plano.
    
    Esta función se ejecuta como tarea de background para evitar que
    la creación de la planta se congele esperando la respuesta de Gemini.
    
    Args:
        planta_id: ID de la planta recién creada
        usuario_id: ID del usuario propietario
        identificacion_id: ID de la identificación original
        db_url: URL de conexión a la base de datos
    """
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.services.gemini_service import GeminiService
    from app.db.models import Planta, Imagen, Especie, Identificacion, AnalisisSalud
    from app.services.imagen_service import AzureBlobService
    import json
    
    # Crear nueva sesión de DB para el background task
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        logger.info(f"🔄 Iniciando análisis en background para planta {planta_id}")
        
        # Obtener la planta
        planta = db.query(Planta).filter(Planta.id == planta_id).first()
        if not planta:
            logger.error(f"❌ Planta {planta_id} no encontrada para análisis")
            return
        
        # Obtener las imágenes de la identificación
        imagenes_bytes_list = []
        imagenes_ids_list = []
        azure_service = AzureBlobService()
        
        identificacion = db.query(Identificacion).filter(
            Identificacion.id == identificacion_id
        ).first()
        
        if identificacion:
            imagenes = db.query(Imagen).filter(
                Imagen.identificacion_id == identificacion.id
            ).order_by(Imagen.created_at).limit(5).all()
            
            logger.info(f"📸 Encontradas {len(imagenes)} imágenes para análisis")
            
            for imagen in imagenes:
                try:
                    imagen_bytes = azure_service.descargar_blob(imagen.nombre_blob)
                    imagenes_bytes_list.append(imagen_bytes)
                    imagenes_ids_list.append(imagen.id)
                    logger.info(f"✅ Imagen {imagen.id} descargada")
                except Exception as e:
                    logger.error(f"❌ Error descargando imagen {imagen.id}: {str(e)}")
                    continue
        
        # Si no hay imágenes de identificación, usar imagen principal
        if not imagenes_bytes_list and planta.imagen_principal_id:
            imagen = db.query(Imagen).filter(Imagen.id == planta.imagen_principal_id).first()
            if imagen:
                try:
                    imagen_bytes = azure_service.descargar_blob(imagen.nombre_blob)
                    imagenes_bytes_list.append(imagen_bytes)
                    imagenes_ids_list.append(imagen.id)
                    logger.info(f"✅ Imagen principal descargada")
                except Exception as e:
                    logger.warning(f"⚠️  Error descargando imagen principal: {str(e)}")
        
        # Obtener información de la especie
        especie_nombre = "Desconocida"
        especie_cientifica = None
        familia = "Desconocida"
        
        if planta.especie_id:
            especie = db.query(Especie).filter(Especie.id == planta.especie_id).first()
            if especie:
                especie_nombre = especie.nombre_comun or "Desconocida"
                especie_cientifica = especie.nombre_cientifico
                familia = especie.familia or "Desconocida"
        
        # Construir contexto
        contexto_planta = {
            "nombre_personal": planta.nombre_personal,
            "nombre_cientifico": especie_cientifica or "Desconocida",
            "nombre_comun": especie_nombre,
            "familia": familia,
            "dias_desde_adquisicion": 0,
            "ubicacion": planta.ubicacion or "No especificada",
            "luz_actual": planta.luz_actual or "No especificada",
            "dias_desde_riego": "N/A",
            "frecuencia_riego_dias": planta.frecuencia_riego_dias or "N/A",
            "estado_riego": "normal",
            "estado_salud": "desconocido",
            "fecha_ultimo_analisis": "Nunca",
            "notas": f"{planta.notas or ''}\\n\\n📸 Análisis inicial automático de la planta recién agregada."
        }
        
        # Ejecutar análisis con Gemini
        logger.info(f"🤖 Llamando a Gemini para análisis de planta {planta_id}...")
        inicio_analisis = datetime.utcnow()
        
        gemini_service = GeminiService()
        resultado_gemini = gemini_service.analizar_salud_planta(
            datos_planta=contexto_planta,
            imagenes_bytes_list=imagenes_bytes_list if imagenes_bytes_list else None,
            usuario_id=usuario_id,
            es_analisis_inicial=True
        )
        
        tiempo_total = (datetime.utcnow() - inicio_analisis).total_seconds()
        logger.info(f"✅ Análisis completado en {tiempo_total:.2f}s")
        
        # Crear registro de análisis
        metadata = resultado_gemini.get("metadata", {})
        metadata["imagenes_ids"] = imagenes_ids_list
        metadata["num_imagenes_analizadas"] = len(imagenes_ids_list)
        metadata["ejecutado_en_background"] = True
        
        nuevo_analisis = AnalisisSalud(
            planta_id=planta.id,
            usuario_id=usuario_id,
            imagen_id=planta.imagen_principal_id,
            estado=resultado_gemini["estado"],
            confianza=resultado_gemini["confianza"],
            resumen_diagnostico=resultado_gemini["resumen"],
            diagnostico_detallado=resultado_gemini.get("diagnostico_completo"),
            problemas_detectados=json.dumps(resultado_gemini.get("problemas_detectados", []), ensure_ascii=False),
            recomendaciones=json.dumps(resultado_gemini.get("recomendaciones", []), ensure_ascii=False),
            metadatos_ia=json.dumps(metadata, ensure_ascii=False),
            modelo_ia_usado=metadata.get("modelo", "gemini-2.5-flash"),
            tiempo_analisis_ms=metadata.get("tiempo_analisis_ms", 0),
            version_prompt=metadata.get("version_prompt", "v1.0"),
            con_imagen=metadata.get("con_imagen", len(imagenes_bytes_list) > 0),
            notas_usuario="Análisis automático al agregar la planta (background)",
            fecha_analisis=datetime.utcnow()
        )
        
        db.add(nuevo_analisis)
        
        # Guardar condiciones ambientales
        condiciones_ambientales = resultado_gemini.get("condiciones_ambientales")
        if condiciones_ambientales:
            planta.condiciones_ambientales_recomendadas = json.dumps(
                condiciones_ambientales,
                ensure_ascii=False
            )
            
            # Actualizar frecuencias
            frecuencia_riego = condiciones_ambientales.get("frecuencia_riego_dias")
            if frecuencia_riego and isinstance(frecuencia_riego, int) and frecuencia_riego > 0:
                planta.frecuencia_riego_dias = frecuencia_riego
                logger.info(f"✅ Frecuencia de riego: {frecuencia_riego} días")
            
            frecuencia_fertilizacion = condiciones_ambientales.get("frecuencia_fertilizacion_dias")
            if frecuencia_fertilizacion and isinstance(frecuencia_fertilizacion, int) and frecuencia_fertilizacion > 0:
                planta.frecuencia_fertilizacion_dias = frecuencia_fertilizacion
                logger.info(f"✅ Frecuencia de fertilización: {frecuencia_fertilizacion} días")
        
        # Actualizar estado de salud
        planta.estado_salud = resultado_gemini["estado"]
        planta.updated_at = datetime.utcnow()
        
        db.commit()
        logger.info(f"✅ Análisis en background completado para planta {planta_id}")
        
    except Exception as e:
        logger.error(f"❌ Error en análisis background para planta {planta_id}: {str(e)}")
        db.rollback()
    finally:
        db.close()


# ==================== ENDPOINTS ====================


@router.post(
    "/",
    response_model=PlantaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nueva planta",
    description="Agrega una nueva planta al jardín del usuario autenticado",
    response_description="Planta creada exitosamente"
)
async def crear_planta(
    planta_data: PlantaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Crea una nueva planta en el jardín del usuario.
    
    - **nombre_personal**: Nombre que el usuario da a su planta (requerido)
    - **especie_id**: ID de la especie (opcional)
    - **estado_salud**: Estado actual (excelente, buena, necesita_atencion, critica)
    - **ubicacion**: Dónde está ubicada la planta
    - **notas**: Notas adicionales del usuario
    - **frecuencia_riego_dias**: Cada cuántos días regar
    - **luz_actual**: Nivel de luz que recibe (baja, media, alta, directa)
    """
    try:
        nueva_planta = PlantaService.crear_planta(
            db=db,
            planta_data=planta_data,
            usuario_id=current_user.id
        )
        
        # Agregar campo calculado necesita_riego
        planta_dict = nueva_planta.to_dict()
        planta_dict["necesita_riego"] = nueva_planta.necesita_riego()
        
        return PlantaResponse(**planta_dict)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear la planta: {str(e)}"
        )


@router.get(
    "/",
    response_model=PlantaListResponse,
    summary="Listar todas las plantas",
    description="Obtiene todas las plantas del jardín del usuario autenticado",
    response_description="Lista de plantas del usuario"
)
async def listar_plantas(
    skip: int = Query(0, ge=0, alias="offset", description="Número de registros a saltar"),
    limit: int = Query(100, ge=1, le=1000, alias="limite", description="Número máximo de registros"),
    solo_activas: bool = Query(True, description="Solo plantas activas (is_active=True)"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Lista todas las plantas activas del usuario con paginación.
    
    Retorna las plantas ordenadas por fecha de creación (más recientes primero).
    El parámetro solo_activas filtra plantas activas (por defecto True).
    """
    try:
        plantas = PlantaService.obtener_plantas_usuario(
            db=db,
            usuario_id=current_user.id,
            skip=skip,
            limit=limit,
            solo_activas=solo_activas
        )
        
        total = PlantaService.contar_plantas_usuario(
            db=db,
            usuario_id=current_user.id,
            solo_activas=solo_activas
        )
        
        # Importar ImagenService para generar URLs con SAS
        from app.services.imagen_service import ImagenService, AzureBlobService
        azure_service = AzureBlobService()
        
        # Convertir a response con campo calculado e imagen URL
        plantas_response = []
        for planta in plantas:
            planta_dict = planta.to_dict()
            planta_dict["necesita_riego"] = planta.necesita_riego()
            
            # Generar URL con SAS token para la imagen si existe
            if planta.imagen_principal_id:
                # Obtener la imagen de la BD para tener el nombre_blob
                imagen = db.query(Imagen).filter(Imagen.id == planta.imagen_principal_id).first()
                if imagen:
                    # Generar URL con SAS token (válida por 1 hora)
                    planta_dict["imagen_principal_url"] = azure_service.generar_url_con_sas(imagen.nombre_blob, expiracion_horas=1)
                else:
                    planta_dict["imagen_principal_url"] = None
            else:
                planta_dict["imagen_principal_url"] = None
                
            plantas_response.append(PlantaResponse(**planta_dict))
        
        return PlantaListResponse(
            plantas=plantas_response,
            total=total
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener las plantas: {str(e)}"
        )


@router.get(
    "/stats",
    response_model=PlantaStats,
    summary="Obtener estadísticas del jardín",
    description="Retorna estadísticas sobre el estado de todas las plantas del usuario",
    response_description="Estadísticas calculadas"
)
async def obtener_estadisticas(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Calcula y retorna estadísticas del jardín del usuario.
    
    Incluye:
    - Total de plantas
    - Plantas saludables (excelente o buena)
    - Plantas que necesitan atención (necesita_atencion o critica)
    - Plantas que necesitan riego hoy
    - Porcentaje de salud general
    """
    try:
        stats = PlantaService.obtener_estadisticas(
            db=db,
            usuario_id=current_user.id
        )
        
        return stats
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al calcular estadísticas: {str(e)}"
        )


@router.get(
    "/con-imagenes",
    response_model=List[PlantaUsuarioResponse],
    summary="Listar plantas con imágenes de identificación",
    description="Obtiene todas las plantas del usuario con las imágenes usadas para identificarlas",
    response_description="Lista de plantas con imágenes de identificación"
)
async def listar_plantas_con_imagenes(
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Lista todas las plantas activas del usuario con imágenes de identificación.
    
    Para cada planta retorna:
    - Datos básicos de la planta
    - Información de la especie (si existe)
    - Imagen principal
    - TODAS las imágenes usadas en la identificación original
    
    Las plantas están ordenadas por fecha de creación (más recientes primero).
    """
    try:
        plantas = PlantaService.obtener_plantas_usuario_con_imagenes(
            db=db,
            usuario_id=current_user.id,
            skip=skip,
            limit=limit
        )
        
        # Convertir a PlantaUsuarioResponse
        return [PlantaUsuarioResponse(**planta) for planta in plantas]
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener las plantas con imágenes: {str(e)}"
        )


@router.get(
    "/{planta_id}",
    response_model=PlantaResponse,
    summary="Obtener planta por ID",
    description="Obtiene los detalles de una planta específica",
    response_description="Detalles de la planta"
)
async def obtener_planta(
    planta_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtiene los detalles de una planta específica por su ID.
    
    Solo retorna la planta si pertenece al usuario autenticado.
    """
    try:
        planta = PlantaService.obtener_planta_por_id(
            db=db,
            planta_id=planta_id,
            usuario_id=current_user.id
        )
        
        if not planta:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Planta con ID {planta_id} no encontrada"
            )
        
        # Importar ImagenService para generar URLs con SAS
        from app.services.imagen_service import AzureBlobService
        azure_service = AzureBlobService()
        
        # Convertir a response con campo calculado e imagen URL
        planta_dict = planta.to_dict()
        planta_dict["necesita_riego"] = planta.necesita_riego()
        
        # Generar URL con SAS token para la imagen si existe
        if planta.imagen_principal_id:
            # Obtener la imagen de la BD para tener el nombre_blob
            imagen = db.query(Imagen).filter(Imagen.id == planta.imagen_principal_id).first()
            if imagen:
                # Generar URL con SAS token (válida por 1 hora)
                planta_dict["imagen_principal_url"] = azure_service.generar_url_con_sas(imagen.nombre_blob, expiracion_horas=1)
            else:
                planta_dict["imagen_principal_url"] = None
        else:
            planta_dict["imagen_principal_url"] = None
        
        return PlantaResponse(**planta_dict)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener la planta: {str(e)}"
        )


@router.get(
    "/{planta_id}/imagenes",
    response_model=List[dict],
    summary="Obtener imágenes de una planta",
    description="Obtiene todas las imágenes asociadas a una planta específica",
    response_description="Lista de imágenes de la planta"
)
async def obtener_imagenes_planta(
    planta_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtiene todas las imágenes asociadas a una planta específica.
    
    Incluye:
    - Imagen principal de la planta
    - Imágenes de identificación
    - Imágenes de análisis de salud
    
    Las URLs incluyen SAS tokens válidos por 1 hora.
    """
    try:
        # Verificar que la planta existe y pertenece al usuario
        planta = db.query(Planta).filter(
            and_(
                Planta.id == planta_id,
                Planta.usuario_id == current_user.id
            )
        ).first()
        
        if not planta:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Planta con ID {planta_id} no encontrada"
            )
        
        # Obtener todas las imágenes asociadas
        imagenes = []
        
        # 1. Imagen principal
        if planta.imagen_principal_id:
            imagen_principal = db.query(Imagen).filter(Imagen.id == planta.imagen_principal_id).first()
            if imagen_principal:
                imagenes.append(imagen_principal)
        
        # 2. Imágenes de identificación (si la planta tiene especie_id)
        if planta.especie_id:
            # Buscar identificación que creó esta planta
            from app.db.models import Identificacion
            identificacion = db.query(Identificacion).filter(
                and_(
                    Identificacion.especie_id == planta.especie_id,
                    Identificacion.usuario_id == current_user.id
                )
            ).first()
            
            if identificacion and identificacion.id:
                imagenes_identificacion = db.query(Imagen).filter(
                    Imagen.identificacion_id == identificacion.id
                ).all()
                imagenes.extend(imagenes_identificacion)
        
        # 3. Imágenes de análisis de salud
        from app.db.models import AnalisisSalud
        analisis = db.query(AnalisisSalud).filter(
            AnalisisSalud.planta_id == planta_id
        ).all()
        
        for analisis_item in analisis:
            if analisis_item.imagen_id:
                imagen_analisis = db.query(Imagen).filter(Imagen.id == analisis_item.imagen_id).first()
                if imagen_analisis and imagen_analisis not in imagenes:
                    imagenes.append(imagen_analisis)
        
        # Generar URLs con SAS tokens
        from app.services.imagen_service import AzureBlobService
        azure_service = AzureBlobService()
        
        imagenes_response = []
        for imagen in imagenes:
            url_con_sas = azure_service.generar_url_con_sas(imagen.nombre_blob, expiracion_horas=1)
            imagenes_response.append({
                "id": imagen.id,
                "nombre_archivo": imagen.nombre_archivo,
                "url_blob": url_con_sas,
                "tamano_bytes": imagen.tamano_bytes,
                "content_type": imagen.content_type,
                "descripcion": imagen.descripcion,
                "organ": imagen.organ,
                "created_at": imagen.created_at.isoformat() if imagen.created_at else None
            })
        
        return imagenes_response
    
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error al obtener imágenes de planta {planta_id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener las imágenes de la planta: {str(e)}"
        )


@router.put(
    "/{planta_id}",
    response_model=PlantaResponse,
    summary="Actualizar planta",
    description="Actualiza los datos de una planta existente",
    response_description="Planta actualizada"
)
async def actualizar_planta(
    planta_id: int,
    planta_data: PlantaUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Actualiza los datos de una planta existente.
    
    Solo se pueden actualizar plantas que pertenecen al usuario autenticado.
    Todos los campos son opcionales - solo se actualizan los campos provistos.
    """
    try:
        planta_actualizada = PlantaService.actualizar_planta(
            db=db,
            planta_id=planta_id,
            usuario_id=current_user.id,
            planta_data=planta_data
        )
        
        if not planta_actualizada:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Planta con ID {planta_id} no encontrada"
            )
        
        # Convertir a response con campo calculado
        planta_dict = planta_actualizada.to_dict()
        planta_dict["necesita_riego"] = planta_actualizada.necesita_riego()
        
        return PlantaResponse(**planta_dict)
    
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar la planta: {str(e)}"
        )


@router.delete(
    "/{planta_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar planta",
    description="Elimina una planta del jardín (soft delete)",
    response_description="Planta eliminada exitosamente"
)
async def eliminar_planta(
    planta_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Elimina una planta del jardín del usuario (soft delete).
    
    La planta no se elimina físicamente de la base de datos,
    solo se marca como inactiva.
    """
    try:
        eliminada = PlantaService.eliminar_planta(
            db=db,
            planta_id=planta_id,
            usuario_id=current_user.id
        )
        
        if not eliminada:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Planta con ID {planta_id} no encontrada"
            )
        
        return None
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar la planta: {str(e)}"
        )


@router.post(
    "/{planta_id}/riego",
    response_model=PlantaResponse,
    summary="Registrar riego",
    description="Registra un nuevo riego en una planta",
    response_description="Planta con riego actualizado"
)
async def registrar_riego(
    planta_id: int,
    riego_data: RegistrarRiegoRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Registra un nuevo riego en una planta.
    
    Actualiza la fecha de último riego y calcula automáticamente
    la fecha del próximo riego basado en la frecuencia configurada.
    
    Si no se provee fecha_riego, se usa la fecha y hora actual.
    """
    try:
        planta_actualizada = PlantaService.registrar_riego(
            db=db,
            planta_id=planta_id,
            usuario_id=current_user.id,
            fecha_riego=riego_data.fecha_riego
        )
        
        if not planta_actualizada:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Planta con ID {planta_id} no encontrada"
            )
        
        # Convertir a response con campo calculado
        planta_dict = planta_actualizada.to_dict()
        planta_dict["necesita_riego"] = planta_actualizada.necesita_riego()
        
        return PlantaResponse(**planta_dict)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al registrar riego: {str(e)}"
        )


@router.post(
    "/{planta_id}/fertilizacion",
    response_model=PlantaResponse,
    summary="Registrar fertilización",
    description="Registra una nueva fertilización en una planta",
    response_description="Planta con fertilización actualizada"
)
async def registrar_fertilizacion(
    planta_id: int,
    fertilizacion_data: RegistrarFertilizacionRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Registra una nueva fertilización en una planta.
    
    Actualiza la fecha de última fertilización y calcula automáticamente
    la fecha de la próxima fertilización basado en la frecuencia configurada.
    
    Si no se provee fecha_fertilizacion, se usa la fecha y hora actual.
    """
    try:
        planta_actualizada = PlantaService.registrar_fertilizacion(
            db=db,
            planta_id=planta_id,
            usuario_id=current_user.id,
            fecha_fertilizacion=fertilizacion_data.fecha_fertilizacion
        )
        
        if not planta_actualizada:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Planta con ID {planta_id} no encontrada"
            )
        
        # Convertir a response con campos calculados
        planta_dict = planta_actualizada.to_dict()
        planta_dict["necesita_riego"] = planta_actualizada.necesita_riego()
        
        return PlantaResponse(**planta_dict)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al registrar fertilización: {str(e)}"
        )


@router.post(
    "/agregar-desde-identificacion",
    response_model=PlantaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Agregar planta desde identificación",
    description="Agrega una planta al jardín del usuario desde una identificación confirmada",
    response_description="Planta creada exitosamente desde identificación"
)
async def agregar_planta_desde_identificacion(
    request_data: AgregarPlantaDesdeIdentificacionRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Agrega una planta al jardín del usuario desde una identificación de PlantNet.
    
    Este endpoint se usa cuando el usuario confirma una identificación
    y decide agregarla a su colección personal.
    
    Pasos que realiza:
    1. Obtiene la identificación por ID
    2. Verifica que pertenece al usuario actual
    3. Obtiene los datos de la especie identificada
    4. Crea una nueva planta con esos datos
    5. Usa la imagen de la identificación como imagen principal
    6. Usa el nombre común como nombre personal (si no se especifica otro)
    
    Args:
        request_data: Datos de la solicitud (identificacion_id, nombre_personalizado, notas)
        db: Sesión de base de datos
        current_user: Usuario autenticado
        
    Returns:
        PlantaResponse: Planta creada con todos sus datos
        
    Raises:
        404: Si la identificación no existe o no pertenece al usuario
        400: Si hay error en los datos proporcionados
        500: Si hay error interno del servidor
    """
    try:
        nueva_planta = PlantaService.agregar_desde_identificacion(
            db=db,
            identificacion_id=request_data.identificacion_id,
            usuario_id=current_user.id,
            nombre_personalizado=request_data.nombre_personalizado,
            notas=request_data.notas,
            ubicacion=request_data.ubicacion
        )
        
        if not nueva_planta:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Identificación con ID {request_data.identificacion_id} no encontrada"
            )
        
        # ✅ ESTABLECER ESTADO "analizando" EN LA DB ANTES DEL THREAD
        nueva_planta.estado_salud = "analizando"
        db.commit()
        db.refresh(nueva_planta)
        logger.info(f"📝 Estado 'analizando' guardado en DB para planta {nueva_planta.id}")
        
        # 🚀 EJECUTAR ANÁLISIS EN SEGUNDO PLANO CON THREADING
        # Esto permite que la UI responda inmediatamente sin esperar a Gemini
        logger.info(f"🚀 Iniciando análisis en background (thread) para planta {nueva_planta.id}")
        
        # Obtener la URL de la base de datos de la configuración
        from app.db.session import get_database_url
        db_url = get_database_url()
        
        # Crear y ejecutar thread en background (daemon=True para que no bloquee el cierre)
        thread = threading.Thread(
            target=ejecutar_analisis_inicial_background,
            args=(nueva_planta.id, current_user.id, request_data.identificacion_id, db_url),
            daemon=True,
            name=f"analisis-planta-{nueva_planta.id}"
        )
        thread.start()
        
        logger.info(f"✅ Planta {nueva_planta.id} creada. Thread de análisis iniciado (no bloqueante)")
        
        # Retornar inmediatamente con estado "analizando"
        # Crear respuesta manualmente para asegurar que estado_salud sea "analizando"
        db.refresh(nueva_planta)
        
        return PlantaResponse(
            id=nueva_planta.id,
            usuario_id=nueva_planta.usuario_id,
            nombre_personal=nueva_planta.nombre_personal,
            especie_id=nueva_planta.especie_id,
            estado_salud="analizando",  # Estado temporal mientras se analiza
            ubicacion=nueva_planta.ubicacion,
            notas=nueva_planta.notas,
            imagen_principal_id=nueva_planta.imagen_principal_id,
            imagen_principal_url=None,
            fecha_ultimo_riego=nueva_planta.fecha_ultimo_riego,
            proximo_riego=nueva_planta.proximo_riego,
            frecuencia_riego_dias=nueva_planta.frecuencia_riego_dias or 7,
            fecha_ultima_fertilizacion=nueva_planta.fecha_ultima_fertilizacion,
            proxima_fertilizacion=nueva_planta.proxima_fertilizacion,
            frecuencia_fertilizacion_dias=nueva_planta.frecuencia_fertilizacion_dias,
            luz_actual=nueva_planta.luz_actual,
            condiciones_ambientales_recomendadas=None,
            fecha_adquisicion=nueva_planta.fecha_adquisicion,
            created_at=nueva_planta.created_at,
            updated_at=nueva_planta.updated_at,
            is_active=nueva_planta.is_active,
            necesita_riego=False,  # No puede necesitar riego si acaba de crearse
            es_favorita=getattr(nueva_planta, 'es_favorita', False),
            fue_regada_hoy=getattr(nueva_planta, 'fue_regada_hoy', False)
        )
    
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al agregar la planta desde identificación: {str(e)}"
        )


@router.post(
    "/reparar-imagenes",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Reparar imágenes de plantas existentes",
    description="Busca y asigna imagen_principal_id a plantas que no la tienen pero tienen identificación asociada"
)
async def reparar_imagenes_plantas(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Endpoint de reparación para plantas creadas con el bug anterior.
    
    Busca plantas del usuario que:
    1. No tienen imagen_principal_id
    2. Tienen identificación asociada
    3. Esa identificación tiene imágenes
    
    Y les asigna la primera imagen como imagen principal.
    
    Returns:
        dict: Información sobre cuántas plantas se repararon
    """
    try:
        from app.db.models import Planta, Identificacion, Imagen
        
        # Buscar plantas sin imagen principal del usuario
        plantas_sin_imagen = db.query(Planta).filter(
            Planta.usuario_id == current_user.id,
            Planta.imagen_principal_id == None,
            Planta.is_active == True
        ).all()
        
        plantas_reparadas = []
        
        for planta in plantas_sin_imagen:
            # Buscar identificaciones del usuario que tengan la especie de esta planta
            identificaciones = db.query(Identificacion).filter(
                Identificacion.usuario_id == current_user.id,
                Identificacion.especie_id == planta.especie_id
            ).order_by(Identificacion.fecha_identificacion.desc()).all()
            
            imagen_encontrada = False
            
            for identificacion in identificaciones:
                # Buscar imágenes de esta identificación
                imagenes = db.query(Imagen).filter(
                    Imagen.identificacion_id == identificacion.id
                ).order_by(Imagen.id.asc()).all()
                
                if not imagenes and identificacion.imagen_id:
                    # Caso legacy: usar imagen_id directamente
                    planta.imagen_principal_id = identificacion.imagen_id
                    imagen_encontrada = True
                    break
                elif imagenes:
                    # Caso múltiples imágenes: usar la primera
                    planta.imagen_principal_id = imagenes[0].id
                    imagen_encontrada = True
                    break
            
            if imagen_encontrada:
                db.add(planta)
                plantas_reparadas.append({
                    "id": planta.id,
                    "nombre": planta.nombre_personal,
                    "imagen_principal_id": planta.imagen_principal_id
                })
        
        # Guardar cambios
        db.commit()
        
        return {
            "plantas_procesadas": len(plantas_sin_imagen),
            "plantas_reparadas": len(plantas_reparadas),
            "detalles": plantas_reparadas
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al reparar imágenes: {str(e)}"
        )
