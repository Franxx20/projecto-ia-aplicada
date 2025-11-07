"""
Servicio de gestión de imágenes con Azure Blob Storage.

Este módulo maneja la subida, descarga y eliminación de imágenes
en Azure Blob Storage, además de gestionar la metadata en PostgreSQL.

Autor: Equipo Backend
Fecha: Octubre 2025
Sprint: Sprint 1 - T-004
"""

import uuid
import os
from typing import Optional, List, BinaryIO
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException, status

# Azure Storage
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, ContentSettings
from azure.core.exceptions import AzureError, ResourceNotFoundError

# Modelos y configuración
from app.db.models import Imagen, Usuario
from app.schemas.imagen import ImagenResponse, ImagenListResponse
from app.core.config import obtener_configuracion

# Configuración
config = obtener_configuracion()


class AzureBlobService:
    """
    Servicio para interactuar con Azure Blob Storage.
    
    Maneja la subida, descarga y eliminación de blobs en Azure Storage,
    además de proporcionar URLs de acceso a los archivos.
    """
    
    def __init__(self):
        """
        Inicializa el servicio de Azure Blob Storage.
        
        Configura la conexión con Azure usando las credenciales
        del archivo de configuración.
        """
        self.container_name = config.azure_storage_container_name
        
        # Configurar cliente de Azure Storage
        if config.azure_storage_connection_string:
            # Usar connection string (más simple para desarrollo)
            self.blob_service_client = BlobServiceClient.from_connection_string(
                config.azure_storage_connection_string
            )
        elif config.azure_storage_account_name and config.azure_storage_account_key:
            # Usar nombre de cuenta y key
            account_url = f"https://{config.azure_storage_account_name}.blob.core.windows.net"
            self.blob_service_client = BlobServiceClient(
                account_url=account_url,
                credential=config.azure_storage_account_key
            )
        else:
            raise ValueError(
                "No se proporcionó configuración válida para Azure Storage. "
                "Configurar AZURE_STORAGE_CONNECTION_STRING o "
                "AZURE_STORAGE_ACCOUNT_NAME + AZURE_STORAGE_ACCOUNT_KEY"
            )
        
        # Asegurar que el contenedor existe
        self._ensure_container_exists()
    
    def _ensure_container_exists(self) -> None:
        """
        Verifica que el contenedor existe, si no lo crea.
        
        Raises:
            AzureError: Si hay un error al crear el contenedor
        """
        try:
            container_client = self.blob_service_client.get_container_client(self.container_name)
            if not container_client.exists():
                container_client.create_container()
                print(f"Contenedor '{self.container_name}' creado exitosamente")
        except AzureError as e:
            print(f"Error al verificar/crear contenedor: {str(e)}")
            # No lanzar excepción aquí, puede ser que el contenedor ya exista
    
    def generar_nombre_blob(self, nombre_archivo: str) -> str:
        """
        Genera un nombre único para el blob usando UUID.
        
        Args:
            nombre_archivo (str): Nombre original del archivo
            
        Returns:
            str: Nombre único del blob (UUID + extensión original)
            
        Example:
            >>> service = AzureBlobService()
            >>> nombre_blob = service.generar_nombre_blob("planta.jpg")
            >>> print(nombre_blob)
            '550e8400-e29b-41d4-a716-446655440000.jpg'
        """
        # Extraer extensión del archivo
        extension = nombre_archivo.split('.')[-1] if '.' in nombre_archivo else ''
        
        # Generar UUID único
        unique_id = str(uuid.uuid4())
        
        # Combinar UUID con extensión
        return f"{unique_id}.{extension}" if extension else unique_id
    
    async def subir_archivo(
        self,
        archivo: UploadFile,
        nombre_blob: Optional[str] = None
    ) -> tuple[str, str]:
        """
        Sube un archivo a Azure Blob Storage.
        
        Args:
            archivo (UploadFile): Archivo a subir
            nombre_blob (Optional[str]): Nombre del blob, si no se proporciona se genera uno
            
        Returns:
            tuple[str, str]: (nombre_blob, url_blob)
            
        Raises:
            HTTPException: Si hay un error al subir el archivo
            
        Example:
            >>> service = AzureBlobService()
            >>> with open("planta.jpg", "rb") as f:
            ...     nombre, url = await service.subir_archivo(f)
            >>> print(nombre)
            '550e8400-e29b-41d4-a716-446655440000.jpg'
        """
        try:
            # Generar nombre si no se proporcionó
            if not nombre_blob:
                nombre_blob = self.generar_nombre_blob(archivo.filename or "archivo")
            
            # Obtener cliente del blob
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=nombre_blob
            )
            
            # Leer contenido del archivo
            contenido = await archivo.read()
            
            # Subir archivo a Azure con content_settings correcto
            blob_client.upload_blob(
                contenido,
                overwrite=True,
                content_settings=ContentSettings(
                    content_type=archivo.content_type or 'application/octet-stream'
                )
            )
            
            # Obtener URL del blob
            url_blob = blob_client.url
            
            return nombre_blob, url_blob
            
        except AzureError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al subir archivo a Azure Storage: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error inesperado al subir archivo: {str(e)}"
            )
    
    async def eliminar_archivo(self, nombre_blob: str) -> bool:
        """
        Elimina un archivo de Azure Blob Storage.
        
        Args:
            nombre_blob (str): Nombre del blob a eliminar
            
        Returns:
            bool: True si se eliminó exitosamente, False si no existía
            
        Raises:
            HTTPException: Si hay un error al eliminar el archivo
            
        Example:
            >>> service = AzureBlobService()
            >>> eliminado = await service.eliminar_archivo("archivo.jpg")
            >>> print(eliminado)
            True
        """
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=nombre_blob
            )
            
            blob_client.delete_blob()
            return True
            
        except ResourceNotFoundError:
            # El blob no existe, devolver False
            return False
        except AzureError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al eliminar archivo de Azure Storage: {str(e)}"
            )
    
    def descargar_blob(self, nombre_blob: str) -> bytes:
        """
        Descarga el contenido de un blob desde Azure Blob Storage.
        
        Args:
            nombre_blob (str): Nombre del blob a descargar
            
        Returns:
            bytes: Contenido del blob en bytes
            
        Raises:
            HTTPException: Si hay un error al descargar el archivo
            
        Example:
            >>> service = AzureBlobService()
            >>> contenido = service.descargar_blob("archivo.jpg")
            >>> print(len(contenido))
            12345
        """
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=nombre_blob
            )
            
            # Descargar el contenido del blob
            downloader = blob_client.download_blob()
            contenido = downloader.readall()
            
            return contenido
            
        except ResourceNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Blob '{nombre_blob}' no encontrado en Azure Storage"
            )
        except AzureError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al descargar archivo de Azure Storage: {str(e)}"
            )
    
    def obtener_url_blob(self, nombre_blob: str) -> str:
        """
        Obtiene la URL pública de un blob.
        
        Args:
            nombre_blob (str): Nombre del blob
            
        Returns:
            str: URL completa del blob
            
        Example:
            >>> service = AzureBlobService()
            >>> url = service.obtener_url_blob("archivo.jpg")
            >>> print(url)
            'https://mystorageaccount.blob.core.windows.net/container/archivo.jpg'
        """
        blob_client = self.blob_service_client.get_blob_client(
            container=self.container_name,
            blob=nombre_blob
        )
        return blob_client.url


class ImagenService:
    """
    Servicio de lógica de negocio para gestión de imágenes.
    
    Coordina las operaciones entre Azure Blob Storage y la base de datos PostgreSQL.
    """
    
    def __init__(self, db: Session):
        """
        Inicializa el servicio de imágenes.
        
        Args:
            db (Session): Sesión de base de datos SQLAlchemy
        """
        self.db = db
        self.azure_service = AzureBlobService()
    
    async def subir_imagen(
        self,
        archivo: UploadFile,
        usuario_id: int,
        descripcion: Optional[str] = None
    ) -> Imagen:
        """
        Sube una imagen a Azure Storage y guarda la metadata en PostgreSQL.
        
        Args:
            archivo (UploadFile): Archivo a subir
            usuario_id (int): ID del usuario propietario
            descripcion (Optional[str]): Descripción opcional de la imagen
            
        Returns:
            Imagen: Modelo de imagen creado
            
        Raises:
            HTTPException: Si hay errores en la validación o subida
            
        Example:
            >>> service = ImagenService(db)
            >>> imagen = await service.subir_imagen(archivo, usuario_id=1)
            >>> print(imagen.url_blob)
            'https://...'
        """
        # Validar que el usuario existe
        usuario = self.db.query(Usuario).filter(Usuario.id == usuario_id).first()
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuario con ID {usuario_id} no encontrado"
            )
        
        # Validar tamaño del archivo
        if archivo.size and archivo.size > config.max_tamano_archivo_mb * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"El archivo excede el tamaño máximo permitido de {config.max_tamano_archivo_mb}MB"
            )
        
        # Validar formato del archivo
        if archivo.content_type and not archivo.content_type.startswith('image/'):
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="El archivo debe ser una imagen"
            )
        
        # Subir archivo a Azure
        nombre_blob, url_blob = await self.azure_service.subir_archivo(archivo)
        
        # Crear registro en la base de datos
        imagen = Imagen(
            usuario_id=usuario_id,
            nombre_archivo=archivo.filename or "sin_nombre",
            nombre_blob=nombre_blob,
            url_blob=url_blob,
            container_name=self.azure_service.container_name,
            content_type=archivo.content_type or "application/octet-stream",
            tamano_bytes=archivo.size or 0,
            descripcion=descripcion
        )
        
        self.db.add(imagen)
        self.db.commit()
        self.db.refresh(imagen)
        
        return imagen
    
    def obtener_imagen(self, imagen_id: int, usuario_id: Optional[int] = None) -> Optional[Imagen]:
        """
        Obtiene una imagen por su ID.
        
        Args:
            imagen_id (int): ID de la imagen
            usuario_id (Optional[int]): ID del usuario (para verificar permisos)
            
        Returns:
            Optional[Imagen]: Imagen encontrada o None
            
        Raises:
            HTTPException: Si la imagen no existe o no tiene permisos
        """
        query = self.db.query(Imagen).filter(Imagen.id == imagen_id, Imagen.is_deleted == False)
        
        if usuario_id is not None:
            query = query.filter(Imagen.usuario_id == usuario_id)
        
        imagen = query.first()
        
        if not imagen:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Imagen con ID {imagen_id} no encontrada"
            )
        
        return imagen
    
    def listar_imagenes_usuario(
        self,
        usuario_id: int,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[List[Imagen], int]:
        """
        Lista las imágenes de un usuario con paginación.
        
        Args:
            usuario_id (int): ID del usuario
            skip (int): Número de registros a saltar
            limit (int): Número máximo de registros a devolver
            
        Returns:
            tuple[List[Imagen], int]: (lista de imágenes, total de imágenes)
        """
        query = self.db.query(Imagen).filter(
            Imagen.usuario_id == usuario_id,
            Imagen.is_deleted == False
        ).order_by(Imagen.created_at.desc())
        
        total = query.count()
        imagenes = query.offset(skip).limit(limit).all()
        
        return imagenes, total
    
    async def eliminar_imagen(self, imagen_id: int, usuario_id: int) -> tuple[Imagen, bool]:
        """
        Elimina una imagen (soft delete en BD, eliminación física en Azure).
        
        Args:
            imagen_id (int): ID de la imagen a eliminar
            usuario_id (int): ID del usuario (para verificar permisos)
            
        Returns:
            tuple[Imagen, bool]: (Imagen eliminada, éxito en Azure)
            
        Raises:
            HTTPException: Si la imagen no existe o no tiene permisos
        """
        imagen = self.obtener_imagen(imagen_id, usuario_id)
        
        # Eliminar de Azure Storage
        eliminado_azure = await self.azure_service.eliminar_archivo(imagen.nombre_blob)
        
        # Soft delete en base de datos
        imagen.soft_delete()
        self.db.commit()
        
        return imagen, eliminado_azure
    
    def actualizar_descripcion(
        self,
        imagen_id: int,
        usuario_id: int,
        descripcion: str
    ) -> Imagen:
        """
        Actualiza la descripción de una imagen.
        
        Args:
            imagen_id (int): ID de la imagen
            usuario_id (int): ID del usuario (para verificar permisos)
            descripcion (str): Nueva descripción
            
        Returns:
            Imagen: Imagen actualizada
            
        Raises:
            HTTPException: Si la imagen no existe o no tiene permisos
        """
        imagen = self.obtener_imagen(imagen_id, usuario_id)
        imagen.update_description(descripcion)
        self.db.commit()
        self.db.refresh(imagen)
        
        return imagen


# Función helper para obtener instancia del servicio
def obtener_servicio_imagen(db: Session) -> ImagenService:
    """
    Factory function para obtener una instancia del servicio de imágenes.
    
    Args:
        db (Session): Sesión de base de datos
        
    Returns:
        ImagenService: Instancia del servicio
        
    Example:
        >>> from fastapi import Depends
        >>> from app.db.session import get_db
        >>> 
        >>> @app.post("/imagenes")
        >>> async def subir_imagen(
        ...     servicio: ImagenService = Depends(obtener_servicio_imagen)
        ... ):
        ...     pass
    """
    return ImagenService(db)
# Forzando actualización
