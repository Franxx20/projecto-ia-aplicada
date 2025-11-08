/**
 * Test de funcionalidad de favoritos y regado
 * 
 * Verifica que los botones de favoritos y regado funcionen correctamente
 */

import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import '@testing-library/jest-dom'
import DashboardPage from '@/app/dashboard/page'
import { useAuth } from '@/hooks/useAuth'
import { useRouter } from 'next/navigation'
import plantService from '@/lib/plant.service'
import dashboardService from '@/lib/dashboard.service'

// Mock de hooks y servicios
jest.mock('@/hooks/useAuth')
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}))
jest.mock('@/lib/plant.service')
jest.mock('@/lib/dashboard.service')

const mockRouter = {
  push: jest.fn(),
  refresh: jest.fn(),
}

const mockUsuario = {
  id: 1,
  email: 'test@example.com',
  nombre: 'Test User',
}

const mockEstadisticas = {
  total_plantas: 2,
  plantas_saludables: 1,
  plantas_necesitan_atencion: 1,
  plantas_necesitan_riego: 0,
  porcentaje_salud: 50,
}

const mockPlantas = [
  {
    id: 1,
    usuario_id: 1,
    nombre_personalizado: 'Mi Planta Favorita',
    especie_id: 1,
    estado_salud: 'buena',
    ubicacion: 'Sala',
    notas: null,
    imagen_principal_id: null,
    imagen_principal_url: null,
    fecha_ultimo_riego: '2025-11-05T00:00:00Z',
    frecuencia_riego_dias: 7,
    luz_actual: 'luz_indirecta',
    fecha_adquisicion: null,
    proxima_riego: '2025-11-12T00:00:00Z',
    created_at: '2025-11-01T00:00:00Z',
    updated_at: '2025-11-05T00:00:00Z',
    is_active: true,
    necesita_riego: false,
    es_favorita: true,
    fue_regada_hoy: false,
    especie: {
      id: 1,
      nombre_cientifico: 'Monstera deliciosa',
      nombre_comun: 'Costilla de Adán',
      familia: 'Araceae',
    },
    imagenes_identificacion: [],
  },
  {
    id: 2,
    usuario_id: 1,
    nombre_personalizado: 'Planta Normal',
    especie_id: 2,
    estado_salud: 'excelente',
    ubicacion: 'Cocina',
    notas: null,
    imagen_principal_id: null,
    imagen_principal_url: null,
    fecha_ultimo_riego: '2025-11-06T00:00:00Z',
    frecuencia_riego_dias: 5,
    luz_actual: 'luz_directa',
    fecha_adquisicion: null,
    proxima_riego: '2025-11-11T00:00:00Z',
    created_at: '2025-11-02T00:00:00Z',
    updated_at: '2025-11-06T00:00:00Z',
    is_active: true,
    necesita_riego: false,
    es_favorita: false,
    fue_regada_hoy: true,
    especie: {
      id: 2,
      nombre_cientifico: 'Pothos aureus',
      nombre_comun: 'Potus',
      familia: 'Araceae',
    },
    imagenes_identificacion: [],
  },
]

describe('Funcionalidad de Favoritos y Regado', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    ;(useAuth as jest.Mock).mockReturnValue({
      usuario: mockUsuario,
      estaAutenticado: true,
      estaCargando: false,
      cerrarSesion: jest.fn(),
    })
    ;(useRouter as jest.Mock).mockReturnValue(mockRouter)
    ;(dashboardService.obtenerEstadisticas as jest.Mock).mockResolvedValue(
      mockEstadisticas
    )
  })

  describe('Botón de Favoritos', () => {
    it('debe mostrar corazón rojo cuando la planta es favorita', async () => {
      ;(plantService.obtenerMisPlantas as jest.Mock).mockResolvedValue(mockPlantas)

      const { container } = render(<DashboardPage />)

      await waitFor(() => {
        // Buscar el corazón con clase fill-red-500
        const corazonRojo = container.querySelector('.fill-red-500')
        expect(corazonRojo).toBeInTheDocument()
      })
    })

    it('debe mostrar corazón gris cuando la planta NO es favorita', async () => {
      ;(plantService.obtenerMisPlantas as jest.Mock).mockResolvedValue(mockPlantas)

      const { container } = render(<DashboardPage />)

      await waitFor(() => {
        // Buscar corazones
        const corazones = container.querySelectorAll('.lucide-heart')
        expect(corazones.length).toBeGreaterThan(0)
        
        // Verificar que hay al menos uno que no es rojo (la segunda planta)
        const corazonGris = Array.from(corazones).find(
          corazon => !corazon.classList.contains('fill-red-500')
        )
        expect(corazonGris).toBeInTheDocument()
      })
    })

    it('debe llamar a actualizarPlanta cuando se hace click en favoritos', async () => {
      ;(plantService.obtenerMisPlantas as jest.Mock).mockResolvedValue(mockPlantas)
      ;(plantService.actualizarPlanta as jest.Mock).mockResolvedValue({
        ...mockPlantas[1],
        es_favorita: true,
      })

      const { container } = render(<DashboardPage />)

      await waitFor(() => {
        expect(screen.getByText('Planta Normal')).toBeInTheDocument()
      })

      // Buscar el botón de favoritos (tiene el icono Heart) de la segunda planta
      const botonesCorazon = container.querySelectorAll('button .lucide-heart')
      // El botón es el parent del icono
      const segundoBotonCorazon = botonesCorazon[1].parentElement as HTMLButtonElement
      
      fireEvent.click(segundoBotonCorazon)

      await waitFor(() => {
        expect(plantService.actualizarPlanta).toHaveBeenCalledWith(2, {
          es_favorita: true,
        })
      })
    })

    it('debe actualizar el estado local sin recargar todo el dashboard', async () => {
      ;(plantService.obtenerMisPlantas as jest.Mock).mockResolvedValue(mockPlantas)
      ;(plantService.actualizarPlanta as jest.Mock).mockResolvedValue({
        ...mockPlantas[1],
        es_favorita: true,
      })

      const { container } = render(<DashboardPage />)

      await waitFor(() => {
        expect(screen.getByText('Planta Normal')).toBeInTheDocument()
      })

      const initialCallCount = (plantService.obtenerMisPlantas as jest.Mock).mock.calls.length

      // Hacer click en favoritos (buscar botón con icono heart)
      const botonesCorazon = container.querySelectorAll('button .lucide-heart')
      const segundoBotonCorazon = botonesCorazon[1].parentElement as HTMLButtonElement
      fireEvent.click(segundoBotonCorazon)

      await waitFor(() => {
        // El icono debe cambiar a rojo (fill-red-500)
        const corazonActualizado = segundoBotonCorazon.querySelector('.fill-red-500')
        expect(corazonActualizado).toBeInTheDocument()
      })

      // NO debe llamar a obtenerMisPlantas nuevamente (actualización optimista)
      expect((plantService.obtenerMisPlantas as jest.Mock).mock.calls.length).toBe(initialCallCount)
    })
  })

  describe('Botón de Regado', () => {
    it('debe mostrar icono azul cuando la planta fue regada hoy', async () => {
      ;(plantService.obtenerMisPlantas as jest.Mock).mockResolvedValue(mockPlantas)

      const { container } = render(<DashboardPage />)

      await waitFor(() => {
        // Buscar el icono de droplets azul
        const iconoAzul = container.querySelector('.text-blue-500')
        expect(iconoAzul).toBeInTheDocument()
      })
    })

    it('debe tener borde azul cuando la planta fue regada hoy', async () => {
      ;(plantService.obtenerMisPlantas as jest.Mock).mockResolvedValue(mockPlantas)

      const { container } = render(<DashboardPage />)

      await waitFor(() => {
        // Buscar botón con borde azul
        const botonAzul = container.querySelector('.border-blue-500')
        expect(botonAzul).toBeInTheDocument()
      })
    })

    it('debe llamar a actualizarPlanta cuando se hace click en regar', async () => {
      ;(plantService.obtenerMisPlantas as jest.Mock).mockResolvedValue(mockPlantas)
      ;(plantService.actualizarPlanta as jest.Mock).mockResolvedValue({
        ...mockPlantas[0],
        fue_regada_hoy: true,
      })

      render(<DashboardPage />)

      await waitFor(() => {
        expect(screen.getByText('Mi Planta Favorita')).toBeInTheDocument()
      })

      // Buscar todos los botones con droplets
      const botonesRegar = screen.getAllByRole('button', { hidden: true }).filter(btn => {
        const svg = btn.querySelector('.lucide-droplets')
        return svg !== null
      })

      // Click en el primer botón de regar (planta que NO fue regada hoy)
      fireEvent.click(botonesRegar[0])

      await waitFor(() => {
        expect(plantService.actualizarPlanta).toHaveBeenCalledWith(1, {
          fue_regada_hoy: true,
        })
      })
    })

    it('el botón de regar NO debe ocupar todo el ancho', async () => {
      ;(plantService.obtenerMisPlantas as jest.Mock).mockResolvedValue(mockPlantas)

      const { container } = render(<DashboardPage />)

      await waitFor(() => {
        expect(screen.getByText('Mi Planta Favorita')).toBeInTheDocument()
      })

      // Buscar los botones de regar (tienen clase rounded-full y lucide-droplets)
      const botonesRegar = container.querySelectorAll('button.rounded-full')
      const botonRegar = Array.from(botonesRegar).find(btn => 
        btn.querySelector('.lucide-droplets')
      )

      expect(botonRegar).toBeInTheDocument()
      // Verificar que NO tiene clase w-full
      expect(botonRegar?.classList.contains('w-full')).toBe(false)
      // Verificar que tiene clase w-10 (tamaño fijo)
      expect(botonRegar?.classList.contains('w-10')).toBe(true)
    })
  })

  describe('Ordenamiento por Favoritos', () => {
    it('debe mostrar plantas favoritas primero', async () => {
      const plantasDesordenadas = [
        { ...mockPlantas[1], id: 3, nombre_personalizado: 'Tercera', es_favorita: false },
        { ...mockPlantas[0], id: 1, nombre_personalizado: 'Primera Favorita', es_favorita: true },
        { ...mockPlantas[1], id: 2, nombre_personalizado: 'Segunda', es_favorita: false },
      ]

      ;(plantService.obtenerMisPlantas as jest.Mock).mockResolvedValue(plantasDesordenadas)

      const { container } = render(<DashboardPage />)

      await waitFor(() => {
        expect(screen.getByText('Primera Favorita')).toBeInTheDocument()
      })

      // Obtener todas las tarjetas de plantas (Cards tienen overflow-hidden)
      const tarjetas = container.querySelectorAll('.overflow-hidden.hover\\:shadow-lg')
      expect(tarjetas.length).toBe(3)

      // La primera tarjeta debe tener el corazón rojo (es favorita)
      const primeraTarjeta = tarjetas[0]
      const corazonRojo = primeraTarjeta.querySelector('.fill-red-500')
      expect(corazonRojo).toBeInTheDocument()
    })
  })

  describe('Manejo de Errores', () => {
    it('debe mostrar alerta cuando falla actualizar favorita', async () => {
      ;(plantService.obtenerMisPlantas as jest.Mock).mockResolvedValue(mockPlantas)
      ;(plantService.actualizarPlanta as jest.Mock).mockRejectedValue(
        new Error('Error de red')
      )

      const alertSpy = jest.spyOn(window, 'alert').mockImplementation(() => {})

      const { container } = render(<DashboardPage />)

      await waitFor(() => {
        expect(screen.getByText('Planta Normal')).toBeInTheDocument()
      })

      // Click en favoritos
      const botonesCorazon = container.querySelectorAll('.lucide-heart')
      const botonCorazon = botonesCorazon[1].parentElement as HTMLButtonElement
      fireEvent.click(botonCorazon)

      await waitFor(() => {
        expect(alertSpy).toHaveBeenCalledWith('Error al actualizar la planta como favorita')
      })

      alertSpy.mockRestore()
    })

    it('debe revertir el cambio optimista si falla actualizar favorita', async () => {
      ;(plantService.obtenerMisPlantas as jest.Mock).mockResolvedValue(mockPlantas)
      ;(plantService.actualizarPlanta as jest.Mock).mockRejectedValue(
        new Error('Error de red')
      )

      const alertSpy = jest.spyOn(window, 'alert').mockImplementation(() => {})

      const { container } = render(<DashboardPage />)

      await waitFor(() => {
        expect(screen.getByText('Planta Normal')).toBeInTheDocument()
      })

      // Verificar estado inicial (no favorita, sin fill-red-500)
      const botonesCorazon = container.querySelectorAll('.lucide-heart')
      const botonCorazon = botonesCorazon[1].parentElement as HTMLButtonElement
      const corazonInicial = botonCorazon.querySelector('.lucide-heart')
      expect(corazonInicial?.classList.contains('fill-red-500')).toBe(false)

      // Click en favoritos (debería fallar)
      fireEvent.click(botonCorazon)

      // Esperar el error
      await waitFor(() => {
        expect(alertSpy).toHaveBeenCalled()
      })

      // El corazón debe volver a su estado original (sin fill-red-500)
      const corazonRevertido = botonCorazon.querySelector('.lucide-heart')
      expect(corazonRevertido?.classList.contains('fill-red-500')).toBe(false)

      alertSpy.mockRestore()
    })

    it('debe mostrar alerta cuando falla actualizar regado', async () => {
      ;(plantService.obtenerMisPlantas as jest.Mock).mockResolvedValue(mockPlantas)
      ;(plantService.actualizarPlanta as jest.Mock).mockRejectedValue(
        new Error('Error de red')
      )

      const alertSpy = jest.spyOn(window, 'alert').mockImplementation(() => {})

      render(<DashboardPage />)

      await waitFor(() => {
        expect(screen.getByText('Mi Planta Favorita')).toBeInTheDocument()
      })

      // Click en regar
      const botonesRegar = screen.getAllByRole('button', { hidden: true }).filter(btn => {
        const svg = btn.querySelector('.lucide-droplets')
        return svg !== null
      })
      fireEvent.click(botonesRegar[0])

      await waitFor(() => {
        expect(alertSpy).toHaveBeenCalledWith('Error al marcar la planta como regada')
      })

      alertSpy.mockRestore()
    })
  })
})
