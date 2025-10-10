/**
 * Tests para la página de Login/Registro
 * 
 * Prueba la funcionalidad de autenticación y registro de usuarios
 * 
 * @author GitHub Copilot
 * @date 2025-10-10
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import '@testing-library/jest-dom'
import LoginPage from '@/app/login/page'
import { AuthProvider } from '@/contexts/AuthContext'
import { authService } from '@/lib/auth.service'

// Mock del router de Next.js
const mockPush = jest.fn()
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: mockPush,
  }),
}))

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

// Mock de fetch global
global.fetch = jest.fn()

// Helper para renderizar con AuthProvider
const renderWithAuth = (component: React.ReactElement) => {
  return render(
    <AuthProvider>
      {component}
    </AuthProvider>
  )
}

describe('LoginPage', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    localStorage.clear()
  })

  describe('Renderizado inicial', () => {
    it('debe renderizar el formulario de login por defecto', async () => {
      renderWithAuth(<LoginPage />)
      
      await waitFor(() => {
        expect(screen.getByText('Bienvenido de Nuevo')).toBeInTheDocument()
      })
      
      expect(screen.getByText('Inicia sesión para continuar cuidando tus plantas')).toBeInTheDocument()
      expect(screen.getByLabelText('Email')).toBeInTheDocument()
      expect(screen.getByLabelText('Contraseña')).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /iniciar sesión/i })).toBeInTheDocument()
    })

    it('debe cambiar a modo registro al hacer clic en "Regístrate"', async () => {
      renderWithAuth(<LoginPage />)
      
      await waitFor(() => {
        expect(screen.getByRole('button', { name: /regístrate/i })).toBeInTheDocument()
      })
      
      const registerLink = screen.getByRole('button', { name: /regístrate/i })
      fireEvent.click(registerLink)
      
      // Verificar que cambió a modo registro checando el botón de submit
      expect(screen.getByRole('button', { name: /crear cuenta/i })).toBeInTheDocument()
      expect(screen.getByText('Comienza tu viaje en el cuidado de plantas hoy')).toBeInTheDocument()
      expect(screen.getByLabelText('Nombre Completo')).toBeInTheDocument()
    })
  })

  describe('Formulario de Login', () => {
    it('debe validar campos requeridos', async () => {
      renderWithAuth(<LoginPage />)
      
      const submitButton = screen.getByRole('button', { name: /iniciar sesión/i })
      fireEvent.click(submitButton)
      
      // HTML5 validation debería prevenir el submit
      expect(mockPush).not.toHaveBeenCalled()
    })

    it('debe manejar login exitoso', async () => {
      const mockResponse = {
        access_token: 'test-token-123',
        refresh_token: 'test-refresh-123',
        token_type: 'bearer',
        user: {
          id: 1,
          email: 'test@example.com',
          nombre: 'Test User',
          es_activo: true,
          fecha_registro: '2025-01-01',
          ultimo_acceso: null,
        },
      }

      // Mock del authService.login
      ;(authService.login as jest.Mock).mockResolvedValueOnce(mockResponse)

      renderWithAuth(<LoginPage />)
      
      const emailInput = screen.getByLabelText('Email')
      const passwordInput = screen.getByLabelText('Contraseña')
      const submitButton = screen.getByRole('button', { name: /iniciar sesión/i })

      fireEvent.change(emailInput, { target: { value: 'test@example.com' } })
      fireEvent.change(passwordInput, { target: { value: 'Password123' } })
      fireEvent.click(submitButton)

      await waitFor(() => {
        expect(authService.login).toHaveBeenCalledWith({ email: 'test@example.com', password: 'Password123' })
        expect(mockPush).toHaveBeenCalledWith('/dashboard')
      }, { timeout: 3000 })
    })

    it('debe manejar errores de login', async () => {
      // Mock del authService.login que lanza error
      ;(authService.login as jest.Mock).mockRejectedValueOnce(new Error('Credenciales inválidas'))

      renderWithAuth(<LoginPage />)
      
      const emailInput = screen.getByLabelText('Email')
      const passwordInput = screen.getByLabelText('Contraseña')
      const submitButton = screen.getByRole('button', { name: /iniciar sesión/i })

      fireEvent.change(emailInput, { target: { value: 'wrong@example.com' } })
      fireEvent.change(passwordInput, { target: { value: 'wrongpassword' } })
      fireEvent.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText('Credenciales inválidas')).toBeInTheDocument()
      }, { timeout: 3000 })
    })
  })

  describe('Formulario de Registro', () => {
    beforeEach(() => {
      renderWithAuth(<LoginPage />)
      const registerLink = screen.getByRole('button', { name: /regístrate/i })
      fireEvent.click(registerLink)
    })

    it('debe mostrar campos adicionales en modo registro', () => {
      expect(screen.getByLabelText('Nombre Completo')).toBeInTheDocument()
      expect(screen.getByText(/mínimo 8 caracteres/i)).toBeInTheDocument()
    })

    it('debe manejar registro exitoso', async () => {
      const mockResponse = {
        id: 1,
        email: 'newuser@example.com',
        nombre: 'New User',
        es_activo: true,
        fecha_registro: '2025-01-10',
        ultimo_acceso: null,
      }

      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      })

      // Mock de window.alert
      const alertMock = jest.spyOn(window, 'alert').mockImplementation(() => {})

      const nombreInput = screen.getByLabelText('Nombre Completo')
      const emailInput = screen.getByLabelText('Email')
      const passwordInput = screen.getByLabelText('Contraseña')
      const submitButton = screen.getByRole('button', { name: /crear cuenta/i })

      fireEvent.change(nombreInput, { target: { value: 'New User' } })
      fireEvent.change(emailInput, { target: { value: 'newuser@example.com' } })
      fireEvent.change(passwordInput, { target: { value: 'Password123' } })
      fireEvent.click(submitButton)

      await waitFor(() => {
        expect(alertMock).toHaveBeenCalledWith('Registro exitoso. Por favor, inicie sesión.')
        expect(screen.getByText('Bienvenido de Nuevo')).toBeInTheDocument()
      })

      alertMock.mockRestore()
    })

    it('debe manejar errores de registro', async () => {
      // Mock del authService.register que lanza error
      ;(authService.register as jest.Mock).mockRejectedValueOnce(new Error('El email ya está registrado'))

      const nombreInput = screen.getByLabelText('Nombre Completo')
      const emailInput = screen.getByLabelText('Email')
      const passwordInput = screen.getByLabelText('Contraseña')
      const submitButton = screen.getByRole('button', { name: /crear cuenta/i })

      fireEvent.change(nombreInput, { target: { value: 'Test User' } })
      fireEvent.change(emailInput, { target: { value: 'existing@example.com' } })
      fireEvent.change(passwordInput, { target: { value: 'Password123' } })
      fireEvent.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText('El email ya está registrado')).toBeInTheDocument()
      }, { timeout: 3000 })
    })
  })

  describe('Estados de carga', () => {
    it('debe deshabilitar el botón durante el login', async () => {
      ;(global.fetch as jest.Mock).mockImplementation(() => 
        new Promise(resolve => setTimeout(() => resolve({ ok: true, json: async () => ({}) }), 100))
      )

      renderWithAuth(<LoginPage />)
      
      const emailInput = screen.getByLabelText('Email')
      const passwordInput = screen.getByLabelText('Contraseña')
      const submitButton = screen.getByRole('button', { name: /iniciar sesión/i })

      fireEvent.change(emailInput, { target: { value: 'test@example.com' } })
      fireEvent.change(passwordInput, { target: { value: 'Password123' } })
      fireEvent.click(submitButton)

      expect(submitButton).toBeDisabled()
      expect(screen.getByText('Procesando...')).toBeInTheDocument()
    })
  })
})
