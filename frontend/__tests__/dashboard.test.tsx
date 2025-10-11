/**
 * Tests para la página del Dashboard
 * 
 * Verifica que el dashboard esté protegido y solo sea accesible
 * para usuarios autenticados. También verifica la funcionalidad
 * del botón de cerrar sesión.
 * 
 * @author GitHub Copilot
 * @date 2025-10-10
 */

import React from 'react'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { useRouter } from 'next/navigation'
import DashboardPage from '@/app/dashboard/page'
import { useAuth } from '@/hooks/useAuth'

// Mock de next/navigation
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}))

// Mock del hook useAuth
jest.mock('@/hooks/useAuth', () => ({
  useAuth: jest.fn(),
}))

describe('DashboardPage', () => {
  const mockPush = jest.fn()
  const mockCerrarSesion = jest.fn()

  beforeEach(() => {
    jest.clearAllMocks()
    ;(useRouter as jest.Mock).mockReturnValue({
      push: mockPush,
    })
  })

  describe('Protección de ruta', () => {
    it('debe redirigir a /login si el usuario no está autenticado', async () => {
      // Arrange: Usuario no autenticado
      ;(useAuth as jest.Mock).mockReturnValue({
        usuario: null,
        estaAutenticado: false,
        estaCargando: false,
        cerrarSesion: mockCerrarSesion,
      })

      // Act: Renderizar el componente
      render(<DashboardPage />)

      // Assert: Debe redirigir a login
      await waitFor(() => {
        expect(mockPush).toHaveBeenCalledWith('/login')
      })
    })

    it('debe mostrar loading mientras se verifica la autenticación', () => {
      // Arrange: Estado de carga
      ;(useAuth as jest.Mock).mockReturnValue({
        usuario: null,
        estaAutenticado: false,
        estaCargando: true,
        cerrarSesion: mockCerrarSesion,
      })

      // Act: Renderizar el componente
      render(<DashboardPage />)

      // Assert: Debe mostrar mensaje de carga
      expect(screen.getByText('Cargando...')).toBeInTheDocument()
    })

    it('debe renderizar el dashboard si el usuario está autenticado', () => {
      // Arrange: Usuario autenticado
      const mockUsuario = {
        id: 1,
        email: 'test@example.com',
        nombre: 'Usuario Test',
        es_activo: true,
        fecha_registro: '2025-01-01T00:00:00Z',
        ultimo_acceso: '2025-01-10T00:00:00Z',
      }

      ;(useAuth as jest.Mock).mockReturnValue({
        usuario: mockUsuario,
        estaAutenticado: true,
        estaCargando: false,
        cerrarSesion: mockCerrarSesion,
      })

      // Act: Renderizar el componente
      render(<DashboardPage />)

      // Assert: Debe mostrar el contenido del dashboard
      expect(screen.getByText(/¡Hola, Usuario Test!/)).toBeInTheDocument()
      expect(screen.getByText('Hello World')).toBeInTheDocument()
    })

    it('no debe renderizar nada si no está autenticado y no está cargando', () => {
      // Arrange: Usuario no autenticado y no cargando
      ;(useAuth as jest.Mock).mockReturnValue({
        usuario: null,
        estaAutenticado: false,
        estaCargando: false,
        cerrarSesion: mockCerrarSesion,
      })

      // Act: Renderizar el componente
      const { container } = render(<DashboardPage />)

      // Assert: El contenedor debe estar vacío (excepto por el script de next)
      // No debe mostrar el dashboard ni el loading
      expect(container.querySelector('main')).not.toBeInTheDocument()
      expect(screen.queryByText('Hello World')).not.toBeInTheDocument()
    })
  })

  describe('Información del usuario', () => {
    const mockUsuario = {
      id: 1,
      email: 'test@example.com',
      nombre: 'Juan Pérez',
      es_activo: true,
      fecha_registro: '2025-01-15T10:30:00Z',
      ultimo_acceso: '2025-01-20T15:45:00Z',
    }

    beforeEach(() => {
      ;(useAuth as jest.Mock).mockReturnValue({
        usuario: mockUsuario,
        estaAutenticado: true,
        estaCargando: false,
        cerrarSesion: mockCerrarSesion,
      })
    })

    it('debe mostrar el nombre del usuario en el header', () => {
      // Act: Renderizar el componente
      render(<DashboardPage />)

      // Assert: El nombre debe aparecer en el header
      const nombreElements = screen.getAllByText('Juan Pérez')
      expect(nombreElements.length).toBeGreaterThan(0)
    })

    it('debe mostrar el email del usuario', () => {
      // Act: Renderizar el componente
      render(<DashboardPage />)

      // Assert: El email debe estar visible
      expect(screen.getByText('test@example.com')).toBeInTheDocument()
    })

    it('debe mostrar el estado "Activo" para usuarios activos', () => {
      // Act: Renderizar el componente
      render(<DashboardPage />)

      // Assert: Debe mostrar "Activo"
      expect(screen.getByText('Activo')).toBeInTheDocument()
    })

    it('debe mostrar el estado "Inactivo" para usuarios inactivos', () => {
      // Arrange: Usuario inactivo
      const usuarioInactivo = { ...mockUsuario, es_activo: false }
      ;(useAuth as jest.Mock).mockReturnValue({
        usuario: usuarioInactivo,
        estaAutenticado: true,
        estaCargando: false,
        cerrarSesion: mockCerrarSesion,
      })

      // Act: Renderizar el componente
      render(<DashboardPage />)

      // Assert: Debe mostrar "Inactivo"
      expect(screen.getByText('Inactivo')).toBeInTheDocument()
    })

    it('debe formatear correctamente la fecha de registro', () => {
      // Act: Renderizar el componente
      render(<DashboardPage />)

      // Assert: La fecha debe estar formateada en español
      // 2025-01-15 debe mostrarse como "15 de enero de 2025"
      expect(screen.getByText(/15 de enero de 2025/)).toBeInTheDocument()
    })
  })

  describe('Funcionalidad de cerrar sesión', () => {
    const mockUsuario = {
      id: 1,
      email: 'test@example.com',
      nombre: 'Usuario Test',
      es_activo: true,
      fecha_registro: '2025-01-01T00:00:00Z',
      ultimo_acceso: '2025-01-10T00:00:00Z',
    }

    beforeEach(() => {
      ;(useAuth as jest.Mock).mockReturnValue({
        usuario: mockUsuario,
        estaAutenticado: true,
        estaCargando: false,
        cerrarSesion: mockCerrarSesion,
      })
    })

    it('debe mostrar el botón de cerrar sesión', () => {
      // Act: Renderizar el componente
      render(<DashboardPage />)

      // Assert: El botón debe estar visible
      expect(screen.getByText('Cerrar Sesión')).toBeInTheDocument()
    })

    it('debe llamar a cerrarSesion cuando se hace clic en el botón', async () => {
      // Arrange: Mock resuelto exitosamente
      mockCerrarSesion.mockResolvedValue(undefined)

      // Act: Renderizar y hacer clic en el botón
      render(<DashboardPage />)
      const botonCerrarSesion = screen.getByText('Cerrar Sesión')
      fireEvent.click(botonCerrarSesion)

      // Assert: Debe llamar a la función cerrarSesion
      await waitFor(() => {
        expect(mockCerrarSesion).toHaveBeenCalledTimes(1)
      })
    })

    it('debe manejar errores al cerrar sesión sin romper la UI', async () => {
      // Arrange: Mock que falla
      const mockError = new Error('Error de red')
      mockCerrarSesion.mockRejectedValue(mockError)
      
      // Espiar console.error
      const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation()

      // Act: Renderizar y hacer clic en el botón
      render(<DashboardPage />)
      const botonCerrarSesion = screen.getByText('Cerrar Sesión')
      fireEvent.click(botonCerrarSesion)

      // Assert: Debe manejar el error y loguearlo
      await waitFor(() => {
        expect(mockCerrarSesion).toHaveBeenCalledTimes(1)
        expect(consoleErrorSpy).toHaveBeenCalledWith('Error al cerrar sesión:', mockError)
      })

      // Cleanup
      consoleErrorSpy.mockRestore()
    })
  })

  describe('Elementos de UI', () => {
    const mockUsuario = {
      id: 1,
      email: 'test@example.com',
      nombre: 'Usuario Test',
      es_activo: true,
      fecha_registro: '2025-01-01T00:00:00Z',
      ultimo_acceso: '2025-01-10T00:00:00Z',
    }

    beforeEach(() => {
      ;(useAuth as jest.Mock).mockReturnValue({
        usuario: mockUsuario,
        estaAutenticado: true,
        estaCargando: false,
        cerrarSesion: mockCerrarSesion,
      })
    })

    it('debe mostrar el logo de Asistente Plantitas', () => {
      // Act: Renderizar el componente
      render(<DashboardPage />)

      // Assert: El texto del logo debe estar presente
      expect(screen.getByText('Asistente Plantitas')).toBeInTheDocument()
    })

    it('debe mostrar el mensaje de bienvenida', () => {
      // Act: Renderizar el componente
      render(<DashboardPage />)

      // Assert: Debe mostrar el mensaje de bienvenida
      expect(screen.getByText(/Bienvenido a tu dashboard/)).toBeInTheDocument()
    })

    it('debe mostrar el título de la card de información', () => {
      // Act: Renderizar el componente
      render(<DashboardPage />)

      // Assert: Debe mostrar el título de la card
      expect(screen.getByText('Información de tu cuenta')).toBeInTheDocument()
    })
  })

  describe('Accesibilidad', () => {
    const mockUsuario = {
      id: 1,
      email: 'test@example.com',
      nombre: 'Usuario Test',
      es_activo: true,
      fecha_registro: '2025-01-01T00:00:00Z',
      ultimo_acceso: '2025-01-10T00:00:00Z',
    }

    beforeEach(() => {
      ;(useAuth as jest.Mock).mockReturnValue({
        usuario: mockUsuario,
        estaAutenticado: true,
        estaCargando: false,
        cerrarSesion: mockCerrarSesion,
      })
    })

    it('el botón de cerrar sesión debe ser clickeable', () => {
      // Act: Renderizar el componente
      render(<DashboardPage />)
      const boton = screen.getByText('Cerrar Sesión').closest('button')

      // Assert: El botón debe existir y ser un elemento button
      expect(boton).toBeInTheDocument()
      expect(boton?.tagName).toBe('BUTTON')
    })

    it('debe tener una estructura semántica correcta con header y main', () => {
      // Act: Renderizar el componente
      const { container } = render(<DashboardPage />)

      // Assert: Debe tener elementos semánticos
      expect(container.querySelector('header')).toBeInTheDocument()
      expect(container.querySelector('main')).toBeInTheDocument()
    })
  })
})
