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
import json
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
        self.updated_at = datetime.now()
    
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
        self.updated_at = datetime.now()
    
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
        self.updated_at = datetime.now()


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
    
    organ = Column(
        String(50),
        nullable=True,
        comment="Tipo de órgano de la planta: flower, leaf, fruit, bark, habit, other"
    )
    
    identificacion_id = Column(
        Integer,
        ForeignKey("identificaciones.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="ID de la identificación asociada (si forma parte de una identificación múltiple)"
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
        Index('idx_imagenes_organ', 'organ'),
        Index('idx_imagenes_identificacion', 'identificacion_id'),
    )
    
    @property
    def url_publica(self) -> str:
        """
        Retorna la URL pública accesible desde el navegador.
        
        Para Azurite (desarrollo), transforma la URL interna de Docker
        a una URL accesible desde localhost.
        
        Returns:
            str: URL pública de la imagen
        """
        if not self.url_blob:
            return ""
        
        # Si la URL contiene 'azurite:10000' (Docker interno),
        # reemplazarla por 'localhost:10000' (accesible desde navegador)
        if 'azurite:10000' in self.url_blob:
            return self.url_blob.replace('azurite:10000', 'localhost:10000')
        
        # Para Azure Storage real, devolver la URL tal cual
        return self.url_blob
    
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
            'url_blob': self.url_publica,  # Usar url_publica para transformar URLs de Azurite
            'container_name': self.container_name,
            'content_type': self.content_type,
            'tamano_bytes': self.tamano_bytes,
            'descripcion': self.descripcion,
            'organ': self.organ,
            'identificacion_id': self.identificacion_id,
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
        self.updated_at = datetime.now()
    
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
        self.updated_at = datetime.now()
    
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
        self.updated_at = datetime.now()


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
        default="desconocido",
        comment="Estado de salud: excelente, saludable, necesita_atencion, enfermedad, plaga, critica, desconocido"
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
    
    proximo_riego = Column(
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
    
    fecha_ultima_fertilizacion = Column(
        DateTime,
        nullable=True,
        comment="Fecha y hora de la última fertilización"
    )
    
    proxima_fertilizacion = Column(
        DateTime,
        nullable=True,
        comment="Fecha y hora de la próxima fertilización recomendada"
    )
    
    frecuencia_fertilizacion_dias = Column(
        Integer,
        nullable=True,
        comment="Frecuencia de fertilización en días"
    )
    
    luz_actual = Column(
        String(20),
        nullable=True,
        comment="Nivel de luz que recibe: baja, media, alta, directa"
    )
    
    condiciones_ambientales_recomendadas = Column(
        Text,
        nullable=True,
        comment="JSON con condiciones ambientales ideales (luz, temperatura, humedad) según análisis inicial"
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
    
    es_favorita = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Indica si la planta ha sido marcada como favorita por el usuario"
    )
    
    fue_regada_hoy = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Indica si la planta fue regada hoy"
    )
    
    # Relaciones
    usuario = relationship("Usuario", backref="plantas")
    # especie = relationship("Especie", backref="plantas")  # Descomentar cuando exista el modelo Especie
    # imagen_principal = relationship("Imagen", foreign_keys=[imagen_principal_id])
    
    # Índices compuestos para optimización de queries
    __table_args__ = (
        Index('idx_usuario_plantas_activas', 'usuario_id', 'is_active'),
        Index('idx_usuario_estado_salud', 'usuario_id', 'estado_salud'),
        Index('idx_proximo_riego', 'proximo_riego'),
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
            'proximo_riego': self.proximo_riego.isoformat() if self.proximo_riego else None,
            'frecuencia_riego_dias': self.frecuencia_riego_dias,
            'fecha_ultima_fertilizacion': self.fecha_ultima_fertilizacion.isoformat() if self.fecha_ultima_fertilizacion else None,
            'proxima_fertilizacion': self.proxima_fertilizacion.isoformat() if self.proxima_fertilizacion else None,
            'frecuencia_fertilizacion_dias': self.frecuencia_fertilizacion_dias,
            'luz_actual': self.luz_actual,
            'condiciones_ambientales_recomendadas': json.loads(self.condiciones_ambientales_recomendadas) if self.condiciones_ambientales_recomendadas else None,
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
        self.updated_at = datetime.now()
    def registrar_riego(self, fecha_riego: Optional[datetime] = None) -> None:
        """
        Registra un nuevo riego de la planta.
        
        Args:
            fecha_riego (Optional[datetime]): Fecha del riego. Si no se provee, usa la fecha actual.
        """
        if fecha_riego is None:
            fecha_riego = datetime.now()
        
        self.fecha_ultimo_riego = fecha_riego
        
        # Calcular próximo riego si hay frecuencia definida
        if self.frecuencia_riego_dias:
            from datetime import timedelta
            self.proximo_riego = fecha_riego + timedelta(days=self.frecuencia_riego_dias)
        
        self.updated_at = datetime.now()
    
    def registrar_fertilizacion(self, fecha_fertilizacion: Optional[datetime] = None) -> None:
        """
        Registra una nueva fertilización de la planta.
        
        Args:
            fecha_fertilizacion (Optional[datetime]): Fecha de la fertilización. Si no se provee, usa la fecha actual.
        """
        if fecha_fertilizacion is None:
            fecha_fertilizacion = datetime.now()
        
        self.fecha_ultima_fertilizacion = fecha_fertilizacion
        
        # Calcular próxima fertilización si hay frecuencia definida
        if self.frecuencia_fertilizacion_dias:
            from datetime import timedelta
            self.proxima_fertilizacion = fecha_fertilizacion + timedelta(days=self.frecuencia_fertilizacion_dias)
        
        self.updated_at = datetime.now()
    
    def necesita_riego(self) -> bool:
        """
        Verifica si la planta necesita riego.
        
        Returns:
            bool: True si necesita riego (fecha actual >= proximo_riego), False en caso contrario
        """
        if not self.proximo_riego:
            return False
        
        # Asegurar que proximo_riego tenga timezone para comparar
        proximo_riego_aware = self.proximo_riego
        
        return datetime.now() >= proximo_riego_aware
    
    def necesita_fertilizacion(self) -> bool:
        """
        Verifica si la planta necesita fertilización.
        
        Returns:
            bool: True si necesita fertilización (fecha actual >= proxima_fertilizacion), False en caso contrario
        """
        if not self.proxima_fertilizacion:
            return False
        
        # Asegurar que proxima_fertilizacion tenga timezone para comparar
        proxima_fertilizacion_aware = self.proxima_fertilizacion
        
        return datetime.now() >= proxima_fertilizacion_aware
    
    def soft_delete(self) -> None:
        """
        Marca la planta como inactiva (soft delete).
        """
        self.is_active = False
        self.updated_at = datetime.now()
    
    def restore(self) -> None:
        """
        Restaura una planta marcada como inactiva.
        """
        self.is_active = True
        self.updated_at = datetime.now()


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
        nullable=True,  # T-022: Nullable para identificaciones con múltiples imágenes
        index=True,
        comment="ID de la imagen (NULL para identificaciones con múltiples imágenes)"
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
    imagen = relationship("Imagen", backref="identificaciones", foreign_keys=[imagen_id])
    imagenes = relationship(
        "Imagen",
        backref="identificacion_asociada",
        foreign_keys="Imagen.identificacion_id",
        cascade="all, delete-orphan"
    )
    especie = relationship("Especie", back_populates="identificaciones")
    
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
        self.fecha_validacion = datetime.now()
        if notas:
            self.notas_usuario = notas
        self.updated_at = datetime.now()
    
    def __repr__(self) -> str:
        """Representación en string del objeto."""
        return (
            f"<Identificacion(id={self.id}, usuario_id={self.usuario_id}, "
            f"especie_id={self.especie_id}, confianza={self.confianza}%)>"
        )
    
    def __str__(self) -> str:
        """String para display."""
        return f"Identificación #{self.id} - {self.confianza}% confianza"
    
    def to_dict(self) -> dict:
        """
        Convierte el modelo a diccionario.
        
        Returns:
            dict: Diccionario con los datos de la identificación
        """
        # Parsear metadatos_ia si existe
        metadatos_plantnet = {}
        if self.metadatos_ia:
            try:
                import json
                metadatos_json = json.loads(self.metadatos_ia)
                metadatos_plantnet = metadatos_json.get("plantnet_response", {})
            except:
                pass
        
        # Incluir información de la especie si existe
        especie_dict = {}
        if self.especie:
            # El modelo Especie usa 'nombre_comun' (singular), lo convertimos a lista para el frontend
            nombres_comunes_list = [self.especie.nombre_comun] if self.especie.nombre_comun else []
            especie_dict = {
                'nombre_cientifico': self.especie.nombre_cientifico,
                'familia': self.especie.familia,
                'nombres_comunes': nombres_comunes_list
            }
        
        # Incluir información de la imagen si existe
        imagen_dict = None
        if self.imagen:
            imagen_dict = {
                'id': self.imagen.id,
                'nombre': self.imagen.nombre_archivo,
                'url': self.imagen.url_publica or self.imagen.url_blob,
                'tamano_bytes': self.imagen.tamano_bytes,
                'tipo_contenido': self.imagen.tipo_contenido
            }
        
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'imagen_id': self.imagen_id,
            'imagen': imagen_dict,  # Agregar información de la imagen
            'especie_id': self.especie_id,
            # Incluir datos de la especie directamente (para retrocompatibilidad)
            'nombre_cientifico': especie_dict.get('nombre_cientifico', ''),
            'familia': especie_dict.get('familia', ''),
            'nombres_comunes': especie_dict.get('nombres_comunes', []),
            'confianza': self.confianza,
            'confianza_porcentaje': self.confianza_porcentaje,
            'es_confiable': self.es_confiable,
            'origen': self.origen,
            'validado': self.validado,
            'fecha_identificacion': self.fecha_identificacion.isoformat() if self.fecha_identificacion else None,
            'fecha_validacion': self.fecha_validacion.isoformat() if self.fecha_validacion else None,
            'notas_usuario': self.notas_usuario,
            'metadatos_ia': self.metadatos_ia,
            'plantnet_response': metadatos_plantnet,  # Para el frontend
            'fecha_creacion': self.created_at.isoformat() if self.created_at else None,  # Alias para el frontend
            'api_name': 'plantnet' if self.origen == 'plantnet' else self.origen,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class AnalisisSalud(Base):
    """
    Modelo de análisis de salud de plantas con Gemini AI.
    
    Este modelo almacena los resultados de los análisis de salud realizados
    por el sistema de IA (Gemini) sobre las plantas del usuario, incluyendo
    diagnósticos, recomendaciones y estadísticas de seguimiento.
    
    Attributes:
        id (int): Identificador único del análisis (Primary Key)
        planta_id (int): ID de la planta analizada (Foreign Key a plantas)
        usuario_id (int): ID del usuario propietario (Foreign Key a usuarios)
        imagen_id (int): ID de la imagen analizada (Foreign Key a imagenes, opcional)
        estado (str): Estado de salud detectado: excelente, saludable, necesita_atencion, 
                     enfermedad, plaga, critica
        confianza (float): Nivel de confianza del análisis (0-100)
        diagnostico (str): Diagnóstico detallado generado por la IA
        recomendaciones (str): JSON con lista de recomendaciones personalizadas
        problemas_detectados (str): JSON con lista de problemas identificados
        notas_usuario (str): Notas adicionales proporcionadas por el usuario
        metadatos_ia (str): JSON con metadatos adicionales de la respuesta de Gemini
        fecha_analisis (datetime): Fecha y hora en que se realizó el análisis
        created_at (datetime): Fecha de creación del registro
        updated_at (datetime): Fecha de última actualización
        
    Relations:
        planta: Relación many-to-one con el modelo Planta
        usuario: Relación many-to-one con el modelo Usuario
        imagen: Relación many-to-one con el modelo Imagen (opcional)
        
    Example:
        >>> analisis = AnalisisSalud(
        ...     planta_id=1,
        ...     usuario_id=1,
        ...     estado="necesita_atencion",
        ...     confianza=85.5,
        ...     diagnostico="Se observan hojas amarillentas...",
        ...     recomendaciones='["Aumentar frecuencia de riego", "Verificar drenaje"]'
        ... )
    """
    
    __tablename__ = "analisis_salud"
    
    # Campos del modelo
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        comment="Identificador único del análisis de salud"
    )
    
    planta_id = Column(
        Integer,
        ForeignKey("plantas.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID de la planta analizada"
    )
    
    usuario_id = Column(
        Integer,
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID del usuario propietario de la planta"
    )
    
    imagen_id = Column(
        Integer,
        ForeignKey("imagenes.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="ID de la imagen utilizada para el análisis (opcional)"
    )
    
    estado = Column(
        String(50),
        nullable=False,
        index=True,
        comment="Estado de salud: excelente, saludable, necesita_atencion, enfermedad, plaga, critica"
    )
    
    confianza = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Nivel de confianza del análisis (0-100)"
    )
    
    resumen_diagnostico = Column(
        Text,
        nullable=False,
        comment="Resumen del diagnóstico en lenguaje natural"
    )
    
    diagnostico_detallado = Column(
        Text,
        nullable=True,
        comment="Diagnóstico técnico detallado (opcional)"
    )
    
    problemas_detectados = Column(
        Text,
        nullable=False,
        default='[]',
        comment="JSON con lista de problemas detectados y su severidad"
    )
    
    recomendaciones = Column(
        Text,
        nullable=False,
        default='[]',
        comment="JSON con lista de recomendaciones personalizadas"
    )
    
    modelo_ia_usado = Column(
        String(100),
        nullable=False,
        comment="Modelo de IA usado (ej: gemini-2.5-flash, gemini-2.5-pro)"
    )
    
    tiempo_analisis_ms = Column(
        Integer,
        nullable=False,
        comment="Tiempo de análisis en milisegundos"
    )
    
    version_prompt = Column(
        String(20),
        nullable=False,
        default='v1',
        comment="Versión del prompt usado"
    )
    
    con_imagen = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Indica si el análisis incluyó imagen"
    )
    
    notas_usuario = Column(
        Text,
        nullable=True,
        comment="Notas o síntomas adicionales proporcionados por el usuario"
    )
    
    metadatos_ia = Column(
        Text,
        nullable=True,
        comment="JSON con metadatos adicionales de la respuesta de Gemini (ej: imagenes_ids, tokens usados, etc.)"
    )
    
    fecha_analisis = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True,
        comment="Fecha y hora en que se realizó el análisis"
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
    planta = relationship("Planta", backref="analisis_salud")
    usuario = relationship("Usuario", backref="analisis_salud")
    imagen = relationship("Imagen", backref="analisis_salud", foreign_keys=[imagen_id])
    
    # Índices compuestos para optimización de queries
    __table_args__ = (
        Index('idx_planta_fecha', 'planta_id', 'fecha_analisis'),
        Index('idx_usuario_fecha', 'usuario_id', 'fecha_analisis'),
        Index('idx_planta_estado', 'planta_id', 'estado'),
        Index('idx_usuario_estado', 'usuario_id', 'estado'),
        Index('idx_fecha_analisis', 'fecha_analisis'),
    )
    
    def __repr__(self) -> str:
        """
        Representación en string del modelo AnalisisSalud.
        
        Returns:
            str: Representación legible del análisis de salud
        """
        return (
            f"<AnalisisSalud(id={self.id}, planta_id={self.planta_id}, "
            f"estado='{self.estado}', confianza={self.confianza})>"
        )
    
    def __str__(self) -> str:
        """
        Representación en string para display.
        
        Returns:
            str: Estado de salud y fecha
        """
        fecha_str = self.fecha_analisis.strftime('%Y-%m-%d %H:%M') if self.fecha_analisis else 'N/A'
        return f"Análisis {self.estado} - {fecha_str}"
    
    def to_dict(self) -> dict:
        """
        Convierte el modelo a diccionario para serialización.
        
        Returns:
            dict: Diccionario con todos los campos del análisis
            
        Example:
            >>> analisis = AnalisisSalud(planta_id=1, estado="saludable")
            >>> data = analisis.to_dict()
            >>> print(data['estado'])
            saludable
        """
        import json
        
        # Parsear JSON fields
        recomendaciones_list = []
        if self.recomendaciones:
            try:
                recomendaciones_list = json.loads(self.recomendaciones)
            except (json.JSONDecodeError, TypeError):
                recomendaciones_list = []
        
        problemas_list = []
        if self.problemas_detectados:
            try:
                problemas_list = json.loads(self.problemas_detectados)
            except (json.JSONDecodeError, TypeError):
                problemas_list = []
        
        return {
            'id': self.id,
            'planta_id': self.planta_id,
            'usuario_id': self.usuario_id,
            'imagen_id': self.imagen_id,
            'estado': self.estado,
            'confianza': self.confianza,
            'resumen_diagnostico': self.resumen_diagnostico,
            'diagnostico_detallado': self.diagnostico_detallado,
            'recomendaciones': recomendaciones_list,
            'problemas_detectados': problemas_list,
            'notas_usuario': self.notas_usuario,
            'modelo_ia_usado': self.modelo_ia_usado,
            'tiempo_analisis_ms': self.tiempo_analisis_ms,
            'version_prompt': self.version_prompt,
            'con_imagen': self.con_imagen,
            'fecha_analisis': self.fecha_analisis.isoformat() if self.fecha_analisis else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def calcular_tendencia(self, analisis_previos: list) -> str:
        """
        Calcula la tendencia de salud basándose en análisis anteriores.
        
        Args:
            analisis_previos (list): Lista de análisis anteriores ordenados por fecha
            
        Returns:
            str: 'mejorando', 'estable', o 'empeorando'
            
        Example:
            >>> # Supongamos que tenemos análisis anteriores
            >>> tendencia = analisis_actual.calcular_tendencia(analisis_previos)
            >>> print(tendencia)
            mejorando
        """
        if not analisis_previos or len(analisis_previos) == 0:
            return 'estable'
        
        # Mapa de estados a valores numéricos (mayor = mejor)
        estados_valor = {
            'critica': 1,
            'plaga': 2,
            'enfermedad': 2,
            'necesita_atencion': 3,
            'saludable': 4,
            'excelente': 5
        }
        
        valor_actual = estados_valor.get(self.estado, 3)
        valor_anterior = estados_valor.get(analisis_previos[0].estado, 3)
        
        if valor_actual > valor_anterior:
            return 'mejorando'
        elif valor_actual < valor_anterior:
            return 'empeorando'
        else:
            return 'estable'
    
    def es_critico(self) -> bool:
        """
        Determina si el estado de salud requiere atención urgente.
        
        Returns:
            bool: True si el estado es crítico, plaga o enfermedad
            
        Example:
            >>> analisis = AnalisisSalud(estado="critica")
            >>> analisis.es_critico()
            True
        """
        return self.estado in ['critica', 'plaga', 'enfermedad']
    
    def obtener_color_estado(self) -> str:
        """
        Retorna el código de color hexadecimal asociado al estado de salud.
        
        Returns:
            str: Código de color hexadecimal
            
        Example:
            >>> analisis = AnalisisSalud(estado="excelente")
            >>> analisis.obtener_color_estado()
            '#22c55e'
        """
        colores = {
            'excelente': '#22c55e',      # Verde brillante
            'saludable': '#84cc16',       # Verde lima
            'necesita_atencion': '#f59e0b',  # Ámbar
            'enfermedad': '#ef4444',      # Rojo
            'plaga': '#dc2626',           # Rojo oscuro
            'critica': '#991b1b'          # Rojo muy oscuro
        }
        return colores.get(self.estado, '#6b7280')  # Gris por defecto


class ChatConversacion(Base):
    """
    Modelo para conversaciones de chat con el asistente de jardinería.
    
    Almacena las conversaciones entre usuarios y el LLM (Gemini AI).
    Cada conversación puede contener múltiples mensajes.
    
    Attributes:
        id (int): Identificador único de la conversación
        usuario_id (int): ID del usuario propietario
        titulo (str): Título de la conversación (auto-generado o personalizado)
        created_at (datetime): Fecha de creación
        updated_at (datetime): Última actualización (último mensaje)
        is_active (bool): Si la conversación está activa (no archivada)
    """
    
    __tablename__ = "chat_conversaciones"
    
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        comment="Identificador único de la conversación"
    )
    
    usuario_id = Column(
        Integer,
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID del usuario propietario de la conversación"
    )
    
    titulo = Column(
        String(255),
        nullable=False,
        default="Nueva conversación",
        comment="Título de la conversación"
    )
    
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True,
        comment="Fecha y hora de creación de la conversación"
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
        comment="Indica si la conversación está activa (no archivada)"
    )
    
    # Relaciones
    mensajes = relationship(
        "ChatMensaje",
        back_populates="conversacion",
        cascade="all, delete-orphan",
        order_by="ChatMensaje.created_at"
    )
    
    usuario = relationship("Usuario", backref="chat_conversaciones")
    
    def __repr__(self) -> str:
        return f"<ChatConversacion(id={self.id}, usuario_id={self.usuario_id}, titulo='{self.titulo}')>"
    
    def to_dict(self) -> dict:
        """Convierte la conversación a diccionario."""
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'titulo': self.titulo,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active,
            'total_mensajes': len(self.mensajes) if hasattr(self, 'mensajes') else 0
        }


class ChatMensaje(Base):
    """
    Modelo para mensajes individuales dentro de una conversación de chat.
    
    Almacena cada mensaje del usuario y del asistente (Gemini AI).
    Incluye tracking de tokens para control de costos y contexto.
    
    Attributes:
        id (int): Identificador único del mensaje
        conversacion_id (int): ID de la conversación a la que pertenece
        rol (str): 'user' o 'assistant'
        contenido (Text): Contenido del mensaje
        planta_id (int): ID de planta si el mensaje está relacionado con una planta específica
        tokens_usados (int): Número de tokens consumidos en la respuesta del LLM
        metadata_json (Text): JSON con información adicional (modelo usado, latencia, etc.)
        created_at (datetime): Fecha y hora de creación del mensaje
    """
    
    __tablename__ = "chat_mensajes"
    
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        comment="Identificador único del mensaje"
    )
    
    conversacion_id = Column(
        Integer,
        ForeignKey("chat_conversaciones.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID de la conversación a la que pertenece el mensaje"
    )
    
    rol = Column(
        String(20),
        nullable=False,
        comment="Rol del emisor: 'user' o 'assistant'"
    )
    
    contenido = Column(
        Text,
        nullable=False,
        comment="Contenido del mensaje"
    )
    
    planta_id = Column(
        Integer,
        ForeignKey("plantas.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="ID de planta relacionada (opcional)"
    )
    
    tokens_usados = Column(
        Integer,
        nullable=True,
        default=0,
        comment="Tokens consumidos por el LLM (solo para mensajes del asistente)"
    )
    
    metadata_json = Column(
        Text,
        nullable=True,
        comment="JSON con metadata adicional (modelo, latencia, contexto usado, etc.)"
    )
    
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True,
        comment="Fecha y hora de creación del mensaje"
    )
    
    # Relaciones
    conversacion = relationship("ChatConversacion", back_populates="mensajes")
    planta = relationship("Planta", backref="chat_mensajes")
    
    # Índices compuestos para queries eficientes
    __table_args__ = (
        Index('idx_conversacion_created', 'conversacion_id', 'created_at'),
        Index('idx_conversacion_rol', 'conversacion_id', 'rol'),
    )
    
    def __repr__(self) -> str:
        preview = self.contenido[:50] + "..." if len(self.contenido) > 50 else self.contenido
        return f"<ChatMensaje(id={self.id}, rol='{self.rol}', contenido='{preview}')>"
    
    def to_dict(self) -> dict:
        """Convierte el mensaje a diccionario."""
        return {
            'id': self.id,
            'conversacion_id': self.conversacion_id,
            'rol': self.rol,
            'contenido': self.contenido,
            'planta_id': self.planta_id,
            'tokens_usados': self.tokens_usados,
            'metadata': self.metadata_json,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class GeminiResponseCache(Base):
    """
    Modelo para caché de respuestas de Gemini AI.
    
    Almacena respuestas de Gemini para preguntas frecuentes, reduciendo
    costos de API y mejorando tiempos de respuesta.
    
    Attributes:
        id (int): Identificador único del registro de caché
        query_hash (str): Hash SHA-256 de la pregunta + contexto
        pregunta (str): Pregunta original del usuario
        contexto_resumido (str): Resumen del contexto usado
        respuesta (Text): Respuesta cacheada de Gemini
        hits (int): Número de veces que se ha usado este caché
        tokens_ahorrados (int): Tokens totales ahorrados con este caché
        created_at (datetime): Fecha de creación del caché
        last_used_at (datetime): Última vez que se usó este caché
        expires_at (datetime): Fecha de expiración del caché
    """
    
    __tablename__ = "gemini_response_cache"
    
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        comment="Identificador único del registro de caché"
    )
    
    query_hash = Column(
        String(64),
        unique=True,
        nullable=False,
        index=True,
        comment="Hash SHA-256 de la pregunta + contexto para identificación única"
    )
    
    pregunta = Column(
        Text,
        nullable=False,
        comment="Pregunta original del usuario"
    )
    
    contexto_resumido = Column(
        Text,
        nullable=True,
        comment="Resumen del contexto usado (especie de planta, problema común, etc.)"
    )
    
    respuesta = Column(
        Text,
        nullable=False,
        comment="Respuesta cacheada de Gemini AI"
    )
    
    hits = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Número de veces que se ha reutilizado este caché"
    )
    
    tokens_ahorrados = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Total de tokens ahorrados con este caché"
    )
    
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True,
        comment="Fecha y hora de creación del caché"
    )
    
    last_used_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        comment="Última vez que se usó este caché"
    )
    
    expires_at = Column(
        DateTime,
        nullable=True,
        index=True,
        comment="Fecha de expiración del caché (NULL = nunca expira)"
    )
    
    # Índices para búsquedas eficientes
    __table_args__ = (
        Index('idx_query_hash_active', 'query_hash', 'expires_at'),
        Index('idx_created_hits', 'created_at', 'hits'),
    )
    
    def __repr__(self) -> str:
        preview = self.pregunta[:50] + "..." if len(self.pregunta) > 50 else self.pregunta
        return f"<GeminiResponseCache(id={self.id}, hits={self.hits}, pregunta='{preview}')>"
    
    def to_dict(self) -> dict:
        """Convierte el caché a diccionario."""
        return {
            'id': self.id,
            'query_hash': self.query_hash,
            'pregunta': self.pregunta,
            'contexto_resumido': self.contexto_resumido,
            'respuesta': self.respuesta,
            'hits': self.hits,
            'tokens_ahorrados': self.tokens_ahorrados,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_used_at': self.last_used_at.isoformat() if self.last_used_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }
    
    def is_expired(self) -> bool:
        """Verifica si el caché ha expirado."""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at
