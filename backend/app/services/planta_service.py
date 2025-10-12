"""
Servicio de lógica de negocio para gestión de plantas.

Este módulo contiene toda la lógica de negocio relacionada con
el CRUD de plantas y estadísticas del jardín del usuario.

Autor: Equipo Backend
Fecha: Octubre 2025
Sprint: Sprint 2 - T-014
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from app.db.models import Planta, Usuario
from app.schemas.planta import (
    PlantaCreate,
    PlantaUpdate,
    PlantaStats
)


class PlantaService:
    """
    Servicio para gestión de plantas del usuario.
    
    Proporciona métodos para crear, leer, actualizar y eliminar plantas,
    así como calcular estadísticas del jardín.
    """
    
    @staticmethod
    def crear_planta(
        db: Session,
        planta_data: PlantaCreate,
        usuario_id: int
    ) -> Planta:
        """
        Crea una nueva planta para un usuario.
        
        Args:
            db (Session): Sesión de base de datos
            planta_data (PlantaCreate): Datos de la planta a crear
            usuario_id (int): ID del usuario propietario
            
        Returns:
            Planta: Planta creada
            
        Raises:
            ValueError: Si el usuario no existe
        """
        # Verificar que el usuario existe
        usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
        if not usuario:
            raise ValueError(f"Usuario con ID {usuario_id} no existe")
        
        # Calcular próximo riego si hay fecha de último riego
        proxima_riego = None
        if planta_data.fecha_ultimo_riego and planta_data.frecuencia_riego_dias:
            proxima_riego = planta_data.fecha_ultimo_riego + timedelta(
                days=planta_data.frecuencia_riego_dias
            )
        
        # Crear la planta
        nueva_planta = Planta(
            usuario_id=usuario_id,
            especie_id=planta_data.especie_id,
            nombre_personal=planta_data.nombre_personal,
            estado_salud=planta_data.estado_salud,
            ubicacion=planta_data.ubicacion,
            notas=planta_data.notas,
            imagen_principal_id=planta_data.imagen_principal_id,
            fecha_ultimo_riego=planta_data.fecha_ultimo_riego,
            proxima_riego=proxima_riego,
            frecuencia_riego_dias=planta_data.frecuencia_riego_dias,
            luz_actual=planta_data.luz_actual,
            fecha_adquisicion=planta_data.fecha_adquisicion,
        )
        
        db.add(nueva_planta)
        db.commit()
        db.refresh(nueva_planta)
        
        return nueva_planta
    
    @staticmethod
    def obtener_plantas_usuario(
        db: Session,
        usuario_id: int,
        skip: int = 0,
        limit: int = 100,
        solo_activas: bool = True
    ) -> List[Planta]:
        """
        Obtiene todas las plantas de un usuario.
        
        Args:
            db (Session): Sesión de base de datos
            usuario_id (int): ID del usuario
            skip (int): Número de registros a saltar (paginación)
            limit (int): Número máximo de registros a retornar
            solo_activas (bool): Si True, solo retorna plantas activas
            
        Returns:
            List[Planta]: Lista de plantas del usuario
        """
        query = db.query(Planta).filter(Planta.usuario_id == usuario_id)
        
        if solo_activas:
            query = query.filter(Planta.is_active == True)
        
        return query.order_by(Planta.created_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def contar_plantas_usuario(
        db: Session,
        usuario_id: int,
        solo_activas: bool = True
    ) -> int:
        """
        Cuenta el total de plantas de un usuario.
        
        Args:
            db (Session): Sesión de base de datos
            usuario_id (int): ID del usuario
            solo_activas (bool): Si True, solo cuenta plantas activas
            
        Returns:
            int: Número total de plantas
        """
        query = db.query(func.count(Planta.id)).filter(Planta.usuario_id == usuario_id)
        
        if solo_activas:
            query = query.filter(Planta.is_active == True)
        
        return query.scalar()
    
    @staticmethod
    def obtener_planta_por_id(
        db: Session,
        planta_id: int,
        usuario_id: int
    ) -> Optional[Planta]:
        """
        Obtiene una planta específica por su ID.
        
        Args:
            db (Session): Sesión de base de datos
            planta_id (int): ID de la planta
            usuario_id (int): ID del usuario (para verificar propiedad)
            
        Returns:
            Optional[Planta]: Planta encontrada o None
        """
        return db.query(Planta).filter(
            and_(
                Planta.id == planta_id,
                Planta.usuario_id == usuario_id,
                Planta.is_active == True
            )
        ).first()
    
    @staticmethod
    def actualizar_planta(
        db: Session,
        planta_id: int,
        usuario_id: int,
        planta_data: PlantaUpdate
    ) -> Optional[Planta]:
        """
        Actualiza los datos de una planta.
        
        Args:
            db (Session): Sesión de base de datos
            planta_id (int): ID de la planta a actualizar
            usuario_id (int): ID del usuario (para verificar propiedad)
            planta_data (PlantaUpdate): Datos a actualizar
            
        Returns:
            Optional[Planta]: Planta actualizada o None si no existe
        """
        planta = PlantaService.obtener_planta_por_id(db, planta_id, usuario_id)
        
        if not planta:
            return None
        
        # Actualizar solo los campos que fueron provistos
        update_data = planta_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(planta, field, value)
        
        # Recalcular próximo riego si se actualizó fecha de último riego o frecuencia
        if 'fecha_ultimo_riego' in update_data or 'frecuencia_riego_dias' in update_data:
            if planta.fecha_ultimo_riego and planta.frecuencia_riego_dias:
                planta.proxima_riego = planta.fecha_ultimo_riego + timedelta(
                    days=planta.frecuencia_riego_dias
                )
        
        planta.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(planta)
        
        return planta
    
    @staticmethod
    def eliminar_planta(
        db: Session,
        planta_id: int,
        usuario_id: int
    ) -> bool:
        """
        Elimina una planta (soft delete).
        
        Args:
            db (Session): Sesión de base de datos
            planta_id (int): ID de la planta a eliminar
            usuario_id (int): ID del usuario (para verificar propiedad)
            
        Returns:
            bool: True si se eliminó, False si no se encontró
        """
        planta = PlantaService.obtener_planta_por_id(db, planta_id, usuario_id)
        
        if not planta:
            return False
        
        planta.soft_delete()
        db.commit()
        
        return True
    
    @staticmethod
    def registrar_riego(
        db: Session,
        planta_id: int,
        usuario_id: int,
        fecha_riego: Optional[datetime] = None
    ) -> Optional[Planta]:
        """
        Registra un nuevo riego en una planta.
        
        Args:
            db (Session): Sesión de base de datos
            planta_id (int): ID de la planta
            usuario_id (int): ID del usuario (para verificar propiedad)
            fecha_riego (Optional[datetime]): Fecha del riego, si no se provee usa la actual
            
        Returns:
            Optional[Planta]: Planta actualizada o None si no existe
        """
        planta = PlantaService.obtener_planta_por_id(db, planta_id, usuario_id)
        
        if not planta:
            return None
        
        planta.registrar_riego(fecha_riego)
        db.commit()
        db.refresh(planta)
        
        return planta
    
    @staticmethod
    def obtener_estadisticas(
        db: Session,
        usuario_id: int
    ) -> PlantaStats:
        """
        Calcula estadísticas del jardín del usuario.
        
        Args:
            db (Session): Sesión de base de datos
            usuario_id (int): ID del usuario
            
        Returns:
            PlantaStats: Estadísticas calculadas
        """
        # Total de plantas activas
        total_plantas = db.query(func.count(Planta.id)).filter(
            and_(
                Planta.usuario_id == usuario_id,
                Planta.is_active == True
            )
        ).scalar()
        
        # Plantas saludables (excelente o buena)
        plantas_saludables = db.query(func.count(Planta.id)).filter(
            and_(
                Planta.usuario_id == usuario_id,
                Planta.is_active == True,
                or_(
                    Planta.estado_salud == 'excelente',
                    Planta.estado_salud == 'buena'
                )
            )
        ).scalar()
        
        # Plantas que necesitan atención (necesita_atencion o critica)
        plantas_necesitan_atencion = db.query(func.count(Planta.id)).filter(
            and_(
                Planta.usuario_id == usuario_id,
                Planta.is_active == True,
                or_(
                    Planta.estado_salud == 'necesita_atencion',
                    Planta.estado_salud == 'critica'
                )
            )
        ).scalar()
        
        # Plantas que necesitan riego hoy
        ahora = datetime.utcnow()
        plantas_necesitan_riego = db.query(func.count(Planta.id)).filter(
            and_(
                Planta.usuario_id == usuario_id,
                Planta.is_active == True,
                Planta.proxima_riego != None,
                Planta.proxima_riego <= ahora
            )
        ).scalar()
        
        # Calcular porcentaje de salud
        porcentaje_salud = 0.0
        if total_plantas > 0:
            porcentaje_salud = round((plantas_saludables / total_plantas) * 100, 2)
        
        return PlantaStats(
            total_plantas=total_plantas,
            plantas_saludables=plantas_saludables,
            plantas_necesitan_atencion=plantas_necesitan_atencion,
            plantas_necesitan_riego=plantas_necesitan_riego,
            porcentaje_salud=porcentaje_salud
        )
    
    @staticmethod
    def buscar_plantas(
        db: Session,
        usuario_id: int,
        query: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Planta]:
        """
        Busca plantas por nombre o ubicación.
        
        Args:
            db (Session): Sesión de base de datos
            usuario_id (int): ID del usuario
            query (str): Término de búsqueda
            skip (int): Número de registros a saltar
            limit (int): Número máximo de registros a retornar
            
        Returns:
            List[Planta]: Lista de plantas encontradas
        """
        search_term = f"%{query}%"
        
        return db.query(Planta).filter(
            and_(
                Planta.usuario_id == usuario_id,
                Planta.is_active == True,
                or_(
                    Planta.nombre_personal.ilike(search_term),
                    Planta.ubicacion.ilike(search_term),
                    Planta.notas.ilike(search_term)
                )
            )
        ).order_by(Planta.created_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def filtrar_por_estado_salud(
        db: Session,
        usuario_id: int,
        estado_salud: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Planta]:
        """
        Filtra plantas por estado de salud.
        
        Args:
            db (Session): Sesión de base de datos
            usuario_id (int): ID del usuario
            estado_salud (str): Estado de salud a filtrar
            skip (int): Número de registros a saltar
            limit (int): Número máximo de registros a retornar
            
        Returns:
            List[Planta]: Lista de plantas filtradas
        """
        return db.query(Planta).filter(
            and_(
                Planta.usuario_id == usuario_id,
                Planta.is_active == True,
                Planta.estado_salud == estado_salud
            )
        ).order_by(Planta.created_at.desc()).offset(skip).limit(limit).all()
