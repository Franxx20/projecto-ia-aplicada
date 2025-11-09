/**
 * axios.ts - Configuración de Axios con interceptores
 * 
 * Instancia configurada de Axios con interceptores para:
 * - Adjuntar automáticamente tokens JWT a las peticiones
 * - Manejar renovación automática de tokens en errores 401
 * - Retry automático de peticiones fallidas después de renovar token
 * 
 * @author GitHub Copilot
 * @date 2025-10-10
 */

import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios'
import { authService } from './auth.service'

/**
 * Instancia de Axios configurada con baseURL
 */
const axiosInstance = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 60000, // 60 segundos (necesario para análisis con IA que pueden tardar)
})

/**
 * Flag para evitar loops infinitos en renovación de tokens
 */
let estaRenovandoToken = false

/**
 * Cola de peticiones pendientes durante la renovación del token
 */
let peticionesPendientes: Array<(token: string) => void> = []

/**
 * Procesa la cola de peticiones pendientes con el nuevo token
 * 
 * @param token - Nuevo token de acceso
 */
const procesarColaPeticiones = (token: string) => {
  peticionesPendientes.forEach((callback) => callback(token))
  peticionesPendientes = []
}

/**
 * Agrega una petición a la cola de espera
 * 
 * @param callback - Función que se ejecutará con el nuevo token
 * @returns Promise que se resuelve con el nuevo token
 */
const agregarPeticionALaCola = (callback: (token: string) => void): Promise<string> => {
  return new Promise((resolve) => {
    peticionesPendientes.push((token: string) => {
      callback(token)
      resolve(token)
    })
  })
}

/**
 * Request Interceptor
 * Adjunta automáticamente el token JWT a todas las peticiones
 */
axiosInstance.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = authService.getToken()
    
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    return config
  },
  (error: AxiosError) => {
    return Promise.reject(error)
  }
)

/**
 * Response Interceptor
 * Maneja errores 401 y renueva el token automáticamente
 */
axiosInstance.interceptors.response.use(
  (response) => {
    return response
  },
  async (error: AxiosError) => {
    const configOriginal = error.config as InternalAxiosRequestConfig & { _retry?: boolean }

    // Si es error 401 y no hemos intentado renovar el token
    if (error.response?.status === 401 && !configOriginal._retry) {
      
      // Evitar rutas de autenticación (login, register, refresh)
      if (
        configOriginal.url?.includes('/auth/login') ||
        configOriginal.url?.includes('/auth/register') ||
        configOriginal.url?.includes('/auth/refresh')
      ) {
        return Promise.reject(error)
      }

      // Si ya estamos renovando el token, agregar esta petición a la cola
      if (estaRenovandoToken) {
        return new Promise((resolve) => {
          agregarPeticionALaCola((token: string) => {
            if (configOriginal.headers) {
              configOriginal.headers.Authorization = `Bearer ${token}`
            }
            resolve(axiosInstance(configOriginal))
          })
        })
      }

      // Marcar que estamos renovando el token
      configOriginal._retry = true
      estaRenovandoToken = true

      try {
        // Intentar renovar el token
        await authService.refreshToken()
        const nuevoToken = authService.getToken()

        if (!nuevoToken) {
          throw new Error('No se pudo obtener el nuevo token')
        }

        // Actualizar el header de la petición original
        if (configOriginal.headers) {
          configOriginal.headers.Authorization = `Bearer ${nuevoToken}`
        }

        // Procesar todas las peticiones en cola
        procesarColaPeticiones(nuevoToken)

        // Reintentar la petición original
        return axiosInstance(configOriginal)
      } catch (refreshError) {
        // Si falla la renovación del token, limpiar y rechazar
        procesarColaPeticiones('')
        
        // Limpiar sesión si el refresh token también expiró
        if (typeof window !== 'undefined') {
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          localStorage.removeItem('user')
          window.location.href = '/login'
        }
        
        return Promise.reject(refreshError)
      } finally {
        estaRenovandoToken = false
      }
    }

    return Promise.reject(error)
  }
)

export default axiosInstance
