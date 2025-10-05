"""
Servicio de autenticación JWT

Implementa toda la lógica de JWT tokens, registro, login y validación
siguiendo las especificaciones del Sprint 1.
"""

from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ..core.config import configuracion
from ..db.models import Usuario
from ..schemas.usuario import TokenData


class ServicioAuth:
    """
    Servicio para manejo de autenticación y JWT tokens
    """
    
    def __init__(self):
        self.clave_secreta = configuracion.clave_secreta_jwt
        self.algoritmo = configuracion.algoritmo_jwt
        self.tiempo_expiracion_access = configuracion.tiempo_expiracion_token
        self.tiempo_expiracion_refresh = configuracion.tiempo_expiracion_refresh
    
    def crear_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        Crear token de acceso JWT
        
        Args:
            data: Datos a incluir en el token
            expires_delta: Tiempo personalizado de expiración
            
        Returns:
            str: Token JWT
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.tiempo_expiracion_access)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        })
        
        encoded_jwt = jwt.encode(to_encode, self.clave_secreta, algorithm=self.algoritmo)
        return encoded_jwt
    
    def crear_refresh_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        Crear token de refresh
        
        Args:
            data: Datos a incluir en el token
            expires_delta: Tiempo personalizado de expiración
            
        Returns:
            str: Refresh token JWT
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(days=self.tiempo_expiracion_refresh)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh"
        })
        
        encoded_jwt = jwt.encode(to_encode, self.clave_secreta, algorithm=self.algoritmo)
        return encoded_jwt
    
    def verificar_token(self, token: str, tipo_esperado: str = "access") -> TokenData:
        """
        Verificar y decodificar token JWT
        
        Args:
            token: Token a verificar
            tipo_esperado: Tipo de token esperado (access/refresh)
            
        Returns:
            TokenData: Datos del token decodificado
            
        Raises:
            HTTPException: Si el token es inválido
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se pudieron validar las credenciales",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        try:
            payload = jwt.decode(token, self.clave_secreta, algorithms=[self.algoritmo])
            
            # Verificar tipo de token
            token_type = payload.get("type")
            if token_type != tipo_esperado:
                raise credentials_exception
            
            # Extraer datos
            email: str = payload.get("sub")
            user_id: int = payload.get("user_id")
            
            if email is None or user_id is None:
                raise credentials_exception
            
            token_data = TokenData(email=email, user_id=user_id)
            return token_data
            
        except JWTError:
            raise credentials_exception
    
    def obtener_usuario_desde_token(self, token: str, db: Session) -> Usuario:
        """
        Obtener usuario desde token JWT
        
        Args:
            token: Token JWT
            db: Sesión de base de datos
            
        Returns:
            Usuario: Usuario autenticado
            
        Raises:
            HTTPException: Si el token es inválido o el usuario no existe
        """
        token_data = self.verificar_token(token)
        
        usuario = db.query(Usuario).filter(Usuario.email == token_data.email).first()
        if usuario is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no encontrado",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not usuario.activo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Usuario inactivo"
            )
        
        return usuario
    
    def autenticar_usuario(self, email: str, password: str, db: Session) -> Optional[Usuario]:
        """
        Autenticar usuario con email y password
        
        Args:
            email: Email del usuario
            password: Password del usuario
            db: Sesión de base de datos
            
        Returns:
            Usuario: Usuario autenticado o None si las credenciales son incorrectas
        """
        usuario = db.query(Usuario).filter(Usuario.email == email).first()
        
        if not usuario:
            return None
        
        if not usuario.verificar_password(password):
            return None
        
        if not usuario.activo:
            return None
        
        return usuario
    
    def crear_tokens_para_usuario(self, usuario: Usuario) -> dict:
        """
        Crear access token y refresh token para un usuario
        
        Args:
            usuario: Usuario para crear tokens
            
        Returns:
            dict: Diccionario con tokens y metadata
        """
        # Datos a incluir en el token
        token_data = {
            "sub": usuario.email,
            "user_id": usuario.id,
            "nombre_usuario": usuario.nombre_usuario
        }
        
        access_token = self.crear_access_token(data=token_data)
        refresh_token = self.crear_refresh_token(data=token_data)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": self.tiempo_expiracion_access * 60  # En segundos
        }
    
    def renovar_access_token(self, refresh_token: str, db: Session) -> dict:
        """
        Renovar access token usando refresh token
        
        Args:
            refresh_token: Refresh token válido
            db: Sesión de base de datos
            
        Returns:
            dict: Nuevo access token
            
        Raises:
            HTTPException: Si el refresh token es inválido
        """
        try:
            # Verificar refresh token
            token_data = self.verificar_token(refresh_token, tipo_esperado="refresh")
            
            # Obtener usuario
            usuario = db.query(Usuario).filter(Usuario.email == token_data.email).first()
            if not usuario or not usuario.activo:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Usuario no válido para renovación de token"
                )
            
            # Crear nuevo access token
            new_token_data = {
                "sub": usuario.email,
                "user_id": usuario.id,
                "nombre_usuario": usuario.nombre_usuario
            }
            
            new_access_token = self.crear_access_token(data=new_token_data)
            
            return {
                "access_token": new_access_token,
                "token_type": "bearer",
                "expires_in": self.tiempo_expiracion_access * 60
            }
            
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token de refresh inválido"
            )


# Instancia global del servicio de autenticación
servicio_auth = ServicioAuth()