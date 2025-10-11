/**
 * Tests unitarios para AuthService
 * 
 * Prueba todas las funciones del servicio de autenticación:
 * - register()
 * - login()
 * - logout()
 * - refreshToken()
 * - getToken()
 * - getCurrentUser()
 * - isAuthenticated()
 * - getAuthHeaders()
 * 
 * @author GitHub Copilot
 * @date 2025-10-10
 */

import { authService } from '@/lib/auth.service'

// Mock de fetch global
global.fetch = jest.fn()

// Mock de localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {}

  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => {
      store[key] = value.toString()
    },
    removeItem: (key: string) => {
      delete store[key]
    },
    clear: () => {
      store = {}
    },
  }
})()

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
})

describe('AuthService', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    localStorageMock.clear()
    ;(global.fetch as jest.Mock).mockClear()
  })

  describe('register()', () => {
    it('debe registrar un usuario exitosamente', async () => {
      // Arrange
      const mockResponse = {
        id: 1,
        email: 'test@example.com',
        nombre: 'Test User',
        es_activo: true,
        fecha_registro: '2025-10-10T10:00:00',
        ultimo_acceso: null,
      }

      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      })

      // Act
      const result = await authService.register({
        email: 'test@example.com',
        password: 'Password123',
        nombre: 'Test User',
      })

      // Assert
      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/auth/register',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            email: 'test@example.com',
            password: 'Password123',
            nombre: 'Test User',
          }),
        }
      )
      expect(result).toEqual(mockResponse)
    })

    it('debe lanzar error cuando el registro falla', async () => {
      // Arrange
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        json: async () => ({ detail: 'El email ya está registrado' }),
      })

      // Act & Assert
      await expect(
        authService.register({
          email: 'existing@example.com',
          password: 'Password123',
          nombre: 'Test User',
        })
      ).rejects.toThrow('El email ya está registrado')
    })

    it('debe lanzar error genérico cuando no hay mensaje de detalle', async () => {
      // Arrange
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        json: async () => ({}),
      })

      // Act & Assert
      await expect(
        authService.register({
          email: 'test@example.com',
          password: 'Password123',
          nombre: 'Test User',
        })
      ).rejects.toThrow('Error al registrarse')
    })

    it('debe manejar errores de red', async () => {
      // Arrange
      ;(global.fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'))

      // Act & Assert
      await expect(
        authService.register({
          email: 'test@example.com',
          password: 'Password123',
          nombre: 'Test User',
        })
      ).rejects.toThrow('Network error')
    })
  })

  describe('login()', () => {
    it('debe hacer login exitosamente y guardar token/usuario', async () => {
      // Arrange
      const mockResponse = {
        access_token: 'test-token-123',
        token_type: 'bearer',
        user: {
          id: 1,
          email: 'test@example.com',
          nombre: 'Test User',
          es_activo: true,
          fecha_registro: '2025-10-10T10:00:00',
          ultimo_acceso: null,
        },
      }

      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      })

      // Act
      const result = await authService.login({
        email: 'test@example.com',
        password: 'Password123',
      })

      // Assert
      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/auth/login',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            email: 'test@example.com',
            password: 'Password123',
          }),
        }
      )
      expect(result).toEqual(mockResponse)
      expect(localStorageMock.getItem('access_token')).toBe('test-token-123')
      expect(localStorageMock.getItem('user')).toBe(JSON.stringify(mockResponse.user))
    })

    it('debe lanzar error cuando las credenciales son inválidas', async () => {
      // Arrange
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        json: async () => ({ detail: 'Credenciales inválidas' }),
      })

      // Act & Assert
      await expect(
        authService.login({
          email: 'wrong@example.com',
          password: 'WrongPassword',
        })
      ).rejects.toThrow('Credenciales inválidas')
    })

    it('debe lanzar error genérico cuando no hay mensaje de detalle', async () => {
      // Arrange
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        json: async () => ({}),
      })

      // Act & Assert
      await expect(
        authService.login({
          email: 'test@example.com',
          password: 'Password123',
        })
      ).rejects.toThrow('Error al iniciar sesión')
    })

    it('debe manejar usuario desactivado (403)', async () => {
      // Arrange
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 403,
        json: async () => ({ detail: 'La cuenta de usuario está desactivada' }),
      })

      // Act & Assert
      await expect(
        authService.login({
          email: 'inactive@example.com',
          password: 'Password123',
        })
      ).rejects.toThrow('La cuenta de usuario está desactivada')
    })
  })

  describe('logout()', () => {
    it('debe hacer logout exitosamente y limpiar localStorage', async () => {
      // Arrange
      localStorageMock.setItem('access_token', 'test-token-123')
      localStorageMock.setItem('user', JSON.stringify({ id: 1, email: 'test@example.com' }))

      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ message: 'Logout exitoso' }),
      })

      // Act
      await authService.logout()

      // Assert
      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/auth/logout',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer test-token-123',
          },
          body: JSON.stringify({ access_token: 'test-token-123' }),
        }
      )
      expect(localStorageMock.getItem('access_token')).toBeNull()
      expect(localStorageMock.getItem('user')).toBeNull()
    })

    it('debe limpiar localStorage incluso si la petición al backend falla', async () => {
      // Arrange
      localStorageMock.setItem('access_token', 'test-token-123')
      localStorageMock.setItem('user', JSON.stringify({ id: 1 }))

      ;(global.fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'))

      // Act
      await authService.logout()

      // Assert
      expect(localStorageMock.getItem('access_token')).toBeNull()
      expect(localStorageMock.getItem('user')).toBeNull()
    })

    it('debe funcionar correctamente cuando no hay token', async () => {
      // Arrange - No hay token en localStorage

      // Act
      await authService.logout()

      // Assert
      expect(global.fetch).not.toHaveBeenCalled()
      expect(localStorageMock.getItem('access_token')).toBeNull()
      expect(localStorageMock.getItem('user')).toBeNull()
    })
  })

  describe('refreshToken()', () => {
    it('debe renovar el token exitosamente', async () => {
      // Arrange
      localStorageMock.setItem('access_token', 'old-token-123')

      const mockResponse = {
        access_token: 'new-token-456',
        token_type: 'bearer',
        expires_in: 604800,
      }

      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      })

      // Act
      const result = await authService.refreshToken()

      // Assert
      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/auth/refresh',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer old-token-123',
          },
          body: JSON.stringify({ access_token: 'old-token-123' }),
        }
      )
      expect(result).toBe('new-token-456')
      expect(localStorageMock.getItem('access_token')).toBe('new-token-456')
    })

    it('debe lanzar error cuando no hay token para renovar', async () => {
      // Arrange - No hay token en localStorage

      // Act & Assert
      await expect(authService.refreshToken()).rejects.toThrow('No hay token para renovar')
    })

    it('debe lanzar error cuando el token expiró', async () => {
      // Arrange
      localStorageMock.setItem('access_token', 'expired-token')

      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        json: async () => ({ detail: 'Token inválido o expirado' }),
      })

      // Act & Assert
      await expect(authService.refreshToken()).rejects.toThrow('Token inválido o expirado')
    })
  })

  describe('getToken()', () => {
    it('debe retornar el token cuando existe en localStorage', () => {
      // Arrange
      localStorageMock.setItem('access_token', 'test-token-123')

      // Act
      const token = authService.getToken()

      // Assert
      expect(token).toBe('test-token-123')
    })

    it('debe retornar null cuando no hay token', () => {
      // Act
      const token = authService.getToken()

      // Assert
      expect(token).toBeNull()
    })
  })

  describe('getCurrentUser()', () => {
    it('debe retornar el usuario cuando existe en localStorage', () => {
      // Arrange
      const mockUser = {
        id: 1,
        email: 'test@example.com',
        nombre: 'Test User',
        es_activo: true,
        fecha_registro: '2025-10-10T10:00:00',
        ultimo_acceso: null,
      }
      localStorageMock.setItem('user', JSON.stringify(mockUser))

      // Act
      const user = authService.getCurrentUser()

      // Assert
      expect(user).toEqual(mockUser)
    })

    it('debe retornar null cuando no hay usuario', () => {
      // Act
      const user = authService.getCurrentUser()

      // Assert
      expect(user).toBeNull()
    })

    it('debe retornar null cuando el JSON del usuario es inválido', () => {
      // Arrange
      localStorageMock.setItem('user', 'invalid-json')

      // Act
      const user = authService.getCurrentUser()

      // Assert
      expect(user).toBeNull()
    })
  })

  describe('isAuthenticated()', () => {
    it('debe retornar true cuando hay token', () => {
      // Arrange
      localStorageMock.setItem('access_token', 'test-token-123')

      // Act
      const isAuth = authService.isAuthenticated()

      // Assert
      expect(isAuth).toBe(true)
    })

    it('debe retornar false cuando no hay token', () => {
      // Act
      const isAuth = authService.isAuthenticated()

      // Assert
      expect(isAuth).toBe(false)
    })
  })

  describe('getAuthHeaders()', () => {
    it('debe retornar headers con autorización cuando hay token', () => {
      // Arrange
      localStorageMock.setItem('access_token', 'test-token-123')

      // Act
      const headers = authService.getAuthHeaders()

      // Assert
      expect(headers).toEqual({
        'Content-Type': 'application/json',
        'Authorization': 'Bearer test-token-123',
      })
    })

    it('debe retornar headers sin autorización cuando no hay token', () => {
      // Act
      const headers = authService.getAuthHeaders()

      // Assert
      expect(headers).toEqual({
        'Content-Type': 'application/json',
      })
    })
  })

  describe('Integración entre métodos', () => {
    it('debe permitir login, verificar autenticación y hacer logout', async () => {
      // Arrange
      const mockLoginResponse = {
        access_token: 'test-token-123',
        token_type: 'bearer',
        user: {
          id: 1,
          email: 'test@example.com',
          nombre: 'Test User',
          es_activo: true,
          fecha_registro: '2025-10-10T10:00:00',
          ultimo_acceso: null,
        },
      }

      ;(global.fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockLoginResponse,
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ message: 'Logout exitoso' }),
        })

      // Act - Login
      await authService.login({
        email: 'test@example.com',
        password: 'Password123',
      })

      // Assert - Usuario autenticado
      expect(authService.isAuthenticated()).toBe(true)
      expect(authService.getCurrentUser()).toEqual(mockLoginResponse.user)
      expect(authService.getToken()).toBe('test-token-123')

      // Act - Logout
      await authService.logout()

      // Assert - Usuario no autenticado
      expect(authService.isAuthenticated()).toBe(false)
      expect(authService.getCurrentUser()).toBeNull()
      expect(authService.getToken()).toBeNull()
    })
  })
})
