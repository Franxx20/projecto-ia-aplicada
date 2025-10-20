"""
Modelos de base de datos para el Asistente Plantitas.

Este módulo define los modelos SQLAlchemy para la gestión de usuarios,
autenticación y gestión de imágenes del sistema.

Autor: Equipo Backend
Fecha: Octubre 2025
Sprint: Sprint 1 - T-002, T-004
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
    
    organ = Column(
        String(50),
        nullable=True,
        default='auto',
        comment="Tipo de órgano de la planta: flower, leaf, fruit, bark, habit, other, auto"
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
            'organ': self.organ,
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


class Planta(Base):
    """
    Modelo de planta para gestión del jardín personal del usuario.
    
    Este modelo representa las plantas que el usuario tiene en su colección personal,
    vinculadas a una especie y con información sobre su cuidado y estado.
    
    Attributes:
        id (int): Identificador único de la planta (Primary Key)
        usuario_id (int): ID del usuario propietario (Foreign Key a usuarios)
        especie_id (int): ID de la especie de la planta (Foreign Key a especies) - opcional
        nombre_personal (str): Nombre personalizado que el usuario da a su planta
        estado_salud (str): Estado de salud: excelente, buena, necesita_atencion, critica
        ubicacion (str): Ubicación física de la planta (ej: "sala", "balcón", "jardín")
        notas (str): Notas adicionales del usuario sobre la planta
        imagen_principal_id (int): ID de la imagen principal de la planta (Foreign Key a imagenes)
        fecha_ultimo_riego (datetime): Fecha y hora del último riego
        proxima_riego (datetime): Fecha y hora del próximo riego recomendado
        frecuencia_riego_dias (int): Frecuencia de riego en días
        luz_actual (str): Nivel de luz que recibe: baja, media, alta, directa
        fecha_adquisicion (datetime): Fecha en que el usuario adquirió la planta
        created_at (datetime): Fecha de creación del registro
        updated_at (datetime): Fecha de última actualización
        is_active (bool): Indica si la planta está activa (no eliminada)
        
    Relations:
        usuario: Relación many-to-one con el modelo Usuario
        especie: Relación many-to-one con el modelo Especie (opcional)
        imagen_principal: Relación many-to-one con el modelo Imagen (opcional)
    """
    
    __tablename__ = "plantas"
    
    # Campos del modelo
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        comment="Identificador único de la planta"
    )
    
    usuario_id = Column(
        Integer,
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID del usuario propietario de la planta"
    )
    
    especie_id = Column(
        Integer,
        nullable=True,
        index=True,
        comment="ID de la especie de la planta (opcional)"
    )
    
    nombre_personal = Column(
        String(255),
        nullable=False,
        comment="Nombre personalizado dado por el usuario"
    )
    
    estado_salud = Column(
        String(50),
        nullable=False,
        default="buena",
        comment="Estado de salud: excelente, buena, necesita_atencion, critica"
    )
    
    ubicacion = Column(
        String(255),
        nullable=True,
        comment="Ubicación física de la planta"
    )
    
    notas = Column(
        Text,
        nullable=True,
        comment="Notas adicionales del usuario"
    )
    
    imagen_principal_id = Column(
        Integer,
        nullable=True,
        comment="ID de la imagen principal de la planta"
    )
    
    fecha_ultimo_riego = Column(
        DateTime,
        nullable=True,
        comment="Fecha y hora del último riego"
    )
    
    proxima_riego = Column(
        DateTime,
        nullable=True,
        comment="Fecha y hora del próximo riego recomendado"
    )
    
    frecuencia_riego_dias = Column(
        Integer,
        nullable=True,
        default=7,
        comment="Frecuencia de riego en días"
    )
    
    luz_actual = Column(
        String(20),
        nullable=True,
        comment="Nivel de luz que recibe: baja, media, alta, directa"
    )
    
    fecha_adquisicion = Column(
        DateTime,
        nullable=True,
        comment="Fecha en que el usuario adquirió la planta"
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
    
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="Indica si la planta está activa (no eliminada)"
    )
    
    # Relaciones
    usuario = relationship("Usuario", backref="plantas")
    # especie = relationship("Especie", backref="plantas")  # Descomentar cuando exista el modelo Especie
    # imagen_principal = relationship("Imagen", foreign_keys=[imagen_principal_id])
    
    # Índices compuestos para optimización de queries
    __table_args__ = (
        Index('idx_usuario_plantas_activas', 'usuario_id', 'is_active'),
        Index('idx_usuario_estado_salud', 'usuario_id', 'estado_salud'),
        Index('idx_proxima_riego', 'proxima_riego'),
        Index('idx_created_at_plantas', 'created_at'),
    )
    
    def __repr__(self) -> str:
        """
        Representación en string del modelo Planta.
        
        Returns:
            str: Representación legible de la planta
        """
        return f"<Planta(id={self.id}, nombre='{self.nombre_personal}', usuario_id={self.usuario_id})>"
    
    def __str__(self) -> str:
        """
        Representación en string para display.
        
        Returns:
            str: Nombre personal de la planta
        """
        return self.nombre_personal
    
    def to_dict(self, include_relations: bool = False) -> dict:
        """
        Convierte el modelo a diccionario.
        
        Args:
            include_relations (bool): Si True, incluye datos de relaciones
            
        Returns:
            dict: Diccionario con los datos de la planta
        """
        data = {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'especie_id': self.especie_id,
            'nombre_personal': self.nombre_personal,
            'estado_salud': self.estado_salud,
            'ubicacion': self.ubicacion,
            'notas': self.notas,
            'imagen_principal_id': self.imagen_principal_id,
            'fecha_ultimo_riego': self.fecha_ultimo_riego.isoformat() if self.fecha_ultimo_riego else None,
            'proxima_riego': self.proxima_riego.isoformat() if self.proxima_riego else None,
            'frecuencia_riego_dias': self.frecuencia_riego_dias,
            'luz_actual': self.luz_actual,
            'fecha_adquisicion': self.fecha_adquisicion.isoformat() if self.fecha_adquisicion else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active
        }
        
        return data
    
    def actualizar_estado_salud(self, nuevo_estado: str) -> None:
        """
        Actualiza el estado de salud de la planta.
        
        Args:
            nuevo_estado (str): Nuevo estado (excelente, buena, necesita_atencion, critica)
        """
        estados_validos = ['excelente', 'buena', 'necesita_atencion', 'critica']
        if nuevo_estado not in estados_validos:
            raise ValueError(f"Estado no válido. Debe ser uno de: {', '.join(estados_validos)}")
        
        self.estado_salud = nuevo_estado
        self.updated_at = datetime.utcnow()
    
    def registrar_riego(self, fecha_riego: Optional[datetime] = None) -> None:
        """
        Registra un nuevo riego de la planta.
        
        Args:
            fecha_riego (Optional[datetime]): Fecha del riego. Si no se provee, usa la fecha actual.
        """
        if fecha_riego is None:
            fecha_riego = datetime.utcnow()
        
        self.fecha_ultimo_riego = fecha_riego
        
        # Calcular próximo riego si hay frecuencia definida
        if self.frecuencia_riego_dias:
            from datetime import timedelta
            self.proxima_riego = fecha_riego + timedelta(days=self.frecuencia_riego_dias)
        
        self.updated_at = datetime.utcnow()
    
    def necesita_riego(self) -> bool:
        """
        Verifica si la planta necesita riego.
        
        Returns:
            bool: True si necesita riego (fecha actual >= proxima_riego), False en caso contrario
        """
        if not self.proxima_riego:
            return False
        
        return datetime.utcnow() >= self.proxima_riego
    
    def soft_delete(self) -> None:
        """
        Marca la planta como inactiva (soft delete).
        """
        self.is_active = False
        self.updated_at = datetime.utcnow()
    
    def restore(self) -> None:
        """
        Restaura una planta marcada como inactiva.
        """
        self.is_active = True
        self.updated_at = datetime.utcnow()


# ==================== MODELO ESPECIE ====================

class Especie(Base):
    """
    Modelo para almacenar información de especies de plantas.
    
    Representa una especie botánica con sus características, requisitos
    de cuidado y relaciones con identificaciones.
    
    Attributes:
        id (int): Identificador único de la especie
        nombre_comun (str): Nombre común de la especie
        nombre_cientifico (str): Nombre científico (único)
        familia (str): Familia taxonómica
        descripcion (str): Descripción de la especie
        cuidados_basicos (str): JSON con cuidados básicos
        nivel_dificultad (str): facil, medio, dificil
        luz_requerida (str): baja, media, alta
        riego_frecuencia (str): Descripción de frecuencia de riego
        temperatura_min (int): Temperatura mínima en grados Celsius
        temperatura_max (int): Temperatura máxima en grados Celsius
        humedad_requerida (str): baja, media, alta
        toxicidad (str): ninguna, leve, moderada, alta
        origen_geografico (str): Región de origen
        imagen_referencia_url (str): URL de imagen de referencia
        created_at (datetime): Fecha de creación
        updated_at (datetime): Fecha de última actualización
        is_active (bool): Indica si está activa
        
    Relations:
        identificaciones: Lista de identificaciones de esta especie
    """
    
    __tablename__ = "especies"
    
    # Campos del modelo
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
        comment="Nombre común de la especie"
    )
    
    nombre_cientifico = Column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
        comment="Nombre científico (único)"
    )
    
    familia = Column(
        String(255),
        nullable=True,
        index=True,
        comment="Familia taxonómica"
    )
    
    descripcion = Column(
        Text,
        nullable=True,
        comment="Descripción detallada de la especie"
    )
    
    cuidados_basicos = Column(
        Text,
        nullable=True,
        comment="JSON con cuidados básicos"
    )
    
    nivel_dificultad = Column(
        String(50),
        nullable=False,
        default="medio",
        comment="Nivel de dificultad: facil, medio, dificil"
    )
    
    luz_requerida = Column(
        String(50),
        nullable=True,
        comment="Nivel de luz: baja, media, alta"
    )
    
    riego_frecuencia = Column(
        String(255),
        nullable=True,
        comment="Descripción de frecuencia de riego"
    )
    
    temperatura_min = Column(
        Integer,
        nullable=True,
        comment="Temperatura mínima en grados Celsius"
    )
    
    temperatura_max = Column(
        Integer,
        nullable=True,
        comment="Temperatura máxima en grados Celsius"
    )
    
    humedad_requerida = Column(
        String(50),
        nullable=True,
        comment="Nivel de humedad: baja, media, alta"
    )
    
    toxicidad = Column(
        String(50),
        nullable=True,
        comment="Nivel de toxicidad: ninguna, leve, moderada, alta"
    )
    
    origen_geografico = Column(
        String(255),
        nullable=True,
        comment="Región geográfica de origen"
    )
    
    imagen_referencia_url = Column(
        String(500),
        nullable=True,
        comment="URL de imagen de referencia"
    )
    
    # Timestamps
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="Fecha de creación"
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
        comment="Indica si la especie está activa"
    )
    
    # Relaciones
    identificaciones = relationship(
        "Identificacion",
        back_populates="especie",
        cascade="all, delete-orphan"
    )
    
    # Índices
    __table_args__ = (
        Index('idx_especie_familia', 'familia'),
        Index('idx_especie_dificultad', 'nivel_dificultad'),
        Index('idx_especie_activa', 'is_active'),
    )
    
    @property
    def nombre_display(self) -> str:
        """Retorna el nombre para mostrar con formato: Nombre Común (nombre científico)."""
        if self.nombre_comun and self.nombre_cientifico:
            return f"{self.nombre_comun} ({self.nombre_cientifico})"
        return self.nombre_comun if self.nombre_comun else self.nombre_cientifico
    
    def __repr__(self) -> str:
        """Representación en string del objeto."""
        return f"<Especie(id={self.id}, nombre_comun='{self.nombre_comun}', nombre_cientifico='{self.nombre_cientifico}')>"
    
    def __str__(self) -> str:
        """String para display."""
        return self.nombre_comun
    
    def to_dict(self) -> dict:
        """
        Convierte el modelo a diccionario.
        
        Returns:
            dict: Diccionario con los datos de la especie
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


# ==================== MODELO IDENTIFICACION ====================

class IdentificacionImagen(Base):
    """
    Tabla intermedia para la relación muchos-a-muchos entre
    Identificacion e Imagen.
    
    Permite que una identificación pueda tener múltiples imágenes
    (hasta 5 según PlantNet API) y que cada imagen pueda estar
    en múltiples identificaciones.
    
    Attributes:
        id (int): Identificador único
        identificacion_id (int): ID de la identificación
        imagen_id (int): ID de la imagen
        orden (int): Orden de la imagen en la identificación (1-5)
        created_at (datetime): Fecha de creación
    """
    
    __tablename__ = "identificacion_imagenes"
    
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        comment="Identificador único"
    )
    
    identificacion_id = Column(
        Integer,
        ForeignKey("identificaciones.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID de la identificación"
    )
    
    imagen_id = Column(
        Integer,
        ForeignKey("imagenes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID de la imagen"
    )
    
    orden = Column(
        Integer,
        nullable=False,
        default=1,
        comment="Orden de la imagen en la identificación (1-5)"
    )
    
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="Fecha de creación"
    )
    
    # Relaciones
    identificacion = relationship("Identificacion", back_populates="imagenes_rel")
    imagen = relationship("Imagen")
    
    # Índices
    __table_args__ = (
        Index('idx_identificacion_imagen', 'identificacion_id', 'imagen_id', unique=True),
        Index('idx_identificacion_orden', 'identificacion_id', 'orden'),
    )
    
    def __repr__(self) -> str:
        """Representación en string del objeto."""
        return f"<IdentificacionImagen(identificacion_id={self.identificacion_id}, imagen_id={self.imagen_id}, orden={self.orden})>"


class Identificacion(Base):
    """
    Modelo para registrar identificaciones de plantas.
    
    Almacena los resultados de identificación de plantas, ya sea por IA
    (PlantNet) o manual por el usuario.
    
    Attributes:
        id (int): Identificador único
        usuario_id (int): ID del usuario que realizó la identificación
        imagen_id (int): ID de la imagen identificada
        especie_id (int): ID de la especie identificada
        confianza (int): Nivel de confianza (0-100)
        origen (str): Origen: ia_plantnet, manual
        validado (bool): Si fue validado por el usuario
        fecha_identificacion (datetime): Fecha de la identificación
        fecha_validacion (datetime): Fecha de validación
        notas_usuario (str): Notas del usuario
        metadatos_ia (str): JSON con metadatos de la IA
        created_at (datetime): Fecha de creación
        updated_at (datetime): Fecha de actualización
        
    Relations:
        usuario: Relación con Usuario
        imagen: Relación con Imagen
        especie: Relación con Especie
    """
    
    __tablename__ = "identificaciones"
    
    # Campos del modelo
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        comment="Identificador único"
    )
    
    usuario_id = Column(
        Integer,
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID del usuario"
    )
    
    imagen_id = Column(
        Integer,
        ForeignKey("imagenes.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
        comment="ID de la imagen principal (para retrocompatibilidad, usar imagenes_rel para múltiples)"
    )
    
    especie_id = Column(
        Integer,
        ForeignKey("especies.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="ID de la especie identificada"
    )
    
    confianza = Column(
        Integer,
        nullable=False,
        comment="Nivel de confianza (0-100)"
    )
    
    origen = Column(
        String(50),
        nullable=False,
        comment="Origen: ia_plantnet, manual"
    )
    
    validado = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Si fue validado por el usuario"
    )
    
    fecha_identificacion = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="Fecha de la identificación"
    )
    
    fecha_validacion = Column(
        DateTime,
        nullable=True,
        comment="Fecha de validación por el usuario"
    )
    
    notas_usuario = Column(
        Text,
        nullable=True,
        comment="Notas del usuario sobre la identificación"
    )
    
    metadatos_ia = Column(
        Text,
        nullable=True,
        comment="JSON con metadatos de la IA (score, versión, etc.)"
    )
    
    # Timestamps
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="Fecha de creación"
    )
    
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        comment="Fecha de actualización"
    )
    
    # Relaciones
    usuario = relationship("Usuario", backref="identificaciones")
    imagen = relationship("Imagen", foreign_keys=[imagen_id], backref="identificaciones")
    especie = relationship("Especie", back_populates="identificaciones")
    imagenes_rel = relationship(
        "IdentificacionImagen",
        back_populates="identificacion",
        cascade="all, delete-orphan",
        order_by="IdentificacionImagen.orden"
    )
    
    # Índices
    __table_args__ = (
        Index('idx_identificacion_usuario', 'usuario_id'),
        Index('idx_identificacion_imagen', 'imagen_id'),
        Index('idx_identificacion_especie', 'especie_id'),
        Index('idx_identificacion_origen', 'origen'),
        Index('idx_identificacion_fecha', 'fecha_identificacion'),
    )
    
    @property
    def es_confiable(self) -> bool:
        """Retorna True si la confianza es >= 70%."""
        return self.confianza >= 70
    
    @property
    def confianza_porcentaje(self) -> str:
        """Retorna la confianza como string con formato de porcentaje."""
        return f"{self.confianza}%"
    
    def validar(self, notas: Optional[str] = None) -> None:
        """
        Marca la identificación como validada por el usuario.
        
        Args:
            notas (Optional[str]): Notas de validación
        """
        self.validado = True
        self.fecha_validacion = datetime.utcnow()
        if notas:
            self.notas_usuario = notas
        self.updated_at = datetime.utcnow()
    
    def agregar_imagen(self, imagen_id: int, orden: int = 1) -> 'IdentificacionImagen':
        """
        Agrega una imagen a la identificación.
        
        Args:
            imagen_id (int): ID de la imagen a agregar
            orden (int): Orden de la imagen (1-5)
            
        Returns:
            IdentificacionImagen: El registro de relación creado
        """
        from app.db.session import SessionLocal
        db = SessionLocal()
        try:
            rel = IdentificacionImagen(
                identificacion_id=self.id,
                imagen_id=imagen_id,
                orden=orden
            )
            db.add(rel)
            db.commit()
            return rel
        finally:
            db.close()
    
    def obtener_imagenes(self) -> list:
        """
        Obtiene todas las imágenes asociadas a esta identificación.
        
        Returns:
            list: Lista de objetos Imagen ordenados por orden
        """
        return [rel.imagen for rel in self.imagenes_rel]
    
    def cantidad_imagenes(self) -> int:
        """
        Retorna la cantidad de imágenes asociadas.
        
        Returns:
            int: Cantidad de imágenes
        """
        return len(self.imagenes_rel)
    
    def __repr__(self) -> str:
        """Representación en string del objeto."""
        return (
            f"<Identificacion(id={self.id}, usuario_id={self.usuario_id}, "
            f"especie_id={self.especie_id}, confianza={self.confianza}%)>"
        )
    
    def __str__(self) -> str:
        """String para display."""
        return f"Identificación #{self.id} - {self.confianza}% confianza"
    
    def to_dict(self, include_images: bool = False) -> dict:
        """
        Convierte el modelo a diccionario.
        
        Args:
            include_images (bool): Si True, incluye los IDs de todas las imágenes
        
        Returns:
            dict: Diccionario con los datos de la identificación
        """
        data = {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'imagen_id': self.imagen_id,
            'especie_id': self.especie_id,
            'confianza': self.confianza,
            'confianza_porcentaje': self.confianza_porcentaje,
            'es_confiable': self.es_confiable,
            'origen': self.origen,
            'validado': self.validado,
            'fecha_identificacion': self.fecha_identificacion.isoformat() if self.fecha_identificacion else None,
            'fecha_validacion': self.fecha_validacion.isoformat() if self.fecha_validacion else None,
            'notas_usuario': self.notas_usuario,
            'metadatos_ia': self.metadatos_ia,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'cantidad_imagenes': self.cantidad_imagenes()
        }
        
        if include_images:
            data['imagenes'] = [
                {
                    'imagen_id': rel.imagen_id,
                    'orden': rel.orden,
                    'organ': rel.imagen.organ if rel.imagen else None
                }
                for rel in self.imagenes_rel
            ]
        
        return data
