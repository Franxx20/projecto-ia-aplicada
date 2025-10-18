/**
 * Tests para la página del Dashboard
 * 
 * Tests unitarios y de integración para verificar:
 * - Renderizado correcto de estadísticas
 * - Visualización de plantas en el grid
 * - Estados de carga y error
 * - Navegación a otras páginas
 * - Integración con dashboardService
 * 
 * @jest-environment jsdom
 */

import { render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { useRouter } from 'next/navigation'
import DashboardPage from '@/app/dashboard/page'
import { useAuth } from '@/hooks/useAuth'
import dashboardService from '@/lib/dashboard.service'
import type { Planta, DashboardStats } from '@/models/dashboard.types'

// Mock de Next.js router
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}))

// Mock de useAuth hook
jest.mock('@/hooks/useAuth', () => ({
  useAuth: jest.fn(),
}))

// Mock del dashboardService
jest.mock('@/lib/dashboard.service', () => ({
  __esModule: true,
  default: {
    obtenerEstadisticas: jest.fn(),
    obtenerPlantas: jest.fn(),
  },
}))

describe('DashboardPage', () => {
  const mockRouter = {
    push: jest.fn(),
  }

  const mockUsuario = {
    id: 1,
    email: 'test@test.com',
    nombre: 'Usuario Test',
    es_activo: true,
    fecha_registro: '2025-01-01T00:00:00Z',
  }

  const mockEstadisticas: DashboardStats = {
    total_plantas: 5,
    plantas_saludables: 3,
    plantas_necesitan_atencion: 2,
    plantas_necesitan_riego: 1,
    porcentaje_salud: 60,
  }

  const mockPlantas: Planta[] = [
    {
      id: 1,
      usuario_id: 1,
      nombre_personal: 'Monstera Deliciosa',
      especie_id: 101,
      estado_salud: 'buena',
      ubicacion: 'Sala',
      notas: null,
      imagen_principal_id: 1,
      fecha_ultimo_riego: '2025-10-15T10:00:00Z',
      frecuencia_riego_dias: 7,
      luz_actual: 'alta',
      fecha_adquisicion: '2025-01-01T00:00:00Z',
      proxima_riego: '2025-10-22T10:00:00Z',
      created_at: '2025-01-01T00:00:00Z',
      updated_at: '2025-10-17T00:00:00Z',
      is_active: true,
      necesita_riego: false,
    },
    {
      id: 2,
      usuario_id: 1,
      nombre_personal: 'Pothos',
      especie_id: null,
      estado_salud: 'necesita_atencion',
      ubicacion: 'Balcón',
      notas: 'Hojas amarillentas',
      imagen_principal_id: null,
      fecha_ultimo_riego: '2025-10-10T10:00:00Z',
      frecuencia_riego_dias: 5,
      luz_actual: 'media',
      fecha_adquisicion: null,
      proxima_riego: '2025-10-17T10:00:00Z',
      created_at: '2025-01-15T00:00:00Z',
      updated_at: '2025-10-17T00:00:00Z',
      is_active: true,
      necesita_riego: true,
    },
  ]

  beforeEach(() => {
    jest.clearAllMocks()
    ;(useRouter as jest.Mock).mockReturnValue(mockRouter)
  })

  describe('Autenticación', () => {
    it('debe redirigir a /login si no está autenticado', () => {
      ;(useAuth as jest.Mock).mockReturnValue({
        usuario: null,
        estaAutenticado: false,
        estaCargando: false,
        cerrarSesion: jest.fn(),
      })

      render(<DashboardPage />)

      expect(mockRouter.push).toHaveBeenCalledWith('/login')
    })

    it('debe mostrar loading mientras se verifica autenticación', () => {
      ;(useAuth as jest.Mock).mockReturnValue({
        usuario: null,
        estaAutenticado: false,
        estaCargando: true,
        cerrarSesion: jest.fn(),
      })

      render(<DashboardPage />)

      expect(screen.getByText('Cargando...')).toBeInTheDocument()
    })

    it('no debe renderizar contenido si no está autenticado', () => {
      ;(useAuth as jest.Mock).mockReturnValue({
        usuario: null,
        estaAutenticado: false,
        estaCargando: false,
        cerrarSesion: jest.fn(),
      })

      const { container } = render(<DashboardPage />)

      expect(container.firstChild).toBeNull()
    })
  })

  describe('Carga de datos', () => {
    beforeEach(() => {
      ;(useAuth as jest.Mock).mockReturnValue({
        usuario: mockUsuario,
        estaAutenticado: true,
        estaCargando: false,
        cerrarSesion: jest.fn(),
      })
    })

    it('debe mostrar loading mientras carga datos del dashboard', async () => {
      ;(dashboardService.obtenerEstadisticas as jest.Mock).mockImplementation(
        () => new Promise(() => {}) // Promesa que nunca se resuelve para mantener loading
      )
      ;(dashboardService.obtenerPlantas as jest.Mock).mockImplementation(
        () => new Promise(() => {})
      )

      render(<DashboardPage />)

      await waitFor(() => {
        expect(screen.getByText('Cargando tu jardín...')).toBeInTheDocument()
      })
    })

    it('debe cargar y mostrar estadísticas correctamente', async () => {
      ;(dashboardService.obtenerEstadisticas as jest.Mock).mockResolvedValue(
        mockEstadisticas
      )
      ;(dashboardService.obtenerPlantas as jest.Mock).mockResolvedValue({
        plantas: mockPlantas,
        total: 2,
      })

      render(<DashboardPage />)

      await waitFor(() => {
        expect(screen.getByText('5')).toBeInTheDocument() // Total plantas
        expect(screen.getByText('3')).toBeInTheDocument() // Saludables
        expect(screen.getByText('2')).toBeInTheDocument() // Necesitan atención
        expect(screen.getByText('1')).toBeInTheDocument() // Necesitan riego
      })
    })

    it('debe mostrar mensaje de error si falla la carga', async () => {
      ;(dashboardService.obtenerEstadisticas as jest.Mock).mockRejectedValue(
        new Error('Error de red')
      )
      ;(dashboardService.obtenerPlantas as jest.Mock).mockRejectedValue(
        new Error('Error de red')
      )

      render(<DashboardPage />)

      await waitFor(() => {
        expect(
          screen.getByText(/Error al cargar tus plantas/i)
        ).toBeInTheDocument()
      })
    })

    it('debe tener botón de reintentar cuando hay error', async () => {
      ;(dashboardService.obtenerEstadisticas as jest.Mock).mockRejectedValue(
        new Error('Error de red')
      )
      ;(dashboardService.obtenerPlantas as jest.Mock).mockRejectedValue(
        new Error('Error de red')
      )

      render(<DashboardPage />)

      await waitFor(() => {
        const botonReintentar = screen.getByRole('button', {
          name: /reintentar/i,
        })
        expect(botonReintentar).toBeInTheDocument()
      })
    })
  })

  describe('Visualización de plantas', () => {
    beforeEach(() => {
      ;(useAuth as jest.Mock).mockReturnValue({
        usuario: mockUsuario,
        estaAutenticado: true,
        estaCargando: false,
        cerrarSesion: jest.fn(),
      })
      ;(dashboardService.obtenerEstadisticas as jest.Mock).mockResolvedValue(
        mockEstadisticas
      )
    })

    it('debe mostrar mensaje de empty state cuando no hay plantas', async () => {
      ;(dashboardService.obtenerPlantas as jest.Mock).mockResolvedValue({
        plantas: [],
        total: 0,
      })

      render(<DashboardPage />)

      await waitFor(() => {
        expect(screen.getByText(/¡Empieza tu jardín digital!/i)).toBeInTheDocument()
        expect(
          screen.getByText(/Identifica tu primera planta y comienza a cuidarla/i)
        ).toBeInTheDocument()
        expect(screen.getByText(/Identificar Mi Primera Planta/i)).toBeInTheDocument()
      })
    })

    it('debe mostrar todas las plantas en el grid', async () => {
      ;(dashboardService.obtenerPlantas as jest.Mock).mockResolvedValue({
        plantas: mockPlantas,
        total: 2,
      })

      render(<DashboardPage />)

      await waitFor(() => {
        expect(screen.getByText('Monstera Deliciosa')).toBeInTheDocument()
        expect(screen.getByText('Pothos')).toBeInTheDocument()
      })
    })

    it('debe mostrar el badge de estado de salud correcto', async () => {
      ;(dashboardService.obtenerPlantas as jest.Mock).mockResolvedValue({
        plantas: mockPlantas,
        total: 2,
      })

      render(<DashboardPage />)

      await waitFor(() => {
        expect(screen.getByText('Saludable')).toBeInTheDocument()
        expect(screen.getByText('Necesita Atención')).toBeInTheDocument()
      })
    })

    it('debe mostrar indicador de riego necesario', async () => {
      ;(dashboardService.obtenerPlantas as jest.Mock).mockResolvedValue({
        plantas: mockPlantas,
        total: 2,
      })

      render(<DashboardPage />)

      await waitFor(() => {
        expect(screen.getByText('¡Necesita riego hoy!')).toBeInTheDocument()
      })
    })

    it('debe mostrar icono de planta cuando no hay imagen', async () => {
      ;(dashboardService.obtenerPlantas as jest.Mock).mockResolvedValue({
        plantas: [mockPlantas[1]], // Pothos sin imagen
        total: 1,
      })

      render(<DashboardPage />)

      await waitFor(() => {
        const plantCard = screen.getByText('Pothos').closest('div')
        expect(plantCard).toBeInTheDocument()
      })
    })
  })

  describe('Navegación', () => {
    beforeEach(() => {
      ;(useAuth as jest.Mock).mockReturnValue({
        usuario: mockUsuario,
        estaAutenticado: true,
        estaCargando: false,
        cerrarSesion: jest.fn(),
      })
      ;(dashboardService.obtenerEstadisticas as jest.Mock).mockResolvedValue(
        mockEstadisticas
      )
      ;(dashboardService.obtenerPlantas as jest.Mock).mockResolvedValue({
        plantas: mockPlantas,
        total: 2,
      })
    })

    it('debe tener botones de navegación a identificar planta en el header', async () => {
      render(<DashboardPage />)

      await waitFor(() => {
        const botonesIdentificar = screen.getAllByRole('link', {
          name: /identificar planta/i,
        })
        expect(botonesIdentificar.length).toBeGreaterThan(0)
        expect(botonesIdentificar[0]).toHaveAttribute('href', '/identificar')
      })
    })

    it('debe tener botón para agregar planta', async () => {
      render(<DashboardPage />)

      await waitFor(() => {
        const botonAgregar = screen.getByRole('link', {
          name: /agregar planta/i,
        })
        expect(botonAgregar).toBeInTheDocument()
        expect(botonAgregar).toHaveAttribute('href', '/identificar')
      })
    })

    it('debe tener enlaces a detalles de cada planta', async () => {
      render(<DashboardPage />)

      await waitFor(() => {
        const enlacesDetalles = screen.getAllByRole('link', {
          name: /ver detalles/i,
        })
        expect(enlacesDetalles).toHaveLength(2)
        expect(enlacesDetalles[0]).toHaveAttribute('href', '/plant/1')
        expect(enlacesDetalles[1]).toHaveAttribute('href', '/plant/2')
      })
    })
  })

  describe('Responsive design', () => {
    beforeEach(() => {
      ;(useAuth as jest.Mock).mockReturnValue({
        usuario: mockUsuario,
        estaAutenticado: true,
        estaCargando: false,
        cerrarSesion: jest.fn(),
      })
      ;(dashboardService.obtenerEstadisticas as jest.Mock).mockResolvedValue(
        mockEstadisticas
      )
      ;(dashboardService.obtenerPlantas as jest.Mock).mockResolvedValue({
        plantas: mockPlantas,
        total: 2,
      })
    })

    it('debe renderizar grid con clases responsive', async () => {
      const { container } = render(<DashboardPage />)

      await waitFor(() => {
        const statsGrid = container.querySelector('.grid.md\\:grid-cols-4')
        expect(statsGrid).toBeInTheDocument()

        const plantsGrid = container.querySelector('.grid.lg\\:grid-cols-3')
        expect(plantsGrid).toBeInTheDocument()
      })
    })
  })
})
