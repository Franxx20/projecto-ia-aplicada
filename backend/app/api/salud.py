"""
Router de salud - Endpoints para análisis de salud de plantas con Gemini AI.

Este módulo contiene todos los endpoints REST para crear análisis de salud,
consultar historial, estadísticas y tendencias de salud de las plantas.

Integra el servicio de Gemini AI para análisis inteligente de salud vegetal.

Autor: Equipo Backend
Fecha: Noviembre 2025
Epic: Epic 3 - Sistema de verificación de Salud con Gemini AI
Task: T-078
"""

from datetime import datetime, timedelta
from typing import List, Optional
import logging
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func

# Configurar logger
logger = logging.getLogger(__name__)

from app.db.session import get_db
from app.schemas.salud_planta import (
    VerificarSaludRequest,
    SolicitudAnalisisSalud,
    SaludAnalisisResponse,
    AnalisisSaludResponse,
    DetalleAnalisisSaludResponse,
    EstadisticasSaludResponse,
    HistorialSaludResponse,
    EstadisticasSaludPlanta
)
from app.services.gemini_service import GeminiService
from app.utils.jwt import get_current_user
from app.db.models import Usuario, Planta, AnalisisSalud, Imagen

# Crear router de salud
router = APIRouter()

# Instanciar servicio de Gemini
gemini_service = GeminiService()


@router.post(
    "/analisis-con-imagen",
    response_model=AnalisisSaludResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear análisis de salud con imagen nueva",
    description="Analiza la salud de una planta subiendo una nueva imagen que se asociará a la planta",
    response_description="Análisis de salud creado exitosamente con imagen asociada"
)
async def crear_analisis_salud_con_imagen(
    planta_id: int = Form(..., description="ID de la planta a analizar"),
    archivo: UploadFile = File(..., description="Imagen de la planta para análisis"),
    sintomas_observados: Optional[str] = Form(None, description="Síntomas observados"),
    notas_adicionales: Optional[str] = Form(None, description="Notas adicionales"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Crea un nuevo análisis de salud subiendo una nueva imagen.
    
    La imagen se:
    1. Sube a Azure Blob Storage
    2. Guarda en la tabla imagenes
    3. Asocia con la planta (aparecerá en la sección Photos)
    4. Usa para el análisis de salud con Gemini AI
    
    **Parámetros:**
    - **planta_id**: ID de la planta a analizar (requerido)
    - **archivo**: Archivo de imagen (JPG, PNG, WEBP) (requerido)
    - **sintomas_observados**: Descripción de síntomas (opcional)
    - **notas_adicionales**: Notas adicionales (opcional)
    
    **Retorna:**
    - Análisis completo de salud con recomendaciones
    - La imagen queda asociada a la planta
    """
    try:
        # 1. Validar que la planta existe y pertenece al usuario
        planta = db.query(Planta).filter(
            and_(
                Planta.id == planta_id,
                Planta.usuario_id == current_user.id
            )
        ).first()
        
        if not planta:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Planta con ID {planta_id} no encontrada o no pertenece al usuario"
            )
        
        # 2. Subir la imagen a Azure y guardarla en BD
        from app.services.imagen_service import ImagenService
        imagen_service = ImagenService(db)
        
        nueva_imagen = await imagen_service.subir_imagen(
            archivo=archivo,
            usuario_id=current_user.id,
            descripcion=f"Análisis de salud de {planta.nombre_personal}"
        )
        
        logger.info(f"✅ Imagen subida: ID={nueva_imagen.id}, {nueva_imagen.tamano_bytes} bytes")
        
        # 3. Descargar la imagen para análisis
        from app.services.imagen_service import AzureBlobService
        azure_service = AzureBlobService()
        imagen_bytes = azure_service.descargar_blob(nueva_imagen.nombre_blob)
        
        # 4. Construir contexto de la planta para el análisis
        especie_nombre = "Desconocida"
        especie_cientifica = None
        familia = "Desconocida"
        
        if planta.especie_id:
            from app.db.models import Especie
            especie = db.query(Especie).filter(Especie.id == planta.especie_id).first()
            if especie:
                especie_nombre = especie.nombre_comun or "Desconocida"
                especie_cientifica = especie.nombre_cientifico
                familia = especie.familia or "Desconocida"
        
        # Calcular datos contextuales
        dias_desde_adquisicion = (datetime.utcnow() - planta.fecha_adquisicion).days if planta.fecha_adquisicion else 0
        dias_desde_riego = (datetime.utcnow() - planta.fecha_ultimo_riego).days if planta.fecha_ultimo_riego else None
        
        estado_riego = "normal"
        if dias_desde_riego and planta.frecuencia_riego_dias:
            if dias_desde_riego > planta.frecuencia_riego_dias + 2:
                estado_riego = "atrasado"
            elif dias_desde_riego < planta.frecuencia_riego_dias - 2:
                estado_riego = "adelantado"
        
        contexto_planta = {
            "nombre_personal": planta.nombre_personal,
            "nombre_cientifico": especie_cientifica or "Desconocida",
            "nombre_comun": especie_nombre,
            "familia": familia,
            "dias_desde_adquisicion": dias_desde_adquisicion,
            "ubicacion": planta.ubicacion or "No especificada",
            "luz_actual": planta.luz_actual or "No especificada",
            "dias_desde_riego": dias_desde_riego or "N/A",
            "frecuencia_riego_dias": planta.frecuencia_riego_dias or "N/A",
            "estado_riego": estado_riego,
            "estado_salud": planta.estado_salud or "desconocido",
            "fecha_ultimo_analisis": "Nunca",
            "notas": f"{planta.notas or ''}\n\nSíntomas observados: {sintomas_observados or 'Ninguno'}\n\nNotas adicionales: {notas_adicionales or 'Ninguna'}"
        }
        
        # 5. Llamar a Gemini AI para análisis
        resultado_gemini = gemini_service.analizar_salud_planta(
            datos_planta=contexto_planta,
            imagen_bytes=imagen_bytes,
            usuario_id=current_user.id
        )
        
        # 6. Crear registro de análisis en BD
        import json
        metadata = resultado_gemini.get("metadata", {})
        
        nuevo_analisis = AnalisisSalud(
            planta_id=planta.id,
            usuario_id=current_user.id,
            imagen_id=nueva_imagen.id,  # ⭐ Asociar la imagen
            estado=resultado_gemini["estado"],
            confianza=resultado_gemini["confianza"],
            resumen_diagnostico=resultado_gemini["resumen"],
            diagnostico_detallado=resultado_gemini.get("diagnostico_completo"),
            problemas_detectados=json.dumps(resultado_gemini.get("problemas_detectados", []), ensure_ascii=False),
            recomendaciones=json.dumps(resultado_gemini.get("recomendaciones", []), ensure_ascii=False),
            modelo_ia_usado=metadata.get("modelo", "gemini-2.5-flash"),
            tiempo_analisis_ms=metadata.get("tiempo_analisis_ms", 0),
            version_prompt=metadata.get("version_prompt", "v1.0"),
            con_imagen=True,
            notas_usuario=notas_adicionales,
            fecha_analisis=datetime.utcnow()
        )
        
        db.add(nuevo_analisis)
        db.commit()
        db.refresh(nuevo_analisis)
        
        # 7. Actualizar estado de la planta
        try:
            estado_gemini = resultado_gemini.get("estado")
            
            def _map_estado_gemini_a_planta(eg: Optional[str]) -> str:
                if not eg:
                    return planta.estado_salud or "desconocido"
                eg_norm = eg.strip().lower()
                if eg_norm in ("excelente", "excellent"):
                    return "excelente"
                if eg_norm in ("saludable", "buena", "good", "healthy"):
                    return "saludable"
                if eg_norm in ("necesita_atencion", "necesita atención", "needs_attention", "attention_needed"):
                    return "necesita_atencion"
                if eg_norm in ("enfermedad", "disease", "sick"):
                    return "enfermedad"
                if eg_norm in ("plaga", "pest", "infestation"):
                    return "plaga"
                if eg_norm in ("critica", "crítica", "critical"):
                    return "critica"
                if eg_norm in ("desconocido", "unknown"):
                    return "desconocido"
                return planta.estado_salud or "desconocido"
            
            nuevo_estado_planta = _map_estado_gemini_a_planta(estado_gemini)
            if nuevo_estado_planta and nuevo_estado_planta != (planta.estado_salud or ""):
                planta.estado_salud = nuevo_estado_planta
                planta.updated_at = datetime.utcnow()
                db.add(planta)
                db.commit()
                db.refresh(planta)
        except Exception:
            logger.exception("Error al actualizar estado de la planta después del análisis")
        
        logger.info(f"✅ Análisis creado con imagen asociada a la planta {planta_id}")
        
        # 8. Preparar respuesta
        analisis_dict = nuevo_analisis.to_dict()
        return AnalisisSaludResponse(**analisis_dict)
    
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        db.rollback()
        logger.exception(f"Error al crear análisis de salud con imagen")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear análisis de salud: {str(e)}"
        )


@router.post(
    "/analisis",
    response_model=AnalisisSaludResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear análisis de salud de planta",
    description="Analiza la salud de una planta usando Gemini AI con o sin imagen",
    response_description="Análisis de salud creado exitosamente"
)
async def crear_analisis_salud(
    solicitud: SolicitudAnalisisSalud,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Crea un nuevo análisis de salud para una planta utilizando Gemini AI.
    
    **Parámetros:**
    - **planta_id**: ID de la planta a analizar (requerido)
    - **imagen_id**: ID de la imagen para análisis visual (opcional)
    - **sintomas_observados**: Descripción de síntomas por parte del usuario (opcional)
    - **notas_adicionales**: Notas o contexto adicional (opcional)
    
    **Proceso:**
    1. Valida que la planta pertenezca al usuario
    2. Obtiene información de la planta (especie, edad, etc.)
    3. Si hay imagen_id, carga la imagen desde Azure Blob Storage
    4. Envía prompt a Gemini AI con contexto de la planta
    5. Parsea respuesta estructurada de Gemini
    6. Guarda análisis en base de datos
    7. Retorna análisis completo con recomendaciones
    
    **Retorna:**
    - Estado de salud (excelente, saludable, necesita_atencion, enfermedad, plaga, critica)
    - Nivel de confianza (0-100)
    - Diagnóstico resumido y detallado
    - Lista de problemas detectados con severidad
    - Recomendaciones personalizadas
    - Metadatos del análisis (modelo usado, tiempo, etc.)
    """
    try:
        # 1. Validar que la planta existe y pertenece al usuario
        planta = db.query(Planta).filter(
            and_(
                Planta.id == solicitud.planta_id,
                Planta.usuario_id == current_user.id
            )
        ).first()
        
        if not planta:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Planta con ID {solicitud.planta_id} no encontrada o no pertenece al usuario"
            )
        
        # 2. Obtener imagen si se proporcionó imagen_id
        imagen = None
        imagen_bytes = None
        
        if solicitud.imagen_id:
            imagen = db.query(Imagen).filter(
                and_(
                    Imagen.id == solicitud.imagen_id,
                    Imagen.usuario_id == current_user.id
                )
            ).first()
            
            if not imagen:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Imagen con ID {solicitud.imagen_id} no encontrada o no pertenece al usuario"
                )
            
            # Descargar imagen desde Azure Blob Storage
            try:
                from app.services.imagen_service import AzureBlobService
                azure_service = AzureBlobService()
                imagen_bytes = azure_service.descargar_blob(imagen.nombre_blob)
                logger.info(f"✅ Imagen descargada desde Azure Blob Storage: {len(imagen_bytes)} bytes")
            except Exception as e:
                logger.error(f"❌ Error al descargar imagen desde Azure: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Error al cargar la imagen para análisis: {str(e)}"
                )
        else:
            imagen_bytes = None
        
        # 3. Construir contexto de la planta para el análisis
        # Nota: La relación especie está comentada en el modelo, usar especie_id directamente
        especie_nombre = "Desconocida"
        especie_cientifica = None
        familia = "Desconocida"
        
        # Intentar obtener información de especie si existe el ID
        if planta.especie_id:
            from app.db.models import Especie
            especie = db.query(Especie).filter(Especie.id == planta.especie_id).first()
            if especie:
                especie_nombre = especie.nombre_comun or "Desconocida"
                especie_cientifica = especie.nombre_cientifico
                familia = especie.familia or "Desconocida"
        
        # Calcular días desde adquisición
        dias_desde_adquisicion = (datetime.utcnow() - planta.fecha_adquisicion).days if planta.fecha_adquisicion else 0
        
        # Calcular días desde último riego
        dias_desde_riego = (datetime.utcnow() - planta.fecha_ultimo_riego).days if planta.fecha_ultimo_riego else None
        
        # Determinar estado de riego
        estado_riego = "normal"
        if dias_desde_riego and planta.frecuencia_riego_dias:
            if dias_desde_riego > planta.frecuencia_riego_dias + 2:
                estado_riego = "atrasado"
            elif dias_desde_riego < planta.frecuencia_riego_dias - 2:
                estado_riego = "adelantado"
        
        # Construir datos en el formato que espera GeminiService
        contexto_planta = {
            "nombre_personal": planta.nombre_personal,
            "nombre_cientifico": especie_cientifica or "Desconocida",
            "nombre_comun": especie_nombre,
            "familia": familia,
            "dias_desde_adquisicion": dias_desde_adquisicion,
            "ubicacion": planta.ubicacion or "No especificada",
            "luz_actual": planta.luz_actual or "No especificada",
            "dias_desde_riego": dias_desde_riego or "N/A",
            "frecuencia_riego_dias": planta.frecuencia_riego_dias or "N/A",
            "estado_riego": estado_riego,
            "estado_salud": "desconocido",  # TODO: Obtener último análisis
            "fecha_ultimo_analisis": "Nunca",  # TODO: Obtener último análisis
            "notas": f"{planta.notas or ''}\n\nSíntomas observados: {solicitud.sintomas_observados or 'Ninguno'}\n\nNotas adicionales: {solicitud.notas_adicionales or 'Ninguna'}"
        }
        
        # 4. Llamar a Gemini AI para análisis
        inicio = datetime.utcnow()
        
        resultado_gemini = gemini_service.analizar_salud_planta(
            datos_planta=contexto_planta,
            imagen_bytes=imagen_bytes,  # TODO: Obtener bytes desde Azure Blob Storage
            usuario_id=current_user.id
        )
        
        # 6. Crear registro de análisis en BD
        import json
        
        # Extraer metadata del resultado de Gemini
        metadata = resultado_gemini.get("metadata", {})
        
        nuevo_analisis = AnalisisSalud(
            planta_id=planta.id,
            usuario_id=current_user.id,
            imagen_id=solicitud.imagen_id,
            estado=resultado_gemini["estado"],
            confianza=resultado_gemini["confianza"],
            resumen_diagnostico=resultado_gemini["resumen"],  # Gemini usa "resumen"
            diagnostico_detallado=resultado_gemini.get("diagnostico_completo"),  # Gemini usa "diagnostico_completo"
            problemas_detectados=json.dumps(resultado_gemini.get("problemas_detectados", []), ensure_ascii=False),
            recomendaciones=json.dumps(resultado_gemini.get("recomendaciones", []), ensure_ascii=False),
            modelo_ia_usado=metadata.get("modelo", "gemini-2.5-flash"),
            tiempo_analisis_ms=metadata.get("tiempo_analisis_ms", 0),
            version_prompt=metadata.get("version_prompt", "v1.0"),
            con_imagen=metadata.get("con_imagen", imagen_bytes is not None),
            notas_usuario=solicitud.notas_adicionales,
            fecha_analisis=datetime.utcnow()
        )
        
        db.add(nuevo_analisis)
        db.commit()
        db.refresh(nuevo_analisis)

        # 7. Actualizar el estado de la planta en base al último análisis
        try:
            estado_gemini = resultado_gemini.get("estado")

            def _map_estado_gemini_a_planta(eg: Optional[str]) -> str:
                """
                Mapea el estado devuelto por Gemini a los valores estándar del sistema.
                
                Estados estándar: excelente, saludable, necesita_atencion, enfermedad, plaga, critica, desconocido
                """
                if not eg:
                    return planta.estado_salud or "desconocido"
                
                eg_norm = eg.strip().lower()
                
                # Mapear estados de Gemini a estados estándar (minúsculas, sin capitalizar)
                if eg_norm in ("excelente", "excellent"):
                    return "excelente"
                if eg_norm in ("saludable", "buena", "good", "healthy"):
                    return "saludable"
                if eg_norm in ("necesita_atencion", "necesita atención", "needs_attention", "attention_needed"):
                    return "necesita_atencion"
                if eg_norm in ("enfermedad", "disease", "sick"):
                    return "enfermedad"
                if eg_norm in ("plaga", "pest", "infestation"):
                    return "plaga"
                if eg_norm in ("critica", "crítica", "critical"):
                    return "critica"
                if eg_norm in ("desconocido", "unknown"):
                    return "desconocido"
                
                # Si no coincide con ninguno, mantener el estado actual
                return planta.estado_salud or "desconocido"

            nuevo_estado_planta = _map_estado_gemini_a_planta(estado_gemini)
            
            # Guardar el estado en minúsculas (sin capitalize)
            if nuevo_estado_planta and nuevo_estado_planta != (planta.estado_salud or ""):
                planta.estado_salud = nuevo_estado_planta  # Sin .capitalize()
                planta.updated_at = datetime.utcnow()
                db.add(planta)
                db.commit()
                db.refresh(planta)
        except Exception:
            # No queremos que la actualización del estado de planta impida devolver el análisis
            logger.exception("Error al actualizar estado de la planta después del análisis")

        # 8. Preparar respuesta
        analisis_dict = nuevo_analisis.to_dict()

        return AnalisisSaludResponse(**analisis_dict)
    
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear análisis de salud: {str(e)}"
        )


@router.get(
    "/analisis/{analisis_id}",
    response_model=DetalleAnalisisSaludResponse,
    summary="Obtener análisis de salud específico",
    description="Recupera un análisis de salud por su ID con toda la información detallada",
    response_description="Análisis de salud encontrado"
)
async def obtener_analisis_salud(
    analisis_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtiene los detalles completos de un análisis de salud específico.
    
    **Parámetros:**
    - **analisis_id**: ID del análisis a recuperar
    
    **Retorna:**
    - Análisis completo con información de la planta asociada
    - Imagen asociada (si existe)
    - Tendencia de salud comparado con análisis previos
    - Indicador si el estado es crítico
    """
    try:
        # Buscar análisis que pertenezca al usuario
        analisis = db.query(AnalisisSalud).filter(
            and_(
                AnalisisSalud.id == analisis_id,
                AnalisisSalud.usuario_id == current_user.id
            )
        ).first()
        
        if not analisis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Análisis con ID {analisis_id} no encontrado"
            )
        
        # Obtener análisis previos de la misma planta para calcular tendencia
        analisis_previos = db.query(AnalisisSalud).filter(
            and_(
                AnalisisSalud.planta_id == analisis.planta_id,
                AnalisisSalud.fecha_analisis < analisis.fecha_analisis
            )
        ).order_by(desc(AnalisisSalud.fecha_analisis)).limit(5).all()
        
        # Preparar respuesta enriquecida
        analisis_dict = analisis.to_dict()
        analisis_dict["tendencia"] = analisis.calcular_tendencia(analisis_previos)
        analisis_dict["es_critico"] = analisis.es_critico()
        analisis_dict["color_estado"] = analisis.obtener_color_estado()
        
        # Agregar info de planta
        if analisis.planta:
            # Obtener nombre de especie si existe especie_id
            especie_nombre = None
            if analisis.planta.especie_id:
                from app.db.models import Especie
                especie = db.query(Especie).filter(Especie.id == analisis.planta.especie_id).first()
                if especie:
                    especie_nombre = especie.nombre_comun
            
            analisis_dict["planta"] = {
                "id": analisis.planta.id,
                "nombre_personal": analisis.planta.nombre_personal,
                "especie": especie_nombre
            }
        
        # Agregar info de imagen si existe
        if analisis.imagen:
            analisis_dict["imagen_url"] = analisis.imagen.url_blob
        
        # 🆕 Agregar TODAS las imágenes usadas en el análisis (si están en metadatos)
        imagenes_urls = []
        try:
            if analisis.metadatos_ia:
                import json
                metadatos = json.loads(analisis.metadatos_ia)
                imagenes_ids = metadatos.get("imagenes_ids", [])
                
                if imagenes_ids:
                    from app.db.models import Imagen
                    from app.services.imagen_service import AzureBlobService
                    
                    azure_service = AzureBlobService()
                    imagenes = db.query(Imagen).filter(Imagen.id.in_(imagenes_ids)).all()
                    
                    for imagen in imagenes:
                        # Generar URL con SAS token
                        url_con_sas = azure_service.generar_url_con_sas(
                            imagen.nombre_blob,
                            expiracion_horas=1
                        )
                        imagenes_urls.append({
                            "id": imagen.id,
                            "url": url_con_sas,
                            "nombre_archivo": imagen.nombre_archivo,
                            "organ": imagen.organ
                        })
                    
                    logger.info(f"✅ Cargadas {len(imagenes_urls)} imágenes para análisis {analisis_id}")
        except Exception as e:
            logger.warning(f"⚠️  Error al cargar imágenes del análisis: {str(e)}")
        
        analisis_dict["imagenes"] = imagenes_urls if imagenes_urls else None
        
        return DetalleAnalisisSaludResponse(**analisis_dict)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener análisis: {str(e)}"
        )


@router.get(
    "/estadisticas/{planta_id}",
    response_model=EstadisticasSaludResponse,
    summary="Obtener estadísticas de salud de una planta",
    description="Recupera estadísticas y métricas de salud de una planta específica",
    response_description="Estadísticas de salud de la planta"
)
async def obtener_estadisticas_salud(
    planta_id: int,
    dias: int = Query(30, ge=7, le=365, description="Días hacia atrás para calcular estadísticas"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Calcula estadísticas de salud para una planta en un período específico.
    
    **Parámetros:**
    - **planta_id**: ID de la planta
    - **dias**: Cantidad de días hacia atrás (default: 30, min: 7, max: 365)
    
    **Retorna:**
    - Total de análisis realizados
    - Estado actual de salud
    - Tendencia general (mejorando/estable/empeorando)
    - Confianza promedio de los análisis
    - Distribución de estados de salud
    - Problemas más frecuentes
    - Análisis más reciente
    """
    try:
        # Validar que la planta existe y pertenece al usuario
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
        
        # Calcular fecha de inicio del período
        fecha_inicio = datetime.utcnow() - timedelta(days=dias)
        
        # Obtener todos los análisis del período
        analisis_periodo = db.query(AnalisisSalud).filter(
            and_(
                AnalisisSalud.planta_id == planta_id,
                AnalisisSalud.fecha_analisis >= fecha_inicio
            )
        ).order_by(desc(AnalisisSalud.fecha_analisis)).all()
        
        if not analisis_periodo:
            # Retornar estadísticas vacías en lugar de 404
            return EstadisticasSaludResponse(
                planta_id=planta_id,
                nombre_planta=str(planta.nombre_personal),
                periodo_dias=dias,
                total_analisis=0,
                estado_actual="sin_datos",
                confianza_actual=0,
                tendencia_general="sin_datos",
                confianza_promedio=0.0,
                distribucion_estados={},
                problemas_frecuentes=[],
                ultimo_analisis=None,
                requiere_atencion=False
            )
        
        # Calcular estadísticas
        total_analisis = len(analisis_periodo)
        analisis_reciente = analisis_periodo[0]
        
        # Confianza promedio
        confianza_promedio = sum(a.confianza for a in analisis_periodo) / total_analisis
        
        # Distribución de estados
        from collections import Counter
        distribucion_estados = Counter(a.estado for a in analisis_periodo)
        
        # Tendencia general (comparar primeros 3 con últimos 3 análisis)
        if total_analisis >= 6:
            ultimos_3 = analisis_periodo[:3]
            primeros_3 = analisis_periodo[-3:]
            tendencia = analisis_reciente.calcular_tendencia(primeros_3)
        elif total_analisis >= 2:
            tendencia = analisis_reciente.calcular_tendencia([analisis_periodo[-1]])
        else:
            tendencia = "insuficientes_datos"
        
        # Problemas más frecuentes
        import json
        todos_problemas = []
        for analisis in analisis_periodo:
            try:
                problemas = json.loads(analisis.problemas_detectados)
                todos_problemas.extend([p.get("tipo", "desconocido") for p in problemas])
            except:
                pass
        
        problemas_frecuentes = Counter(todos_problemas).most_common(5)
        
        # Calcular días desde el último análisis
        dias_desde_ultimo = (datetime.utcnow() - analisis_reciente.fecha_analisis).days
        
        # Preparar respuesta
        estadisticas = {
            "planta_id": planta_id,
            "nombre_planta": planta.nombre_personal,
            "periodo_dias": dias,
            "total_analisis": total_analisis,
            "estado_actual": analisis_reciente.estado,
            "confianza_actual": analisis_reciente.confianza,
            "tendencia_general": tendencia,
            "confianza_promedio": round(confianza_promedio, 1),
            "distribucion_estados": dict(distribucion_estados),
            "problemas_frecuentes": [{"tipo": tipo, "frecuencia": freq} for tipo, freq in problemas_frecuentes],
            "ultimo_analisis": analisis_reciente.to_dict(),
            "requiere_atencion": analisis_reciente.es_critico(),
            # Campos de compatibilidad con frontend
            "ultimo_estado": analisis_reciente.estado,
            "tendencia": tendencia,
            "dias_desde_ultimo_analisis": dias_desde_ultimo
        }
        
        return EstadisticasSaludResponse(**estadisticas)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al calcular estadísticas: {str(e)}"
        )


@router.get(
    "/historial",
    response_model=HistorialSaludResponse,
    summary="Obtener historial de análisis de salud",
    description="Lista el historial de análisis de salud con filtros opcionales",
    response_description="Lista paginada de análisis de salud"
)
async def obtener_historial_salud(
    planta_id: Optional[int] = Query(None, description="Filtrar por ID de planta"),
    estado: Optional[str] = Query(None, description="Filtrar por estado (excelente, saludable, etc.)"),
    fecha_desde: Optional[datetime] = Query(None, description="Filtrar desde fecha (ISO format)"),
    fecha_hasta: Optional[datetime] = Query(None, description="Filtrar hasta fecha (ISO format)"),
    limite: int = Query(20, ge=1, le=100, description="Cantidad máxima de resultados"),
    offset: int = Query(0, ge=0, description="Cantidad de resultados a saltar (paginación)"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtiene el historial de análisis de salud con filtros opcionales.
    
    **Parámetros de filtrado:**
    - **planta_id**: Filtrar por planta específica (opcional)
    - **estado**: Filtrar por estado de salud (opcional)
    - **fecha_desde**: Análisis desde esta fecha (opcional)
    - **fecha_hasta**: Análisis hasta esta fecha (opcional)
    - **limite**: Cantidad máxima de resultados (default: 20, max: 100)
    - **offset**: Cantidad de resultados a saltar para paginación (default: 0)
    
    **Retorna:**
    - Lista de análisis ordenados por fecha descendente
    - Total de resultados que coinciden con los filtros
    - Metadatos de paginación
    """
    try:
        # Construir query base con eager loading de la relación planta
        from sqlalchemy.orm import joinedload
        
        query = db.query(AnalisisSalud).options(
            joinedload(AnalisisSalud.planta)
        ).filter(
            AnalisisSalud.usuario_id == current_user.id
        )
        
        # Aplicar filtros opcionales
        if planta_id:
            # Validar que la planta pertenece al usuario
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
            
            query = query.filter(AnalisisSalud.planta_id == planta_id)
        
        if estado:
            query = query.filter(AnalisisSalud.estado == estado)
        
        if fecha_desde:
            query = query.filter(AnalisisSalud.fecha_analisis >= fecha_desde)
        
        if fecha_hasta:
            query = query.filter(AnalisisSalud.fecha_analisis <= fecha_hasta)
        
        # Obtener total antes de paginar
        total = query.count()
        
        # Aplicar ordenamiento y paginación
        analisis_lista = query.order_by(
            desc(AnalisisSalud.fecha_analisis)
        ).limit(limite).offset(offset).all()
        
        # Convertir a formato HistorialSaludItem
        resultados = []
        for analisis in analisis_lista:
            import json
            
            # Obtener URL de imagen si existe
            imagen_url = None
            if analisis.imagen_id is not None:
                from app.db.models import Imagen
                imagen = db.query(Imagen).filter(Imagen.id == analisis.imagen_id).first()
                if imagen and imagen.url_blob:
                    imagen_url = imagen.url_blob
            
            # Contar problemas y recomendaciones
            num_problemas = 0
            problemas_detectados_str = analisis.problemas_detectados
            if problemas_detectados_str:
                try:
                    problemas_list = json.loads(problemas_detectados_str)
                    num_problemas = len(problemas_list) if isinstance(problemas_list, list) else 0
                except (json.JSONDecodeError, TypeError):
                    num_problemas = 0
            
            num_recomendaciones = 0
            recomendaciones_str = analisis.recomendaciones
            if recomendaciones_str:
                try:
                    recomendaciones_list = json.loads(recomendaciones_str)
                    num_recomendaciones = len(recomendaciones_list) if isinstance(recomendaciones_list, list) else 0
                except (json.JSONDecodeError, TypeError):
                    num_recomendaciones = 0
            
            # Truncar resumen si es muy largo
            resumen_original = analisis.resumen_diagnostico if analisis.resumen_diagnostico else ""
            resumen = resumen_original
            if len(resumen_original) > 200:
                resumen = resumen_original[:197] + "..."
            
            # Obtener nombre de la planta
            planta_nombre = None
            if analisis.planta:
                planta_nombre = analisis.planta.nombre_personal
            
            # Crear item del historial según el schema HistorialSaludItem
            item = {
                "id": analisis.id,
                "planta_id": analisis.planta_id,
                "estado": analisis.estado,
                "confianza": analisis.confianza,
                "resumen": resumen,
                "fecha_analisis": analisis.fecha_analisis,
                "con_imagen": analisis.con_imagen,
                "imagen_analizada_url": imagen_url,
                "num_problemas": num_problemas,
                "num_recomendaciones": num_recomendaciones,
                "planta_nombre": planta_nombre
            }
            
            resultados.append(item)
        
        # Preparar respuesta con metadata de paginación
        return HistorialSaludResponse(
            total=total,
            planta_id=planta_id,
            limite=limite,
            offset=offset,
            analisis=resultados
        )
    
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        print(f"ERROR en obtener_historial_salud: {str(e)}")
        print(f"Traceback completo:\n{error_traceback}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener historial: {str(e)}"
        )
