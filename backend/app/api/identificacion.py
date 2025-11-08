"""
API de Identificación de Plantas con PlantNet.

Endpoints para identificar plantas usando IA, consultar historial
y gestionar identificaciones validadas por el usuario.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import Usuario
from app.services.identificacion_service import IdentificacionService
from app.services.imagen_service import ImagenService
from app.utils.jwt import get_current_user
from app.schemas.plantnet import (
    PlantNetIdentificacionRequest,
    PlantNetQuotaInfo
)
from app.schemas.identificacion import (
    IdentificacionMultipleRequest,
    IdentificacionResponse
)
from pydantic import BaseModel, Field


# Schemas de request/response

class IdentificarRequest(BaseModel):
    """Request para identificar una planta desde una imagen ya subida."""
    imagen_id: int = Field(..., description="ID de la imagen en el sistema")
    organos: Optional[List[str]] = Field(
        default=["auto"],
        description="Órganos de la planta: leaf, flower, fruit, bark, auto"
    )
    guardar_resultado: bool = Field(
        default=True,
        description="Si True, guarda el resultado en la base de datos"
    )


class IdentificarResponse(BaseModel):
    """Response de identificación de planta."""
    identificacion_id: Optional[int] = Field(None, description="ID de la identificación creada")
    especie: dict = Field(..., description="Información de la especie identificada")
    confianza: float = Field(..., description="Nivel de confianza (0-100)")
    confianza_porcentaje: str = Field(..., description="Confianza formateada como porcentaje")
    es_confiable: bool = Field(..., description="True si confianza >= 70%")
    plantnet_response: dict = Field(..., description="Respuesta completa de PlantNet")
    mejor_resultado: dict = Field(..., description="Mejor resultado simplificado")


class HistorialResponse(BaseModel):
    """Response con historial de identificaciones."""
    total: int = Field(..., description="Total de identificaciones")
    identificaciones: List[dict] = Field(..., description="Lista de identificaciones")


class ValidarRequest(BaseModel):
    """Request para validar una identificación."""
    notas: Optional[str] = Field(None, description="Notas sobre la validación")


router = APIRouter()


@router.post(
    "/desde-imagen",
    response_model=IdentificarResponse,
    status_code=status.HTTP_200_OK,
    summary="Identificar planta desde imagen existente",
    description="Identifica una planta usando una imagen ya subida al sistema"
)
async def identificar_desde_imagen(
    request: IdentificarRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Identifica una planta desde una imagen ya subida al sistema.
    
    - **imagen_id**: ID de la imagen en la base de datos
    - **organos**: Órganos de la planta en la imagen (leaf, flower, fruit, bark, auto)
    - **guardar_resultado**: Si True, guarda el resultado en la BD
    
    Returns:
        Información de la especie identificada, nivel de confianza y metadatos
    """
    try:
        resultado = await IdentificacionService.identificar_desde_imagen(
            db=db,
            imagen_id=request.imagen_id,
            usuario_id=current_user.id,
            organos=request.organos,
            guardar_resultado=request.guardar_resultado
        )
        
        return IdentificarResponse(**resultado)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al identificar planta: {str(e)}"
        )


@router.post(
    "/desde-archivo",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Identificar planta subiendo archivo",
    description="Sube una imagen y la identifica directamente con PlantNet"
)
async def identificar_desde_archivo(
    archivo: UploadFile = File(..., description="Archivo de imagen (JPG, PNG)"),
    organos: str = Form(default="auto", description="Órganos separados por coma: leaf,flower,fruit,bark,auto"),
    guardar_imagen: bool = Form(default=True, description="Si True, guarda la imagen en el sistema"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Identifica una planta subiendo un archivo de imagen directamente.
    
    - **archivo**: Archivo de imagen (JPG, PNG, hasta 5MB)
    - **organos**: Órganos de la planta (separados por coma)
    - **guardar_imagen**: Si True, guarda la imagen en el sistema
    
    Returns:
        Información de la especie identificada y metadatos
    """
    try:
        # Guardar la imagen temporalmente usando ImagenService
        imagen_guardada = await ImagenService.guardar_imagen(
            db=db,
            usuario_id=current_user.id,
            archivo=archivo
        )
        
        # Procesar lista de órganos
        lista_organos = [o.strip() for o in organos.split(",")]
        
        # Identificar la planta
        resultado = await IdentificacionService.identificar_desde_imagen(
            db=db,
            imagen_id=imagen_guardada["imagen"].id,
            usuario_id=current_user.id,
            organos=lista_organos,
            guardar_resultado=guardar_imagen
        )
        
        # Agregar información de la imagen guardada
        resultado["imagen"] = {
            "id": imagen_guardada["imagen"].id,
            "url": imagen_guardada["url"],
            "nombre": imagen_guardada["imagen"].nombre_archivo
        }
        
        return resultado
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al procesar imagen: {str(e)}"
        )


@router.get(
    "/historial",
    response_model=HistorialResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener historial de identificaciones",
    description="Lista el historial de identificaciones del usuario autenticado"
)
async def obtener_historial(
    limite: int = 50,
    offset: int = 0,
    solo_validadas: bool = False,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtiene el historial de identificaciones del usuario autenticado.
    
    - **limite**: Número máximo de resultados (default: 50)
    - **offset**: Desplazamiento para paginación (default: 0)
    - **solo_validadas**: Si True, solo retorna identificaciones validadas
    
    Returns:
        Lista de identificaciones con información de especie e imagen
    """
    try:
        identificaciones = IdentificacionService.obtener_historial_usuario(
            db=db,
            usuario_id=current_user.id,
            limite=limite,
            offset=offset,
            solo_validadas=solo_validadas
        )
        
        return HistorialResponse(
            total=len(identificaciones),
            identificaciones=identificaciones
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener historial: {str(e)}"
        )


@router.get(
    "/historial/{identificacion_id}",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Obtener detalle de identificación",
    description="Obtiene el detalle completo de una identificación específica"
)
async def obtener_detalle_identificacion(
    identificacion_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtiene el detalle completo de una identificación específica.
    
    - **identificacion_id**: ID de la identificación
    
    Returns:
        Detalle completo de la identificación con metadatos de PlantNet
    """
    from app.db.models import Identificacion
    
    try:
        identificacion = db.query(Identificacion).filter(
            Identificacion.id == identificacion_id,
            Identificacion.usuario_id == current_user.id
        ).first()
        
        if not identificacion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Identificación {identificacion_id} no encontrada"
            )
        
        return identificacion.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener identificación: {str(e)}"
        )


@router.post(
    "/validar/{identificacion_id}",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Validar identificación",
    description="Marca una identificación como validada por el usuario"
)
async def validar_identificacion(
    identificacion_id: int,
    request: ValidarRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Valida una identificación realizada por IA.
    
    - **identificacion_id**: ID de la identificación
    - **notas**: Notas opcionales sobre la validación
    
    Returns:
        Identificación actualizada con fecha de validación
    """
    try:
        identificacion = IdentificacionService.validar_identificacion(
            db=db,
            identificacion_id=identificacion_id,
            usuario_id=current_user.id,
            notas=request.notas
        )
        
        return identificacion.to_dict()
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al validar identificación: {str(e)}"
        )


@router.get(
    "/quota",
    response_model=PlantNetQuotaInfo,
    status_code=status.HTTP_200_OK,
    summary="Consultar cuota de PlantNet",
    description="Obtiene información sobre la cuota de requests disponibles"
)
async def obtener_quota(
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtiene información sobre la cuota de requests de PlantNet.
    
    Returns:
        Información de cuota (requests realizados, restantes, límite diario)
    """
    try:
        quota_info = await IdentificacionService.obtener_quota_info()
        return PlantNetQuotaInfo(**quota_info)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener información de cuota: {str(e)}"
        )


@router.post(
    "/multiple",
    status_code=status.HTTP_201_CREATED,
    summary="Identificar planta con múltiples imágenes (T-022)",
    description="Identifica una planta usando de 1 a 5 imágenes con especificación opcional de órgano por imagen"
)
async def identificar_multiples_imagenes(
    archivos: List[UploadFile] = File(
        ...,
        description="De 1 a 5 archivos de imagen (JPG, PNG)",
        max_length=5
    ),
    organos: str = Form(
        default="sin_especificar",
        description="Órganos separados por coma (leaf,flower,fruit,bark,auto,sin_especificar). Si se proporciona un solo valor, se aplica a todas las imágenes."
    ),
    guardar_resultado: bool = Form(
        default=True,
        description="Si True, guarda el resultado en la base de datos"
    ),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Identifica una planta usando múltiples imágenes (T-022).
    
    Permite enviar de 1 a 5 imágenes con especificación opcional del órgano
    (parte de la planta) para cada imagen.
    
    - **archivos**: Lista de 1 a 5 archivos de imagen
    - **organos**: Órganos separados por coma o un solo valor para todas las imágenes
      - Valores válidos: leaf, flower, fruit, bark, auto, sin_especificar
      - "sin_especificar": No se envía el parámetro organ a PlantNet (detección auto)
    - **guardar_resultado**: Si True, guarda en la base de datos
    
    Returns:
        IdentificacionResponse con información de la especie identificada,
        nivel de confianza y metadatos de cada imagen.
    
    Raises:
        400: Si el número de imágenes es inválido o los órganos son incorrectos
        500: Si hay error en la API de PlantNet
    """
    try:
        # Validar número de archivos
        if len(archivos) < 1 or len(archivos) > 5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Debe proporcionar entre 1 y 5 imágenes"
            )
        
        # Procesar lista de órganos
        lista_organos = [o.strip() for o in organos.split(",")]
        
        # Si se proporciona un solo órgano, aplicarlo a todas las imágenes
        if len(lista_organos) == 1:
            lista_organos = lista_organos * len(archivos)
        
        # Validar que el número de órganos coincida con el número de archivos
        if len(lista_organos) != len(archivos):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El número de órganos ({len(lista_organos)}) debe coincidir con el número de imágenes ({len(archivos)})"
            )
        
        # Validar órganos válidos
        organos_validos = ["leaf", "flower", "fruit", "bark", "auto", "sin_especificar"]
        for organ in lista_organos:
            if organ not in organos_validos:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Órgano '{organ}' inválido. Valores válidos: {', '.join(organos_validos)}"
                )
        
        # Preparar lista de tuplas (UploadFile, organ)
        imagenes_con_organos = list(zip(archivos, lista_organos))
        
        # Llamar al servicio
        resultado = await IdentificacionService.identificar_desde_multiples_imagenes(
            db=db,
            imagenes=imagenes_con_organos,
            usuario_id=current_user.id,
            guardar_resultado=guardar_resultado
        )
        
        return JSONResponse(content=resultado, status_code=status.HTTP_201_CREATED)
        
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
            detail=f"Error al procesar imágenes: {str(e)}"
        )
