"""
Router de gestión de imágenes

Endpoints para subir, listar, obtener y eliminar imágenes almacenadas en Azure Blob Storage.

Autor: Equipo Backend
Fecha: Octubre 2025
Sprint: Sprint 1 - T-004
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.imagen import (
    ImagenResponse,
    ImagenListResponse,
    ImagenUploadResponse,
    ImagenDeleteResponse,
    ImagenUpdate
)
from app.services.imagen_service import ImagenService, obtener_servicio_imagen
from app.utils.jwt import get_current_user
from app.db.models import Usuario

# Crear router de imágenes
router = APIRouter()


@router.post(
    "/subir",
    response_model=ImagenUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Subir nueva imagen",
    description="Sube una imagen a Azure Blob Storage y guarda la metadata en PostgreSQL",
    response_description="Imagen subida exitosamente",
    responses={
        201: {
            "description": "Imagen subida exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "nombre_archivo": "planta_monstera.jpg",
                        "url_blob": "https://mystorageaccount.blob.core.windows.net/plantitas-imagenes/550e8400-e29b-41d4-a716-446655440000.jpg",
                        "tamano_bytes": 245678,
                        "content_type": "image/jpeg",
                        "created_at": "2025-10-12T10:30:00",
                        "mensaje": "Imagen subida exitosamente"
                    }
                }
            }
        },
        413: {"description": "Archivo demasiado grande"},
        415: {"description": "Formato de archivo no soportado"},
        401: {"description": "No autenticado"}
    }
)
async def subir_imagen(
    archivo: UploadFile = File(..., description="Archivo de imagen a subir"),
    descripcion: Optional[str] = Form(None, description="Descripción opcional de la imagen"),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Sube una nueva imagen al sistema.
    
    - **archivo**: Archivo de imagen (JPG, PNG, WEBP)
    - **descripcion**: Descripción opcional de la imagen
    
    La imagen se almacena en Azure Blob Storage y la metadata en PostgreSQL.
    Solo el usuario propietario puede acceder y gestionar sus imágenes.
    """
    servicio = ImagenService(db)
    imagen = await servicio.subir_imagen(
        archivo=archivo,
        usuario_id=current_user.id,
        descripcion=descripcion
    )
    
    return ImagenUploadResponse(
        id=imagen.id,
        nombre_archivo=imagen.nombre_archivo,
        url_blob=imagen.url_blob,
        tamano_bytes=imagen.tamano_bytes,
        content_type=imagen.content_type,
        created_at=imagen.created_at,
        mensaje="Imagen subida exitosamente"
    )


@router.get(
    "",
    response_model=ImagenListResponse,
    summary="Listar imágenes del usuario",
    description="Obtiene la lista de imágenes subidas por el usuario actual con paginación",
    response_description="Lista de imágenes del usuario",
    responses={
        200: {
            "description": "Lista de imágenes obtenida exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "imagenes": [
                            {
                                "id": 1,
                                "usuario_id": 1,
                                "nombre_archivo": "planta.jpg",
                                "url_blob": "https://storage.blob.core.windows.net/container/file.jpg",
                                "tamano_bytes": 245678,
                                "content_type": "image/jpeg",
                                "created_at": "2025-10-12T10:30:00",
                                "descripcion": "Mi planta favorita"
                            }
                        ],
                        "total": 15,
                        "pagina": 1,
                        "tamano_pagina": 20,
                        "total_paginas": 1
                    }
                }
            }
        },
        401: {"description": "No autenticado"}
    }
)
async def listar_imagenes(
    skip: int = 0,
    limit: int = 20,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lista todas las imágenes del usuario autenticado.
    
    - **skip**: Número de registros a saltar (para paginación)
    - **limit**: Número máximo de registros a devolver (máx: 100)
    
    Las imágenes se devuelven ordenadas por fecha de creación (más recientes primero).
    """
    # Validar límite máximo
    if limit > 100:
        limit = 100
    
    servicio = ImagenService(db)
    imagenes, total = servicio.listar_imagenes_usuario(
        usuario_id=current_user.id,
        skip=skip,
        limit=limit
    )
    
    # Calcular total de páginas
    total_paginas = (total + limit - 1) // limit if limit > 0 else 0
    pagina_actual = (skip // limit) + 1 if limit > 0 else 1
    
    return ImagenListResponse(
        imagenes=[ImagenResponse.model_validate(img) for img in imagenes],
        total=total,
        pagina=pagina_actual,
        tamano_pagina=limit,
        total_paginas=total_paginas
    )


@router.get(
    "/{imagen_id}",
    response_model=ImagenResponse,
    summary="Obtener imagen por ID",
    description="Obtiene los detalles de una imagen específica",
    response_description="Detalles de la imagen",
    responses={
        200: {
            "description": "Imagen encontrada",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "usuario_id": 1,
                        "nombre_archivo": "planta_monstera.jpg",
                        "nombre_blob": "550e8400-e29b-41d4-a716-446655440000.jpg",
                        "url_blob": "https://storage.blob.core.windows.net/container/file.jpg",
                        "container_name": "plantitas-imagenes",
                        "content_type": "image/jpeg",
                        "tamano_bytes": 245678,
                        "descripcion": "Mi planta favorita",
                        "created_at": "2025-10-12T10:30:00",
                        "updated_at": "2025-10-12T10:30:00",
                        "is_deleted": False
                    }
                }
            }
        },
        404: {"description": "Imagen no encontrada"},
        401: {"description": "No autenticado"}
    }
)
async def obtener_imagen(
    imagen_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene los detalles de una imagen específica.
    
    - **imagen_id**: ID de la imagen a obtener
    
    Solo el usuario propietario puede ver los detalles de sus imágenes.
    """
    servicio = ImagenService(db)
    imagen = servicio.obtener_imagen(imagen_id, usuario_id=current_user.id)
    
    return ImagenResponse.model_validate(imagen)


@router.patch(
    "/{imagen_id}",
    response_model=ImagenResponse,
    summary="Actualizar descripción de imagen",
    description="Actualiza la descripción de una imagen existente",
    response_description="Imagen actualizada",
    responses={
        200: {"description": "Imagen actualizada exitosamente"},
        404: {"description": "Imagen no encontrada"},
        401: {"description": "No autenticado"}
    }
)
async def actualizar_imagen(
    imagen_id: int,
    datos: ImagenUpdate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Actualiza la descripción de una imagen.
    
    - **imagen_id**: ID de la imagen a actualizar
    - **descripcion**: Nueva descripción de la imagen
    
    Solo el usuario propietario puede actualizar sus imágenes.
    """
    if datos.descripcion is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe proporcionar una descripción"
        )
    
    servicio = ImagenService(db)
    imagen = servicio.actualizar_descripcion(
        imagen_id=imagen_id,
        usuario_id=current_user.id,
        descripcion=datos.descripcion
    )
    
    return ImagenResponse.model_validate(imagen)


@router.delete(
    "/{imagen_id}",
    response_model=ImagenDeleteResponse,
    summary="Eliminar imagen",
    description="Elimina una imagen del sistema (soft delete en BD, eliminación física en Azure)",
    response_description="Imagen eliminada exitosamente",
    responses={
        200: {
            "description": "Imagen eliminada exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "nombre_archivo": "planta.jpg",
                        "mensaje": "Imagen eliminada exitosamente",
                        "eliminado_de_azure": True
                    }
                }
            }
        },
        404: {"description": "Imagen no encontrada"},
        401: {"description": "No autenticado"}
    }
)
async def eliminar_imagen(
    imagen_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Elimina una imagen del sistema.
    
    - **imagen_id**: ID de la imagen a eliminar
    
    La imagen se marca como eliminada en la base de datos (soft delete)
    y se elimina físicamente de Azure Blob Storage.
    
    Solo el usuario propietario puede eliminar sus imágenes.
    """
    servicio = ImagenService(db)
    imagen, eliminado_azure = await servicio.eliminar_imagen(
        imagen_id=imagen_id,
        usuario_id=current_user.id
    )
    
    return ImagenDeleteResponse(
        id=imagen.id,
        nombre_archivo=imagen.nombre_archivo,
        mensaje="Imagen eliminada exitosamente",
        eliminado_de_azure=eliminado_azure
    )
