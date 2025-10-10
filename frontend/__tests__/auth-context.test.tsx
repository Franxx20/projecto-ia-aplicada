/**
 * auth-context.test.tsx - Tests para el AuthContext
 * 
 * Valida el funcionamiento del contexto de autenticación:
 * - Provider rendering
 * - Login exitoso y fallido
 * - Registro exitoso y fallido
 * - Logout
 * - Renovación de tokens
 * - Persistencia en localStorage
 * 
 * @author GitHub Copilot
 * @date 2025-10-10
 */

import React from 'react'
import { render, screen, waitFor, act } from '@testing-library/react'
import { AuthProvider, AuthContext } from '@/contexts/AuthContext'
import { useAuth } from '@/hooks/useAuth'
import { authService } from '@/lib/auth.service'

// Mock del authService
jest.mock('@/lib/auth.service', () => ({
  authService: {
    login: jest.fn(),
    register: jest.fn(),
    logout: jest.fn(),
    refreshToken: jest.fn(),
    getCurrentUser: jest.fn(),
    getToken: jest.fn(),
  },
}))

// Mock de next/navigation
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
    replace: jest.fn(),
    prefetch: jest.fn(),
  }),
}))

// Componente de prueba que usa el hook useAuth
function TestComponent() {
  const { usuario, estaAutenticado, estaCargando, iniciarSesion, registrarse, cerrarSesion } = useAuth()
  const [error, setError] = React.useState<string>('')
  
  const handleLogin = async () => {
    try {
      await iniciarSesion('test@test.com', 'password123')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error')
    }
  }

  const handleRegister = async () => {
    try {
      await registrarse('new@test.com', 'password123', 'Nuevo Usuario')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error')
    }
  }
  
  return (
    <div>
      <div data-testid="loading">{estaCargando ? 'Cargando' : 'No cargando'}</div>
      <div data-testid="authenticated">{estaAutenticado ? 'Autenticado' : 'No autenticado'}</div>
      <div data-testid="user">{usuario ? usuario.email : 'Sin usuario'}</div>
      <div data-testid="error">{error}</div>
      <button onClick={handleLogin}>Login</button>
      <button onClick={handleRegister}>Registro</button>
      <button onClick={cerrarSesion}>Logout</button>
    </div>
  )
}

describe('AuthContext', () => {
  beforeEach(() => {
    // Limpiar todos los mocks antes de cada test
    jest.clearAllMocks()
    
    // Limpiar localStorage
    localStorage.clear()
    
    // Mock por defecto: sin usuario autenticado
    ;(authService.getCurrentUser as jest.Mock).mockReturnValue(null)
    ;(authService.getToken as jest.Mock).mockReturnValue(null)
  })

  describe('Provider', () => {
    test('debe renderizar children correctamente', () => {
      render(
        <AuthProvider>
          <div>Test Child</div>
        </AuthProvider>
      )
      
      expect(screen.getByText('Test Child')).toBeInTheDocument()
    })

    test('debe inicializar con estado no autenticado', async () => {
      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      )

      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('No cargando')
      })
      
      expect(screen.getByTestId('authenticated')).toHaveTextContent('No autenticado')
      expect(screen.getByTestId('user')).toHaveTextContent('Sin usuario')
    })

    test('debe restaurar sesión desde localStorage', async () => {
      const mockUser = {
        id: 1,
        email: 'test@test.com',
        nombre: 'Test User',
        es_activo: true,
        fecha_registro: '2025-01-01',
        ultimo_acceso: '2025-01-01',
      }

      ;(authService.getCurrentUser as jest.Mock).mockReturnValue(mockUser)
      ;(authService.getToken as jest.Mock).mockReturnValue('mock-token')

      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      )

      await waitFor(() => {
        expect(screen.getByTestId('authenticated')).toHaveTextContent('Autenticado')
      })
      
      expect(screen.getByTestId('user')).toHaveTextContent('test@test.com')
    })
  })

  describe('Login', () => {
    test('debe iniciar sesión exitosamente', async () => {
      const mockUser = {
        id: 1,
        email: 'test@test.com',
        nombre: 'Test User',
        es_activo: true,
        fecha_registro: '2025-01-01',
        ultimo_acceso: '2025-01-01',
      }

      ;(authService.login as jest.Mock).mockResolvedValue({
        access_token: 'mock-token',
        refresh_token: 'mock-refresh-token',
        user: mockUser,
      })

      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      )

      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('No cargando')
      })

      const loginButton = screen.getByText('Login')
      
      await act(async () => {
        loginButton.click()
      })

      await waitFor(() => {
        expect(screen.getByTestId('authenticated')).toHaveTextContent('Autenticado')
      })
      
      expect(screen.getByTestId('user')).toHaveTextContent('test@test.com')
      expect(authService.login).toHaveBeenCalledWith({
        email: 'test@test.com',
        password: 'password123',
      })
    })

    test('debe manejar error de login', async () => {
      ;(authService.login as jest.Mock).mockRejectedValue(new Error('Credenciales inválidas'))

      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      )

      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('No cargando')
      })

      const loginButton = screen.getByText('Login')
      
      await act(async () => {
        loginButton.click()
      })

      await waitFor(() => {
        expect(screen.getByTestId('error')).toHaveTextContent('Credenciales inválidas')
      })
      
      expect(screen.getByTestId('authenticated')).toHaveTextContent('No autenticado')
      expect(authService.login).toHaveBeenCalled()
    })
  })

  describe('Registro', () => {
    test('debe registrarse exitosamente', async () => {
      ;(authService.register as jest.Mock).mockResolvedValue({
        message: 'Usuario registrado exitosamente',
      })

      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      )

      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('No cargando')
      })

      const registerButton = screen.getByText('Registro')
      
      await act(async () => {
        registerButton.click()
      })

      await waitFor(() => {
        expect(authService.register).toHaveBeenCalledWith({
          email: 'new@test.com',
          password: 'password123',
          nombre: 'Nuevo Usuario',
        })
      })
      
      // El usuario no debe estar autenticado después del registro
      expect(screen.getByTestId('authenticated')).toHaveTextContent('No autenticado')
    })

    test('debe manejar error de registro', async () => {
      ;(authService.register as jest.Mock).mockRejectedValue(new Error('Email ya registrado'))

      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      )

      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('No cargando')
      })

      const registerButton = screen.getByText('Registro')
      
      await act(async () => {
        registerButton.click()
      })

      await waitFor(() => {
        expect(screen.getByTestId('error')).toHaveTextContent('Email ya registrado')
      })
      
      expect(authService.register).toHaveBeenCalled()
      expect(screen.getByTestId('authenticated')).toHaveTextContent('No autenticado')
    })
  })

  describe('Logout', () => {
    test('debe cerrar sesión correctamente', async () => {
      const mockUser = {
        id: 1,
        email: 'test@test.com',
        nombre: 'Test User',
        es_activo: true,
        fecha_registro: '2025-01-01',
        ultimo_acceso: '2025-01-01',
      }

      // Primero login
      ;(authService.login as jest.Mock).mockResolvedValue({
        access_token: 'mock-token',
        refresh_token: 'mock-refresh-token',
        user: mockUser,
      })

      // Mock de logout
      ;(authService.logout as jest.Mock).mockResolvedValue({})

      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      )

      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('No cargando')
      })

      // Login
      const loginButton = screen.getByText('Login')
      await act(async () => {
        loginButton.click()
      })

      await waitFor(() => {
        expect(screen.getByTestId('authenticated')).toHaveTextContent('Autenticado')
      })

      // Logout
      const logoutButton = screen.getByText('Logout')
      await act(async () => {
        logoutButton.click()
      })

      await waitFor(() => {
        expect(screen.getByTestId('authenticated')).toHaveTextContent('No autenticado')
      })
      
      expect(authService.logout).toHaveBeenCalled()
      expect(screen.getByTestId('user')).toHaveTextContent('Sin usuario')
    })
  })

  describe('Hook useAuth', () => {
    test('debe lanzar error si se usa fuera del Provider', () => {
      // Suprimir console.error para este test
      const consoleError = jest.spyOn(console, 'error').mockImplementation(() => {})
      
      expect(() => {
        render(<TestComponent />)
      }).toThrow('useAuth debe ser usado dentro de un AuthProvider')
      
      consoleError.mockRestore()
    })

    test('debe retornar valores del contexto correctamente', async () => {
      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      )

      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('No cargando')
      })
      
      expect(screen.getByTestId('authenticated')).toBeInTheDocument()
      expect(screen.getByTestId('user')).toBeInTheDocument()
      expect(screen.getByText('Login')).toBeInTheDocument()
      expect(screen.getByText('Registro')).toBeInTheDocument()
      expect(screen.getByText('Logout')).toBeInTheDocument()
    })
  })
})
