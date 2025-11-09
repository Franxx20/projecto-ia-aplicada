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
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func

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
        imagen_base64 = None
        
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
            
            # TODO: Cargar imagen desde Azure Blob Storage y convertir a bytes
            # Por ahora dejamos None para análisis solo por texto
            imagen_bytes = None
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
        
        # 7. Preparar respuesta
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
            analisis_dict["imagen_url"] = analisis.imagen.blob_url
        
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
            "requiere_atencion": analisis_reciente.es_critico()
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
        # Construir query base
        query = db.query(AnalisisSalud).filter(
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
        
        # Convertir a diccionarios y agregar información adicional
        resultados = []
        for analisis in analisis_lista:
            analisis_dict = analisis.to_dict()
            
            # Agregar nombre de planta
            if analisis.planta:
                analisis_dict["planta_nombre"] = analisis.planta.nombre_personal
            
            # Agregar indicadores calculados
            analisis_dict["es_critico"] = analisis.es_critico()
            analisis_dict["color_estado"] = analisis.obtener_color_estado()
            
            resultados.append(analisis_dict)
        
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener historial: {str(e)}"
        )
