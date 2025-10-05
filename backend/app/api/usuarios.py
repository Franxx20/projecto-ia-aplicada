"""
Endpoints de gestión de usuarios

APIs para actualización de perfil, cambio de password y gestión de usuarios
según las especificaciones del Sprint 1.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from ..db import obtener_db
from ..db.models import Usuario
from ..schemas.usuario import (
    UsuarioRespuesta,
    UsuarioPublico,
    UsuarioActualizacion,
    CambioPassword,
    MensajeRespuesta,
    EstadisticasUsuario
)
from ..services.usuario import servicio_usuario
from ..core.dependencies import obtener_usuario_actual, verificar_admin

# Configurar router
router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


@router.get(
    "/me",
    response_model=UsuarioRespuesta,
    summary="Obtener mi perfil",
    description="Obtiene el perfil completo del usuario autenticado"
)
async def obtener_mi_perfil(
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    """
    Obtener perfil del usuario actual
    
    Retorna toda la información del usuario autenticado,
    incluyendo datos personales y configuraciones.
    """
    return UsuarioRespuesta.from_orm(usuario_actual)


@router.put(
    "/me",
    response_model=UsuarioRespuesta,
    summary="Actualizar mi perfil",
    description="Actualiza los datos del perfil del usuario autenticado"
)
async def actualizar_mi_perfil(
    datos_actualizacion: UsuarioActualizacion,
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(obtener_db)
):
    """
    Actualizar perfil del usuario actual
    
    Permite actualizar nombre completo, biografía, ubicación
    y configuración de notificaciones.
    
    - **nombre_completo**: Nombre completo del usuario
    - **bio**: Biografía o descripción personal
    - **ubicacion**: Ubicación geográfica
    - **notificaciones_activas**: Si desea recibir notificaciones
    """
    try:
        usuario_actualizado = servicio_usuario.actualizar_usuario(
            usuario_actual.id,
            datos_actualizacion,
            db
        )
        
        return UsuarioRespuesta.from_orm(usuario_actualizado)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar perfil: {str(e)}"
        )


@router.post(
    "/me/cambiar-password",
    response_model=MensajeRespuesta,
    summary="Cambiar password",
    description="Cambia el password del usuario autenticado"
)
async def cambiar_mi_password(
    datos_cambio: CambioPassword,
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(obtener_db)
):
    """
    Cambiar password del usuario actual
    
    Requiere el password actual para verificación y el nuevo password
    que debe cumplir con los requisitos de seguridad.
    
    - **password_actual**: Password actual para verificación
    - **password_nuevo**: Nuevo password (mín. 8 caracteres)
    - **confirmar_password_nuevo**: Confirmación del nuevo password
    """
    try:
        servicio_usuario.cambiar_password(
            usuario_actual.id,
            datos_cambio,
            db
        )
        
        return MensajeRespuesta(
            mensaje="Password cambiado exitosamente",
            detalle="El password ha sido actualizado correctamente"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al cambiar password: {str(e)}"
        )


@router.delete(
    "/me",
    response_model=MensajeRespuesta,
    summary="Desactivar mi cuenta",
    description="Desactiva la cuenta del usuario autenticado"
)
async def desactivar_mi_cuenta(
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(obtener_db)
):
    """
    Desactivar cuenta propia
    
    Desactiva la cuenta del usuario actual (soft delete).
    La cuenta puede ser reactivada posteriormente por un administrador.
    """
    try:
        servicio_usuario.desactivar_usuario(usuario_actual.id, db)
        
        return MensajeRespuesta(
            mensaje="Cuenta desactivada exitosamente",
            detalle="Tu cuenta ha sido desactivada. Contacta al administrador para reactivarla."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al desactivar cuenta: {str(e)}"
        )


@router.get(
    "/me/estadisticas",
    response_model=EstadisticasUsuario,
    summary="Obtener mis estadísticas",
    description="Obtiene estadísticas del usuario autenticado"
)
async def obtener_mis_estadisticas(
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(obtener_db)
):
    """
    Obtener estadísticas del usuario actual
    
    Retorna estadísticas de uso como:
    - Total de plantas identificadas
    - Total de fotos subidas  
    - Plantas favoritas
    - Días activo
    
    TODO: Implementar cálculo real de estadísticas en sprints futuros
    """
    # Por ahora retornamos estadísticas básicas
    # En sprints futuros se implementarán con datos reales
    return EstadisticasUsuario(
        total_plantas_identificadas=0,
        total_fotos_subidas=0,
        plantas_favoritas=0,
        dias_activo=0,
        ultimo_login=usuario_actual.ultimo_login
    )


# === ENDPOINTS PÚBLICOS ===

@router.get(
    "/{user_id}",
    response_model=UsuarioPublico,
    summary="Obtener perfil público",
    description="Obtiene el perfil público de un usuario por ID"
)
async def obtener_perfil_publico(
    user_id: int,
    db: Session = Depends(obtener_db)
):
    """
    Obtener perfil público de usuario
    
    Retorna información pública del usuario (sin datos sensibles).
    No requiere autenticación.
    """
    usuario = servicio_usuario.obtener_usuario_por_id(user_id, db)
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    if not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no disponible"
        )
    
    return UsuarioPublico.from_orm(usuario)


@router.get(
    "/username/{nombre_usuario}",
    response_model=UsuarioPublico,
    summary="Obtener perfil por nombre de usuario",
    description="Obtiene el perfil público por nombre de usuario"
)
async def obtener_perfil_por_username(
    nombre_usuario: str,
    db: Session = Depends(obtener_db)
):
    """
    Obtener perfil público por nombre de usuario
    
    Busca un usuario por su nombre de usuario único.
    """
    usuario = servicio_usuario.obtener_usuario_por_nombre_usuario(nombre_usuario, db)
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    if not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no disponible"
        )
    
    return UsuarioPublico.from_orm(usuario)


# === ENDPOINTS DE ADMINISTRACIÓN ===

@router.get(
    "/",
    response_model=List[UsuarioPublico],
    summary="Listar usuarios (Admin)",
    description="Lista todos los usuarios del sistema (solo administradores)",
    dependencies=[Depends(verificar_admin)]
)
async def listar_usuarios(
    skip: int = Query(0, ge=0, description="Número de usuarios a saltar"),
    limit: int = Query(100, ge=1, le=1000, description="Límite de usuarios a retornar"),
    db: Session = Depends(obtener_db)
):
    """
    Listar usuarios (solo administradores)
    
    Retorna una lista paginada de todos los usuarios del sistema.
    Solo disponible para usuarios con permisos de administrador.
    """
    usuarios = servicio_usuario.listar_usuarios(skip=skip, limit=limit, db=db)
    return [UsuarioPublico.from_orm(usuario) for usuario in usuarios]


@router.post(
    "/{user_id}/activar",
    response_model=MensajeRespuesta,
    summary="Activar usuario (Admin)",
    description="Activa un usuario desactivado (solo administradores)",
    dependencies=[Depends(verificar_admin)]
)
async def activar_usuario(
    user_id: int,
    db: Session = Depends(obtener_db)
):
    """
    Activar usuario (solo administradores)
    
    Reactiva una cuenta de usuario que había sido desactivada.
    """
    try:
        usuario = servicio_usuario.activar_usuario(user_id, db)
        
        return MensajeRespuesta(
            mensaje="Usuario activado exitosamente",
            detalle=f"Usuario {usuario.nombre_usuario} ha sido reactivado"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al activar usuario: {str(e)}"
        )


@router.post(
    "/{user_id}/desactivar",
    response_model=MensajeRespuesta,
    summary="Desactivar usuario (Admin)",
    description="Desactiva un usuario (solo administradores)",
    dependencies=[Depends(verificar_admin)]
)
async def desactivar_usuario(
    user_id: int,
    db: Session = Depends(obtener_db)
):
    """
    Desactivar usuario (solo administradores)
    
    Desactiva una cuenta de usuario. La cuenta puede ser reactivada.
    """
    try:
        usuario = servicio_usuario.desactivar_usuario(user_id, db)
        
        return MensajeRespuesta(
            mensaje="Usuario desactivado exitosamente",
            detalle=f"Usuario {usuario.nombre_usuario} ha sido desactivado"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al desactivar usuario: {str(e)}"
        )