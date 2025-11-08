/**
 * Tests para la página de detalle de planta
 * 
 * Tests unitarios y de integración para verificar:
 * - Renderizado correcto de información de planta
 * - Funcionalidad de tabs (Care, Environment, Activity, Photos)
 * - Registro de riego
 * - Estados de carga y error
 * - Navegación y redirección
 * - Integración con dashboardService
 * 
 * @jest-environment jsdom
 */

import { render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { useRouter, useParams } from 'next/navigation'
import PlantDetailPage from '@/app/plant/[id]/page'
import { useAuth } from '@/hooks/useAuth'
import dashboardService from '@/lib/dashboard.service'
import type { Planta } from '@/models/dashboard.types'

// Mock de Next.js router
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
  useParams: jest.fn(),
}))

// Mock de useAuth hook
jest.mock('@/hooks/useAuth', () => ({
  useAuth: jest.fn(),
}))

// Mock del dashboardService
jest.mock('@/lib/dashboard.service', () => ({
  __esModule: true,
  default: {
    obtenerPlanta: jest.fn(),
    registrarRiego: jest.fn(),
  },
}))

// Mock de Carousel component
jest.mock('@/components/ui/carousel', () => ({
  Carousel: ({ children }: { children: React.ReactNode }) => <div data-testid="carousel">{children}</div>,
  CarouselContent: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  CarouselItem: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
}))

describe('PlantDetailPage', () => {
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

  const mockPlanta: Planta = {
    id: 1,
    usuario_id: 1,
    nombre_personal: 'Monstera Deliciosa',
    especie_id: 101,
    estado_salud: 'buena',
    ubicacion: 'Living Room - East Window',
    notas: 'Gift from mom. Growing beautifully with new leaves every month.',
    imagen_principal_id: 1,
    imagen_principal_url: 'https://example.com/monstera.jpg',
    fecha_ultimo_riego: '2025-11-05T10:00:00Z',
    frecuencia_riego_dias: 7,
    luz_actual: 'alta',
    fecha_adquisicion: '2025-03-15T00:00:00Z',
    proxima_riego: '2025-11-10T10:00:00Z',
    created_at: '2025-03-15T00:00:00Z',
    updated_at: '2025-11-07T00:00:00Z',
    is_active: true,
    necesita_riego: false,
  }

  const mockPlantaNecesitaRiego: Planta = {
    ...mockPlanta,
    id: 2,
    nombre_personal: 'Pothos Dorado',
    estado_salud: 'necesita_atencion',
    fecha_ultimo_riego: '2025-10-20T10:00:00Z',
    proxima_riego: '2025-11-06T10:00:00Z',
    necesita_riego: true,
    imagen_principal_url: null,
  }

  beforeEach(() => {
    jest.clearAllMocks()
    ;(useRouter as jest.Mock).mockReturnValue(mockRouter)
    ;(useParams as jest.Mock).mockReturnValue({ id: '1' })
  })

  describe('Autenticación y Seguridad', () => {
    it('debe redirigir a /login si no está autenticado', async () => {
      ;(useAuth as jest.Mock).mockReturnValue({
        usuario: null,
        estaAutenticado: false,
        estaCargando: false,
      })

      render(<PlantDetailPage />)

      await waitFor(() => {
        expect(mockRouter.push).toHaveBeenCalledWith('/login')
      })
    })

    it('debe mostrar loading mientras se verifica autenticación', () => {
      ;(useAuth as jest.Mock).mockReturnValue({
        usuario: null,
        estaAutenticado: false,
        estaCargando: true,
      })

      render(<PlantDetailPage />)

      expect(screen.getByText('Cargando planta...')).toBeInTheDocument()
    })

    it('no debe hacer fetch de datos si no hay ID de planta', async () => {
      ;(useParams as jest.Mock).mockReturnValue({ id: undefined })
      ;(useAuth as jest.Mock).mockReturnValue({
        usuario: mockUsuario,
        estaAutenticado: true,
        estaCargando: false,
      })

      render(<PlantDetailPage />)

      await waitFor(() => {
        expect(dashboardService.obtenerPlanta).not.toHaveBeenCalled()
      })
    })
  })

  describe('Carga de datos', () => {
    beforeEach(() => {
      ;(useAuth as jest.Mock).mockReturnValue({
        usuario: mockUsuario,
        estaAutenticado: true,
        estaCargando: false,
      })
    })

    it('debe mostrar loading mientras carga los datos de la planta', async () => {
      ;(dashboardService.obtenerPlanta as jest.Mock).mockImplementation(
        () => new Promise(() => {}) // Promesa que nunca se resuelve
      )

      render(<PlantDetailPage />)

      expect(screen.getByText('Cargando planta...')).toBeInTheDocument()
    })

    it('debe cargar y mostrar la información de la planta correctamente', async () => {
      ;(dashboardService.obtenerPlanta as jest.Mock).mockResolvedValue(mockPlanta)

      render(<PlantDetailPage />)

      await waitFor(() => {
        expect(screen.getByText('Monstera Deliciosa')).toBeInTheDocument()
        expect(screen.getByText('Living Room - East Window')).toBeInTheDocument()
        expect(screen.getByText(/Gift from mom/i)).toBeInTheDocument()
      })
    })

    it('debe mostrar mensaje de error si la planta no existe', async () => {
      ;(dashboardService.obtenerPlanta as jest.Mock).mockRejectedValue(
        new Error('Planta no encontrada')
      )

      render(<PlantDetailPage />)

      await waitFor(() => {
        expect(screen.getByText('Error')).toBeInTheDocument()
        expect(screen.getByText('Planta no encontrada')).toBeInTheDocument()
      })
    })

    it('debe tener botón de volver al dashboard cuando hay error', async () => {
      ;(dashboardService.obtenerPlanta as jest.Mock).mockRejectedValue(
        new Error('Error de red')
      )

      render(<PlantDetailPage />)

      await waitFor(() => {
        const botonVolver = screen.getByRole('link', {
          name: /volver al dashboard/i,
        })
        expect(botonVolver).toBeInTheDocument()
        expect(botonVolver).toHaveAttribute('href', '/dashboard')
      })
    })

    it('debe llamar a obtenerPlanta con el ID correcto', async () => {
      ;(useParams as jest.Mock).mockReturnValue({ id: '42' })
      ;(dashboardService.obtenerPlanta as jest.Mock).mockResolvedValue(mockPlanta)

      render(<PlantDetailPage />)

      await waitFor(() => {
        expect(dashboardService.obtenerPlanta).toHaveBeenCalledWith(42)
      })
    })
  })

  describe('Información Básica de la Planta', () => {
    beforeEach(() => {
      ;(useAuth as jest.Mock).mockReturnValue({
        usuario: mockUsuario,
        estaAutenticado: true,
        estaCargando: false,
      })
      ;(dashboardService.obtenerPlanta as jest.Mock).mockResolvedValue(mockPlanta)
    })

    it('debe mostrar el nombre de la planta', async () => {
      render(<PlantDetailPage />)

      await waitFor(() => {
        expect(screen.getByText('Monstera Deliciosa')).toBeInTheDocument()
      })
    })

    it('debe mostrar el badge de estado de salud correcto', async () => {
      render(<PlantDetailPage />)

      await waitFor(() => {
        expect(screen.getByText('Saludable')).toBeInTheDocument()
      })
    })

    it('debe mostrar el health score con barra de progreso', async () => {
      render(<PlantDetailPage />)

      await waitFor(() => {
        expect(screen.getByText('Health Score')).toBeInTheDocument()
        expect(screen.getByText(/\d+%/)).toBeInTheDocument()
      })
    })

    it('debe mostrar la ubicación de la planta', async () => {
      render(<PlantDetailPage />)

      await waitFor(() => {
        expect(screen.getByText('Living Room - East Window')).toBeInTheDocument()
      })
    })

    it('debe mostrar el nivel de luz actual', async () => {
      render(<PlantDetailPage />)

      await waitFor(() => {
        expect(screen.getByText(/Luz alta/i)).toBeInTheDocument()
      })
    })

    it('debe mostrar las notas de la planta si existen', async () => {
      render(<PlantDetailPage />)

      await waitFor(() => {
        expect(screen.getByText(/Gift from mom/i)).toBeInTheDocument()
      })
    })

    it('debe mostrar imagen placeholder cuando no hay imagen', async () => {
      ;(dashboardService.obtenerPlanta as jest.Mock).mockResolvedValue(
        mockPlantaNecesitaRiego
      )

      render(<PlantDetailPage />)

      await waitFor(() => {
        expect(screen.getByText('Pothos Dorado')).toBeInTheDocument()
      })
    })
  })

  describe('Sistema de Tabs', () => {
    beforeEach(() => {
      ;(useAuth as jest.Mock).mockReturnValue({
        usuario: mockUsuario,
        estaAutenticado: true,
        estaCargando: false,
      })
      ;(dashboardService.obtenerPlanta as jest.Mock).mockResolvedValue(mockPlanta)
    })

    it('debe mostrar las 4 tabs principales', async () => {
      render(<PlantDetailPage />)

      await waitFor(() => {
        expect(screen.getByRole('tab', { name: /care/i })).toBeInTheDocument()
        expect(screen.getByRole('tab', { name: /environment/i })).toBeInTheDocument()
        expect(screen.getByRole('tab', { name: /activity/i })).toBeInTheDocument()
        expect(screen.getByRole('tab', { name: /photos/i })).toBeInTheDocument()
      })
    })

    it('debe mostrar el tab Care por defecto', async () => {
      render(<PlantDetailPage />)

      await waitFor(() => {
        expect(screen.getByText('Watering Schedule')).toBeInTheDocument()
        expect(screen.getByText('Fertilizing Schedule')).toBeInTheDocument()
      })
    })

    it('debe cambiar al tab Environment cuando se hace click', async () => {
      const user = userEvent.setup()
      render(<PlantDetailPage />)

      await waitFor(() => {
        expect(screen.getByRole('tab', { name: /environment/i })).toBeInTheDocument()
      })

      const environmentTab = screen.getByRole('tab', { name: /environment/i })
      await user.click(environmentTab)

      await waitFor(() => {
        expect(screen.getByText('Light Requirements')).toBeInTheDocument()
        expect(screen.getByText('Temperature')).toBeInTheDocument()
        expect(screen.getByText('Humidity')).toBeInTheDocument()
      })
    })

    it('debe cambiar al tab Activity cuando se hace click', async () => {
      const user = userEvent.setup()
      render(<PlantDetailPage />)

      await waitFor(() => {
        expect(screen.getByRole('tab', { name: /activity/i })).toBeInTheDocument()
      })

      const activityTab = screen.getByRole('tab', { name: /activity/i })
      await user.click(activityTab)

      await waitFor(() => {
        expect(screen.getByText('Recent Activity')).toBeInTheDocument()
        expect(screen.getByText('Add Activity')).toBeInTheDocument()
      })
    })

    it('debe cambiar al tab Photos cuando se hace click', async () => {
      const user = userEvent.setup()
      render(<PlantDetailPage />)

      await waitFor(() => {
        expect(screen.getByRole('tab', { name: /photos/i })).toBeInTheDocument()
      })

      const photosTab = screen.getByRole('tab', { name: /photos/i })
      await user.click(photosTab)

      await waitFor(() => {
        expect(screen.getByText('Photo Gallery')).toBeInTheDocument()
      })
    })
  })

  describe('Tab Care - Watering Schedule', () => {
    beforeEach(() => {
      ;(useAuth as jest.Mock).mockReturnValue({
        usuario: mockUsuario,
        estaAutenticado: true,
        estaCargando: false,
      })
      ;(dashboardService.obtenerPlanta as jest.Mock).mockResolvedValue(mockPlanta)
    })

    it('debe mostrar la fecha del último riego', async () => {
      render(<PlantDetailPage />)

      await waitFor(() => {
        expect(screen.getByText('Last Watered')).toBeInTheDocument()
        // Buscar específicamente el texto "Hace 2 días" (fecha del último riego)
        expect(screen.getByText('Hace 2 días')).toBeInTheDocument()
      })
    })

    it('debe mostrar la frecuencia de riego', async () => {
      render(<PlantDetailPage />)

      await waitFor(() => {
        expect(screen.getByText('Frequency')).toBeInTheDocument()
        expect(screen.getByText(/Every 7 days/i)).toBeInTheDocument()
      })
    })

    it('debe mostrar botón "Mark as Watered"', async () => {
      render(<PlantDetailPage />)

      await waitFor(() => {
        const botonRegar = screen.getByRole('button', {
          name: /mark as watered/i,
        })
        expect(botonRegar).toBeInTheDocument()
      })
    })

    it('debe mostrar alerta si la planta necesita riego', async () => {
      ;(dashboardService.obtenerPlanta as jest.Mock).mockResolvedValue(
        mockPlantaNecesitaRiego
      )

      render(<PlantDetailPage />)

      await waitFor(() => {
        expect(screen.getByText(/necesita riego ahora/i)).toBeInTheDocument()
      })
    })

    it('debe mostrar el schedule de fertilización', async () => {
      render(<PlantDetailPage />)

      await waitFor(() => {
        expect(screen.getByText('Fertilizing Schedule')).toBeInTheDocument()
        expect(screen.getByText('Last Fertilized')).toBeInTheDocument()
        expect(screen.getByText('Next Fertilizing')).toBeInTheDocument()
      })
    })

    it('debe mostrar care tips', async () => {
      render(<PlantDetailPage />)

      await waitFor(() => {
        expect(screen.getByText('Care Tips')).toBeInTheDocument()
        expect(screen.getByText(/water when top 2 inches/i)).toBeInTheDocument()
      })
    })
  })

  describe('Funcionalidad de Registro de Riego', () => {
    beforeEach(() => {
      ;(useAuth as jest.Mock).mockReturnValue({
        usuario: mockUsuario,
        estaAutenticado: true,
        estaCargando: false,
      })
    })

    it('debe registrar riego cuando se hace click en "Mark as Watered"', async () => {
      const user = userEvent.setup()
      ;(dashboardService.obtenerPlanta as jest.Mock).mockResolvedValue(mockPlanta)
      ;(dashboardService.registrarRiego as jest.Mock).mockResolvedValue({})

      render(<PlantDetailPage />)

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /mark as watered/i })).toBeInTheDocument()
      })

      const botonRegar = screen.getByRole('button', { name: /mark as watered/i })
      await user.click(botonRegar)

      await waitFor(() => {
        expect(dashboardService.registrarRiego).toHaveBeenCalledWith(1)
      })
    })

    it('debe mostrar loading mientras registra el riego', async () => {
      const user = userEvent.setup()
      ;(dashboardService.obtenerPlanta as jest.Mock).mockResolvedValue(mockPlanta)
      ;(dashboardService.registrarRiego as jest.Mock).mockImplementation(
        () => new Promise((resolve) => setTimeout(resolve, 1000))
      )

      render(<PlantDetailPage />)

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /mark as watered/i })).toBeInTheDocument()
      })

      const botonRegar = screen.getByRole('button', { name: /mark as watered/i })
      await user.click(botonRegar)

      expect(screen.getByText('Registrando...')).toBeInTheDocument()
    })

    it('debe recargar los datos de la planta después de registrar riego', async () => {
      const user = userEvent.setup()
      const plantaActualizada = { ...mockPlanta, fecha_ultimo_riego: '2025-11-07T10:00:00Z' }
      
      ;(dashboardService.obtenerPlanta as jest.Mock)
        .mockResolvedValueOnce(mockPlanta)
        .mockResolvedValueOnce(plantaActualizada)
      ;(dashboardService.registrarRiego as jest.Mock).mockResolvedValue({})

      render(<PlantDetailPage />)

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /mark as watered/i })).toBeInTheDocument()
      })

      const botonRegar = screen.getByRole('button', { name: /mark as watered/i })
      await user.click(botonRegar)

      await waitFor(() => {
        expect(dashboardService.obtenerPlanta).toHaveBeenCalledTimes(2)
      })
    })

    it('debe deshabilitar el botón mientras registra riego', async () => {
      const user = userEvent.setup()
      ;(dashboardService.obtenerPlanta as jest.Mock).mockResolvedValue(mockPlanta)
      ;(dashboardService.registrarRiego as jest.Mock).mockImplementation(
        () => new Promise((resolve) => setTimeout(resolve, 1000))
      )

      render(<PlantDetailPage />)

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /mark as watered/i })).toBeInTheDocument()
      })

      const botonRegar = screen.getByRole('button', { name: /mark as watered/i })
      await user.click(botonRegar)

      expect(botonRegar).toBeDisabled()
    })
  })

  describe('Tab Environment', () => {
    beforeEach(() => {
      ;(useAuth as jest.Mock).mockReturnValue({
        usuario: mockUsuario,
        estaAutenticado: true,
        estaCargando: false,
      })
      ;(dashboardService.obtenerPlanta as jest.Mock).mockResolvedValue(mockPlanta)
    })

    it('debe mostrar la información de luz con barra de progreso', async () => {
      const user = userEvent.setup()
      render(<PlantDetailPage />)

      const environmentTab = await screen.findByRole('tab', { name: /environment/i })
      await user.click(environmentTab)

      await waitFor(() => {
        expect(screen.getByText('Light Requirements')).toBeInTheDocument()
        expect(screen.getByText('Current Light Level')).toBeInTheDocument()
      })
    })

    it('debe mostrar el rango de temperatura ideal', async () => {
      const user = userEvent.setup()
      render(<PlantDetailPage />)

      const environmentTab = await screen.findByRole('tab', { name: /environment/i })
      await user.click(environmentTab)

      await waitFor(() => {
        expect(screen.getByText('Temperature')).toBeInTheDocument()
        expect(screen.getByText(/65-85°F/i)).toBeInTheDocument()
      })
    })

    it('debe mostrar información de humedad', async () => {
      const user = userEvent.setup()
      render(<PlantDetailPage />)

      const environmentTab = await screen.findByRole('tab', { name: /environment/i })
      await user.click(environmentTab)

      await waitFor(() => {
        expect(screen.getByText('Humidity')).toBeInTheDocument()
        expect(screen.getByText(/60-80%/i)).toBeInTheDocument()
      })
    })
  })

  describe('Tab Activity', () => {
    beforeEach(() => {
      ;(useAuth as jest.Mock).mockReturnValue({
        usuario: mockUsuario,
        estaAutenticado: true,
        estaCargando: false,
      })
      ;(dashboardService.obtenerPlanta as jest.Mock).mockResolvedValue(mockPlanta)
    })

    it('debe mostrar el historial de actividades', async () => {
      const user = userEvent.setup()
      render(<PlantDetailPage />)

      const activityTab = await screen.findByRole('tab', { name: /activity/i })
      await user.click(activityTab)

      await waitFor(() => {
        expect(screen.getByText('Recent Activity')).toBeInTheDocument()
      })
    })

    it('debe mostrar botones para agregar actividades', async () => {
      const user = userEvent.setup()
      render(<PlantDetailPage />)

      const activityTab = await screen.findByRole('tab', { name: /activity/i })
      await user.click(activityTab)

      await waitFor(() => {
        expect(screen.getByText('Add Activity')).toBeInTheDocument()
        expect(screen.getByText('Log Watering')).toBeInTheDocument()
        expect(screen.getByText('Log Fertilizing')).toBeInTheDocument()
        expect(screen.getByText('Add Photo')).toBeInTheDocument()
        expect(screen.getByText('Report Issue')).toBeInTheDocument()
      })
    })
  })

  describe('Tab Photos', () => {
    beforeEach(() => {
      ;(useAuth as jest.Mock).mockReturnValue({
        usuario: mockUsuario,
        estaAutenticado: true,
        estaCargando: false,
      })
      ;(dashboardService.obtenerPlanta as jest.Mock).mockResolvedValue(mockPlanta)
    })

    it('debe mostrar la galería de fotos', async () => {
      const user = userEvent.setup()
      render(<PlantDetailPage />)

      const photosTab = await screen.findByRole('tab', { name: /photos/i })
      await user.click(photosTab)

      await waitFor(() => {
        expect(screen.getByText('Photo Gallery')).toBeInTheDocument()
      })
    })

    it('debe mostrar botón para agregar nuevas fotos', async () => {
      const user = userEvent.setup()
      render(<PlantDetailPage />)

      const photosTab = await screen.findByRole('tab', { name: /photos/i })
      await user.click(photosTab)

      await waitFor(() => {
        expect(screen.getByText('Add New Photo')).toBeInTheDocument()
      })
    })
  })

  describe('Navegación', () => {
    beforeEach(() => {
      ;(useAuth as jest.Mock).mockReturnValue({
        usuario: mockUsuario,
        estaAutenticado: true,
        estaCargando: false,
      })
      ;(dashboardService.obtenerPlanta as jest.Mock).mockResolvedValue(mockPlanta)
    })

    it('debe tener botón "Volver al Jardín" en el header', async () => {
      render(<PlantDetailPage />)

      await waitFor(() => {
        const botonVolver = screen.getByRole('link', {
          name: /volver al jardín/i,
        })
        expect(botonVolver).toBeInTheDocument()
        expect(botonVolver).toHaveAttribute('href', '/dashboard')
      })
    })

    it('debe tener botones de editar y eliminar en el header', async () => {
      render(<PlantDetailPage />)

      await waitFor(() => {
        const botones = screen.getAllByRole('button')
        expect(botones.length).toBeGreaterThan(0)
      })
    })
  })

  describe('Responsive design', () => {
    beforeEach(() => {
      ;(useAuth as jest.Mock).mockReturnValue({
        usuario: mockUsuario,
        estaAutenticado: true,
        estaCargando: false,
      })
      ;(dashboardService.obtenerPlanta as jest.Mock).mockResolvedValue(mockPlanta)
    })

    it('debe renderizar layout con clases responsive', async () => {
      const { container } = render(<PlantDetailPage />)

      await waitFor(() => {
        const mainGrid = container.querySelector('.grid.lg\\:grid-cols-3')
        expect(mainGrid).toBeInTheDocument()
      })
    })
  })
})
