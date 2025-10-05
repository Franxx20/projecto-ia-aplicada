"""
Modelos de base de datos para el Asistente Plantitas.

Este módulo define los modelos SQLAlchemy para la gestión de usuarios
y autenticación del sistema.

Autor: Equipo Backend
Fecha: Octubre 2025
Sprint: Sprint 1 - T-002
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Boolean, Column, Integer, String, DateTime, Index
from sqlalchemy.ext.declarative import declarative_base
from passlib.context import CryptContext

# Configuración de base declarativa de SQLAlchemy
Base = declarative_base()

# Configuración de contexto de encriptación de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Usuario(Base):
    """
    Modelo de usuario para autenticación y gestión de cuentas.
    
    Este modelo representa a los usuarios del sistema Asistente Plantitas.
    Incluye funcionalidades de hashing de contraseñas y validación.
    
    Attributes:
        id (int): Identificador único del usuario (Primary Key)
        email (str): Correo electrónico único del usuario
        password_hash (str): Contraseña hasheada con bcrypt
        nombre (str): Nombre completo del usuario (opcional)
        created_at (datetime): Fecha y hora de creación de la cuenta
        updated_at (datetime): Fecha y hora de última actualización
        is_active (bool): Estado de activación de la cuenta
        is_superuser (bool): Indica si el usuario tiene privilegios de administrador
    """
    
    __tablename__ = "usuarios"
    
    # Campos del modelo
    id = Column(
        Integer, 
        primary_key=True, 
        index=True,
        comment="Identificador único del usuario"
    )
    
    email = Column(
        String(255), 
        unique=True, 
        index=True, 
        nullable=False,
        comment="Correo electrónico único del usuario"
    )
    
    password_hash = Column(
        String(255), 
        nullable=False,
        comment="Contraseña hasheada con bcrypt"
    )
    
    nombre = Column(
        String(255), 
        nullable=True,
        comment="Nombre completo del usuario"
    )
    
    created_at = Column(
        DateTime, 
        default=datetime.utcnow, 
        nullable=False,
        comment="Fecha y hora de creación de la cuenta"
    )
    
    updated_at = Column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow,
        nullable=False,
        comment="Fecha y hora de última actualización"
    )
    
    is_active = Column(
        Boolean, 
        default=True, 
        nullable=False,
        comment="Estado de activación de la cuenta"
    )
    
    is_superuser = Column(
        Boolean, 
        default=False, 
        nullable=False,
        comment="Indica si el usuario tiene privilegios de administrador"
    )
    
    # Índices compuestos para optimización de queries
    __table_args__ = (
        Index('idx_email_active', 'email', 'is_active'),
        Index('idx_created_at', 'created_at'),
    )
    
    def __repr__(self) -> str:
        """
        Representación en string del modelo Usuario.
        
        Returns:
            str: Representación legible del usuario
        """
        return f"<Usuario(id={self.id}, email='{self.email}', nombre='{self.nombre}')>"
    
    def __str__(self) -> str:
        """
        Representación en string para display.
        
        Returns:
            str: Email del usuario
        """
        return self.email
    
    # Métodos de gestión de contraseñas
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hashea una contraseña usando bcrypt.
        
        Args:
            password (str): Contraseña en texto plano
            
        Returns:
            str: Contraseña hasheada
            
        Example:
            >>> hashed = Usuario.hash_password("mi_contraseña_segura")
            >>> print(len(hashed))  # Longitud típica del hash
            60
        """
        return pwd_context.hash(password)
    
    def set_password(self, password: str) -> None:
        """
        Establece la contraseña del usuario hasheándola.
        
        Args:
            password (str): Contraseña en texto plano
            
        Example:
            >>> usuario = Usuario(email="test@example.com")
            >>> usuario.set_password("mi_contraseña")
            >>> print(usuario.password_hash[:7])
            $2b$12$
        """
        self.password_hash = self.hash_password(password)
    
    def verify_password(self, password: str) -> bool:
        """
        Verifica si una contraseña coincide con el hash almacenado.
        
        Args:
            password (str): Contraseña en texto plano a verificar
            
        Returns:
            bool: True si la contraseña es correcta, False en caso contrario
            
        Example:
            >>> usuario = Usuario(email="test@example.com")
            >>> usuario.set_password("mi_contraseña")
            >>> usuario.verify_password("mi_contraseña")
            True
            >>> usuario.verify_password("contraseña_incorrecta")
            False
        """
        return pwd_context.verify(password, self.password_hash)
    
    # Métodos de utilidad
    
    def to_dict(self, include_password: bool = False) -> dict:
        """
        Convierte el modelo a diccionario.
        
        Args:
            include_password (bool): Si True, incluye el hash de contraseña.
                                    Por defecto False por seguridad.
            
        Returns:
            dict: Diccionario con los datos del usuario
            
        Example:
            >>> usuario = Usuario(email="test@example.com", nombre="Test User")
            >>> data = usuario.to_dict()
            >>> print(data.keys())
            dict_keys(['id', 'email', 'nombre', 'created_at', 'updated_at', 'is_active', 'is_superuser'])
        """
        data = {
            'id': self.id,
            'email': self.email,
            'nombre': self.nombre,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active,
            'is_superuser': self.is_superuser
        }
        
        if include_password:
            data['password_hash'] = self.password_hash
            
        return data
    
    def activate(self) -> None:
        """
        Activa la cuenta del usuario.
        
        Example:
            >>> usuario = Usuario(email="test@example.com")
            >>> usuario.is_active = False
            >>> usuario.activate()
            >>> print(usuario.is_active)
            True
        """
        self.is_active = True
        self.updated_at = datetime.utcnow()
    
    def deactivate(self) -> None:
        """
        Desactiva la cuenta del usuario.
        
        Example:
            >>> usuario = Usuario(email="test@example.com")
            >>> usuario.deactivate()
            >>> print(usuario.is_active)
            False
        """
        self.is_active = False
        self.updated_at = datetime.utcnow()
    
    def update_info(self, nombre: Optional[str] = None, email: Optional[str] = None) -> None:
        """
        Actualiza la información del usuario.
        
        Args:
            nombre (Optional[str]): Nuevo nombre del usuario
            email (Optional[str]): Nuevo email del usuario
            
        Example:
            >>> usuario = Usuario(email="test@example.com", nombre="Test")
            >>> usuario.update_info(nombre="Nuevo Nombre")
            >>> print(usuario.nombre)
            Nuevo Nombre
        """
        if nombre is not None:
            self.nombre = nombre
        if email is not None:
            self.email = email
        self.updated_at = datetime.utcnow()


# Función de inicialización de base de datos
def init_db(engine):
    """
    Inicializa la base de datos creando todas las tablas.
    
    Args:
        engine: Motor SQLAlchemy engine
        
    Example:
        >>> from sqlalchemy import create_engine
        >>> engine = create_engine('sqlite:///test.db')
        >>> init_db(engine)
    """
    Base.metadata.create_all(bind=engine)


def drop_all_tables(engine):
    """
    Elimina todas las tablas de la base de datos.
    
    ADVERTENCIA: Esta función elimina TODOS los datos.
    Solo usar en desarrollo o testing.
    
    Args:
        engine: Motor SQLAlchemy engine
    """
    Base.metadata.drop_all(bind=engine)
