"""
Modelos de base de datos para el Asistente Plantitas.

Este módulo define los modelos SQLAlchemy para la gestión de usuarios,
autenticación, gestión de imágenes y especies de plantas del sistema.

Autor: Equipo Backend
Fecha: Octubre 2025
Sprint: Sprint 1 - T-002, T-004 | Sprint 2 - T-017
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Boolean, Column, Integer, String, DateTime, Index, ForeignKey, Text
from sqlalchemy.orm import relationship
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
        # Bcrypt tiene un límite de 72 bytes. Truncar para evitar errores.
        # Este es el comportamiento estándar recomendado.
        return pwd_context.hash(password[:72])
    
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


class Imagen(Base):
    """
    Modelo de imagen para gestión de archivos en Azure Blob Storage.
    
    Este modelo almacena la metadata de las imágenes subidas por los usuarios,
    incluyendo referencias al blob en Azure Storage y relación con el usuario propietario.
    
    Attributes:
        id (int): Identificador único de la imagen (Primary Key)
        usuario_id (int): ID del usuario propietario (Foreign Key a usuarios)
        nombre_archivo (str): Nombre original del archivo subido
        nombre_blob (str): Nombre único del blob en Azure Storage (UUID + extensión)
        url_blob (str): URL completa del blob en Azure Storage
        container_name (str): Nombre del contenedor de Azure donde está almacenada
        content_type (str): Tipo MIME del archivo (image/jpeg, image/png, etc.)
        tamano_bytes (int): Tamaño del archivo en bytes
        descripcion (str): Descripción opcional de la imagen
        created_at (datetime): Fecha y hora de subida
        updated_at (datetime): Fecha y hora de última actualización
        is_deleted (bool): Soft delete - indica si la imagen fue eliminada lógicamente
        
    Relations:
        usuario: Relación many-to-one con el modelo Usuario
    """
    
    __tablename__ = "imagenes"
    
    # Campos del modelo
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        comment="Identificador único de la imagen"
    )
    
    usuario_id = Column(
        Integer,
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID del usuario propietario de la imagen"
    )
    
    nombre_archivo = Column(
        String(255),
        nullable=False,
        comment="Nombre original del archivo subido"
    )
    
    nombre_blob = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="Nombre único del blob en Azure Storage (UUID + extensión)"
    )
    
    url_blob = Column(
        Text,
        nullable=False,
        comment="URL completa del blob en Azure Storage"
    )
    
    container_name = Column(
        String(100),
        nullable=False,
        default="plantitas-imagenes",
        comment="Nombre del contenedor de Azure donde está almacenada"
    )
    
    content_type = Column(
        String(100),
        nullable=False,
        comment="Tipo MIME del archivo (image/jpeg, image/png, etc.)"
    )
    
    tamano_bytes = Column(
        Integer,
        nullable=False,
        comment="Tamaño del archivo en bytes"
    )
    
    descripcion = Column(
        Text,
        nullable=True,
        comment="Descripción opcional de la imagen"
    )
    
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="Fecha y hora de subida de la imagen"
    )
    
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        comment="Fecha y hora de última actualización"
    )
    
    is_deleted = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Soft delete - indica si la imagen fue eliminada lógicamente"
    )
    
    # Relaciones
    usuario = relationship("Usuario", backref="imagenes")
    
    # Índices compuestos para optimización de queries
    __table_args__ = (
        Index('idx_usuario_created', 'usuario_id', 'created_at'),
        Index('idx_usuario_deleted', 'usuario_id', 'is_deleted'),
        Index('idx_imagenes_created_at', 'created_at'),
    )
    
    def __repr__(self) -> str:
        """
        Representación en string del modelo Imagen.
        
        Returns:
            str: Representación legible de la imagen
        """
        return f"<Imagen(id={self.id}, usuario_id={self.usuario_id}, nombre='{self.nombre_archivo}')>"
    
    def __str__(self) -> str:
        """
        Representación en string para display.
        
        Returns:
            str: Nombre del archivo
        """
        return self.nombre_archivo
    
    def to_dict(self) -> dict:
        """
        Convierte el modelo a diccionario.
        
        Returns:
            dict: Diccionario con los datos de la imagen
            
        Example:
            >>> imagen = Imagen(nombre_archivo="planta.jpg", usuario_id=1)
            >>> data = imagen.to_dict()
            >>> print(data.keys())
            dict_keys(['id', 'usuario_id', 'nombre_archivo', 'url_blob', ...])
        """
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'nombre_archivo': self.nombre_archivo,
            'nombre_blob': self.nombre_blob,
            'url_blob': self.url_blob,
            'container_name': self.container_name,
            'content_type': self.content_type,
            'tamano_bytes': self.tamano_bytes,
            'descripcion': self.descripcion,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_deleted': self.is_deleted
        }
    
    def soft_delete(self) -> None:
        """
        Marca la imagen como eliminada (soft delete).
        
        No elimina físicamente el blob de Azure Storage.
        Para eliminar completamente, usar el servicio de imágenes.
        
        Example:
            >>> imagen = Imagen(nombre_archivo="test.jpg", usuario_id=1)
            >>> imagen.soft_delete()
            >>> print(imagen.is_deleted)
            True
        """
        self.is_deleted = True
        self.updated_at = datetime.utcnow()
    
    def restore(self) -> None:
        """
        Restaura una imagen marcada como eliminada.
        
        Example:
            >>> imagen = Imagen(nombre_archivo="test.jpg", usuario_id=1)
            >>> imagen.is_deleted = True
            >>> imagen.restore()
            >>> print(imagen.is_deleted)
            False
        """
        self.is_deleted = False
        self.updated_at = datetime.utcnow()
    
    def update_description(self, descripcion: str) -> None:
        """
        Actualiza la descripción de la imagen.
        
        Args:
            descripcion (str): Nueva descripción
            
        Example:
            >>> imagen = Imagen(nombre_archivo="test.jpg", usuario_id=1)
            >>> imagen.update_description("Foto de mi planta favorita")
            >>> print(imagen.descripcion)
            Foto de mi planta favorita
        """
        self.descripcion = descripcion
        self.updated_at = datetime.utcnow()


class Especie(Base):
    """
    Modelo de especie de planta para el catálogo del sistema.
    
    Este modelo almacena información detallada sobre especies de plantas,
    incluyendo datos botánicos, consejos de cuidado y características.
    
    Attributes:
        id (int): Identificador único de la especie (Primary Key)
        nombre_comun (str): Nombre común de la planta (ej: "Monstera Deliciosa")
        nombre_cientifico (str): Nombre científico de la especie
        familia (str): Familia botánica a la que pertenece
        descripcion (str): Descripción general de la planta
        cuidados_basicos (str): Instrucciones básicas de cuidado (JSON string)
        nivel_dificultad (str): Nivel de dificultad de cuidado (facil, medio, dificil)
        luz_requerida (str): Requerimientos de luz (baja, media, alta, directa)
        riego_frecuencia (str): Frecuencia de riego recomendada
        temperatura_min (int): Temperatura mínima tolerable en °C
        temperatura_max (int): Temperatura máxima tolerable en °C
        humedad_requerida (str): Nivel de humedad requerido (baja, media, alta)
        toxicidad (str): Nivel de toxicidad (no_toxica, leve, moderada, alta)
        origen_geografico (str): Región de origen de la especie
        imagen_referencia_url (str): URL de imagen de referencia
        created_at (datetime): Fecha de creación del registro
        updated_at (datetime): Fecha de última actualización
        is_active (bool): Indica si la especie está activa en el catálogo
    
    Example:
        >>> especie = Especie(
        ...     nombre_comun="Monstera Deliciosa",
        ...     nombre_cientifico="Monstera deliciosa",
        ...     familia="Araceae",
        ...     nivel_dificultad="facil"
        ... )
        >>> print(especie.nombre_display)
        Monstera Deliciosa (Monstera deliciosa)
    """
    
    __tablename__ = "especies"
    
    # Campos principales
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        comment="Identificador único de la especie"
    )
    
    nombre_comun = Column(
        String(255),
        nullable=False,
        index=True,
        comment="Nombre común de la planta"
    )
    
    nombre_cientifico = Column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
        comment="Nombre científico de la especie (único)"
    )
    
    familia = Column(
        String(100),
        nullable=True,
        index=True,
        comment="Familia botánica"
    )
    
    descripcion = Column(
        Text,
        nullable=True,
        comment="Descripción general de la planta"
    )
    
    cuidados_basicos = Column(
        Text,
        nullable=True,
        comment="Instrucciones básicas de cuidado en formato JSON"
    )
    
    # Nivel de dificultad
    nivel_dificultad = Column(
        String(20),
        nullable=False,
        default="medio",
        comment="Nivel de dificultad: facil, medio, dificil"
    )
    
    # Requerimientos de luz
    luz_requerida = Column(
        String(20),
        nullable=True,
        comment="Requerimientos de luz: baja, media, alta, directa"
    )
    
    # Requerimientos de riego
    riego_frecuencia = Column(
        String(100),
        nullable=True,
        comment="Frecuencia de riego recomendada"
    )
    
    # Temperatura
    temperatura_min = Column(
        Integer,
        nullable=True,
        comment="Temperatura mínima tolerable en °C"
    )
    
    temperatura_max = Column(
        Integer,
        nullable=True,
        comment="Temperatura máxima tolerable en °C"
    )
    
    # Humedad
    humedad_requerida = Column(
        String(20),
        nullable=True,
        comment="Nivel de humedad: baja, media, alta"
    )
    
    # Toxicidad
    toxicidad = Column(
        String(20),
        nullable=True,
        default="no_toxica",
        comment="Nivel de toxicidad: no_toxica, leve, moderada, alta"
    )
    
    # Información adicional
    origen_geografico = Column(
        String(255),
        nullable=True,
        comment="Región de origen de la especie"
    )
    
    imagen_referencia_url = Column(
        String(500),
        nullable=True,
        comment="URL de imagen de referencia de la especie"
    )
    
    # Metadatos
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="Fecha de creación del registro"
    )
    
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        comment="Fecha de última actualización"
    )
    
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="Indica si la especie está activa en el catálogo"
    )
    
    # Relaciones
    identificaciones = relationship("Identificacion", back_populates="especie")
    
    # Índices compuestos para optimización
    __table_args__ = (
        Index('idx_nombre_comun', 'nombre_comun'),
        Index('idx_nombre_cientifico', 'nombre_cientifico'),
        Index('idx_familia', 'familia'),
        Index('idx_nivel_dificultad', 'nivel_dificultad'),
        Index('idx_especies_active', 'is_active'),
    )
    
    @property
    def nombre_display(self) -> str:
        """
        Retorna el nombre completo para display.
        
        Returns:
            str: Nombre común seguido del nombre científico
            
        Example:
            >>> especie = Especie(nombre_comun="Monstera", nombre_cientifico="M. deliciosa")
            >>> print(especie.nombre_display)
            Monstera (M. deliciosa)
        """
        return f"{self.nombre_comun} ({self.nombre_cientifico})"
    
    def __repr__(self) -> str:
        """
        Representación en string del modelo Especie.
        
        Returns:
            str: Representación legible de la especie
        """
        return f"<Especie(id={self.id}, nombre='{self.nombre_comun}', cientifico='{self.nombre_cientifico}')>"
    
    def __str__(self) -> str:
        """
        Representación en string para display.
        
        Returns:
            str: Nombre común de la especie
        """
        return self.nombre_comun
    
    def to_dict(self) -> dict:
        """
        Convierte el modelo a diccionario.
        
        Returns:
            dict: Diccionario con los datos de la especie
            
        Example:
            >>> especie = Especie(nombre_comun="Monstera", nombre_cientifico="M. deliciosa")
            >>> data = especie.to_dict()
            >>> print(data['nombre_display'])
            Monstera (M. deliciosa)
        """
        return {
            'id': self.id,
            'nombre_comun': self.nombre_comun,
            'nombre_cientifico': self.nombre_cientifico,
            'nombre_display': self.nombre_display,
            'familia': self.familia,
            'descripcion': self.descripcion,
            'cuidados_basicos': self.cuidados_basicos,
            'nivel_dificultad': self.nivel_dificultad,
            'luz_requerida': self.luz_requerida,
            'riego_frecuencia': self.riego_frecuencia,
            'temperatura_min': self.temperatura_min,
            'temperatura_max': self.temperatura_max,
            'humedad_requerida': self.humedad_requerida,
            'toxicidad': self.toxicidad,
            'origen_geografico': self.origen_geografico,
            'imagen_referencia_url': self.imagen_referencia_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active
        }


class Identificacion(Base):
    """
    Modelo de identificación de planta.
    
    Este modelo representa el resultado de una identificación de planta,
    ya sea realizada por IA o manualmente por el usuario. Relaciona
    un usuario, una imagen y una especie identificada.
    
    Attributes:
        id (int): Identificador único de la identificación (Primary Key)
        usuario_id (int): ID del usuario que realizó/recibió la identificación
        imagen_id (int): ID de la imagen analizada
        especie_id (int): ID de la especie identificada
        confianza (float): Nivel de confianza de la identificación (0.0 - 1.0)
        origen (str): Origen de la identificación (ia_plantnet, ia_local, manual)
        validado (bool): Indica si la identificación fue validada por el usuario
        notas_usuario (str): Notas adicionales del usuario
        metadatos_ia (str): Metadatos del proceso de IA en formato JSON
        fecha_identificacion (datetime): Fecha y hora de la identificación
        fecha_validacion (datetime): Fecha y hora de validación por usuario
        created_at (datetime): Fecha de creación del registro
        updated_at (datetime): Fecha de última actualización
    
    Example:
        >>> identificacion = Identificacion(
        ...     usuario_id=1,
        ...     imagen_id=5,
        ...     especie_id=10,
        ...     confianza=0.95,
        ...     origen="ia_plantnet"
        ... )
        >>> print(identificacion.es_confiable)
        True
    """
    
    __tablename__ = "identificaciones"
    
    # Campos principales
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        comment="Identificador único de la identificación"
    )
    
    usuario_id = Column(
        Integer,
        ForeignKey('usuarios.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="ID del usuario que realizó/recibió la identificación"
    )
    
    imagen_id = Column(
        Integer,
        ForeignKey('imagenes.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="ID de la imagen analizada"
    )
    
    especie_id = Column(
        Integer,
        ForeignKey('especies.id', ondelete='RESTRICT'),
        nullable=False,
        index=True,
        comment="ID de la especie identificada"
    )
    
    # Nivel de confianza (0.0 - 1.0)
    confianza = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Nivel de confianza de la identificación (0-100)"
    )
    
    # Origen de la identificación
    origen = Column(
        String(50),
        nullable=False,
        default="manual",
        comment="Origen: ia_plantnet, ia_local, manual"
    )
    
    # Validación por usuario
    validado = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Indica si fue validada por el usuario"
    )
    
    # Notas del usuario
    notas_usuario = Column(
        Text,
        nullable=True,
        comment="Notas adicionales del usuario"
    )
    
    # Metadatos del proceso de IA
    metadatos_ia = Column(
        Text,
        nullable=True,
        comment="Metadatos del proceso de IA en formato JSON"
    )
    
    # Timestamps
    fecha_identificacion = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="Fecha y hora de la identificación"
    )
    
    fecha_validacion = Column(
        DateTime,
        nullable=True,
        comment="Fecha y hora de validación por usuario"
    )
    
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="Fecha de creación del registro"
    )
    
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        comment="Fecha de última actualización"
    )
    
    # Relaciones
    usuario = relationship("Usuario", backref="identificaciones")
    imagen = relationship("Imagen", backref="identificaciones")
    especie = relationship("Especie", back_populates="identificaciones")
    
    # Índices compuestos para optimización
    __table_args__ = (
        Index('idx_usuario_identificacion', 'usuario_id', 'fecha_identificacion'),
        Index('idx_imagen_especie', 'imagen_id', 'especie_id'),
        Index('idx_especie_confianza', 'especie_id', 'confianza'),
        Index('idx_origen', 'origen'),
        Index('idx_validado', 'validado'),
    )
    
    @property
    def es_confiable(self) -> bool:
        """
        Indica si la identificación tiene un nivel de confianza alto.
        
        Returns:
            bool: True si confianza >= 70%
            
        Example:
            >>> id1 = Identificacion(confianza=85)
            >>> print(id1.es_confiable)
            True
            >>> id2 = Identificacion(confianza=45)
            >>> print(id2.es_confiable)
            False
        """
        return self.confianza >= 70
    
    @property
    def confianza_porcentaje(self) -> str:
        """
        Retorna el nivel de confianza como porcentaje formateado.
        
        Returns:
            str: Confianza en formato "XX%"
            
        Example:
            >>> identificacion = Identificacion(confianza=85)
            >>> print(identificacion.confianza_porcentaje)
            85%
        """
        return f"{self.confianza}%"
    
    def validar(self, notas: Optional[str] = None) -> None:
        """
        Marca la identificación como validada por el usuario.
        
        Args:
            notas (str, optional): Notas adicionales del usuario
            
        Example:
            >>> identificacion = Identificacion(validado=False)
            >>> identificacion.validar("Es correcto, es una Monstera")
            >>> print(identificacion.validado)
            True
        """
        self.validado = True
        self.fecha_validacion = datetime.utcnow()
        if notas:
            self.notas_usuario = notas
        self.updated_at = datetime.utcnow()
    
    def __repr__(self) -> str:
        """
        Representación en string del modelo Identificacion.
        
        Returns:
            str: Representación legible de la identificación
        """
        return (
            f"<Identificacion(id={self.id}, usuario_id={self.usuario_id}, "
            f"especie_id={self.especie_id}, confianza={self.confianza}%)>"
        )
    
    def __str__(self) -> str:
        """
        Representación en string para display.
        
        Returns:
            str: Descripción de la identificación
        """
        return f"Identificación #{self.id} - Confianza: {self.confianza_porcentaje}"
    
    def to_dict(self) -> dict:
        """
        Convierte el modelo a diccionario.
        
        Returns:
            dict: Diccionario con los datos de la identificación
            
        Example:
            >>> identificacion = Identificacion(usuario_id=1, confianza=85)
            >>> data = identificacion.to_dict()
            >>> print(data['confianza_porcentaje'])
            85%
        """
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'imagen_id': self.imagen_id,
            'especie_id': self.especie_id,
            'confianza': self.confianza,
            'confianza_porcentaje': self.confianza_porcentaje,
            'es_confiable': self.es_confiable,
            'origen': self.origen,
            'validado': self.validado,
            'notas_usuario': self.notas_usuario,
            'metadatos_ia': self.metadatos_ia,
            'fecha_identificacion': self.fecha_identificacion.isoformat() if self.fecha_identificacion else None,
            'fecha_validacion': self.fecha_validacion.isoformat() if self.fecha_validacion else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

