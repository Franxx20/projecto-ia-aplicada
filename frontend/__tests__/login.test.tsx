/**
 * Tests para la página de Login/Registro
 * 
 * Prueba la funcionalidad de autenticación y registro de usuarios
 * 
 * @author GitHub Copilot
 * @date 2025-10-10
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import '@testing-library/jest-dom'
import LoginPage from '@/app/login/page'

// Mock del router de Next.js
const mockPush = vi.fn()
vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: mockPush,
  }),
}))

// Mock de fetch global
global.fetch = vi.fn()

describe('LoginPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
  })

  describe('Renderizado inicial', () => {
    it('debe renderizar el formulario de login por defecto', () => {
      render(<LoginPage />)
      
      expect(screen.getByText('Bienvenido de Nuevo')).toBeInTheDocument()
      expect(screen.getByText('Inicia sesión para continuar cuidando tus plantas')).toBeInTheDocument()
      expect(screen.getByLabelText('Email')).toBeInTheDocument()
      expect(screen.getByLabelText('Contraseña')).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /iniciar sesión/i })).toBeInTheDocument()
    })

    it('debe cambiar a modo registro al hacer clic en "Regístrate"', () => {
      render(<LoginPage />)
      
      const registerLink = screen.getByRole('button', { name: /regístrate/i })
      fireEvent.click(registerLink)
      
      expect(screen.getByText('Crear Cuenta')).toBeInTheDocument()
      expect(screen.getByText('Comienza tu viaje en el cuidado de plantas hoy')).toBeInTheDocument()
      expect(screen.getByLabelText('Nombre Completo')).toBeInTheDocument()
    })
  })

  describe('Formulario de Login', () => {
    it('debe validar campos requeridos', async () => {
      render(<LoginPage />)
      
      const submitButton = screen.getByRole('button', { name: /iniciar sesión/i })
      fireEvent.click(submitButton)
      
      // HTML5 validation debería prevenir el submit
      expect(mockPush).not.toHaveBeenCalled()
    })

    it('debe manejar login exitoso', async () => {
      const mockResponse = {
        access_token: 'test-token-123',
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

      ;(global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      })

      render(<LoginPage />)
      
      const emailInput = screen.getByLabelText('Email')
      const passwordInput = screen.getByLabelText('Contraseña')
      const submitButton = screen.getByRole('button', { name: /iniciar sesión/i })

      fireEvent.change(emailInput, { target: { value: 'test@example.com' } })
      fireEvent.change(passwordInput, { target: { value: 'Password123' } })
      fireEvent.click(submitButton)

      await waitFor(() => {
        expect(localStorage.getItem('access_token')).toBe('test-token-123')
        expect(mockPush).toHaveBeenCalledWith('/dashboard')
      })
    })

    it('debe manejar errores de login', async () => {
      ;(global.fetch as any).mockResolvedValueOnce({
        ok: false,
        json: async () => ({ detail: 'Credenciales inválidas' }),
      })

      render(<LoginPage />)
      
      const emailInput = screen.getByLabelText('Email')
      const passwordInput = screen.getByLabelText('Contraseña')
      const submitButton = screen.getByRole('button', { name: /iniciar sesión/i })

      fireEvent.change(emailInput, { target: { value: 'wrong@example.com' } })
      fireEvent.change(passwordInput, { target: { value: 'wrongpassword' } })
      fireEvent.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText('Credenciales inválidas')).toBeInTheDocument()
      })
    })
  })

  describe('Formulario de Registro', () => {
    beforeEach(() => {
      render(<LoginPage />)
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

      ;(global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      })

      // Mock de window.alert
      const alertMock = vi.spyOn(window, 'alert').mockImplementation(() => {})

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
      ;(global.fetch as any).mockResolvedValueOnce({
        ok: false,
        json: async () => ({ detail: 'El email ya está registrado' }),
      })

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
      })
    })
  })

  describe('Estados de carga', () => {
    it('debe deshabilitar el botón durante el login', async () => {
      ;(global.fetch as any).mockImplementation(() => 
        new Promise(resolve => setTimeout(() => resolve({ ok: true, json: async () => ({}) }), 100))
      )

      render(<LoginPage />)
      
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
