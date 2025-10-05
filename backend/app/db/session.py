"""
Configuración de sesión de base de datos SQLAlchemy

Gestiona la creación de sesiones de base de datos y el engine de SQLAlchemy.
Proporciona la función get_db como dependency para FastAPI.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from typing import Generator

from app.core.config import obtener_configuracion

# Obtener configuración
configuracion = obtener_configuracion()

# Crear engine de SQLAlchemy
# Para SQLite: check_same_thread=False permite usar la misma conexión en múltiples threads
# Para PostgreSQL en producción, esto no es necesario
engine = create_engine(
    configuracion.url_base_datos,
    echo=configuracion.db_echo,  # Mostrar queries SQL en logs si está activado
    connect_args={"check_same_thread": False} if "sqlite" in configuracion.url_base_datos else {},
    pool_pre_ping=True,  # Verificar conexión antes de usar
)

# Crear SessionLocal class
# Esta clase se usa para crear instancias de sesión de base de datos
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class para modelos
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency para obtener sesión de base de datos en endpoints FastAPI
    
    Crea una nueva sesión de base de datos para cada request y la cierra
    automáticamente cuando el request termina.
    
    Yields:
        Session: Sesión de base de datos SQLAlchemy
        
    Example:
        >>> from fastapi import Depends
        >>> @app.get("/usuarios")
        >>> def listar_usuarios(db: Session = Depends(get_db)):
        >>>     usuarios = db.query(Usuario).all()
        >>>     return usuarios
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def crear_tablas():
    """
    Crear todas las tablas en la base de datos
    
    Crea las tablas basándose en los modelos definidos que heredan de Base.
    Útil para desarrollo y testing, pero en producción se deben usar migraciones
    de Alembic.
    
    Note:
        En producción, usar Alembic para migraciones:
        >>> alembic upgrade head
    """
    Base.metadata.create_all(bind=engine)


def eliminar_tablas():
    """
    Eliminar todas las tablas de la base de datos
    
    ⚠️ CUIDADO: Esta función elimina TODAS las tablas.
    Solo usar en desarrollo y testing.
    
    Warning:
        NO usar en producción. Perderás todos los datos.
    """
    Base.metadata.drop_all(bind=engine)
