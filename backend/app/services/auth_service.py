"""
Servicio de autenticación y autorización
Lógica de negocio para gestión de usuarios y autenticación
"""

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from typing import Optional
from datetime import datetime

from app.db.models import Usuario
from app.schemas.auth import UserRegisterRequest, UserResponse, UserLoginRequest, TokenResponse
from app.utils.jwt import crear_token_acceso, crear_refresh_token, validar_refresh_token, decodificar_token
from app.core.config import obtener_configuracion


# Blacklist en memoria para tokens invalidados (logout)
# En producción, usar Redis o una tabla de base de datos
_token_blacklist: set = set()


def agregar_token_a_blacklist(token: str) -> None:
    """
    Agregar un token a la blacklist de tokens invalidados
    
    Args:
        token: Token JWT a invalidar
    """
    _token_blacklist.add(token)


def token_esta_en_blacklist(token: str) -> bool:
    """
    Verificar si un token está en la blacklist
    
    Args:
        token: Token JWT a verificar
        
    Returns:
        bool: True si el token está invalidado, False en caso contrario
    """
    return token in _token_blacklist


def limpiar_blacklist() -> None:
    """
    Limpiar la blacklist (útil para testing)
    """
    _token_blacklist.clear()


class AuthService:
    """
    Servicio para gestión de autenticación y autorización de usuarios
    
    Maneja registro, login, validación de credenciales y gestión de tokens JWT
    """

    @staticmethod
    def registrar_usuario(
        db: Session,
        datos_registro: UserRegisterRequest
    ) -> Usuario:
        """
        Registrar un nuevo usuario en el sistema
        
        Validaciones:
        - Email único (no puede existir otro usuario con el mismo email)
        - Contraseña cumple requisitos de seguridad (validado en schema)
        - Nombre válido si se proporciona (validado en schema)
        
        Args:
            db: Sesión de base de datos SQLAlchemy
            datos_registro: Datos del usuario a registrar (validados por Pydantic)
            
        Returns:
            Usuario: Instancia del usuario creado
            
        Raises:
            HTTPException 409: Si el email ya está registrado
            HTTPException 500: Si hay un error inesperado en la base de datos
        """
        # Verificar si el email ya existe
        usuario_existente = db.query(Usuario).filter(
            Usuario.email == datos_registro.email.lower()
        ).first()
        
        if usuario_existente:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"El email {datos_registro.email} ya está registrado en el sistema"
            )
        
        try:
            # Crear nuevo usuario
            nuevo_usuario = Usuario(
                email=datos_registro.email.lower(),  # Normalizar email a minúsculas
                nombre=datos_registro.nombre
            )
            
            # Establecer contraseña (se hashea automáticamente en el modelo)
            nuevo_usuario.set_password(datos_registro.password)
            
            # Guardar en base de datos
            db.add(nuevo_usuario)
            db.commit()
            db.refresh(nuevo_usuario)
            
            return nuevo_usuario
            
        except IntegrityError as e:
            db.rollback()
            # Este caso no debería ocurrir si la verificación inicial funciona
            # pero es una red de seguridad adicional
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El email ya está registrado (error de concurrencia)"
            )
        except Exception as e:
            db.rollback()
            # Log del error en producción
            print(f"Error inesperado al registrar usuario: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno al registrar usuario. Por favor, intente nuevamente."
            )

    @staticmethod
    def login_usuario(
        db: Session,
        datos_login: UserLoginRequest
    ) -> TokenResponse:
        """
        Autenticar usuario y generar token JWT
        
        Validaciones:
        - Email existe en el sistema
        - Contraseña es correcta
        - Usuario está activo (no desactivado)
        
        Args:
            db: Sesión de base de datos SQLAlchemy
            datos_login: Credenciales del usuario (email y password)
            
        Returns:
            TokenResponse: Token JWT y datos del usuario
            
        Raises:
            HTTPException 401: Si las credenciales son inválidas o el usuario está inactivo
            HTTPException 500: Si hay un error inesperado
        """
        try:
            # Buscar usuario por email (normalizado a minúsculas)
            usuario = db.query(Usuario).filter(
                Usuario.email == datos_login.email.lower()
            ).first()
            
            # Verificar que el usuario existe
            if not usuario:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Credenciales inválidas",
                    headers={"WWW-Authenticate": "Bearer"}
                )
            
            # Verificar la contraseña
            if not usuario.verify_password(datos_login.password):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Credenciales inválidas",
                    headers={"WWW-Authenticate": "Bearer"}
                )
            
            # Verificar que la cuenta esté activa
            if not usuario.is_active:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="La cuenta de usuario está desactivada. Contacte al administrador."
                )
            
            # Actualizar último acceso
            usuario.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(usuario)
            
            # Generar token JWT
            config = obtener_configuracion()
            token_data = {
                "sub": usuario.email,  # Subject: email del usuario
                "user_id": usuario.id,
                "nombre": usuario.nombre,
            }
            
            access_token = crear_token_acceso(
                datos=token_data,
                expiracion_minutos=config.jwt_expiracion_minutos
            )
            
            # Crear response con token y datos del usuario
            return TokenResponse(
                access_token=access_token,
                token_type="bearer",
                user=UserResponse(
                    id=usuario.id,
                    email=usuario.email,
                    nombre=usuario.nombre,
                    is_active=usuario.is_active,
                    created_at=usuario.created_at,
                    updated_at=usuario.updated_at
                )
            )
            
        except HTTPException:
            # Re-lanzar excepciones HTTP sin modificar
            raise
        except Exception as e:
            # Log del error en producción
            print(f"Error inesperado al hacer login: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno al procesar login. Por favor, intente nuevamente."
            )

    @staticmethod
    def validar_credenciales(
        db: Session,
        email: str,
        password: str
    ) -> Optional[Usuario]:
        """
        Validar credenciales de un usuario
        
        Args:
            db: Sesión de base de datos SQLAlchemy
            email: Email del usuario
            password: Contraseña en texto plano
            
        Returns:
            Optional[Usuario]: Usuario si las credenciales son válidas, None en caso contrario
        """
        # Buscar usuario por email (normalizado a minúsculas)
        usuario = db.query(Usuario).filter(
            Usuario.email == email.lower()
        ).first()
        
        if not usuario:
            return None
        
        # Verificar contraseña
        if not usuario.verify_password(password):
            return None
        
        # Verificar que la cuenta esté activa
        if not usuario.es_activo:
            return None
        
        return usuario

    @staticmethod
    def obtener_usuario_por_email(
        db: Session,
        email: str
    ) -> Optional[Usuario]:
        """
        Obtener usuario por email
        
        Args:
            db: Sesión de base de datos SQLAlchemy
            email: Email del usuario
            
        Returns:
            Optional[Usuario]: Usuario si existe, None en caso contrario
        """
        return db.query(Usuario).filter(
            Usuario.email == email.lower()
        ).first()

    @staticmethod
    def obtener_usuario_por_id(
        db: Session,
        usuario_id: int
    ) -> Optional[Usuario]:
        """
        Obtener usuario por ID
        
        Args:
            db: Sesión de base de datos SQLAlchemy
            usuario_id: ID del usuario
            
        Returns:
            Optional[Usuario]: Usuario si existe, None en caso contrario
        """
        return db.query(Usuario).filter(Usuario.id == usuario_id).first()

    @staticmethod
    def desactivar_usuario(
        db: Session,
        usuario_id: int
    ) -> bool:
        """
        Desactivar cuenta de usuario (soft delete)
        
        Args:
            db: Sesión de base de datos SQLAlchemy
            usuario_id: ID del usuario a desactivar
            
        Returns:
            bool: True si se desactivó exitosamente, False si el usuario no existe
        """
        usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
        
        if not usuario:
            return False
        
        usuario.desactivar()
        db.commit()
        
        return True

    @staticmethod
    def activar_usuario(
        db: Session,
        usuario_id: int
    ) -> bool:
        """
        Activar cuenta de usuario
        
        Args:
            db: Sesión de base de datos SQLAlchemy
            usuario_id: ID del usuario a activar
            
        Returns:
            bool: True si se activó exitosamente, False si el usuario no existe
        """
        usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
        
        if not usuario:
            return False
        
        usuario.activar()
        db.commit()
        
        return True

    @staticmethod
    def refresh_token(
        db: Session,
        token_actual: str
    ) -> dict:
        """
        Renovar un token JWT existente con uno de mayor duración
        
        Validaciones:
        - El token actual debe ser válido y no expirado
        - El token no debe estar en la blacklist (logout)
        - El usuario debe existir y estar activo
        
        Args:
            db: Sesión de base de datos SQLAlchemy
            token_actual: Token JWT actual a renovar
            
        Returns:
            dict: Diccionario con access_token (nuevo token) y expires_in (segundos)
            
        Raises:
            HTTPException 401: Si el token es inválido, está en blacklist, o el usuario no existe/inactivo
        """
        # Verificar si el token está en la blacklist
        if token_esta_en_blacklist(token_actual):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="El token ha sido invalidado (logout)",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Decodificar y validar el token actual
        payload = decodificar_token(token_actual)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido o expirado",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Extraer email del token
        email = payload.get("sub")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido: no contiene subject (email)",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Verificar que el usuario existe y está activo
        usuario = AuthService.obtener_usuario_por_email(db, email)
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no encontrado",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        if not usuario.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="La cuenta de usuario está desactivada"
            )
        
        # Generar nuevo refresh token con expiración extendida
        config = obtener_configuracion()
        token_data = {
            "sub": usuario.email,
            "user_id": usuario.id,
            "nombre": usuario.nombre,
        }
        
        nuevo_token = crear_refresh_token(
            datos=token_data,
            expiracion_dias=config.jwt_refresh_expiracion_dias
        )
        
        # Calcular tiempo de expiración en segundos
        expires_in_seconds = config.jwt_refresh_expiracion_dias * 24 * 60 * 60
        
        return {
            "access_token": nuevo_token,
            "token_type": "bearer",
            "expires_in": expires_in_seconds
        }

    @staticmethod
    def logout(token: str) -> dict:
        """
        Invalidar un token JWT (logout)
        
        Agrega el token a la blacklist para que no pueda ser usado nuevamente
        
        Args:
            token: Token JWT a invalidar
            
        Returns:
            dict: Mensaje de confirmación
            
        Raises:
            HTTPException 401: Si el token es inválido o ya está en la blacklist
        """
        # Verificar si el token ya está en la blacklist
        if token_esta_en_blacklist(token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="El token ya ha sido invalidado",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Validar que el token es válido antes de agregarlo a la blacklist
        payload = decodificar_token(token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido o expirado",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Agregar token a la blacklist
        agregar_token_a_blacklist(token)
        
        return {
            "message": "Logout exitoso",
            "detail": "El token ha sido invalidado correctamente"
        }
