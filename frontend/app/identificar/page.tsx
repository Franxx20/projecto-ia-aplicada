/**
 * page.tsx - Página de identificación de plantas
 * 
 * Permite a los usuarios:
 * - Subir fotos de plantas
 * - Identificar especies mediante PlantNet API
 * - Ver resultados de identificación
 * 
 * @author GitHub Copilot
 * @date 2025-10-12
 * @updated 2025-10-12 - T-017: Integración con PlantNet API
 */

'use client'

import React, { useState } from 'react'
import { useRouter } from 'next/navigation'
import { ArrowLeft, Sparkles, AlertCircle, Loader2 } from 'lucide-react'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { MultipleImageUpload } from '@/components/MultipleImageUpload'
import plantService from '@/lib/plant.service'
import type { OrganType } from '@/models/plant.types'

/**
 * Interfaz para imagen con órgano seleccionado
 */
interface ImagenConOrgano {
  id: string
  archivo: File
  previewUrl: string
  organ: OrganType
  tamano: number
}

/**
 * Página de identificación de plantas
 * 
 * Componente principal que integra el upload de múltiples imágenes
 * y la identificación de plantas usando PlantNet API
 */
export default function IdentificarPage() {
  const router = useRouter()
  const [imagenesSeleccionadas, setImagenesSeleccionadas] = useState<ImagenConOrgano[]>([])
  const [estaIdentificando, setEstaIdentificando] = useState(false)
  const [progresoUpload, setProgresoUpload] = useState(0)
  const [errorIdentificacion, setErrorIdentificacion] = useState<string | null>(null)

  /**
   * Maneja la selección de múltiples imágenes
   */
  const handleImagenesSeleccionadas = (imagenes: ImagenConOrgano[]) => {
    setImagenesSeleccionadas(imagenes)
    setErrorIdentificacion(null)
  }

  /**
   * Inicia el proceso de identificación con múltiples imágenes
   * usando PlantNet API a través del backend
   */
  const identificarPlanta = async () => {
    if (imagenesSeleccionadas.length === 0) {
      setErrorIdentificacion('Debes seleccionar al menos una imagen')
      return
    }

    setEstaIdentificando(true)
    setErrorIdentificacion(null)
    setProgresoUpload(0)

    try {
      // Extraer archivos y órganos
      const archivos = imagenesSeleccionadas.map(img => img.archivo)
      const organos = imagenesSeleccionadas.map(img => img.organ)

      console.log('Identificando planta con:', {
        cantidadImagenes: archivos.length,
        organos: organos,
      })

      // Llamar al servicio de identificación con múltiples imágenes
      const respuesta = await plantService.identificarDesdeMultiplesImagenes(
        archivos,
        organos,
        true, // guardar resultado
        (progreso: number) => {
          setProgresoUpload(progreso)
          console.log(`Progreso de upload: ${progreso}%`)
        }
      )

      console.log('Identificación exitosa:', respuesta)

      // Navegar a la página de resultados con el ID de identificación
      router.push(`/identificar/resultados?identificacionId=${respuesta.id}`)
    } catch (error) {
      console.error('Error al identificar planta:', error)
      const mensaje = error instanceof Error ? error.message : 'Error al identificar la planta'
      setErrorIdentificacion(mensaje)
      setEstaIdentificando(false)
      setProgresoUpload(0)
    }
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-card sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center gap-4">
          <Button variant="ghost" size="icon" asChild>
            <Link href="/dashboard">
              <ArrowLeft className="w-5 h-5" />
            </Link>
          </Button>
          <div>
            <h1 className="text-2xl font-bold">Identificar Planta</h1>
            <p className="text-sm text-muted-foreground">
              Sube una foto y descubre qué planta es
            </p>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 py-8">
        <div className="space-y-6">
          {/* Card principal */}
          <Card>
            <CardHeader className="text-center">
              <CardTitle className="text-2xl flex items-center justify-center gap-2">
                <Sparkles className="w-6 h-6 text-primary" />
                Identificación con IA
              </CardTitle>
              <CardDescription className="text-base">
                Usa nuestra tecnología de inteligencia artificial para identificar
                más de 71,000 especies de plantas con un 90-95% de precisión
              </CardDescription>
            </CardHeader>

            <CardContent className="space-y-6">
              {/* Componente de upload múltiple */}
              <MultipleImageUpload
                maxImagenes={5}
                onImagenesSeleccionadas={handleImagenesSeleccionadas}
                organPorDefecto="sin_especificar"
              />

              {/* Mensaje de error si existe */}
              {errorIdentificacion && (
                <div className="p-4 bg-red-50 border border-red-200 rounded-lg flex items-start space-x-3">
                  <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                  <div>
                    <h3 className="font-semibold text-red-900 mb-1">Error al identificar</h3>
                    <p className="text-sm text-red-700">{errorIdentificacion}</p>
                  </div>
                </div>
              )}

              {/* Botón de identificación */}
              {imagenesSeleccionadas.length > 0 && (
                <Button
                  size="lg"
                  className="w-full"
                  onClick={identificarPlanta}
                  disabled={estaIdentificando}
                >
                  {estaIdentificando ? (
                    <>
                      <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                      Identificando Planta... {progresoUpload > 0 && `${progresoUpload}%`}
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-5 h-5 mr-2" />
                      Identificar Planta
                    </>
                  )}
                </Button>
              )}
            </CardContent>
          </Card>

          {/* Información adicional */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Cómo funciona</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 md:grid-cols-3">
                <div className="space-y-2">
                  <div className="flex items-center justify-center w-10 h-10 rounded-full bg-primary/10 text-primary font-bold">
                    1
                  </div>
                  <h3 className="font-semibold">Sube una foto</h3>
                  <p className="text-sm text-muted-foreground">
                    Toma o selecciona una foto clara de tu planta
                  </p>
                </div>

                <div className="space-y-2">
                  <div className="flex items-center justify-center w-10 h-10 rounded-full bg-primary/10 text-primary font-bold">
                    2
                  </div>
                  <h3 className="font-semibold">Análisis IA</h3>
                  <p className="text-sm text-muted-foreground">
                    Nuestra IA analiza las características de la planta
                  </p>
                </div>

                <div className="space-y-2">
                  <div className="flex items-center justify-center w-10 h-10 rounded-full bg-primary/10 text-primary font-bold">
                    3
                  </div>
                  <h3 className="font-semibold">Resultados</h3>
                  <p className="text-sm text-muted-foreground">
                    Obtén el nombre científico, cuidados y más información
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Powered by */}
          <div className="text-center text-sm text-muted-foreground">
            <p>Powered by PlantNet API • 71,000+ especies • 90-95% precisión</p>
          </div>
        </div>
      </main>
    </div>
  )
}
