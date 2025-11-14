"use client"

/**
 * AuthContext - Contexto de Autenticación Global
 * 
 * Proporciona estado y métodos de autenticación a toda la aplicación
 * Maneja login, registro, logout, refresh de tokens y estado del usuario
 * 
 * @author GitHub Copilot
 * @date 2025-10-10
 */

import React, { createContext, useState, useEffect, useCallback, useMemo, ReactNode } from 'react'
import { useRouter } from 'next/navigation'
import { authService } from '@/lib/auth.service'

/**
 * Interfaz del Usuario autenticado
 */
export interface Usuario {
  id: number
  email: string
  nombre: string
  es_activo: boolean
  fecha_registro: string
  ultimo_acceso: string | null
}

/**
 * Interfaz del contexto de autenticación
 */
interface AuthContextType {
  usuario: Usuario | null
  estaAutenticado: boolean
  estaCargando: boolean
  iniciarSesion: (email: string, password: string) => Promise<void>
  registrarse: (email: string, password: string, nombre: string) => Promise<void>
  cerrarSesion: () => Promise<void>
  renovarToken: () => Promise<void>
  actualizarUsuario: (usuario: Usuario) => void
}

/**
 * Contexto de autenticación
 */
export const AuthContext = createContext<AuthContextType | undefined>(undefined)

/**
 * Props del Provider
 */
interface AuthProviderProps {
  children: ReactNode
}

/**
 * Provider del contexto de autenticación
 * 
 * Envuelve la aplicación y provee el estado de autenticación
 * Maneja la persistencia de sesión y renovación automática de tokens
 */
export function AuthProvider({ children }: AuthProviderProps) {
  const [usuario, setUsuario] = useState<Usuario | null>(null)
  const [estaCargando, setEstaCargando] = useState(true)
  const router = useRouter()

  /**
   * Verifica si hay una sesión activa al cargar la aplicación
   */
  useEffect(() => {
    const verificarSesion = () => {
      try {
        const usuarioGuardado = authService.getCurrentUser()
        const token = authService.getToken()

        if (usuarioGuardado && token) {
          setUsuario(usuarioGuardado)
        }
      } catch (error) {
        console.error('Error al verificar sesión:', error)
      } finally {
        setEstaCargando(false)
      }
    }

    verificarSesion()
  }, [])

  /**
   * Configura renovación automática de tokens cada 4 horas
   * (los tokens expiran en 8 horas, renovamos 4 horas antes por seguridad)
   */
  useEffect(() => {
    if (!usuario) return

    const intervalo = setInterval(async () => {
      try {
        console.log('🔄 Renovando token automáticamente...')
        await renovarToken()
        console.log('✅ Token renovado exitosamente')
      } catch (error) {
        console.error('❌ Error al renovar token automáticamente:', error)
        // No cerrar sesión inmediatamente, el interceptor de axios lo manejará
      }
    }, 4 * 60 * 60 * 1000) // 4 horas

    return () => clearInterval(intervalo)
  }, [usuario])

  /**
   * Inicia sesión con email y contraseña
   * 
   * @param email - Email del usuario
   * @param password - Contraseña del usuario
   * @throws Error si las credenciales son inválidas
   */
  const iniciarSesion = useCallback(async (email: string, password: string) => {
    setEstaCargando(true)
    try {
      const respuesta = await authService.login({ email, password })
      setUsuario(respuesta.user)
    } finally {
      setEstaCargando(false)
    }
  }, [])

  /**
   * Registra un nuevo usuario
   * 
   * @param email - Email del nuevo usuario
   * @param password - Contraseña del nuevo usuario
   * @param nombre - Nombre completo del nuevo usuario
   * @throws Error si el email ya está registrado
   */
  const registrarse = useCallback(async (email: string, password: string, nombre: string) => {
    setEstaCargando(true)
    try {
      await authService.register({ email, password, nombre })
      // Después del registro, no iniciamos sesión automáticamente
      // El usuario debe hacer login manualmente
    } finally {
      setEstaCargando(false)
    }
  }, [])

  /**
   * Cierra la sesión del usuario actual
   * Limpia el estado y redirige a la landing page
   */
  const cerrarSesion = useCallback(async () => {
    setEstaCargando(true)
    try {
      await authService.logout()
      setUsuario(null)
      router.push('/')
    } catch (error) {
      console.error('Error al cerrar sesión:', error)
      // Aunque falle, limpiamos el estado local
      setUsuario(null)
      router.push('/')
    } finally {
      setEstaCargando(false)
    }
  }, [router])

  /**
   * Renueva el token de acceso
   * Útil para mantener la sesión activa
   * 
   * @throws Error si el token no se puede renovar
   */
  const renovarToken = useCallback(async () => {
    try {
      await authService.refreshToken()
      // El token se actualiza automáticamente en authService
    } catch (error) {
      console.error('Error al renovar token:', error)
      throw error
    }
  }, [])

  /**
   * Actualiza la información del usuario en el estado
   * Útil después de editar el perfil
   * 
   * @param nuevoUsuario - Datos actualizados del usuario
   */
  const actualizarUsuario = useCallback((nuevoUsuario: Usuario) => {
    setUsuario(nuevoUsuario)
    // También actualizamos en localStorage
    if (typeof window !== 'undefined') {
      localStorage.setItem('user', JSON.stringify(nuevoUsuario))
    }
  }, [])

  const valor: AuthContextType = useMemo(() => ({
    usuario,
    estaAutenticado: !!usuario,
    estaCargando,
    iniciarSesion,
    registrarse,
    cerrarSesion,
    renovarToken,
    actualizarUsuario,
  }), [usuario, estaCargando, iniciarSesion, registrarse, cerrarSesion, renovarToken, actualizarUsuario])

  return <AuthContext.Provider value={valor}>{children}</AuthContext.Provider>
}
