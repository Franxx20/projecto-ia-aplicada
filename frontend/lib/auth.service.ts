/**
 * Servicio de Autenticación
 * 
 * Maneja todas las operaciones relacionadas con autenticación JWT
 * Conecta con el backend FastAPI para login, registro, refresh y logout
 * 
 * @author GitHub Copilot
 * @date 2025-10-10
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

/**
 * Interfaz para la respuesta de login
 */
interface TokenResponse {
  access_token: string
  token_type: string
  user: {
    id: number
    email: string
    nombre: string
    es_activo: boolean
    fecha_registro: string
    ultimo_acceso: string | null
  }
}

/**
 * Interfaz para la respuesta de registro
 */
interface UserResponse {
  id: number
  email: string
  nombre: string
  es_activo: boolean
  fecha_registro: string
  ultimo_acceso: string | null
}

/**
 * Interfaz para datos de registro
 */
interface RegisterData {
  email: string
  password: string
  nombre: string
}

/**
 * Interfaz para datos de login
 */
interface LoginData {
  email: string
  password: string
}

class AuthService {
  /**
   * Registra un nuevo usuario
   */
  async register(data: RegisterData): Promise<UserResponse> {
    const response = await fetch(`${API_URL}/api/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Error al registrarse')
    }

    return response.json()
  }

  /**
   * Inicia sesión con email y contraseña
   */
  async login(data: LoginData): Promise<TokenResponse> {
    const response = await fetch(`${API_URL}/api/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include', // ✅ Permite envío de cookies
      body: JSON.stringify(data),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Error al iniciar sesión')
    }

    const tokenData = await response.json()
    
    // ✅ Guardar token en AMBOS lugares: localStorage Y cookies
    if (typeof window !== 'undefined') {
      // localStorage para acceso desde JavaScript
      localStorage.setItem('access_token', tokenData.access_token)
      localStorage.setItem('user', JSON.stringify(tokenData.user))
      
      // Cookies para que el middleware de Next.js pueda acceder
      document.cookie = `access_token=${tokenData.access_token}; path=/; max-age=1800; SameSite=Lax`
    }

    return tokenData
  }

  /**
   * Cierra sesión del usuario actual
   */
  async logout(): Promise<void> {
    const token = this.getToken()
    
    if (token) {
      try {
        await fetch(`${API_URL}/api/auth/logout`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
          },
          body: JSON.stringify({ access_token: token }),
        })
      } catch (error) {
        console.error('Error al cerrar sesión:', error)
      }
    }

    // Limpiar localStorage
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token')
      localStorage.removeItem('user')
    }
  }

  /**
   * Renueva el token de acceso
   */
  async refreshToken(): Promise<string> {
    const currentToken = this.getToken()
    
    if (!currentToken) {
      throw new Error('No hay token para renovar')
    }

    const response = await fetch(`${API_URL}/api/auth/refresh`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${currentToken}`,
      },
      body: JSON.stringify({ access_token: currentToken }),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Error al renovar token')
    }

    const data = await response.json()
    
    // Actualizar token en localStorage
    if (typeof window !== 'undefined') {
      localStorage.setItem('access_token', data.access_token)
    }

    return data.access_token
  }

  /**
   * Obtiene el token de acceso actual
   */
  getToken(): string | null {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('access_token')
    }
    return null
  }

  /**
   * Obtiene el usuario actual
   */
  getCurrentUser(): TokenResponse['user'] | null {
    if (typeof window !== 'undefined') {
      const userStr = localStorage.getItem('user')
      if (userStr) {
        try {
          return JSON.parse(userStr)
        } catch {
          return null
        }
      }
    }
    return null
  }

  /**
   * Verifica si el usuario está autenticado
   */
  isAuthenticated(): boolean {
    return this.getToken() !== null
  }

  /**
   * Obtiene headers con autorización
   */
  getAuthHeaders(): HeadersInit {
    const token = this.getToken()
    return {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` }),
    }
  }
}

// Exportar una instancia única del servicio
export const authService = new AuthService()
export default authService
