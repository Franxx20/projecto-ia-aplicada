"""
Servicio para manejo de imágenes

Implementa upload, procesamiento y almacenamiento de imágenes
con soporte para Azure Blob Storage y almacenamiento local.
"""

import io
import os
import uuid
import aiofiles
from pathlib import Path
from typing import Optional, Tuple, BinaryIO
try:
    from PIL import Image
except ImportError:
    Image = None
from fastapi import UploadFile, HTTPException, status
import logging

from ..core.config import configuracion

logger = logging.getLogger(__name__)


class ServicioImagenes:
    """
    Servicio para gestión completa de imágenes
    """
    
    def __init__(self):
        self.directorio_uploads = Path(configuracion.directorio_uploads)
        self.tamano_maximo = configuracion.tamaño_maximo_archivo
        self.tipos_permitidos = configuracion.tipos_archivos_permitidos
        
        # Crear directorio si no existe
        self.directorio_uploads.mkdir(parents=True, exist_ok=True)
    
    def validar_archivo(self, archivo: UploadFile) -> bool:
        """
        Validar que el archivo cumpla con los requisitos
        
        Args:
            archivo: Archivo subido
            
        Returns:
            bool: True si es válido
            
        Raises:
            HTTPException: Si el archivo no es válido
        """
        # Verificar que hay contenido
        if not archivo.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se proporcionó ningún archivo"
            )
        
        # Verificar extensión
        extension = archivo.filename.split('.')[-1].lower()
        if extension not in self.tipos_permitidos:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tipo de archivo no permitido. Tipos válidos: {', '.join(self.tipos_permitidos)}"
            )
        
        # Verificar tipo MIME
        if not archivo.content_type or not archivo.content_type.startswith('image/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El archivo debe ser una imagen"
            )
        
        return True
    
    def generar_nombre_unico(self, nombre_original: str) -> str:
        """
        Generar nombre único para el archivo
        
        Args:
            nombre_original: Nombre original del archivo
            
        Returns:
            str: Nombre único generado
        """
        extension = nombre_original.split('.')[-1].lower()
        nombre_unico = f"{uuid.uuid4().hex}.{extension}"
        return nombre_unico
    
    def procesar_imagen(self, contenido: bytes, nombre_archivo: str) -> Tuple[bytes, dict]:
        """
        Procesar imagen: redimensionar, optimizar y extraer metadata
        
        Args:
            contenido: Contenido binario de la imagen
            nombre_archivo: Nombre del archivo
            
        Returns:
            Tuple[bytes, dict]: Contenido procesado y metadata
        """
        try:
            # Si PIL no está disponible, retornar contenido sin procesar
            if Image is None:
                metadata = {
                    "formato_original": "unknown",
                    "tamaño_original": "unknown",
                    "modo": "unknown",
                    "nombre_archivo": nombre_archivo,
                    "redimensionada": False,
                    "tamaño_procesado": "unknown",
                    "tamaño_archivo_original": len(contenido),
                    "tamaño_archivo_procesado": len(contenido),
                    "compresion_ratio": 1.0,
                    "nota": "PIL no disponible, imagen sin procesar"
                }
                return contenido, metadata
            
            # Abrir imagen con PIL
            imagen = Image.open(io.BytesIO(contenido))
            
            # Extraer metadata original
            metadata = {
                "formato_original": imagen.format,
                "tamaño_original": imagen.size,
                "modo": imagen.mode,
                "nombre_archivo": nombre_archivo
            }
            
            # Convertir a RGB si es necesario
            if imagen.mode in ('RGBA', 'P'):
                imagen = imagen.convert('RGB')
            
            # Redimensionar si es muy grande (máximo 1920x1920)
            max_size = (1920, 1920)
            if imagen.size[0] > max_size[0] or imagen.size[1] > max_size[1]:
                imagen.thumbnail(max_size, Image.Resampling.LANCZOS)
                metadata["redimensionada"] = True
                metadata["tamaño_procesado"] = imagen.size
            else:
                metadata["redimensionada"] = False
                metadata["tamaño_procesado"] = imagen.size
            
            # Guardar imagen procesada
            output = io.BytesIO()
            imagen.save(output, format='JPEG', quality=85, optimize=True)
            contenido_procesado = output.getvalue()
            
            metadata["tamaño_archivo_original"] = len(contenido)
            metadata["tamaño_archivo_procesado"] = len(contenido_procesado)
            metadata["compresion_ratio"] = len(contenido_procesado) / len(contenido)
            
            return contenido_procesado, metadata
            
        except Exception as e:
            logger.error(f"Error procesando imagen: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error al procesar la imagen: {str(e)}"
            )
    
    async def guardar_archivo_local(self, archivo: UploadFile) -> dict:
        """
        Guardar archivo en el sistema de archivos local
        
        Args:
            archivo: Archivo a guardar
            
        Returns:
            dict: Información del archivo guardado
        """
        try:
            # Validar archivo
            self.validar_archivo(archivo)
            
            # Leer contenido
            contenido = await archivo.read()
            
            # Verificar tamaño
            if len(contenido) > self.tamano_maximo:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"Archivo muy grande. Máximo permitido: {self.tamano_maximo} bytes"
                )
            
            # Procesar imagen
            contenido_procesado, metadata = self.procesar_imagen(contenido, archivo.filename)
            
            # Generar nombre único
            nombre_unico = self.generar_nombre_unico(archivo.filename)
            ruta_archivo = self.directorio_uploads / nombre_unico
            
            # Guardar archivo procesado
            async with aiofiles.open(ruta_archivo, 'wb') as f:
                await f.write(contenido_procesado)
            
            # Generar URL de acceso
            url_archivo = f"/uploads/{nombre_unico}"
            
            return {
                "filename": nombre_unico,
                "original_filename": archivo.filename,
                "url": url_archivo,
                "ruta_local": str(ruta_archivo),
                "tamaño": len(contenido_procesado),
                "tipo_mime": "image/jpeg",
                "metadata": metadata
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error guardando archivo: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error interno al guardar archivo: {str(e)}"
            )
    
    async def guardar_archivo_azure(self, archivo: UploadFile) -> dict:
        """
        Guardar archivo en Azure Blob Storage
        
        Args:
            archivo: Archivo a guardar
            
        Returns:
            dict: Información del archivo guardado en Azure
            
        Note:
            Requiere configuración de Azure Blob Storage
        """
        try:
            # Implementación futura: Azure Blob Storage
            # Por ahora, usar almacenamiento local como fallback
            
            if not configuracion.azure_storage_connection_string:
                logger.warning("Azure Blob Storage no configurado, usando almacenamiento local")
                return await self.guardar_archivo_local(archivo)
            
            # Implementación Azure Blob Storage pendiente
            # Requiere: from azure.storage.blob import BlobServiceClient
            # Por ahora retornamos error indicando que no está implementado
            logger.info("Azure Blob Storage configurado pero no implementado aún")
            return await self.guardar_archivo_local(archivo)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error con Azure Blob Storage: {e}")
            # Fallback a almacenamiento local
            return await self.guardar_archivo_local(archivo)
    
    def eliminar_archivo(self, nombre_archivo: str) -> bool:
        """
        Eliminar archivo del almacenamiento local
        
        Args:
            nombre_archivo: Nombre del archivo a eliminar
            
        Returns:
            bool: True si se eliminó correctamente
        """
        try:
            ruta_archivo = self.directorio_uploads / nombre_archivo
            if ruta_archivo.exists():
                ruta_archivo.unlink()
                return True
            return False
        except Exception as e:
            logger.error(f"Error eliminando archivo {nombre_archivo}: {e}")
            return False
    
    def obtener_info_archivo(self, nombre_archivo: str) -> Optional[dict]:
        """
        Obtener información de un archivo
        
        Args:
            nombre_archivo: Nombre del archivo
            
        Returns:
            dict: Información del archivo o None si no existe
        """
        try:
            ruta_archivo = self.directorio_uploads / nombre_archivo
            if not ruta_archivo.exists():
                return None
            
            stat = ruta_archivo.stat()
            
            return {
                "filename": nombre_archivo,
                "tamaño": stat.st_size,
                "fecha_creacion": stat.st_ctime,
                "fecha_modificacion": stat.st_mtime,
                "url": f"/uploads/{nombre_archivo}"
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo info de archivo {nombre_archivo}: {e}")
            return None


# Instancia global del servicio de imágenes
servicio_imagenes = ServicioImagenes()