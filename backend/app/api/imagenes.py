"""
API Endpoints para manejo de imágenes

Endpoints para upload, consulta y gestión de imágenes
con validación y autenticación.
"""

import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, status
from fastapi.responses import FileResponse
from typing import Optional, List

from ..schemas.imagen import ImagenUploadResponse, ImagenInfo, ErrorResponse
from ..core.dependencies import obtener_usuario_actual
from ..db.models import Usuario
from ..services.imagenes import servicio_imagenes
from ..core.config import configuracion

# Configurar logging
logger = logging.getLogger(__name__)

# Router de imágenes
router = APIRouter(prefix="/images", tags=["imágenes"])


@router.post(
    "/upload",
    response_model=ImagenUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Subir imagen",
    description="Sube una imagen al servidor con validación y procesamiento automático"
)
async def subir_imagen(
    archivo: UploadFile = File(..., description="Archivo de imagen a subir"),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    """
    Subir una imagen al servidor
    
    - **archivo**: Archivo de imagen (JPG, PNG, GIF, WebP)
    - **usuario_actual**: Usuario autenticado (automático)
    
    La imagen se procesa automáticamente:
    - Validación de tipo y tamaño
    - Redimensionamiento si es necesario
    - Optimización de calidad
    - Generación de nombre único
    """
    try:
        logger.info(f"Usuario {usuario_actual.nombre_usuario} subiendo imagen: {archivo.filename}")
        
        # Validar que se proporcionó un archivo
        if not archivo.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se proporcionó ningún archivo"
            )
        
        # Usar servicio de Azure si está configurado, sino local
        if configuracion.usar_azure_storage:
            resultado = await servicio_imagenes.guardar_archivo_azure(archivo)
        else:
            resultado = await servicio_imagenes.guardar_archivo_local(archivo)
        
        logger.info(f"Imagen subida exitosamente: {resultado['filename']}")
        
        return ImagenUploadResponse(**resultado)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error inesperado subiendo imagen: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.get(
    "/info/{filename}",
    response_model=ImagenInfo,
    summary="Información de imagen",
    description="Obtiene información detallada de una imagen almacenada"
)
async def obtener_info_imagen(
    filename: str,
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    """
    Obtener información de una imagen
    
    - **filename**: Nombre del archivo de imagen
    - **usuario_actual**: Usuario autenticado (automático)
    """
    try:
        info = servicio_imagenes.obtener_info_archivo(filename)
        
        if not info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Imagen no encontrada: {filename}"
            )
        
        return ImagenInfo(**info)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo info de imagen {filename}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.get(
    "/download/{filename}",
    response_class=FileResponse,
    summary="Descargar imagen",
    description="Descarga una imagen del servidor"
)
async def descargar_imagen(
    filename: str,
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    """
    Descargar una imagen
    
    - **filename**: Nombre del archivo de imagen
    - **usuario_actual**: Usuario autenticado (automático)
    """
    try:
        # Verificar que la imagen existe
        info = servicio_imagenes.obtener_info_archivo(filename)
        
        if not info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Imagen no encontrada: {filename}"
            )
        
        # Construir ruta completa del archivo
        ruta_archivo = servicio_imagenes.directorio_uploads / filename
        
        return FileResponse(
            path=str(ruta_archivo),
            filename=filename,
            media_type="application/octet-stream"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error descargando imagen {filename}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.delete(
    "/{filename}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar imagen",
    description="Elimina una imagen del servidor"
)
async def eliminar_imagen(
    filename: str,
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    """
    Eliminar una imagen
    
    - **filename**: Nombre del archivo de imagen
    - **usuario_actual**: Usuario autenticado (automático)
    """
    try:
        # Verificar que la imagen existe
        info = servicio_imagenes.obtener_info_archivo(filename)
        
        if not info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Imagen no encontrada: {filename}"
            )
        
        # Eliminar archivo
        eliminado = servicio_imagenes.eliminar_archivo(filename)
        
        if not eliminado:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"No se pudo eliminar la imagen: {filename}"
            )
        
        logger.info(f"Usuario {usuario_actual.nombre_usuario} eliminó imagen: {filename}")
        
        return {"message": f"Imagen {filename} eliminada correctamente"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error eliminando imagen {filename}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.get(
    "/health",
    summary="Health check del servicio de imágenes",
    description="Verifica el estado del servicio de imágenes"
)
async def health_check():
    """
    Health check del servicio de imágenes
    
    Verifica:
    - Directorio de uploads accesible
    - Configuración correcta
    - Estado de servicios externos (Azure si está configurado)
    """
    try:
        status_check = {
            "status": "healthy",
            "directorio_uploads": str(servicio_imagenes.directorio_uploads),
            "directorio_existe": servicio_imagenes.directorio_uploads.exists(),
            "azure_configurado": bool(configuracion.azure_storage_connection_string),
            "usar_azure": configuracion.usar_azure_storage,
            "tipos_permitidos": servicio_imagenes.tipos_permitidos,
            "tamaño_maximo": servicio_imagenes.tamano_maximo
        }
        
        return status_check
        
    except Exception as e:
        logger.error(f"Error en health check de imágenes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Servicio de imágenes no disponible: {str(e)}"
        )