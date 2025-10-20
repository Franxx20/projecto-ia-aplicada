/**
 * Tests para PlantService
 * 
 * Suite de pruebas de integración para validar:
 * - Método identificarDesdeMultiplesImagenes
 * - Validación de parámetros
 * - Construcción de FormData
 * - Progreso de upload
 * - Manejo de errores
 * 
 * @author Equipo Frontend
 * @date Enero 2026
 * @sprint Sprint 3
 * @task T-023
 */

import plantService from '@/lib/plant.service'
import axios from '@/lib/axios'
import { IdentificarResponse, OrganType } from '@/models/plant.types'

// Mock de axios
jest.mock('@/lib/axios')
const mockedAxios = axios as jest.Mocked<typeof axios>

// Helper para crear archivos de prueba
const crearArchivoMock = (nombre: string, tamano: number = 1024): File => {
  const contenido = new Array(tamano).fill('a').join('')
  const blob = new Blob([contenido], { type: 'image/jpeg' })
  return new File([blob], nombre, { type: 'image/jpeg' })
}

// Datos de respuesta mock
const mockRespuesta: IdentificarResponse = {
  id: 456,
  usuario_id: 1,
  cantidad_imagenes: 3,
  origen: 'multiple',
  proyecto_usado: 'all',
  confianza: 0.95,
  fecha_identificacion: '2026-01-15T10:30:00Z',
  imagenes: [
    {
      id: 1,
      nombre_archivo: 'leaf1.jpg',
      url_blob: 'https://example.com/leaf1.jpg',
      organ: 'leaf',
      tamano_bytes: 102400,
    },
    {
      id: 2,
      nombre_archivo: 'flower1.jpg',
      url_blob: 'https://example.com/flower1.jpg',
      organ: 'flower',
      tamano_bytes: 204800,
    },
    {
      id: 3,
      nombre_archivo: 'bark1.jpg',
      url_blob: 'https://example.com/bark1.jpg',
      organ: 'bark',
      tamano_bytes: 153600,
    },
  ],
  resultados: {
    query: {
      project: 'all',
      images: ['https://example.com/leaf1.jpg'],
      organs: ['leaf', 'flower', 'bark'],
      includeRelatedImages: true,
      noReject: false,
    },
    predictedOrgans: [],
    bestMatch: 'Monstera deliciosa',
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
          commonNames: ['Costilla de Adán'],
        },
      },
    ],
    version: 'v2.1.0',
    remainingIdentificationRequests: 450,
  },
}

describe('PlantService - identificarDesdeMultiplesImagenes', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('Validación de parámetros', () => {
    it('debe rechazar si no se proporciona ningún archivo', async () => {
      const archivos: File[] = []
      const organos: OrganType[] = []

      await expect(
        plantService.identificarDesdeMultiplesImagenes(archivos, organos)
      ).rejects.toThrow('Debe proporcionar entre 1 y 5 imágenes')
    })

    it('debe rechazar si se proporcionan más de 5 archivos', async () => {
      const archivos = [
        crearArchivoMock('img1.jpg'),
        crearArchivoMock('img2.jpg'),
        crearArchivoMock('img3.jpg'),
        crearArchivoMock('img4.jpg'),
        crearArchivoMock('img5.jpg'),
        crearArchivoMock('img6.jpg'),
      ]
      const organos: OrganType[] = ['leaf', 'leaf', 'leaf', 'leaf', 'leaf', 'leaf']

      await expect(
        plantService.identificarDesdeMultiplesImagenes(archivos, organos)
      ).rejects.toThrow('Debe proporcionar entre 1 y 5 imágenes')
    })

    it('debe rechazar si el número de órganos no coincide con el número de archivos', async () => {
      const archivos = [
        crearArchivoMock('img1.jpg'),
        crearArchivoMock('img2.jpg'),
      ]
      const organos: OrganType[] = ['leaf'] // Solo 1 órgano para 2 archivos

      await expect(
        plantService.identificarDesdeMultiplesImagenes(archivos, organos)
      ).rejects.toThrow('Debe proporcionar un órgano por cada imagen')
    })

    it('debe aceptar 1 archivo con 1 órgano', async () => {
      const archivos = [crearArchivoMock('img1.jpg')]
      const organos: OrganType[] = ['leaf']

      mockedAxios.post.mockResolvedValue({ data: mockRespuesta })

      await expect(
        plantService.identificarDesdeMultiplesImagenes(archivos, organos)
      ).resolves.toBeDefined()
    })

    it('debe aceptar 5 archivos con 5 órganos', async () => {
      const archivos = [
        crearArchivoMock('img1.jpg'),
        crearArchivoMock('img2.jpg'),
        crearArchivoMock('img3.jpg'),
        crearArchivoMock('img4.jpg'),
        crearArchivoMock('img5.jpg'),
      ]
      const organos: OrganType[] = ['leaf', 'flower', 'fruit', 'bark', 'habit']

      mockedAxios.post.mockResolvedValue({ data: mockRespuesta })

      await expect(
        plantService.identificarDesdeMultiplesImagenes(archivos, organos)
      ).resolves.toBeDefined()
    })
  })

  describe('Construcción de FormData', () => {
    it('debe agregar todos los archivos al FormData', async () => {
      const archivos = [
        crearArchivoMock('leaf.jpg'),
        crearArchivoMock('flower.jpg'),
        crearArchivoMock('bark.jpg'),
      ]
      const organos: OrganType[] = ['leaf', 'flower', 'bark']

      mockedAxios.post.mockResolvedValue({ data: mockRespuesta })

      await plantService.identificarDesdeMultiplesImagenes(archivos, organos)

      expect(mockedAxios.post).toHaveBeenCalledWith(
        '/api/identificar/multiple',
        expect.any(FormData),
        expect.objectContaining({
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        })
      )

      // Verificar que se llamó con FormData
      const llamada = mockedAxios.post.mock.calls[0]
      expect(llamada[1]).toBeInstanceOf(FormData)
    })

    it('debe agregar los órganos como string separado por comas', async () => {
      const archivos = [
        crearArchivoMock('img1.jpg'),
        crearArchivoMock('img2.jpg'),
      ]
      const organos: OrganType[] = ['leaf', 'flower']

      mockedAxios.post.mockResolvedValue({ data: mockRespuesta })

      await plantService.identificarDesdeMultiplesImagenes(archivos, organos)

      const formData = mockedAxios.post.mock.calls[0][1] as FormData
      expect(formData.get('organos')).toBe('leaf,flower')
    })

    it('debe agregar guardar_resultado como string "true" por defecto', async () => {
      const archivos = [crearArchivoMock('img1.jpg')]
      const organos: OrganType[] = ['leaf']

      mockedAxios.post.mockResolvedValue({ data: mockRespuesta })

      await plantService.identificarDesdeMultiplesImagenes(archivos, organos)

      const formData = mockedAxios.post.mock.calls[0][1] as FormData
      expect(formData.get('guardar_resultado')).toBe('true')
    })

    it('debe agregar guardar_resultado como string "false" cuando se especifica', async () => {
      const archivos = [crearArchivoMock('img1.jpg')]
      const organos: OrganType[] = ['leaf']

      mockedAxios.post.mockResolvedValue({ data: mockRespuesta })

      await plantService.identificarDesdeMultiplesImagenes(archivos, organos, false)

      const formData = mockedAxios.post.mock.calls[0][1] as FormData
      expect(formData.get('guardar_resultado')).toBe('false')
    })
  })

  describe('Callback de progreso', () => {
    it('debe llamar al callback de progreso durante el upload', async () => {
      const archivos = [crearArchivoMock('img1.jpg', 10000)]
      const organos: OrganType[] = ['leaf']
      const onProgress = jest.fn()

      mockedAxios.post.mockImplementation((url, data, config) => {
        // Simular progreso del upload
        if (config?.onUploadProgress) {
          config.onUploadProgress({ loaded: 5000, total: 10000 } as any)
          config.onUploadProgress({ loaded: 10000, total: 10000 } as any)
        }
        return Promise.resolve({ data: mockRespuesta })
      })

      await plantService.identificarDesdeMultiplesImagenes(
        archivos,
        organos,
        true,
        onProgress
      )

      expect(onProgress).toHaveBeenCalledWith(50)
      expect(onProgress).toHaveBeenCalledWith(100)
      expect(onProgress).toHaveBeenCalledTimes(2)
    })

    it('no debe fallar si no se proporciona callback de progreso', async () => {
      const archivos = [crearArchivoMock('img1.jpg')]
      const organos: OrganType[] = ['leaf']

      mockedAxios.post.mockImplementation((url, data, config) => {
        if (config?.onUploadProgress) {
          config.onUploadProgress({ loaded: 1000, total: 1000 } as any)
        }
        return Promise.resolve({ data: mockRespuesta })
      })

      await expect(
        plantService.identificarDesdeMultiplesImagenes(archivos, organos)
      ).resolves.toBeDefined()
    })

    it('debe manejar progreso sin total definido', async () => {
      const archivos = [crearArchivoMock('img1.jpg')]
      const organos: OrganType[] = ['leaf']
      const onProgress = jest.fn()

      mockedAxios.post.mockImplementation((url, data, config) => {
        if (config?.onUploadProgress) {
          // Simular evento sin total
          config.onUploadProgress({ loaded: 5000 } as any)
        }
        return Promise.resolve({ data: mockRespuesta })
      })

      await plantService.identificarDesdeMultiplesImagenes(
        archivos,
        organos,
        true,
        onProgress
      )

      // No debe llamar al callback si no hay total
      expect(onProgress).not.toHaveBeenCalled()
    })
  })

  describe('Respuesta exitosa', () => {
    it('debe retornar los datos de la respuesta correctamente', async () => {
      const archivos = [
        crearArchivoMock('leaf.jpg'),
        crearArchivoMock('flower.jpg'),
        crearArchivoMock('bark.jpg'),
      ]
      const organos: OrganType[] = ['leaf', 'flower', 'bark']

      mockedAxios.post.mockResolvedValue({ data: mockRespuesta })

      const resultado = await plantService.identificarDesdeMultiplesImagenes(
        archivos,
        organos
      )

      expect(resultado).toEqual(mockRespuesta)
      expect(resultado.cantidad_imagenes).toBe(3)
      expect(resultado.imagenes).toHaveLength(3)
      expect(resultado.confianza).toBe(0.95)
    })

    it('debe incluir información de todas las imágenes', async () => {
      const archivos = [
        crearArchivoMock('leaf.jpg'),
        crearArchivoMock('flower.jpg'),
      ]
      const organos: OrganType[] = ['leaf', 'flower']

      mockedAxios.post.mockResolvedValue({ data: mockRespuesta })

      const resultado = await plantService.identificarDesdeMultiplesImagenes(
        archivos,
        organos
      )

      expect(resultado.imagenes[0].organ).toBe('leaf')
      expect(resultado.imagenes[1].organ).toBe('flower')
      expect(resultado.imagenes[0].nombre_archivo).toBe('leaf1.jpg')
      expect(resultado.imagenes[1].nombre_archivo).toBe('flower1.jpg')
    })
  })

  describe('Manejo de errores', () => {
    it('debe lanzar error cuando hay problema en el servidor', async () => {
      const archivos = [crearArchivoMock('img1.jpg')]
      const organos: OrganType[] = ['leaf']

      mockedAxios.post.mockRejectedValue(new Error('Imagen demasiado grande'))

      await expect(
        plantService.identificarDesdeMultiplesImagenes(archivos, organos)
      ).rejects.toThrow('Imagen demasiado grande')
    })

    it('debe lanzar error cuando falla la red', async () => {
      const archivos = [crearArchivoMock('img1.jpg')]
      const organos: OrganType[] = ['leaf']

      mockedAxios.post.mockRejectedValue(new Error('Network Error'))

      await expect(
        plantService.identificarDesdeMultiplesImagenes(archivos, organos)
      ).rejects.toThrow('Network Error')
    })

    it('debe manejar errores durante el upload', async () => {
      const archivos = [crearArchivoMock('img1.jpg')]
      const organos: OrganType[] = ['leaf']

      mockedAxios.post.mockRejectedValue(new Error('Upload failed'))

      await expect(
        plantService.identificarDesdeMultiplesImagenes(archivos, organos)
      ).rejects.toThrow()
    })

    it('debe manejar cuando el servidor devuelve error 500', async () => {
      const archivos = [crearArchivoMock('img1.jpg', 20 * 1024 * 1024)] // 20MB
      const organos: OrganType[] = ['leaf']

      mockedAxios.post.mockRejectedValue(new Error('Server error'))

      await expect(
        plantService.identificarDesdeMultiplesImagenes(archivos, organos)
      ).rejects.toThrow()
    })
  })

  describe('Diferentes tipos de órganos', () => {
    it('debe aceptar todos los tipos de órganos válidos', async () => {
      const todosLosOrganos: OrganType[] = [
        'auto',
        'leaf',
        'flower',
        'fruit',
        'bark',
        'habit',
        'other',
        'sin_especificar',
      ]

      for (const organ of todosLosOrganos) {
        const archivos = [crearArchivoMock(`${organ}.jpg`)]
        const organos: OrganType[] = [organ]

        mockedAxios.post.mockResolvedValue({ data: mockRespuesta })

        await expect(
          plantService.identificarDesdeMultiplesImagenes(archivos, organos)
        ).resolves.toBeDefined()
      }
    })

    it('debe permitir mezclar diferentes tipos de órganos', async () => {
      const archivos = [
        crearArchivoMock('img1.jpg'),
        crearArchivoMock('img2.jpg'),
        crearArchivoMock('img3.jpg'),
        crearArchivoMock('img4.jpg'),
      ]
      const organos: OrganType[] = ['leaf', 'flower', 'fruit', 'bark']

      mockedAxios.post.mockResolvedValue({ data: mockRespuesta })

      const resultado = await plantService.identificarDesdeMultiplesImagenes(
        archivos,
        organos
      )

      expect(resultado).toBeDefined()
    })
  })

  describe('Edge cases', () => {
    it('debe manejar archivos con nombres especiales', async () => {
      const archivos = [
        crearArchivoMock('imagen con espacios.jpg'),
        crearArchivoMock('imagen-con-guiones.jpg'),
        crearArchivoMock('imagen_con_guiones_bajos.jpg'),
      ]
      const organos: OrganType[] = ['leaf', 'flower', 'bark']

      mockedAxios.post.mockResolvedValue({ data: mockRespuesta })

      await expect(
        plantService.identificarDesdeMultiplesImagenes(archivos, organos)
      ).resolves.toBeDefined()
    })

    it('debe manejar archivos de diferentes tamaños', async () => {
      const archivos = [
        crearArchivoMock('pequeña.jpg', 1024), // 1KB
        crearArchivoMock('mediana.jpg', 100 * 1024), // 100KB
        crearArchivoMock('grande.jpg', 5 * 1024 * 1024), // 5MB
      ]
      const organos: OrganType[] = ['leaf', 'flower', 'bark']

      mockedAxios.post.mockResolvedValue({ data: mockRespuesta })

      await expect(
        plantService.identificarDesdeMultiplesImagenes(archivos, organos)
      ).resolves.toBeDefined()
    })

    it('debe manejar respuesta con imagenes vacías', async () => {
      const archivos = [crearArchivoMock('img1.jpg')]
      const organos: OrganType[] = ['leaf']

      const respuestaVacia: IdentificarResponse = {
        ...mockRespuesta,
        imagenes: [],
        cantidad_imagenes: 0,
      }

      mockedAxios.post.mockResolvedValue({ data: respuestaVacia })

      const resultado = await plantService.identificarDesdeMultiplesImagenes(
        archivos,
        organos
      )

      expect(resultado.cantidad_imagenes).toBe(0)
      expect(resultado.imagenes).toHaveLength(0)
    })
  })
})
