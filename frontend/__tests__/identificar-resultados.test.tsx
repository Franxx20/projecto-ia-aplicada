/**
 * Tests para la Página de Resultados de Identificación
 * 
 * Suite de pruebas unitarias para validar:
 * - Estados de carga
 * - Manejo de errores
 * - Renderizado de resultados
 * - Navegación
 * - Información de PlantNet
 * 
 * @author Equipo Frontend
 * @date Enero 2026
 * @sprint Sprint 3
 * @task T-023
 */

import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import ResultadosPage from '@/app/identificar/resultados/page'
import plantService from '@/lib/plant.service'
import { IdentificarResponseSimple } from '@/models/plant.types'

// Mock de next/navigation
const mockPush = jest.fn()
const mockGet = jest.fn()

jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: mockPush,
  }),
  useSearchParams: () => ({
    get: mockGet,
  }),
}))

// Mock del plant service
jest.mock('@/lib/plant.service', () => ({
  __esModule: true,
  default: {
    identificarDesdeImagen: jest.fn(),
  },
}))

// Datos de prueba
const mockPlantSimplified: any = {
  nombre_cientifico: 'Monstera deliciosa Liebm.',
  nombre_cientifico_sin_autor: 'Monstera deliciosa',
  autor: 'Liebm.',
  nombres_comunes: ['Costilla de Adán', 'Cerimán', 'Swiss Cheese Plant'],
  genero: 'Monstera',
  familia: 'Araceae',
  score: 0.95,
  confianza_porcentaje: 95,
  gbif_id: '2768084',
  powo_id: '1234567',
}

const mockResultado: IdentificarResponseSimple = {
  identificacion_id: 123,
  especie: mockPlantSimplified,
  confianza: 0.95,
  confianza_porcentaje: '95.0%',
  es_confiable: true,
  mejor_resultado: mockPlantSimplified,
  plantnet_response: {
    query: {
      project: 'all',
      images: ['https://example.com/image.jpg'],
      organs: ['leaf'],
      includeRelatedImages: true,
      noReject: false,
    },
    predictedOrgans: [{
      image: 'https://example.com/image.jpg',
      filename: 'image.jpg',
      organ: 'leaf',
      score: 0.98,
    }],
    bestMatch: 'Monstera deliciosa Liebm.',
    results: [
      {
        score: 0.95,
        species: {
          scientificNameWithoutAuthor: 'Monstera deliciosa',
          scientificName: 'Monstera deliciosa Liebm.',
          scientificNameAuthorship: 'Liebm.',
          genus: {
            scientificNameWithoutAuthor: 'Monstera',
            scientificName: 'Monstera',
          },
          family: {
            scientificNameWithoutAuthor: 'Araceae',
            scientificName: 'Araceae',
          },
          commonNames: ['Costilla de Adán', 'Cerimán', 'Swiss Cheese Plant'],
        },
        gbif: {
          id: '2768084',
        },
        powo: {
          id: '1234567',
        },
      },
      {
        score: 0.75,
        species: {
          scientificNameWithoutAuthor: 'Philodendron bipinnatifidum',
          scientificName: 'Philodendron bipinnatifidum Schott',
          scientificNameAuthorship: 'Schott',
          genus: {
            scientificNameWithoutAuthor: 'Philodendron',
            scientificName: 'Philodendron',
          },
          family: {
            scientificNameWithoutAuthor: 'Araceae',
            scientificName: 'Araceae',
          },
          commonNames: ['Tree Philodendron', 'Selloum'],
        },
      },
    ],
    version: 'v2.1.0',
    remainingIdentificationRequests: 450,
  },
}

describe('ResultadosPage', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    mockGet.mockReturnValue('123') // imagenId por defecto
  })

  describe('Estado de carga', () => {
    it('debe mostrar el indicador de carga mientras identifica', () => {
      const mockIdentificar = jest.fn(() => new Promise(() => {})) // Promise que nunca se resuelve
      ;(plantService.identificarDesdeImagen as jest.Mock).mockImplementation(mockIdentificar)

      render(<ResultadosPage />)

      expect(screen.getByText('Identificando planta...')).toBeInTheDocument()
      expect(screen.getByText(/Estamos analizando tu imagen con PlantNet AI/i)).toBeInTheDocument()
    })

    it('debe mostrar el ícono de carga animado', () => {
      const mockIdentificar = jest.fn(() => new Promise(() => {}))
      ;(plantService.identificarDesdeImagen as jest.Mock).mockImplementation(mockIdentificar)

      const { container } = render(<ResultadosPage />)

      const loader = container.querySelector('.animate-spin')
      expect(loader).toBeInTheDocument()
    })
  })

  describe('Manejo de errores', () => {
    it('debe mostrar error cuando no se proporciona imagenId', async () => {
      mockGet.mockReturnValue(null)

      render(<ResultadosPage />)

      await waitFor(() => {
        expect(screen.getByText('Error al identificar la planta')).toBeInTheDocument()
        expect(screen.getByText('No se proporcionó una imagen para identificar')).toBeInTheDocument()
      })
    })

    it('debe mostrar error cuando falla la identificación', async () => {
      ;(plantService.identificarDesdeImagen as jest.Mock).mockRejectedValue(
        new Error('Error de red')
      )

      render(<ResultadosPage />)

      await waitFor(() => {
        expect(screen.getByText('Error al identificar la planta')).toBeInTheDocument()
        expect(screen.getByText('Error de red')).toBeInTheDocument()
      })
    })

    it('debe mostrar botón para volver a intentar en caso de error', async () => {
      mockGet.mockReturnValue(null)

      render(<ResultadosPage />)

      await waitFor(() => {
        const boton = screen.getByRole('button', { name: /Volver a intentar/i })
        expect(boton).toBeInTheDocument()
      })
    })

    it('debe navegar a /identificar al hacer clic en "Volver a intentar"', async () => {
      mockGet.mockReturnValue(null)

      render(<ResultadosPage />)

      await waitFor(() => {
        const boton = screen.getByRole('button', { name: /Volver a intentar/i })
        fireEvent.click(boton)
      })

      expect(mockPush).toHaveBeenCalledWith('/identificar')
    })
  })

  describe('Renderizado de resultados exitosos', () => {
    beforeEach(() => {
      ;(plantService.identificarDesdeImagen as jest.Mock).mockResolvedValue(mockResultado)
    })

    it('debe renderizar el título de la página', async () => {
      render(<ResultadosPage />)

      await waitFor(() => {
        expect(screen.getByText('Resultados de Identificación')).toBeInTheDocument()
      })
    })

    it('debe renderizar la descripción de PlantNet AI', async () => {
      render(<ResultadosPage />)

      await waitFor(() => {
        expect(screen.getByText('PlantNet AI ha identificado las siguientes especies')).toBeInTheDocument()
      })
    })

    it('debe renderizar el nombre científico del mejor resultado', async () => {
      render(<ResultadosPage />)

      await waitFor(() => {
        expect(screen.getByText('Monstera deliciosa Liebm.')).toBeInTheDocument()
      })
    })

    it('debe renderizar la autoría del nombre científico', async () => {
      render(<ResultadosPage />)

      await waitFor(() => {
        expect(screen.getByText(/Autor: Liebm\./i)).toBeInTheDocument()
      })
    })

    it('debe renderizar los nombres comunes', async () => {
      render(<ResultadosPage />)

      await waitFor(() => {
        expect(screen.getByText('Costilla de Adán')).toBeInTheDocument()
        expect(screen.getByText('Cerimán')).toBeInTheDocument()
        expect(screen.getByText('Swiss Cheese Plant')).toBeInTheDocument()
      })
    })

    it('debe renderizar la familia y el género', async () => {
      render(<ResultadosPage />)

      await waitFor(() => {
        expect(screen.getAllByText('Araceae')).toHaveLength(2) // 2 resultados tienen Araceae
        expect(screen.getByText('Monstera')).toBeInTheDocument()
      })
    })

    it('debe renderizar el porcentaje de confianza formateado', async () => {
      render(<ResultadosPage />)

      await waitFor(() => {
        expect(screen.getByText('95.0%')).toBeInTheDocument()
      })
    })

    it('debe indicar el mejor resultado con un badge', async () => {
      render(<ResultadosPage />)

      await waitFor(() => {
        expect(screen.getByText('(Mejor coincidencia)')).toBeInTheDocument()
      })
    })

    it('debe renderizar múltiples resultados', async () => {
      render(<ResultadosPage />)

      await waitFor(() => {
        expect(screen.getByText('Philodendron bipinnatifidum Schott')).toBeInTheDocument()
        expect(screen.getByText('75.0%')).toBeInTheDocument()
      })
    })

    it('debe renderizar enlaces a GBIF y POWO cuando existen', async () => {
      render(<ResultadosPage />)

      await waitFor(() => {
        const gbifLink = screen.getAllByRole('link', { name: /GBIF/i })[0]
        expect(gbifLink).toHaveAttribute('href', 'https://www.gbif.org/species/2768084')
        expect(gbifLink).toHaveAttribute('target', '_blank')

        const powoLink = screen.getAllByRole('link', { name: /POWO/i })[0]
        expect(powoLink).toHaveAttribute('href', 'https://powo.science.kew.org/taxon/1234567')
      })
    })
  })

  describe('Información de PlantNet', () => {
    beforeEach(() => {
      ;(plantService.identificarDesdeImagen as jest.Mock).mockResolvedValue(mockResultado)
    })

    it('debe renderizar la versión de PlantNet', async () => {
      render(<ResultadosPage />)

      await waitFor(() => {
        expect(screen.getByText(/v2\.1\.0/i)).toBeInTheDocument()
      })
    })

    it('debe renderizar los requests restantes', async () => {
      render(<ResultadosPage />)

      await waitFor(() => {
        expect(screen.getByText(/450/i)).toBeInTheDocument()
      })
    })

    it('debe renderizar el panel informativo sobre niveles de confianza', async () => {
      render(<ResultadosPage />)

      await waitFor(() => {
        expect(screen.getByText('Acerca de estos resultados')).toBeInTheDocument()
        expect(screen.getByText(/Confianza alta \(≥80%\)/i)).toBeInTheDocument()
        expect(screen.getByText(/Confianza media \(60-79%\)/i)).toBeInTheDocument()
        expect(screen.getByText(/Confianza baja \(<60%\)/i)).toBeInTheDocument()
      })
    })

    it('debe renderizar el footer con enlace a PlantNet', async () => {
      render(<ResultadosPage />)

      await waitFor(() => {
        const link = screen.getByRole('link', { name: /PlantNet/i })
        expect(link).toHaveAttribute('href', 'https://plantnet.org')
        expect(link).toHaveAttribute('target', '_blank')
      })
    })
  })

  describe('Navegación', () => {
    beforeEach(() => {
      ;(plantService.identificarDesdeImagen as jest.Mock).mockResolvedValue(mockResultado)
    })

    it('debe renderizar el botón para identificar otra planta (header)', async () => {
      render(<ResultadosPage />)

      await waitFor(() => {
        const botones = screen.getAllByRole('button', { name: /Identificar otra planta/i })
        expect(botones.length).toBeGreaterThan(0)
      })
    })

    it('debe navegar a /identificar al hacer clic en el botón del header', async () => {
      render(<ResultadosPage />)

      await waitFor(async () => {
        const botones = screen.getAllByRole('button', { name: /Identificar otra planta/i })
        fireEvent.click(botones[0])
      })

      expect(mockPush).toHaveBeenCalledWith('/identificar')
    })

    it('debe renderizar el botón grande para identificar otra planta (footer)', async () => {
      render(<ResultadosPage />)

      await waitFor(() => {
        const botones = screen.getAllByRole('button', { name: /Identificar otra planta/i })
        expect(botones.length).toBe(2) // Header + Footer
      })
    })
  })

  describe('Llamadas al servicio', () => {
    it('debe llamar a identificarDesdeImagen con los parámetros correctos', async () => {
      mockGet.mockReturnValue('456')
      ;(plantService.identificarDesdeImagen as jest.Mock).mockResolvedValue(mockResultado)

      render(<ResultadosPage />)

      await waitFor(() => {
        expect(plantService.identificarDesdeImagen).toHaveBeenCalledWith(
          456,
          ['auto'],
          true
        )
      })
    })

    it('debe llamar a identificarDesdeImagen solo una vez', async () => {
      ;(plantService.identificarDesdeImagen as jest.Mock).mockResolvedValue(mockResultado)

      render(<ResultadosPage />)

      await waitFor(() => {
        expect(plantService.identificarDesdeImagen).toHaveBeenCalledTimes(1)
      })
    })
  })

  describe('Accesibilidad', () => {
    beforeEach(() => {
      ;(plantService.identificarDesdeImagen as jest.Mock).mockResolvedValue(mockResultado)
    })

    it('debe tener aria-label en las barras de progreso', async () => {
      render(<ResultadosPage />)

      await waitFor(() => {
        const progressBars = screen.getAllByRole('progressbar')
        expect(progressBars[0]).toHaveAttribute('aria-label', 'Confianza: 95%')
      })
    })

    it('debe abrir enlaces externos en nueva pestaña con rel noopener noreferrer', async () => {
      render(<ResultadosPage />)

      await waitFor(() => {
        const gbifLink = screen.getAllByRole('link', { name: /GBIF/i })[0]
        expect(gbifLink).toHaveAttribute('rel', 'noopener noreferrer')
      })
    })
  })

  describe('Edge cases', () => {
    it('debe manejar resultados sin nombres comunes', async () => {
      const resultadoSinNombres: IdentificarResponseSimple = {
        ...mockResultado,
        plantnet_response: {
          ...mockResultado.plantnet_response,
          results: [
            {
              ...mockResultado.plantnet_response.results[0],
              species: {
                ...mockResultado.plantnet_response.results[0].species,
                commonNames: [],
              },
            },
          ],
        },
      }

      ;(plantService.identificarDesdeImagen as jest.Mock).mockResolvedValue(resultadoSinNombres)

      render(<ResultadosPage />)

      await waitFor(() => {
        expect(screen.queryByText('Nombres comunes:')).not.toBeInTheDocument()
      })
    })

    it('debe manejar resultados sin enlaces GBIF/POWO', async () => {
      const resultadoSinEnlaces: IdentificarResponseSimple = {
        ...mockResultado,
        plantnet_response: {
          ...mockResultado.plantnet_response,
          results: [
            {
              ...mockResultado.plantnet_response.results[0],
              gbif: undefined,
              powo: undefined,
            },
          ],
        },
      }

      ;(plantService.identificarDesdeImagen as jest.Mock).mockResolvedValue(resultadoSinEnlaces)

      render(<ResultadosPage />)

      await waitFor(() => {
        expect(screen.queryByText(/Enlaces externos:/i)).not.toBeInTheDocument()
      })
    })

    it('debe limitar los nombres comunes a 5', async () => {
      const resultadoMuchosNombres: IdentificarResponseSimple = {
        ...mockResultado,
        plantnet_response: {
          ...mockResultado.plantnet_response,
          results: [
            {
              ...mockResultado.plantnet_response.results[0],
              species: {
                ...mockResultado.plantnet_response.results[0].species,
                commonNames: ['Nombre1', 'Nombre2', 'Nombre3', 'Nombre4', 'Nombre5', 'Nombre6', 'Nombre7'],
              },
            },
          ],
        },
      }

      ;(plantService.identificarDesdeImagen as jest.Mock).mockResolvedValue(resultadoMuchosNombres)

      render(<ResultadosPage />)

      await waitFor(() => {
        expect(screen.getByText('Nombre1')).toBeInTheDocument()
        expect(screen.getByText('Nombre5')).toBeInTheDocument()
        expect(screen.queryByText('Nombre6')).not.toBeInTheDocument()
      })
    })

    it('debe limitar los resultados a 10', async () => {
      const muchosResultados: IdentificarResponseSimple = {
        ...mockResultado,
        plantnet_response: {
          ...mockResultado.plantnet_response,
          results: Array(15).fill(mockResultado.plantnet_response.results[0]).map((r, i) => ({
            ...r,
            score: 0.9 - i * 0.05,
          })),
        },
      }

      ;(plantService.identificarDesdeImagen as jest.Mock).mockResolvedValue(muchosResultados)

      render(<ResultadosPage />)

      await waitFor(() => {
        const resultCards = screen.getAllByText(/#\d+/)
        expect(resultCards).toHaveLength(10)
      })
    })
  })
})
