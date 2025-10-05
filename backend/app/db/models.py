"""
Modelos de Usuario para autenticación y gestión de usuarios

Implementación completa del modelo User con autenticación segura,
siguiendo las especificaciones del Sprint 1.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from passlib.context import CryptContext
from typing import Optional
import re

from .base import Base

# Configuración para hashing de passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Usuario(Base):
    """
    Modelo de Usuario para el sistema de autenticación
    
    Implementa todas las funcionalidades necesarias para registro,
    login y gestión de sesiones con seguridad.
    """
    __tablename__ = "usuarios"
    
    # === CAMPOS PRINCIPALES ===
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    nombre_usuario = Column(String(50), unique=True, index=True, nullable=False)
    nombre_completo = Column(String(255), nullable=True)
    
    # === AUTENTICACIÓN ===
    password_hash = Column(String(255), nullable=False)
    activo = Column(Boolean, default=True, nullable=False)
    verificado = Column(Boolean, default=False, nullable=False)
    
    # === TIMESTAMPS ===
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    fecha_actualizacion = Column(DateTime(timezone=True), onupdate=func.now())
    ultimo_login = Column(DateTime(timezone=True), nullable=True)
    
    # === INFORMACIÓN ADICIONAL ===
    bio = Column(Text, nullable=True)
    ubicacion = Column(String(255), nullable=True)
    
    # === CONFIGURACIÓN DE USUARIO ===
    notificaciones_activas = Column(Boolean, default=True, nullable=False)
    
    def __repr__(self) -> str:
        return f"<Usuario(id={self.id}, email='{self.email}', nombre_usuario='{self.nombre_usuario}')>"
    
    # === MÉTODOS DE AUTENTICACIÓN ===
    
    @staticmethod
    def crear_password_hash(password: str) -> str:
        """
        Crear hash seguro de password usando bcrypt
        
        Args:
            password: Password en texto plano
            
        Returns:
            str: Hash del password
        """
        return pwd_context.hash(password)
    
    def verificar_password(self, password: str) -> bool:
        """
        Verificar si el password coincide con el hash almacenado
        
        Args:
            password: Password en texto plano
            
        Returns:
            bool: True si el password es correcto
        """
        return pwd_context.verify(password, self.password_hash)
    
    def establecer_password(self, password: str) -> None:
        """
        Establecer nuevo password para el usuario
        
        Args:
            password: Nuevo password en texto plano
        """
        if not self.validar_password(password):
            raise ValueError("Password no cumple con los requisitos de seguridad")
        
        self.password_hash = self.crear_password_hash(password)
    
    # === MÉTODOS DE VALIDACIÓN ===
    
    @staticmethod
    def validar_email(email: str) -> bool:
        """
        Validar formato de email
        
        Args:
            email: Email a validar
            
        Returns:
            bool: True si el email es válido
        """
        patron_email = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(patron_email, email) is not None
    
    @staticmethod
    def validar_password(password: str) -> bool:
        """
        Validar que el password cumple con los requisitos de seguridad
        
        Requisitos:
        - Mínimo 8 caracteres
        - Al menos una letra mayúscula
        - Al menos una letra minúscula  
        - Al menos un número
        - Al menos un carácter especial
        
        Args:
            password: Password a validar
            
        Returns:
            bool: True si el password es válido
        """
        if len(password) < 8:
            return False
        
        if not re.search(r'[A-Z]', password):
            return False
        
        if not re.search(r'[a-z]', password):
            return False
        
        if not re.search(r'\d', password):
            return False
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False
        
        return True
    
    @staticmethod
    def validar_nombre_usuario(nombre_usuario: str) -> bool:
        """
        Validar formato de nombre de usuario
        
        Requisitos:
        - Entre 3 y 50 caracteres
        - Solo letras, números y guiones bajos
        - No puede empezar con número
        
        Args:
            nombre_usuario: Nombre de usuario a validar
            
        Returns:
            bool: True si es válido
        """
        if len(nombre_usuario) < 3 or len(nombre_usuario) > 50:
            return False
        
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', nombre_usuario):
            return False
        
        return True
    
    # === MÉTODOS DE UTILIDAD ===
    
    def to_dict(self, incluir_sensible: bool = False) -> dict:
        """
        Convertir usuario a diccionario
        
        Args:
            incluir_sensible: Si incluir información sensible
            
        Returns:
            dict: Datos del usuario
        """
        datos = {
            "id": self.id,
            "email": self.email,
            "nombre_usuario": self.nombre_usuario,
            "nombre_completo": self.nombre_completo,
            "activo": self.activo,
            "verificado": self.verificado,
            "fecha_creacion": self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            "ultimo_login": self.ultimo_login.isoformat() if self.ultimo_login else None,
            "bio": self.bio,
            "ubicacion": self.ubicacion,
            "notificaciones_activas": self.notificaciones_activas
        }
        
        if incluir_sensible:
            datos.update({
                "password_hash": self.password_hash,
                "fecha_actualizacion": self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None
            })
        
        return datos
    
    def actualizar_ultimo_login(self) -> None:
        """
        Actualizar timestamp de último login
        """
        self.ultimo_login = func.now()
    
    def es_admin(self) -> bool:
        """
        Verificar si el usuario tiene permisos de administrador
        
        TODO: Implementar sistema de roles en Sprint futuro
        
        Returns:
            bool: True si es admin
        """
        # Por ahora, retornamos False. En sprints futuros implementaremos roles
        return False