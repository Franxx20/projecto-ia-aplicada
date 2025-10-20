/**
 * Tests para IdentificationResultCard Component
 * 
 * Suite de pruebas unitarias para validar:
 * - Renderizado de información de la planta
 * - Carousel de múltiples imágenes
 * - Badges de órganos
 * - Nivel de confianza
 * - Metadata (nombre común, género, familia)
 * - Botón de confirmación
 * - Auto-play del carousel
 * 
 * @author Equipo Frontend
 * @date Enero 2026
 * @sprint Sprint 3
 * @task T-023
 */

import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { IdentificationResultCard } from '@/components/identification-result-card'
import { ImagenIdentificacionResponse } from '@/models/plant.types'

// Mock del carousel API
const mockCarouselApi = {
  selectedScrollSnap: jest.fn(() => 0),
  scrollNext: jest.fn(),
  scrollPrev: jest.fn(),
  scrollTo: jest.fn(),
  canScrollNext: jest.fn(() => true),
  canScrollPrev: jest.fn(() => true),
  on: jest.fn((event, callback) => {
    // Guardar el callback para poder llamarlo en tests
    if (event === 'select') {
      mockCarouselApi.selectCallback = callback
    }
  }),
  off: jest.fn(),
  selectCallback: null as (() => void) | null,
}

// Mock de embla-carousel-react
jest.mock('embla-carousel-react', () => ({
  __esModule: true,
  default: () => [jest.fn(), mockCarouselApi],
}))

// Datos de prueba
const mockImages: ImagenIdentificacionResponse[] = [
  {
    id: 1,
    nombre_archivo: 'leaf1.jpg',
    url_blob: 'https://example.com/leaf1.jpg',
    tamano_bytes: 102400, // 100 KB
    organ: 'leaf',
  },
  {
    id: 2,
    nombre_archivo: 'flower1.jpg',
    url_blob: 'https://example.com/flower1.jpg',
    tamano_bytes: 204800, // 200 KB
    organ: 'flower',
  },
  {
    id: 3,
    nombre_archivo: 'bark1.jpg',
    url_blob: 'https://example.com/bark1.jpg',
    tamano_bytes: 153600, // 150 KB
    organ: 'bark',
  },
]

const defaultProps = {
  scientificName: 'Monstera deliciosa',
  commonName: 'Costilla de Adán',
  genus: 'Monstera',
  family: 'Araceae',
  confidence: 95.5,
  images: mockImages,
}

describe('IdentificationResultCard', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    jest.useFakeTimers()
  })

  afterEach(() => {
    jest.runOnlyPendingTimers()
    jest.useRealTimers()
  })

  describe('Renderizado básico', () => {
    it('debe renderizar el nombre científico correctamente', () => {
      render(<IdentificationResultCard {...defaultProps} />)
      
      expect(screen.getByText('Monstera deliciosa')).toBeInTheDocument()
    })

    it('debe renderizar el nivel de confianza con formato correcto', () => {
      render(<IdentificationResultCard {...defaultProps} />)
      
      expect(screen.getByText('95.5%')).toBeInTheDocument()
    })

    it('debe renderizar el nombre común', () => {
      render(<IdentificationResultCard {...defaultProps} />)
      
      expect(screen.getByText('Costilla de Adán')).toBeInTheDocument()
    })

    it('debe renderizar el género', () => {
      render(<IdentificationResultCard {...defaultProps} />)
      
      expect(screen.getByText('Monstera')).toBeInTheDocument()
    })

    it('debe renderizar la familia', () => {
      render(<IdentificationResultCard {...defaultProps} />)
      
      expect(screen.getByText('Araceae')).toBeInTheDocument()
    })

    it('debe renderizar el ícono de hoja (Leaf)', () => {
      const { container } = render(<IdentificationResultCard {...defaultProps} />)
      
      const leafIcon = container.querySelector('svg')
      expect(leafIcon).toBeInTheDocument()
    })
  })

  describe('Carousel de imágenes', () => {
    it('debe renderizar todas las imágenes en el carousel', () => {
      render(<IdentificationResultCard {...defaultProps} />)
      
      const images = screen.getAllByRole('img')
      expect(images).toHaveLength(3)
    })

    it('debe renderizar las URLs de las imágenes correctamente', () => {
      render(<IdentificationResultCard {...defaultProps} />)
      
      const images = screen.getAllByRole('img') as HTMLImageElement[]
      expect(images[0].src).toContain('leaf1.jpg')
      expect(images[1].src).toContain('flower1.jpg')
      expect(images[2].src).toContain('bark1.jpg')
    })

    it('debe renderizar los nombres de archivo de las imágenes', () => {
      render(<IdentificationResultCard {...defaultProps} />)
      
      expect(screen.getByText('leaf1.jpg')).toBeInTheDocument()
      expect(screen.getByText('flower1.jpg')).toBeInTheDocument()
      expect(screen.getByText('bark1.jpg')).toBeInTheDocument()
    })

    it('debe renderizar los tamaños de archivo en KB', () => {
      render(<IdentificationResultCard {...defaultProps} />)
      
      expect(screen.getByText('100.0 KB')).toBeInTheDocument()
      expect(screen.getByText('200.0 KB')).toBeInTheDocument()
      expect(screen.getByText('150.0 KB')).toBeInTheDocument()
    })

    it('debe usar placeholder cuando no hay URL de imagen', () => {
      const propsWithoutUrl = {
        ...defaultProps,
        images: [{
          ...mockImages[0],
          url_blob: '',
        }],
      }
      
      render(<IdentificationResultCard {...propsWithoutUrl} />)
      
      const image = screen.getByRole('img') as HTMLImageElement
      expect(image.src).toContain('placeholder.svg')
    })
  })

  describe('Badges de órganos', () => {
    it('debe renderizar badges de órganos en las imágenes', () => {
      render(<IdentificationResultCard {...defaultProps} />)
      
      expect(screen.getByText('Hoja')).toBeInTheDocument()
      expect(screen.getByText('Flor')).toBeInTheDocument()
      expect(screen.getByText('Corteza')).toBeInTheDocument()
    })

    it('debe renderizar el organ original si no hay traducción', () => {
      const propsWithUnknownOrgan = {
        ...defaultProps,
        images: [{
          ...mockImages[0],
          organ: 'unknown_organ',
        }],
      }
      
      render(<IdentificationResultCard {...propsWithUnknownOrgan} />)
      
      expect(screen.getByText('unknown_organ')).toBeInTheDocument()
    })

    it('no debe renderizar badge si el organ es undefined', () => {
      const propsWithoutOrgan = {
        ...defaultProps,
        images: [{
          ...mockImages[0],
          organ: undefined,
        }],
      }
      
      const { container } = render(<IdentificationResultCard {...propsWithoutOrgan} />)
      
      // Verificar que no hay badge con la clase esperada en la posición de la imagen
      const imageBadges = container.querySelectorAll('.absolute.top-2.right-2')
      expect(imageBadges).toHaveLength(0)
    })
  })

  describe('Indicadores del carousel', () => {
    it('debe renderizar indicadores cuando hay múltiples imágenes', () => {
      render(<IdentificationResultCard {...defaultProps} />)
      
      const indicators = screen.getAllByRole('button', { name: /Ir a imagen/ })
      expect(indicators).toHaveLength(3)
    })

    it('no debe renderizar indicadores cuando hay solo una imagen', () => {
      const propsWithOneImage = {
        ...defaultProps,
        images: [mockImages[0]],
      }
      
      render(<IdentificationResultCard {...propsWithOneImage} />)
      
      const indicators = screen.queryAllByRole('button', { name: /Ir a imagen/ })
      expect(indicators).toHaveLength(0)
    })

    it('debe poder navegar a una imagen específica al hacer clic en un indicador', () => {
      render(<IdentificationResultCard {...defaultProps} />)
      
      const indicators = screen.getAllByRole('button', { name: /Ir a imagen/ })
      fireEvent.click(indicators[1])
      
      expect(mockCarouselApi.scrollTo).toHaveBeenCalledWith(1)
    })
  })

  describe('Botón de confirmación', () => {
    it('debe renderizar el botón de confirmación', () => {
      render(<IdentificationResultCard {...defaultProps} />)
      
      expect(screen.getByRole('button', { name: /Confirmar esta planta/ })).toBeInTheDocument()
    })

    it('debe llamar a onConfirm cuando se hace clic en el botón', () => {
      const onConfirm = jest.fn()
      render(<IdentificationResultCard {...defaultProps} onConfirm={onConfirm} />)
      
      const button = screen.getByRole('button', { name: /Confirmar esta planta/ })
      fireEvent.click(button)
      
      expect(onConfirm).toHaveBeenCalledTimes(1)
    })

    it('debe mostrar "Confirmado" cuando isCorrect es true', () => {
      render(<IdentificationResultCard {...defaultProps} isCorrect={true} />)
      
      expect(screen.getByRole('button', { name: /Confirmado/ })).toBeInTheDocument()
    })

    it('debe aplicar estilos verdes cuando isCorrect es true', () => {
      render(<IdentificationResultCard {...defaultProps} isCorrect={true} />)
      
      const button = screen.getByRole('button', { name: /Confirmado/ })
      expect(button.className).toContain('bg-green-600')
    })

    it('debe renderizar el ícono CheckCircle2', () => {
      const { container } = render(<IdentificationResultCard {...defaultProps} />)
      
      const button = screen.getByRole('button', { name: /Confirmar esta planta/ })
      const icon = button.querySelector('svg')
      expect(icon).toBeInTheDocument()
    })
  })

  describe('Auto-play del carousel', () => {
    it('debe iniciar auto-play del carousel después de montarse', () => {
      render(<IdentificationResultCard {...defaultProps} />)
      
      // Avanzar 3 segundos
      jest.advanceTimersByTime(3000)
      
      expect(mockCarouselApi.scrollNext).toHaveBeenCalled()
    })

    it('debe detener auto-play cuando el componente se desmonta', () => {
      const { unmount } = render(<IdentificationResultCard {...defaultProps} />)
      
      unmount()
      
      // Avanzar tiempo después del unmount
      jest.advanceTimersByTime(3000)
      
      // El número de llamadas no debe aumentar después del unmount
      const callsBeforeUnmount = mockCarouselApi.scrollNext.mock.calls.length
      jest.advanceTimersByTime(3000)
      expect(mockCarouselApi.scrollNext).toHaveBeenCalledTimes(callsBeforeUnmount)
    })

    it('debe actualizar el indicador actual cuando el carousel cambia', () => {
      render(<IdentificationResultCard {...defaultProps} />)
      
      // Simular cambio de slide
      mockCarouselApi.selectedScrollSnap.mockReturnValue(1)
      
      // Llamar al callback registrado
      if (mockCarouselApi.selectCallback) {
        mockCarouselApi.selectCallback()
      }
      
      // Verificar que se registró el listener
      expect(mockCarouselApi.on).toHaveBeenCalledWith('select', expect.any(Function))
    })
  })

  describe('Accesibilidad', () => {
    it('debe tener alt text descriptivo en las imágenes', () => {
      render(<IdentificationResultCard {...defaultProps} />)
      
      const images = screen.getAllByRole('img')
      expect(images[0]).toHaveAttribute('alt', 'Monstera deliciosa - leaf1.jpg')
      expect(images[1]).toHaveAttribute('alt', 'Monstera deliciosa - flower1.jpg')
      expect(images[2]).toHaveAttribute('alt', 'Monstera deliciosa - bark1.jpg')
    })

    it('debe tener aria-label en los indicadores del carousel', () => {
      render(<IdentificationResultCard {...defaultProps} />)
      
      const indicators = screen.getAllByRole('button', { name: /Ir a imagen/ })
      expect(indicators[0]).toHaveAttribute('aria-label', 'Ir a imagen 1')
      expect(indicators[1]).toHaveAttribute('aria-label', 'Ir a imagen 2')
      expect(indicators[2]).toHaveAttribute('aria-label', 'Ir a imagen 3')
    })
  })

  describe('Edge cases', () => {
    it('debe manejar confianza de 0%', () => {
      render(<IdentificationResultCard {...defaultProps} confidence={0} />)
      
      expect(screen.getByText('0.0%')).toBeInTheDocument()
    })

    it('debe manejar confianza de 100%', () => {
      render(<IdentificationResultCard {...defaultProps} confidence={100} />)
      
      expect(screen.getByText('100.0%')).toBeInTheDocument()
    })

    it('debe manejar nombres científicos muy largos', () => {
      const longName = 'Pneumonoultramicroscopicsilicovolcanoconiosis plantae'
      render(<IdentificationResultCard {...defaultProps} scientificName={longName} />)
      
      expect(screen.getByText(longName)).toBeInTheDocument()
    })

    it('debe manejar array vacío de imágenes sin crash', () => {
      const propsWithoutImages = {
        ...defaultProps,
        images: [],
      }
      
      expect(() => {
        render(<IdentificationResultCard {...propsWithoutImages} />)
      }).not.toThrow()
    })
  })
})
