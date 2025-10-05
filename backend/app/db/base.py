"""
Configuración base de SQLAlchemy para el proyecto

Configuración de la base de datos, session y Base declarativa
siguiendo las convenciones del proyecto.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import logging

from ..core.config import configuracion

# Configurar logging
logger = logging.getLogger(__name__)

# Crear engine de SQLAlchemy
engine = create_engine(
    configuracion.url_base_datos,
    pool_pre_ping=True,  # Verificar conexiones antes de usar
    echo=configuracion.debug,  # Mostrar SQL queries en debug
)

# Crear SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base declarativa para modelos
Base = declarative_base()


def obtener_db() -> Generator[Session, None, None]:
    """
    Dependency para obtener sesión de base de datos
    
    Yields:
        Session: Sesión de SQLAlchemy
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Error en sesión de base de datos: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def crear_tablas():
    """
    Crear todas las tablas en la base de datos
    """
    logger.info("Creando tablas en la base de datos...")
    Base.metadata.create_all(bind=engine)
    logger.info("Tablas creadas exitosamente")


def eliminar_tablas():
    """
    Eliminar todas las tablas (solo para desarrollo/testing)
    """
    if configuracion.entorno == "desarrollo":
        logger.warning("Eliminando todas las tablas...")
        Base.metadata.drop_all(bind=engine)
        logger.warning("Tablas eliminadas")
    else:
        raise RuntimeError("No se pueden eliminar tablas en producción")