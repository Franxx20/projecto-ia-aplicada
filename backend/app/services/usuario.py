"""
Servicio de usuarios

Implementa toda la lógica de negocio para gestión de usuarios:
registro, actualización, validaciones, etc.
"""

from typing import Optional, List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from ..db.models import Usuario
from ..schemas.usuario import UsuarioRegistro, UsuarioActualizacion, CambioPassword
from .auth import servicio_auth


class ServicioUsuario:
    """
    Servicio para gestión de usuarios
    """
    
    def crear_usuario(self, usuario_data: UsuarioRegistro, db: Session) -> Usuario:
        """
        Crear nuevo usuario en el sistema
        
        Args:
            usuario_data: Datos del usuario a crear
            db: Sesión de base de datos
            
        Returns:
            Usuario: Usuario creado
            
        Raises:
            HTTPException: Si hay errores de validación o el usuario ya existe
        """
        # Verificar que el email no esté en uso
        usuario_existente = db.query(Usuario).filter(Usuario.email == usuario_data.email).first()
        if usuario_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está registrado"
            )
        
        # Verificar que el nombre de usuario no esté en uso
        nombre_existente = db.query(Usuario).filter(Usuario.nombre_usuario == usuario_data.nombre_usuario).first()
        if nombre_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El nombre de usuario ya está en uso"
            )
        
        # Crear nuevo usuario
        try:
            usuario_db = Usuario(
                email=usuario_data.email,
                nombre_usuario=usuario_data.nombre_usuario,
                nombre_completo=usuario_data.nombre_completo,
                bio=usuario_data.bio,
                ubicacion=usuario_data.ubicacion,
                notificaciones_activas=usuario_data.notificaciones_activas
            )
            
            # Establecer password hasheado
            usuario_db.establecer_password(usuario_data.password)
            
            # Guardar en base de datos
            db.add(usuario_db)
            db.commit()
            db.refresh(usuario_db)
            
            return usuario_db
            
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error al crear usuario: violación de constraint único"
            )
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error interno al crear usuario: {str(e)}"
            )
    
    def obtener_usuario_por_id(self, user_id: int, db: Session) -> Optional[Usuario]:
        """
        Obtener usuario por ID
        
        Args:
            user_id: ID del usuario
            db: Sesión de base de datos
            
        Returns:
            Usuario: Usuario encontrado o None
        """
        return db.query(Usuario).filter(Usuario.id == user_id).first()
    
    def obtener_usuario_por_email(self, email: str, db: Session) -> Optional[Usuario]:
        """
        Obtener usuario por email
        
        Args:
            email: Email del usuario
            db: Sesión de base de datos
            
        Returns:
            Usuario: Usuario encontrado o None
        """
        return db.query(Usuario).filter(Usuario.email == email).first()
    
    def obtener_usuario_por_nombre_usuario(self, nombre_usuario: str, db: Session) -> Optional[Usuario]:
        """
        Obtener usuario por nombre de usuario
        
        Args:
            nombre_usuario: Nombre de usuario
            db: Sesión de base de datos
            
        Returns:
            Usuario: Usuario encontrado o None
        """
        return db.query(Usuario).filter(Usuario.nombre_usuario == nombre_usuario).first()
    
    def actualizar_usuario(self, user_id: int, usuario_data: UsuarioActualizacion, db: Session) -> Usuario:
        """
        Actualizar datos del usuario
        
        Args:
            user_id: ID del usuario a actualizar
            usuario_data: Nuevos datos del usuario
            db: Sesión de base de datos
            
        Returns:
            Usuario: Usuario actualizado
            
        Raises:
            HTTPException: Si el usuario no existe o hay errores de validación
        """
        usuario = self.obtener_usuario_por_id(user_id, db)
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        # Actualizar solo los campos proporcionados
        datos_actualizacion = usuario_data.dict(exclude_unset=True)
        for campo, valor in datos_actualizacion.items():
            setattr(usuario, campo, valor)
        
        try:
            db.commit()
            db.refresh(usuario)
            return usuario
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al actualizar usuario: {str(e)}"
            )
    
    def cambiar_password(self, user_id: int, cambio_data: CambioPassword, db: Session) -> Usuario:
        """
        Cambiar password del usuario
        
        Args:
            user_id: ID del usuario
            cambio_data: Datos del cambio de password
            db: Sesión de base de datos
            
        Returns:
            Usuario: Usuario actualizado
            
        Raises:
            HTTPException: Si hay errores de validación
        """
        usuario = self.obtener_usuario_por_id(user_id, db)
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        # Verificar password actual
        if not usuario.verificar_password(cambio_data.password_actual):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password actual incorrecta"
            )
        
        # Establecer nuevo password
        try:
            usuario.establecer_password(cambio_data.password_nuevo)
            db.commit()
            db.refresh(usuario)
            return usuario
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al cambiar password: {str(e)}"
            )
    
    def desactivar_usuario(self, user_id: int, db: Session) -> Usuario:
        """
        Desactivar usuario (soft delete)
        
        Args:
            user_id: ID del usuario
            db: Sesión de base de datos
            
        Returns:
            Usuario: Usuario desactivado
            
        Raises:
            HTTPException: Si el usuario no existe
        """
        usuario = self.obtener_usuario_por_id(user_id, db)
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        usuario.activo = False
        
        try:
            db.commit()
            db.refresh(usuario)
            return usuario
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al desactivar usuario: {str(e)}"
            )
    
    def activar_usuario(self, user_id: int, db: Session) -> Usuario:
        """
        Activar usuario
        
        Args:
            user_id: ID del usuario
            db: Sesión de base de datos
            
        Returns:
            Usuario: Usuario activado
            
        Raises:
            HTTPException: Si el usuario no existe
        """
        usuario = self.obtener_usuario_por_id(user_id, db)
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        usuario.activo = True
        
        try:
            db.commit()
            db.refresh(usuario)
            return usuario
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al activar usuario: {str(e)}"
            )
    
    def listar_usuarios(self, skip: int = 0, limit: int = 100, db: Session = None) -> List[Usuario]:
        """
        Listar usuarios con paginación
        
        Args:
            skip: Número de usuarios a saltar
            limit: Límite de usuarios a retornar
            db: Sesión de base de datos
            
        Returns:
            List[Usuario]: Lista de usuarios
        """
        return db.query(Usuario).offset(skip).limit(limit).all()
    
    def contar_usuarios(self, db: Session) -> int:
        """
        Contar total de usuarios
        
        Args:
            db: Sesión de base de datos
            
        Returns:
            int: Número total de usuarios
        """
        return db.query(Usuario).count()
    
    def verificar_disponibilidad_email(self, email: str, db: Session) -> bool:
        """
        Verificar si un email está disponible
        
        Args:
            email: Email a verificar
            db: Sesión de base de datos
            
        Returns:
            bool: True si está disponible
        """
        usuario = db.query(Usuario).filter(Usuario.email == email).first()
        return usuario is None
    
    def verificar_disponibilidad_nombre_usuario(self, nombre_usuario: str, db: Session) -> bool:
        """
        Verificar si un nombre de usuario está disponible
        
        Args:
            nombre_usuario: Nombre de usuario a verificar
            db: Sesión de base de datos
            
        Returns:
            bool: True si está disponible
        """
        usuario = db.query(Usuario).filter(Usuario.nombre_usuario == nombre_usuario).first()
        return usuario is None


# Instancia global del servicio de usuario
servicio_usuario = ServicioUsuario()