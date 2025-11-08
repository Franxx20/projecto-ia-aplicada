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
import time
from fastapi import APIRouter, Depends, HTTPException, status, Query, File, UploadFile, Form
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.planta import (
    PlantaCreate,
    PlantaUpdate,
    PlantaResponse,
    PlantaStats,
    PlantaListResponse,
    RegistrarRiegoRequest,
    AgregarPlantaDesdeIdentificacionRequest
)
from app.schemas.salud_planta import (
    SaludAnalisisResponse,
    HistorialSaludResponse,
    HistorialSaludItem,
    EstadoSaludDetallado
)
from app.services.planta_service import PlantaService
from app.services.gemini_service import GeminiService
from app.services.imagen_service import ImagenService
from app.utils.jwt import get_current_user
from app.db.models import Usuario, Imagen, Planta, AnalisisSalud

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
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Lista todas las plantas activas del usuario con paginación.
    
    Retorna las plantas ordenadas por fecha de creación (más recientes primero).
    """
    try:
        plantas = PlantaService.obtener_plantas_usuario(
            db=db,
            usuario_id=current_user.id,
            skip=skip,
            limit=limit
        )
        
        total = PlantaService.contar_plantas_usuario(
            db=db,
            usuario_id=current_user.id
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
    "/{planta_id}/verificar-salud",
    response_model=SaludAnalisisResponse,
    status_code=status.HTTP_200_OK,
    summary="Verificar salud de planta",
    description="Analiza la salud de una planta usando Google Gemini AI con imagen opcional",
    response_description="Análisis completo de la salud de la planta"
)
async def verificar_salud_planta(
    planta_id: int,
    imagen: Optional[UploadFile] = File(None, description="Imagen opcional de la planta para análisis visual"),
    incluir_imagen_principal: bool = Form(False, description="Si es True, usa la imagen principal de la planta si no se proporciona otra"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Analiza la salud de una planta usando IA de Google Gemini.
    
    Este endpoint realiza un análisis completo de la salud de una planta
    utilizando el contexto de la planta (especie, ubicación, cuidados) y
    opcionalmente una imagen para análisis visual.
    
    **Flujo del análisis:**
    1. Obtiene los datos completos de la planta desde la BD
    2. Si se proporciona imagen, la sube a Azure Storage
    3. Si no hay imagen pero incluir_imagen_principal=True, usa la imagen principal
    4. Construye el contexto con datos de la planta (especie, ubicación, cuidados)
    5. Llama a Gemini AI para analizar la salud
    6. Guarda el análisis en la tabla analisis_salud
    7. Actualiza el estado_salud de la planta si cambió significativamente
    8. Retorna el análisis completo
    
    **Args:**
    - **planta_id**: ID de la planta a analizar
    - **imagen**: Imagen opcional para análisis visual (JPG, PNG, WEBP)
    - **incluir_imagen_principal**: Si True y no hay imagen, usa la imagen principal
    
    **Returns:**
    - Análisis completo con estado de salud, problemas detectados y recomendaciones
    
    **Ejemplos de uso:**
    - Análisis con imagen nueva: POST con multipart/form-data e imagen
    - Análisis sin imagen: POST sin imagen (análisis basado en contexto)
    - Análisis con imagen principal: POST con incluir_imagen_principal=True
    
    **Raises:**
    - 404: Si la planta no existe o no pertenece al usuario
    - 400: Si hay error en los datos proporcionados
    - 503: Si el servicio de Gemini no está disponible
    - 500: Si hay error interno del servidor
    """
    try:
        # 1. Obtener la planta y verificar pertenencia
        query = db.query(Planta).filter(
            Planta.id == planta_id,
            Planta.usuario_id == current_user.id
        )
        
        # Filtrar por activa solo si el campo existe
        if hasattr(Planta, 'activa'):
            query = query.filter(Planta.activa == True)
        
        planta = query.first()
        
        if not planta:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Planta con ID {planta_id} no encontrada"
            )
        
        # 2. Procesar imagen si se proporcionó
        imagen_id = None
        imagen_url = None
        imagen_bytes = None
        
        if imagen and imagen.filename:
            # Subir nueva imagen a Azure Storage
            imagen_service = ImagenService(db)
            imagen_obj = await imagen_service.subir_imagen(
                archivo=imagen,
                usuario_id=current_user.id,
                descripcion=f"Análisis de salud - {planta.nombre_personal}"
            )
            imagen_id = imagen_obj.id
            imagen_url = imagen_obj.url_blob
            
            # Leer bytes de la imagen para Gemini
            await imagen.seek(0)  # Reset file pointer
            imagen_bytes = await imagen.read()
            
        elif incluir_imagen_principal and planta.imagen_principal_id:
            # Usar imagen principal existente
            imagen_principal = db.query(Imagen).filter(
                Imagen.id == planta.imagen_principal_id
            ).first()
            
            if imagen_principal:
                imagen_id = imagen_principal.id
                imagen_url = imagen_principal.url_blob
                
                # Descargar imagen desde Azure para enviar a Gemini
                from app.services.imagen_service import AzureBlobService
                azure_service = AzureBlobService()
                imagen_bytes = azure_service.descargar_blob(imagen_principal.nombre_blob)
        
        # 3. Construir contexto de la planta
        ahora = datetime.now()
        contexto_planta = {
            "nombre_personal": getattr(planta, 'nombre_personal', 'Planta sin nombre'),
            "ubicacion": getattr(planta, 'ubicacion', 'Sin ubicación'),
            "frecuencia_riego_dias": getattr(planta, 'frecuencia_riego_dias', 7),
            "luz_actual": getattr(planta, 'luz_actual', 'media'),
            "notas": getattr(planta, 'notas', None),
            "edad_aproximada_dias": (ahora - planta.created_at).days if hasattr(planta, 'created_at') and planta.created_at else None,
            "ultimo_riego": getattr(planta, 'ultimo_riego').isoformat() if hasattr(planta, 'ultimo_riego') and getattr(planta, 'ultimo_riego') else None,
            "estado_salud_actual": getattr(planta, 'estado_salud', 'desconocido')
        }
        
        # Agregar datos de especie si existe
        if hasattr(planta, 'especie') and planta.especie:
            contexto_planta["especie"] = {
                "nombre_cientifico": getattr(planta.especie, 'nombre_cientifico', 'Desconocido'),
                "nombre_comun": getattr(planta.especie, 'nombre_comun', 'Desconocido'),
                "familia": getattr(planta.especie, 'familia', 'Desconocido')
            }
        
        # 4. Llamar a Gemini Service para análisis
        resultado_dict = GeminiService.analizar_salud_planta(
            datos_planta=contexto_planta,
            imagen_bytes=imagen_bytes,
            usuario_id=current_user.id
        )
        
        tiempo_analisis = resultado_dict["metadata"]["tiempo_analisis_ms"]
        
        # Convertir resultado dict a schemas
        from app.schemas.salud_planta import (
            EstadoSaludDetallado,
            ProblemaDetectado,
            RecomendacionItem,
            SaludAnalisisMetadata
        )
        
        # 5. Guardar análisis en BD
        nuevo_analisis = AnalisisSalud(
            planta_id=planta_id,
            usuario_id=current_user.id,
            imagen_id=imagen_id,
            estado_salud=resultado_dict["estado"],
            confianza=resultado_dict["confianza"],
            resumen_diagnostico=resultado_dict["resumen"],
            diagnostico_detallado=resultado_dict.get("diagnostico_completo", ""),
            modelo_ia_usado=resultado_dict["metadata"]["modelo"],
            tiempo_analisis_ms=tiempo_analisis,
            version_prompt=resultado_dict["metadata"]["version_prompt"],
            con_imagen=resultado_dict["metadata"]["con_imagen"],
            fecha_analisis=ahora
        )
        
        # Guardar problemas y recomendaciones como JSON
        problemas_list = resultado_dict.get("problemas_detectados", [])
        if problemas_list:
            nuevo_analisis.set_problemas(problemas_list)
        
        recomendaciones_list = resultado_dict.get("recomendaciones", [])
        if recomendaciones_list:
            nuevo_analisis.set_recomendaciones(recomendaciones_list)
        
        db.add(nuevo_analisis)
        
        # 6. Actualizar estado de salud de la planta si cambió significativamente
        # Solo actualizar si el nuevo estado es diferente y la confianza es alta (>70%)
        if resultado_dict["confianza"] >= 0.7 and resultado_dict["estado"] != planta.estado_salud:
            planta.estado_salud = resultado_dict["estado"]
            planta.updated_at = datetime.now()
        
        db.commit()
        db.refresh(nuevo_analisis)
        
        # 7. Construir respuesta usando los schemas
        problemas_response = [ProblemaDetectado(**p) for p in problemas_list]
        recomendaciones_response = [RecomendacionItem(**r) for r in recomendaciones_list]
        
        metadata_response = SaludAnalisisMetadata(
            confianza=resultado_dict["confianza"],
            modelo_usado=resultado_dict["metadata"]["modelo"],
            tiempo_analisis_ms=tiempo_analisis,
            version_prompt=resultado_dict["metadata"]["version_prompt"],
            con_imagen=resultado_dict["metadata"]["con_imagen"],
            fecha_analisis=resultado_dict["metadata"]["timestamp"]
        )
        
        return SaludAnalisisResponse(
            id=nuevo_analisis.id,
            planta_id=planta_id,
            usuario_id=current_user.id,
            estado=EstadoSaludDetallado(resultado_dict["estado"]),
            confianza=resultado_dict["confianza"],
            resumen=resultado_dict["resumen"],
            diagnostico_detallado=resultado_dict.get("diagnostico_completo", ""),
            problemas_detectados=problemas_response,
            recomendaciones=recomendaciones_response,
            metadata=metadata_response,
            imagen_analizada_url=imagen_url
        )
    
    except HTTPException:
        raise
    except ValueError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al analizar salud de la planta: {str(e)}"
        )


@router.get(
    "/{planta_id}/historial-salud",
    response_model=HistorialSaludResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener historial de análisis de salud",
    description="Obtiene el historial paginado de análisis de salud de una planta específica",
    response_description="Lista paginada de análisis de salud históricos"
)
async def obtener_historial_salud(
    planta_id: int,
    skip: int = Query(0, ge=0, description="Número de registros a saltar para paginación"),
    limit: int = Query(10, ge=1, le=100, description="Número máximo de registros a retornar"),
    estado: Optional[str] = Query(None, description="Filtrar por estado de salud específico"),
    fecha_desde: Optional[datetime] = Query(None, description="Filtrar análisis desde esta fecha"),
    fecha_hasta: Optional[datetime] = Query(None, description="Filtrar análisis hasta esta fecha"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtiene el historial de análisis de salud de una planta.
    
    Este endpoint retorna todos los análisis de salud realizados sobre una planta
    específica, ordenados por fecha descendente (más recientes primero).
    
    **Características:**
    - Paginación mediante skip/limit
    - Filtrado por estado de salud
    - Filtrado por rango de fechas
    - URLs de imágenes incluidas (si existen)
    - Contador de problemas y recomendaciones
    
    **Filtros disponibles:**
    - **estado**: Filtra por estado (excelente, saludable, necesita_atencion, enfermedad, plaga, critica)
    - **fecha_desde**: Análisis posteriores a esta fecha
    - **fecha_hasta**: Análisis anteriores a esta fecha
    
    **Respuesta:**
    - Lista de análisis con información resumida
    - Total de análisis que cumplen los criterios
    - Información de la planta
    
    **Ejemplos de uso:**
    - Últimos 10 análisis: GET /api/plantas/5/historial-salud
    - Análisis con problemas: GET /api/plantas/5/historial-salud?estado=enfermedad
    - Análisis del último mes: GET /api/plantas/5/historial-salud?fecha_desde=2025-01-01
    
    **Args:**
    - **planta_id**: ID de la planta
    - **skip**: Registros a saltar (default: 0)
    - **limit**: Máximo de registros (default: 10, max: 100)
    - **estado**: Estado de salud a filtrar (opcional)
    - **fecha_desde**: Fecha inicio del rango (opcional)
    - **fecha_hasta**: Fecha fin del rango (opcional)
    
    **Returns:**
    - HistorialSaludResponse con lista de análisis y metadatos
    
    **Raises:**
    - 404: Si la planta no existe o no pertenece al usuario
    - 400: Si los parámetros son inválidos
    - 500: Si hay error interno del servidor
    """
    try:
        # 1. Verificar que la planta existe y pertenece al usuario
        query_planta = db.query(Planta).filter(
            Planta.id == planta_id,
            Planta.usuario_id == current_user.id
        )
        
        # Filtrar por activa solo si el campo existe
        if hasattr(Planta, 'activa'):
            query_planta = query_planta.filter(Planta.activa == True)
        
        planta = query_planta.first()
        
        if not planta:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Planta con ID {planta_id} no encontrada"
            )
        
        # 2. Construir query base para análisis
        query = db.query(AnalisisSalud).filter(
            AnalisisSalud.planta_id == planta_id
        )
        
        # 3. Aplicar filtros opcionales
        if estado:
            # Validar que el estado es válido
            try:
                estado_enum = EstadoSaludDetallado(estado)
                query = query.filter(AnalisisSalud.estado_salud == estado_enum.value)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Estado '{estado}' no válido. Debe ser uno de: {[e.value for e in EstadoSaludDetallado]}"
                )
        
        if fecha_desde:
            query = query.filter(AnalisisSalud.fecha_analisis >= fecha_desde)
        
        if fecha_hasta:
            query = query.filter(AnalisisSalud.fecha_analisis <= fecha_hasta)
        
        # 4. Obtener total de registros que cumplen los filtros
        total = query.count()
        
        # 5. Aplicar ordenamiento y paginación
        analisis_list = query.order_by(
            AnalisisSalud.fecha_analisis.desc()
        ).offset(skip).limit(limit).all()
        
        # 6. Construir respuesta con URLs de imágenes
        from app.services.imagen_service import AzureBlobService
        azure_service = AzureBlobService()
        
        historial_items = []
        for analisis in analisis_list:
            # Obtener URL de imagen si existe
            imagen_url = None
            if analisis.imagen_id:
                imagen = db.query(Imagen).filter(Imagen.id == analisis.imagen_id).first()
                if imagen:
                    imagen_url = azure_service.generar_url_con_sas(
                        imagen.nombre_blob,
                        expiracion_horas=1
                    )
            
            # Contar problemas y recomendaciones
            problemas_list = analisis.get_problemas_list()
            recomendaciones_list = analisis.get_recomendaciones_list()
            
            # Truncar resumen si es muy largo
            resumen_truncado = analisis.resumen_diagnostico[:197] + "..." if len(analisis.resumen_diagnostico) > 200 else analisis.resumen_diagnostico
            
            item = HistorialSaludItem(
                id=analisis.id,
                planta_id=analisis.planta_id,
                estado=EstadoSaludDetallado(analisis.estado_salud),
                confianza=analisis.confianza,
                resumen=resumen_truncado,
                fecha_analisis=analisis.fecha_analisis,
                con_imagen=analisis.con_imagen,
                imagen_analizada_url=imagen_url,
                num_problemas=len(problemas_list),
                num_recomendaciones=len(recomendaciones_list)
            )
            historial_items.append(item)
        
        # 7. Construir respuesta final
        return HistorialSaludResponse(
            analisis=historial_items,
            total=total,
            planta_id=planta_id
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener historial de salud: {str(e)}"
        )
