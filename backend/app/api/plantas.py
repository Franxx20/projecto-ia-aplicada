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
from fastapi import APIRouter, Depends, HTTPException, status, Query
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
        
        # 🌱 NUEVO: Crear análisis de salud automático después de agregar la planta
        try:
            from app.services.gemini_service import GeminiService
            from app.db.models import Imagen, Especie, AnalisisSalud, Identificacion
            from app.services.imagen_service import AzureBlobService
            import json
            
            # 🖼️ Obtener TODAS las imágenes asociadas a la identificación (máximo 5)
            imagenes_bytes_list = []
            imagenes_ids_list = []  # 🆕 Guardar IDs de las imágenes
            azure_service = AzureBlobService()
            
            # Buscar la identificación
            identificacion = db.query(Identificacion).filter(
                Identificacion.id == request_data.identificacion_id
            ).first()
            
            if identificacion:
                logger.info(f"🔍 Identificación encontrada: ID={identificacion.id}, Usuario={identificacion.usuario_id}")
                
                # Obtener todas las imágenes asociadas a esta identificación
                imagenes = db.query(Imagen).filter(
                    Imagen.identificacion_id == identificacion.id
                ).order_by(Imagen.created_at).limit(5).all()  # Máximo 5 imágenes, ordenadas por fecha
                
                logger.info(f"🖼️  Encontradas {len(imagenes)} imágenes para la identificación {identificacion.id}")
                
                # DIAGNÓSTICO: Buscar también imágenes sin identificacion_id del mismo usuario
                imagenes_huerfanas = db.query(Imagen).filter(
                    Imagen.usuario_id == current_user.id,
                    Imagen.identificacion_id == None,
                    Imagen.created_at >= identificacion.created_at
                ).order_by(Imagen.created_at.desc()).limit(5).all()
                
                if imagenes_huerfanas:
                    logger.warning(f"⚠️  ENCONTRADAS {len(imagenes_huerfanas)} IMÁGENES HUÉRFANAS (sin identificacion_id):")
                    for img in imagenes_huerfanas:
                        logger.warning(f"     - ID: {img.id}, Nombre: {img.nombre_archivo}, Created: {img.created_at}")
                
                # Log detallado de cada imagen encontrada con identificacion_id
                for idx, imagen in enumerate(imagenes, 1):
                    logger.info(f"  📸 Imagen {idx}/{len(imagenes)}:")
                    logger.info(f"     - ID: {imagen.id}")
                    logger.info(f"     - Nombre: {imagen.nombre_archivo}")
                    logger.info(f"     - Órgano: {imagen.organ}")
                    logger.info(f"     - Tamaño: {imagen.tamano_bytes} bytes")
                    logger.info(f"     - Blob: {imagen.nombre_blob}")
                    logger.info(f"     - identificacion_id: {imagen.identificacion_id}")
                
                for imagen in imagenes:
                    try:
                        imagen_bytes = azure_service.descargar_blob(imagen.nombre_blob)
                        imagenes_bytes_list.append(imagen_bytes)
                        imagenes_ids_list.append(imagen.id)  # 🆕 Guardar ID
                        logger.info(f"  ✅ Imagen {imagen.id} ({imagen.nombre_archivo}) descargada: {len(imagen_bytes)} bytes")
                    except Exception as e:
                        logger.error(f"  ❌ ERROR descargando imagen {imagen.id} ({imagen.nombre_archivo}): {str(e)}")
                        continue
            else:
                logger.warning(f"⚠️  No se encontró identificación {request_data.identificacion_id}")
            
            # Si no se encontraron imágenes de la identificación, intentar con la imagen principal
            if not imagenes_bytes_list and nueva_planta.imagen_principal_id:
                imagen = db.query(Imagen).filter(Imagen.id == nueva_planta.imagen_principal_id).first()
                if imagen:
                    try:
                        imagen_bytes = azure_service.descargar_blob(imagen.nombre_blob)
                        imagenes_bytes_list.append(imagen_bytes)
                        logger.info(f"✅ Imagen principal descargada: {len(imagen_bytes)} bytes")
                    except Exception as e:
                        logger.warning(f"⚠️  No se pudo descargar imagen principal: {str(e)}")
            
            logger.info(f"📊 Total de imágenes para análisis inicial: {len(imagenes_bytes_list)}")
            
            # Obtener información de la especie
            especie_nombre = "Desconocida"
            especie_cientifica = None
            familia = "Desconocida"
            
            if nueva_planta.especie_id:
                especie = db.query(Especie).filter(Especie.id == nueva_planta.especie_id).first()
                if especie:
                    especie_nombre = especie.nombre_comun or "Desconocida"
                    especie_cientifica = especie.nombre_cientifico
                    familia = especie.familia or "Desconocida"
            
            # Construir contexto para el análisis inicial
            contexto_planta = {
                "nombre_personal": nueva_planta.nombre_personal,
                "nombre_cientifico": especie_cientifica or "Desconocida",
                "nombre_comun": especie_nombre,
                "familia": familia,
                "dias_desde_adquisicion": 0,  # Recién agregada
                "ubicacion": nueva_planta.ubicacion or "No especificada",
                "luz_actual": nueva_planta.luz_actual or "No especificada",
                "dias_desde_riego": "N/A",
                "frecuencia_riego_dias": nueva_planta.frecuencia_riego_dias or "N/A",
                "estado_riego": "normal",
                "estado_salud": "desconocido",
                "fecha_ultimo_analisis": "Nunca",
                "notas": f"{nueva_planta.notas or ''}\n\n📸 Análisis inicial automático de la planta recién agregada."
            }
            
            # Llamar a Gemini para análisis INICIAL (con condiciones ambientales)
            gemini_service = GeminiService()
            inicio = datetime.utcnow()
            
            # 🔍 DIAGNÓSTICO: Verificar qué se está enviando a Gemini
            logger.info("=" * 80)
            logger.info("🔍 DIAGNÓSTICO - DATOS ENVIADOS A GEMINI")
            logger.info("=" * 80)
            logger.info(f"📊 Número de imágenes en imagenes_bytes_list: {len(imagenes_bytes_list) if imagenes_bytes_list else 0}")
            logger.info(f"🆔 IDs de imágenes: {imagenes_ids_list}")
            logger.info(f"📋 es_analisis_inicial: True")
            logger.info(f"👤 usuario_id: {current_user.id}")
            
            if imagenes_bytes_list:
                for idx, img_bytes in enumerate(imagenes_bytes_list, 1):
                    logger.info(f"  🖼️  Imagen {idx}: {len(img_bytes)} bytes")
            else:
                logger.warning("⚠️  ¡imagenes_bytes_list está VACÍO! Gemini NO recibirá imágenes")
            logger.info("=" * 80)
            
            resultado_gemini = gemini_service.analizar_salud_planta(
                datos_planta=contexto_planta,
                imagenes_bytes_list=imagenes_bytes_list if imagenes_bytes_list else None,
                usuario_id=current_user.id,
                es_analisis_inicial=True  # ⭐ Solicitar condiciones ambientales
            )
            
            # 📋 LOG: Respuesta completa de Gemini para debug
            logger.info("=" * 80)
            logger.info("📊 RESPUESTA COMPLETA DE GEMINI (Análisis Inicial)")
            logger.info("=" * 80)
            logger.info(f"🌱 Planta: {nueva_planta.nombre_personal}")
            logger.info(f"🖼️  Imágenes analizadas: {len(imagenes_bytes_list)}")
            logger.info(f"🔬 Estado: {resultado_gemini.get('estado')}")
            logger.info(f"📈 Confianza: {resultado_gemini.get('confianza')}%")
            logger.info(f"📝 Resumen: {resultado_gemini.get('resumen')}")
            logger.info("-" * 80)
            
            if resultado_gemini.get("condiciones_ambientales"):
                logger.info("🌍 CONDICIONES AMBIENTALES RECOMENDADAS:")
                cond_amb = resultado_gemini["condiciones_ambientales"]
                logger.info(f"  ☀️  Luz: {cond_amb.get('luz_recomendada', 'N/A')}")
                logger.info(f"  🌡️  Temperatura: {cond_amb.get('temperatura_ideal', 'N/A')}")
                logger.info(f"  💧 Humedad mín: {cond_amb.get('humedad_minima', 'N/A')}%")
                logger.info(f"  💧 Humedad máx: {cond_amb.get('humedad_maxima', 'N/A')}%")
                logger.info(f"  🚿 Frecuencia riego: {cond_amb.get('frecuencia_riego_dias', 'N/A')} días")
                logger.info(f"  📖 Descripción riego: {cond_amb.get('descripcion_riego', 'N/A')}")
            else:
                logger.warning("⚠️  No se recibieron condiciones ambientales de Gemini")
            
            logger.info("-" * 80)
            if resultado_gemini.get("recomendaciones"):
                logger.info(f"💡 RECOMENDACIONES ({len(resultado_gemini['recomendaciones'])} items):")
                for i, rec in enumerate(resultado_gemini["recomendaciones"][:3], 1):
                    logger.info(f"  {i}. [{rec.get('prioridad', 'media')}] {rec.get('accion', 'N/A')}")
            
            if resultado_gemini.get("problemas_detectados"):
                logger.info(f"🔍 PROBLEMAS DETECTADOS ({len(resultado_gemini['problemas_detectados'])} items):")
                for i, prob in enumerate(resultado_gemini["problemas_detectados"][:3], 1):
                    logger.info(f"  {i}. {prob.get('tipo', 'N/A')}: {prob.get('descripcion', 'N/A')}")
            
            logger.info("=" * 80)
            
            # Crear registro de análisis
            metadata = resultado_gemini.get("metadata", {})
            
            # 🆕 Agregar IDs de todas las imágenes usadas en el análisis
            metadata["imagenes_ids"] = imagenes_ids_list
            metadata["num_imagenes_analizadas"] = len(imagenes_ids_list)
            
            nuevo_analisis = AnalisisSalud(
                planta_id=nueva_planta.id,
                usuario_id=current_user.id,
                imagen_id=nueva_planta.imagen_principal_id,  # Mantener por compatibilidad
                estado=resultado_gemini["estado"],
                confianza=resultado_gemini["confianza"],
                resumen_diagnostico=resultado_gemini["resumen"],
                diagnostico_detallado=resultado_gemini.get("diagnostico_completo"),
                problemas_detectados=json.dumps(resultado_gemini.get("problemas_detectados", []), ensure_ascii=False),
                recomendaciones=json.dumps(resultado_gemini.get("recomendaciones", []), ensure_ascii=False),
                metadatos_ia=json.dumps(metadata, ensure_ascii=False),  # 🆕 Incluir IDs de imágenes
                modelo_ia_usado=metadata.get("modelo", "gemini-2.5-flash"),
                tiempo_analisis_ms=metadata.get("tiempo_analisis_ms", 0),
                version_prompt=metadata.get("version_prompt", "v1.0"),
                con_imagen=metadata.get("con_imagen", len(imagenes_bytes_list) > 0),
                notas_usuario="Análisis automático al agregar la planta",
                fecha_analisis=datetime.utcnow()
            )
            
            db.add(nuevo_analisis)
            
            # ⭐ Guardar condiciones ambientales en la planta (solo en análisis inicial)
            condiciones_ambientales = resultado_gemini.get("condiciones_ambientales")
            if condiciones_ambientales:
                nueva_planta.condiciones_ambientales_recomendadas = json.dumps(
                    condiciones_ambientales,
                    ensure_ascii=False
                )
                
                # ⭐ Actualizar frecuencia de riego si Gemini la proporcionó
                frecuencia_riego = condiciones_ambientales.get("frecuencia_riego_dias")
                if frecuencia_riego and isinstance(frecuencia_riego, int) and frecuencia_riego > 0:
                    nueva_planta.frecuencia_riego_dias = frecuencia_riego
                    logger.info(f"✅ Frecuencia de riego actualizada a {frecuencia_riego} días")
                
                logger.info(f"✅ Condiciones ambientales guardadas para planta {nueva_planta.id}")
            
            # Actualizar estado de la planta basándose en el análisis
            nueva_planta.estado_salud = resultado_gemini["estado"]
            nueva_planta.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(nueva_planta)
            
            # 📋 LOG: Datos finales de la planta guardada
            logger.info("=" * 80)
            logger.info("💾 DATOS FINALES GUARDADOS EN LA BASE DE DATOS")
            logger.info("=" * 80)
            logger.info(f"🆔 Planta ID: {nueva_planta.id}")
            logger.info(f"🌱 Nombre: {nueva_planta.nombre_personal}")
            logger.info(f"🔬 Estado salud: {nueva_planta.estado_salud}")
            logger.info(f"🚿 Frecuencia riego: {nueva_planta.frecuencia_riego_dias} días")
            logger.info(f"📅 Próximo riego: {nueva_planta.proximo_riego}")
            if nueva_planta.condiciones_ambientales_recomendadas:
                try:
                    cond = json.loads(nueva_planta.condiciones_ambientales_recomendadas)
                    logger.info(f"🌍 Condiciones ambientales guardadas: {list(cond.keys())}")
                except:
                    logger.info(f"🌍 Condiciones ambientales: {nueva_planta.condiciones_ambientales_recomendadas[:100]}...")
            else:
                logger.warning("⚠️  No hay condiciones ambientales guardadas en la BD")
            logger.info("=" * 80)
            
            logger.info(f"✅ Análisis automático creado para planta {nueva_planta.id}: {resultado_gemini['estado']}")

            
        except Exception as e:
            # No queremos que el análisis automático impida crear la planta
            logger.warning(f"⚠️  No se pudo crear análisis automático: {str(e)}")
            # Continuar sin el análisis
        
        # Agregar campo calculado necesita_riego
        planta_dict = nueva_planta.to_dict()
        planta_dict["necesita_riego"] = nueva_planta.necesita_riego()
        
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
