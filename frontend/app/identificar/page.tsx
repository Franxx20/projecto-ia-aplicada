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
 */

'use client'

import React, { useState } from 'react'
import { useRouter } from 'next/navigation'
import { ArrowLeft, Sparkles } from 'lucide-react'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import ImageUpload from '@/components/ImageUpload'
import type { ImageUploadResponse } from '@/models/image.types'

/**
 * Página de identificación de plantas
 * 
 * Componente principal que integra el upload de imágenes
 * y la identificación de plantas usando PlantNet API
 */
export default function IdentificarPage() {
  const router = useRouter()
  const [imagenSubida, setImagenSubida] = useState<ImageUploadResponse | null>(null)
  const [estaIdentificando, setEstaIdentificando] = useState(false)

  /**
   * Maneja el éxito del upload de imagen
   * y procede a identificar la planta
   */
  const handleUploadSuccess = async (response: ImageUploadResponse) => {
    console.log('Imagen subida exitosamente:', response)
    setImagenSubida(response)

    // Aquí podrías llamar automáticamente a la API de identificación
    // Por ahora, solo guardamos la imagen y mostramos el botón
  }

  /**
   * Maneja errores en el upload
   */
  const handleUploadError = (error: Error) => {
    console.error('Error al subir imagen:', error)
    // El componente ImageUpload ya muestra el error
  }

  /**
   * Inicia el proceso de identificación de la planta
   */
  const identificarPlanta = async () => {
    if (!imagenSubida) return

    setEstaIdentificando(true)

    try {
      // TODO: Implementar llamada a la API de PlantNet (T-017)
      // Por ahora, mostramos un mensaje de que la funcionalidad está en desarrollo
      
      // Simular delay de API
      await new Promise(resolve => setTimeout(resolve, 2000))

      // Mostrar mensaje temporal
      alert('✅ Imagen subida correctamente!\n\n🚧 La identificación con PlantNet API está en desarrollo (Tarea T-017).\n\nPor ahora, la imagen se guardó exitosamente en el servidor.')
      
      setEstaIdentificando(false)

      // Comentado: Navegar a la página de resultados
      // router.push('/identificar/resultados?imageId=' + imagenSubida.id)
    } catch (error) {
      console.error('Error al identificar planta:', error)
      setEstaIdentificando(false)
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
              {/* Componente de upload */}
              <ImageUpload
                autoUpload={true}
                onUploadSuccess={handleUploadSuccess}
                onUploadError={handleUploadError}
                showCameraCapture={true}
                showTips={true}
              />

              {/* Botón de identificación */}
              {imagenSubida && (
                <div className="pt-4">
                  <Button
                    size="lg"
                    className="w-full"
                    onClick={identificarPlanta}
                    disabled={estaIdentificando}
                  >
                    {estaIdentificando ? (
                      <>
                        <Sparkles className="w-5 h-5 mr-2 animate-pulse" />
                        Identificando Planta...
                      </>
                    ) : (
                      <>
                        <Sparkles className="w-5 h-5 mr-2" />
                        Identificar Planta
                      </>
                    )}
                  </Button>
                </div>
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
