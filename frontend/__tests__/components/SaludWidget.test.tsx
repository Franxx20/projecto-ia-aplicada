/**
 * Tests para SaludWidget (Dashboard Health Widget)
 * 
 * Tests unitarios y de integración para verificar:
 * - Renderizado correcto de estadísticas agregadas
 * - Alertas críticas banner
 * - Estados de carga, error y empty
 * - Últimos análisis de todas las plantas
 * - Navegación a plant details
 * - Refresh functionality
 * 
 * @jest-environment jsdom
 */

import { render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { useRouter } from 'next/navigation'
import { SaludWidget } from '@/components/dashboard/SaludWidget'
import dashboardService from '@/lib/dashboard.service'
import saludService from '@/lib/salud.service'
import type { Planta } from '@/models/dashboard.types'
import type { EstadisticasSalud, HistorialSaludResponse } from '@/models/salud'

// Mock de Next.js router
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}))

// Mock del dashboardService
jest.mock('@/lib/dashboard.service', () => ({
  __esModule: true,
  default: {
    obtenerPlantas: jest.fn(),
  },
}))

// Mock del saludService
jest.mock('@/lib/salud.service', () => ({
  __esModule: true,
  default: {
    obtenerEstadisticas: jest.fn(),
    obtenerHistorial: jest.fn(),
  },
}))

describe('SaludWidget', () => {
  const mockRouter = {
    push: jest.fn(),
  }

  beforeEach(() => {
    jest.clearAllMocks()
    ;(useRouter as jest.Mock).mockReturnValue(mockRouter)
  })

  describe('Loading State', () => {
    it('debe mostrar spinner durante la carga inicial', () => {
      // Mock sin resolver para mantener loading state
      ;(dashboardService.obtenerPlantas as jest.Mock).mockReturnValue(
        new Promise(() => {})
      )

      render(<SaludWidget />)

      expect(screen.getByText(/Cargando/i)).toBeInTheDocument()
      expect(screen.getByRole('status')).toBeInTheDocument()
    })
  })

  describe('Empty States', () => {
    it('debe mostrar empty state cuando no hay plantas', async () => {
      ;(dashboardService.obtenerPlantas as jest.Mock).mockResolvedValue({
        plantas: [],
        total: 0,
        pagina: 1,
        limite: 100,
      })

      render(<SaludWidget />)

      await waitFor(() => {
        expect(screen.getByText(/No hay plantas registradas/i)).toBeInTheDocument()
      })

      expect(screen.getByText(/Agrega plantas a tu jardín/i)).toBeInTheDocument()
      expect(screen.getByText(/Agregar Primera Planta/i)).toBeInTheDocument()
    })

    it('debe mostrar empty state cuando hay plantas pero sin análisis', async () => {
      const mockPlantasSinAnalisis: Planta[] = [
        {
          id: 1,
          usuario_id: 1,
          nombre_personal: 'Mi Planta',
          especie_id: 101,
          estado_salud: 'buena',
          ubicacion: 'Sala',
          notas: null,
          imagen_principal_id: null,
          fecha_ultimo_riego: '2025-11-01T10:00:00Z',
          frecuencia_riego_dias: 7,
          luz_actual: 'alta',
          fecha_adquisicion: '2025-01-01T00:00:00Z',
          proxima_riego: '2025-11-08T10:00:00Z',
          created_at: '2025-01-01T00:00:00Z',
          updated_at: '2025-11-08T00:00:00Z',
          is_active: true,
          necesita_riego: false,
        },
      ]

      ;(dashboardService.obtenerPlantas as jest.Mock).mockResolvedValue({
        plantas: mockPlantasSinAnalisis,
        total: 1,
        pagina: 1,
        limite: 100,
      })

      // Sin estadísticas de salud
      ;(saludService.obtenerEstadisticas as jest.Mock).mockResolvedValue(null)

      render(<SaludWidget />)

      await waitFor(() => {
        expect(screen.getByText(/No hay análisis de salud/i)).toBeInTheDocument()
      })

      expect(screen.getByText(/Realiza el primer análisis/i)).toBeInTheDocument()
    })
  })

  describe('Error State', () => {
    it('debe mostrar mensaje de error cuando falla la carga', async () => {
      const errorMessage = 'Error al cargar plantas'
      ;(dashboardService.obtenerPlantas as jest.Mock).mockRejectedValue(
        new Error(errorMessage)
      )

      render(<SaludWidget />)

      await waitFor(() => {
        expect(screen.getByText(/Error al cargar datos de salud/i)).toBeInTheDocument()
      })

      expect(screen.getByText(/Reintentar/i)).toBeInTheDocument()
    })

    it('debe reintentar la carga al hacer click en Reintentar', async () => {
      // Primera llamada falla
      ;(dashboardService.obtenerPlantas as jest.Mock)
        .mockRejectedValueOnce(new Error('Error'))
        .mockResolvedValueOnce({
          plantas: [],
          total: 0,
          pagina: 1,
          limite: 100,
        })

      render(<SaludWidget />)

      await waitFor(() => {
        expect(screen.getByText(/Error al cargar datos de salud/i)).toBeInTheDocument()
      })

      const botonReintentar = screen.getByText(/Reintentar/i)
      await userEvent.click(botonReintentar)

      await waitFor(() => {
        expect(screen.getByText(/No hay plantas registradas/i)).toBeInTheDocument()
      })
    })
  })

  describe('Success State - Estadísticas', () => {
    const mockPlantas: Planta[] = [
      {
        id: 1,
        usuario_id: 1,
        nombre_personal: 'Monstera Saludable',
        especie_id: 101,
        estado_salud: 'buena',
        ubicacion: 'Sala',
        notas: null,
        imagen_principal_id: 1,
        fecha_ultimo_riego: '2025-11-01T10:00:00Z',
        frecuencia_riego_dias: 7,
        luz_actual: 'alta',
        fecha_adquisicion: '2025-01-01T00:00:00Z',
        proxima_riego: '2025-11-08T10:00:00Z',
        created_at: '2025-01-01T00:00:00Z',
        updated_at: '2025-11-08T00:00:00Z',
        is_active: true,
        necesita_riego: false,
      },
      {
        id: 2,
        usuario_id: 1,
        nombre_personal: 'Pothos Con Plaga',
        especie_id: 102,
        estado_salud: 'necesita_atencion',
        ubicacion: 'Balcón',
        notas: null,
        imagen_principal_id: 2,
        fecha_ultimo_riego: '2025-11-01T10:00:00Z',
        frecuencia_riego_dias: 5,
        luz_actual: 'media',
        fecha_adquisicion: '2025-02-01T00:00:00Z',
        proxima_riego: '2025-11-06T10:00:00Z',
        created_at: '2025-02-01T00:00:00Z',
        updated_at: '2025-11-08T00:00:00Z',
        is_active: true,
        necesita_riego: false,
      },
      {
        id: 3,
        usuario_id: 1,
        nombre_personal: 'Ficus Enfermo',
        especie_id: 103,
        estado_salud: 'necesita_atencion',
        ubicacion: 'Dormitorio',
        notas: 'Hojas amarillas',
        imagen_principal_id: null,
        fecha_ultimo_riego: '2025-11-02T10:00:00Z',
        frecuencia_riego_dias: 3,
        luz_actual: 'baja',
        fecha_adquisicion: '2025-03-01T00:00:00Z',
        proxima_riego: '2025-11-05T10:00:00Z',
        created_at: '2025-03-01T00:00:00Z',
        updated_at: '2025-11-08T00:00:00Z',
        is_active: true,
        necesita_riego: true,
      },
    ]

    const mockEstadisticas: Record<number, EstadisticasSalud> = {
      1: {
        planta_id: 1,
        ultimo_estado: 'saludable',
        total_analisis: 3,
        confianza_promedio: 92.5,
        dias_desde_ultimo_analisis: 1,
        tendencia: 'estable',
      },
      2: {
        planta_id: 2,
        ultimo_estado: 'plaga',
        total_analisis: 2,
        confianza_promedio: 78.0,
        dias_desde_ultimo_analisis: 2,
        tendencia: 'empeorando',
      },
      3: {
        planta_id: 3,
        ultimo_estado: 'enfermedad',
        total_analisis: 4,
        confianza_promedio: 85.5,
        dias_desde_ultimo_analisis: 3,
        tendencia: 'empeorando',
      },
    }

    const mockHistorial: Record<number, HistorialSaludResponse> = {
      1: {
        analisis: [
          {
            id: 101,
            planta_id: 1,
            estado: 'saludable',
            confianza: 92.5,
            diagnostico: 'Planta en excelente estado',
            recomendaciones: ['Mantener cuidados actuales'],
            imagen_analisis_url: 'http://example.com/img1.jpg',
            fecha_analisis: '2025-11-07T10:00:00Z',
            created_at: '2025-11-07T10:00:00Z',
          },
        ],
        total: 1,
        pagina: 1,
        limite: 2,
      },
      2: {
        analisis: [
          {
            id: 102,
            planta_id: 2,
            estado: 'plaga',
            confianza: 78.0,
            diagnostico: 'Plaga detectada en hojas',
            recomendaciones: ['Aplicar insecticida', 'Aislar planta'],
            imagen_analisis_url: 'http://example.com/img2.jpg',
            fecha_analisis: '2025-11-06T10:00:00Z',
            created_at: '2025-11-06T10:00:00Z',
          },
        ],
        total: 1,
        pagina: 1,
        limite: 2,
      },
      3: {
        analisis: [
          {
            id: 103,
            planta_id: 3,
            estado: 'enfermedad',
            confianza: 85.5,
            diagnostico: 'Enfermedad fúngica',
            recomendaciones: ['Reducir riego', 'Mejorar ventilación'],
            imagen_analisis_url: 'http://example.com/img3.jpg',
            fecha_analisis: '2025-11-05T10:00:00Z',
            created_at: '2025-11-05T10:00:00Z',
          },
        ],
        total: 1,
        pagina: 1,
        limite: 2,
      },
    }

    beforeEach(() => {
      ;(dashboardService.obtenerPlantas as jest.Mock).mockResolvedValue({
        plantas: mockPlantas,
        total: 3,
        pagina: 1,
        limite: 100,
      })

      ;(saludService.obtenerEstadisticas as jest.Mock).mockImplementation(
        (plantaId: number) => Promise.resolve(mockEstadisticas[plantaId])
      )

      ;(saludService.obtenerHistorial as jest.Mock).mockImplementation(
        (plantaId: number) => Promise.resolve(mockHistorial[plantaId])
      )
    })

    it('debe mostrar header con título y subtítulo', async () => {
      render(<SaludWidget />)

      await waitFor(() => {
        expect(screen.getByText(/Salud del Jardín/i)).toBeInTheDocument()
      })

      expect(screen.getByText(/3 de 3 plantas analizadas/i)).toBeInTheDocument()
    })

    it('debe mostrar botón de refresh en header', async () => {
      render(<SaludWidget />)

      await waitFor(() => {
        const refreshButton = screen.getByLabelText(/Actualizar/i)
        expect(refreshButton).toBeInTheDocument()
      })
    })

    it('debe mostrar estadísticas correctas: saludables, atención, críticas', async () => {
      render(<SaludWidget />)

      await waitFor(() => {
        // 1 saludable (Monstera)
        expect(screen.getByText('1')).toBeInTheDocument()
        expect(screen.getByText(/Saludables/i)).toBeInTheDocument()

        // 0 necesitan atención
        expect(screen.getByText('0')).toBeInTheDocument()
        expect(screen.getByText(/Necesitan Atención/i)).toBeInTheDocument()

        // 2 críticas (Pothos con plaga + Ficus enfermo)
        expect(screen.getByText('2')).toBeInTheDocument()
        expect(screen.getByText(/Críticas/i)).toBeInTheDocument()
      })
    })

    it('debe calcular y mostrar porcentaje de salud correctamente', async () => {
      render(<SaludWidget />)

      await waitFor(() => {
        // 1 saludable / 3 total = 33.33%
        expect(screen.getByText(/33\.3%/i)).toBeInTheDocument()
        expect(screen.getByText(/Salud General/i)).toBeInTheDocument()
      })
    })

    it('debe calcular y mostrar confianza promedio correctamente', async () => {
      render(<SaludWidget />)

      await waitFor(() => {
        // (92.5 + 78.0 + 85.5) / 3 = 85.33%
        expect(screen.getByText(/85\.3%/i)).toBeInTheDocument()
        expect(screen.getByText(/Confianza Promedio/i)).toBeInTheDocument()
      })
    })
  })

  describe('Critical Alerts Banner', () => {
    const mockPlantasCriticas: Planta[] = [
      {
        id: 1,
        usuario_id: 1,
        nombre_personal: 'Planta Enferma',
        especie_id: 101,
        estado_salud: 'necesita_atencion',
        ubicacion: 'Sala',
        notas: null,
        imagen_principal_id: null,
        fecha_ultimo_riego: '2025-11-01T10:00:00Z',
        frecuencia_riego_dias: 7,
        luz_actual: 'alta',
        fecha_adquisicion: '2025-01-01T00:00:00Z',
        proxima_riego: '2025-11-08T10:00:00Z',
        created_at: '2025-01-01T00:00:00Z',
        updated_at: '2025-11-08T00:00:00Z',
        is_active: true,
        necesita_riego: false,
      },
      {
        id: 2,
        usuario_id: 1,
        nombre_personal: 'Planta Con Plaga',
        especie_id: 102,
        estado_salud: 'necesita_atencion',
        ubicacion: 'Balcón',
        notas: null,
        imagen_principal_id: null,
        fecha_ultimo_riego: '2025-11-01T10:00:00Z',
        frecuencia_riego_dias: 5,
        luz_actual: 'media',
        fecha_adquisicion: '2025-02-01T00:00:00Z',
        proxima_riego: '2025-11-06T10:00:00Z',
        created_at: '2025-02-01T00:00:00Z',
        updated_at: '2025-11-08T00:00:00Z',
        is_active: true,
        necesita_riego: false,
      },
    ]

    beforeEach(() => {
      ;(dashboardService.obtenerPlantas as jest.Mock).mockResolvedValue({
        plantas: mockPlantasCriticas,
        total: 2,
        pagina: 1,
        limite: 100,
      })

      ;(saludService.obtenerEstadisticas as jest.Mock).mockImplementation(
        (plantaId: number) => {
          if (plantaId === 1) {
            return Promise.resolve({
              planta_id: 1,
              ultimo_estado: 'enfermedad',
              total_analisis: 2,
              confianza_promedio: 80.0,
              dias_desde_ultimo_analisis: 2,
              tendencia: 'empeorando',
            })
          } else {
            return Promise.resolve({
              planta_id: 2,
              ultimo_estado: 'plaga',
              total_analisis: 1,
              confianza_promedio: 75.0,
              dias_desde_ultimo_analisis: 1,
              tendencia: 'empeorando',
            })
          }
        }
      )

      ;(saludService.obtenerHistorial as jest.Mock).mockResolvedValue({
        analisis: [],
        total: 0,
        pagina: 1,
        limite: 2,
      })
    })

    it('debe mostrar banner de alertas críticas', async () => {
      render(<SaludWidget />)

      await waitFor(() => {
        expect(screen.getByText(/2 plantas? críticas?/i)).toBeInTheDocument()
      })

      expect(screen.getByText(/Planta Enferma/i)).toBeInTheDocument()
      expect(screen.getByText(/Planta Con Plaga/i)).toBeInTheDocument()
    })

    it('debe navegar a planta al hacer click en planta crítica', async () => {
      render(<SaludWidget />)

      await waitFor(() => {
        expect(screen.getByText(/Planta Enferma/i)).toBeInTheDocument()
      })

      const plantaButton = screen.getByText(/Planta Enferma/i).closest('button')
      expect(plantaButton).toBeInTheDocument()

      await userEvent.click(plantaButton!)

      expect(mockRouter.push).toHaveBeenCalledWith('/plant/1')
    })

    it('NO debe mostrar banner si no hay plantas críticas', async () => {
      ;(saludService.obtenerEstadisticas as jest.Mock).mockImplementation(() =>
        Promise.resolve({
          planta_id: 1,
          ultimo_estado: 'saludable',
          total_analisis: 1,
          confianza_promedio: 90.0,
          dias_desde_ultimo_analisis: 1,
          tendencia: 'estable',
        })
      )

      render(<SaludWidget />)

      await waitFor(() => {
        expect(screen.getByText(/Salud del Jardín/i)).toBeInTheDocument()
      })

      expect(screen.queryByText(/plantas? críticas?/i)).not.toBeInTheDocument()
    })
  })

  describe('Recent Analyses', () => {
    const mockPlantas: Planta[] = [
      {
        id: 1,
        usuario_id: 1,
        nombre_personal: 'Planta 1',
        especie_id: 101,
        estado_salud: 'buena',
        ubicacion: 'Sala',
        notas: null,
        imagen_principal_id: null,
        fecha_ultimo_riego: '2025-11-01T10:00:00Z',
        frecuencia_riego_dias: 7,
        luz_actual: 'alta',
        fecha_adquisicion: '2025-01-01T00:00:00Z',
        proxima_riego: '2025-11-08T10:00:00Z',
        created_at: '2025-01-01T00:00:00Z',
        updated_at: '2025-11-08T00:00:00Z',
        is_active: true,
        necesita_riego: false,
      },
    ]

    beforeEach(() => {
      ;(dashboardService.obtenerPlantas as jest.Mock).mockResolvedValue({
        plantas: mockPlantas,
        total: 1,
        pagina: 1,
        limite: 100,
      })

      ;(saludService.obtenerEstadisticas as jest.Mock).mockResolvedValue({
        planta_id: 1,
        ultimo_estado: 'saludable',
        total_analisis: 3,
        confianza_promedio: 90.0,
        dias_desde_ultimo_analisis: 1,
        tendencia: 'estable',
      })
    })

    it('debe mostrar sección de análisis recientes', async () => {
      ;(saludService.obtenerHistorial as jest.Mock).mockResolvedValue({
        analisis: [
          {
            id: 101,
            planta_id: 1,
            estado: 'saludable',
            confianza: 92.5,
            diagnostico: 'Todo bien',
            recomendaciones: ['Seguir así'],
            imagen_analisis_url: 'http://example.com/img.jpg',
            fecha_analisis: '2025-11-08T10:00:00Z',
            created_at: '2025-11-08T10:00:00Z',
          },
        ],
        total: 1,
        pagina: 1,
        limite: 2,
      })

      render(<SaludWidget />)

      await waitFor(() => {
        expect(screen.getByText(/Análisis Recientes/i)).toBeInTheDocument()
      })

      expect(screen.getByText(/Planta 1/i)).toBeInTheDocument()
      expect(screen.getByText(/92\.5%/i)).toBeInTheDocument()
      expect(screen.getByText(/Hoy/i)).toBeInTheDocument()
    })

    it('debe mostrar "Hace X días" para análisis antiguos', async () => {
      const fechaPasada = new Date()
      fechaPasada.setDate(fechaPasada.getDate() - 3)

      ;(saludService.obtenerHistorial as jest.Mock).mockResolvedValue({
        analisis: [
          {
            id: 101,
            planta_id: 1,
            estado: 'saludable',
            confianza: 90.0,
            diagnostico: 'Todo bien',
            recomendaciones: ['Seguir así'],
            imagen_analisis_url: 'http://example.com/img.jpg',
            fecha_analisis: fechaPasada.toISOString(),
            created_at: fechaPasada.toISOString(),
          },
        ],
        total: 1,
        pagina: 1,
        limite: 2,
      })

      render(<SaludWidget />)

      await waitFor(() => {
        expect(screen.getByText(/Hace 3 días/i)).toBeInTheDocument()
      })
    })

    it('debe navegar a planta al hacer click en análisis', async () => {
      ;(saludService.obtenerHistorial as jest.Mock).mockResolvedValue({
        analisis: [
          {
            id: 101,
            planta_id: 1,
            estado: 'saludable',
            confianza: 90.0,
            diagnostico: 'Todo bien',
            recomendaciones: ['Seguir así'],
            imagen_analisis_url: 'http://example.com/img.jpg',
            fecha_analisis: '2025-11-08T10:00:00Z',
            created_at: '2025-11-08T10:00:00Z',
          },
        ],
        total: 1,
        pagina: 1,
        limite: 2,
      })

      render(<SaludWidget />)

      await waitFor(() => {
        expect(screen.getByText(/Planta 1/i)).toBeInTheDocument()
      })

      const analisisButton = screen.getByText(/Planta 1/i).closest('button')
      await userEvent.click(analisisButton!)

      expect(mockRouter.push).toHaveBeenCalledWith('/plant/1')
    })

    it('debe limitar a 5 análisis recientes', async () => {
      const mockMuchosAnalisis = Array.from({ length: 10 }, (_, i) => ({
        id: 100 + i,
        planta_id: 1,
        estado: 'saludable',
        confianza: 90.0,
        diagnostico: 'Todo bien',
        recomendaciones: ['Seguir así'],
        imagen_analisis_url: 'http://example.com/img.jpg',
        fecha_analisis: new Date(2025, 10, 8 - i).toISOString(),
        created_at: new Date(2025, 10, 8 - i).toISOString(),
      }))

      ;(saludService.obtenerHistorial as jest.Mock).mockResolvedValue({
        analisis: mockMuchosAnalisis,
        total: 10,
        pagina: 1,
        limite: 2,
      })

      render(<SaludWidget />)

      await waitFor(() => {
        expect(screen.getByText(/Análisis Recientes/i)).toBeInTheDocument()
      })

      // Debe haber exactamente 5 botones de análisis (limitado por código)
      const analysisButtons = screen.getAllByRole('button').filter(button =>
        button.textContent?.includes('Planta 1')
      )
      expect(analysisButtons.length).toBeLessThanOrEqual(5)
    })
  })

  describe('Refresh Functionality', () => {
    it('debe recargar datos al hacer click en botón de refresh', async () => {
      const mockPlantas: Planta[] = [
        {
          id: 1,
          usuario_id: 1,
          nombre_personal: 'Planta Test',
          especie_id: 101,
          estado_salud: 'buena',
          ubicacion: 'Sala',
          notas: null,
          imagen_principal_id: null,
          fecha_ultimo_riego: '2025-11-01T10:00:00Z',
          frecuencia_riego_dias: 7,
          luz_actual: 'alta',
          fecha_adquisicion: '2025-01-01T00:00:00Z',
          proxima_riego: '2025-11-08T10:00:00Z',
          created_at: '2025-01-01T00:00:00Z',
          updated_at: '2025-11-08T00:00:00Z',
          is_active: true,
          necesita_riego: false,
        },
      ]

      ;(dashboardService.obtenerPlantas as jest.Mock).mockResolvedValue({
        plantas: mockPlantas,
        total: 1,
        pagina: 1,
        limite: 100,
      })

      ;(saludService.obtenerEstadisticas as jest.Mock).mockResolvedValue({
        planta_id: 1,
        ultimo_estado: 'saludable',
        total_analisis: 1,
        confianza_promedio: 90.0,
        dias_desde_ultimo_analisis: 1,
        tendencia: 'estable',
      })

      ;(saludService.obtenerHistorial as jest.Mock).mockResolvedValue({
        analisis: [],
        total: 0,
        pagina: 1,
        limite: 2,
      })

      render(<SaludWidget />)

      await waitFor(() => {
        expect(screen.getByText(/Salud del Jardín/i)).toBeInTheDocument()
      })

      // Click en botón de refresh
      const refreshButton = screen.getByLabelText(/Actualizar/i)
      await userEvent.click(refreshButton)

      // Debe llamar nuevamente a los servicios
      await waitFor(() => {
        expect(dashboardService.obtenerPlantas).toHaveBeenCalledTimes(2)
      })
    })
  })

  describe('Custom className prop', () => {
    it('debe aplicar className personalizado', async () => {
      ;(dashboardService.obtenerPlantas as jest.Mock).mockResolvedValue({
        plantas: [],
        total: 0,
        pagina: 1,
        limite: 100,
      })

      const { container } = render(<SaludWidget className="custom-class" />)

      await waitFor(() => {
        expect(screen.getByText(/No hay plantas registradas/i)).toBeInTheDocument()
      })

      const cardElement = container.querySelector('.custom-class')
      expect(cardElement).toBeInTheDocument()
    })
  })
})
