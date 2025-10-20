/**
 * IdentificationResultCard Component
 * 
 * Tarjeta para mostrar un resultado de identificación de plantas con:
 * - Carousel de múltiples imágenes con organ labels
 * - Información científica (nombre, género, familia)
 * - Badge de nivel de confianza
 * - Botón de confirmación
 * 
 * @author Equipo Frontend
 * @date Enero 2026
 * @sprint Sprint 3
 * @task T-023
 */

"use client"

import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Carousel, CarouselContent, CarouselItem, type CarouselApi } from "@/components/ui/carousel"
import { CheckCircle2, Leaf } from "lucide-react"
import { cn } from "@/lib/utils"
import { useEffect, useState } from "react"
import { ImagenIdentificacionResponse, NOMBRES_ORGANOS } from "@/models/plant.types"

interface IdentificationResultCardProps {
  scientificName: string
  commonName: string
  genus: string
  family: string
  confidence: number
  images: ImagenIdentificacionResponse[]
  isCorrect?: boolean
  onConfirm?: () => void
}

export function IdentificationResultCard({
  scientificName,
  commonName,
  genus,
  family,
  confidence,
  images,
  isCorrect = false,
  onConfirm,
}: IdentificationResultCardProps) {
  const [api, setApi] = useState<CarouselApi>()
  const [current, setCurrent] = useState(0)

  useEffect(() => {
    if (!api) return

    setCurrent(api.selectedScrollSnap())

    const intervalId = setInterval(() => {
      api.scrollNext()
    }, 3000)

    api.on("select", () => {
      setCurrent(api.selectedScrollSnap())
    })

    return () => clearInterval(intervalId)
  }, [api])

  return (
    <Card className="overflow-hidden">
      <div className="p-6 space-y-4">
        {/* Header with confidence and names */}
        <div className="space-y-3">
          <div className="flex items-center gap-3">
            <div className="bg-primary/10 rounded-full p-2 flex items-center justify-center">
              <Leaf className="w-5 h-5 text-primary" />
            </div>
            <Badge variant="secondary" className="text-base font-semibold">
              {confidence.toFixed(1)}%
            </Badge>
            <h3 className="text-2xl font-semibold text-primary italic flex-1">{scientificName}</h3>
          </div>

          {/* Metadata row */}
          <div className="grid grid-cols-3 gap-4 text-sm">
            <div>
              <p className="text-muted-foreground uppercase text-xs mb-1">Nombre Común</p>
              <p className="font-medium">{commonName}</p>
            </div>
            <div>
              <p className="text-muted-foreground uppercase text-xs mb-1">Género</p>
              <p className="font-medium italic">{genus}</p>
            </div>
            <div>
              <p className="text-muted-foreground uppercase text-xs mb-1">Familia</p>
              <p className="font-medium italic">{family}</p>
            </div>
          </div>
        </div>

        {/* Carousel de imágenes con organ labels */}
        <div className="relative">
          <Carousel
            setApi={setApi}
            opts={{
              align: "center",
              loop: true,
            }}
            className="w-full"
          >
            <CarouselContent>
              {images.map((imagen, index) => (
                <CarouselItem key={imagen.id}>
                  <div className="space-y-2">
                    <div className="aspect-[4/3] rounded-lg overflow-hidden bg-muted relative">
                      <img
                        src={imagen.url_blob || "/placeholder.svg"}
                        alt={`${scientificName} - ${imagen.nombre_archivo}`}
                        className="w-full h-full object-cover"
                      />
                      {/* Organ badge en la imagen */}
                      {imagen.organ && (
                        <Badge 
                          className="absolute top-2 right-2 bg-black/70 text-white hover:bg-black/80"
                          variant="secondary"
                        >
                          {NOMBRES_ORGANOS[imagen.organ as keyof typeof NOMBRES_ORGANOS] || imagen.organ}
                        </Badge>
                      )}
                    </div>
                    {/* Información de la imagen */}
                    <div className="flex items-center justify-between text-xs text-muted-foreground px-1">
                      <span>{imagen.nombre_archivo}</span>
                      <span>{(imagen.tamano_bytes / 1024).toFixed(1)} KB</span>
                    </div>
                  </div>
                </CarouselItem>
              ))}
            </CarouselContent>
          </Carousel>
          
          {/* Indicadores de carousel */}
          {images.length > 1 && (
            <div className="flex justify-center gap-2 mt-3">
              {images.map((img, index) => (
                <button
                  key={`indicator-${img.id}`}
                  className={cn(
                    "w-2 h-2 rounded-full transition-all",
                    index === current 
                      ? "bg-primary w-4" 
                      : "bg-muted-foreground/30"
                  )}
                  onClick={() => api?.scrollTo(index)}
                  aria-label={`Ir a imagen ${index + 1}`}
                />
              ))}
            </div>
          )}
        </div>

        <Button
          onClick={onConfirm}
          size="lg"
          className={cn(
            "w-full text-base font-semibold shadow-lg transition-all",
            isCorrect
              ? "bg-green-600 hover:bg-green-700 text-white"
              : "bg-primary hover:bg-primary/90 hover:shadow-xl hover:scale-[1.02]",
          )}
        >
          <CheckCircle2 className="w-5 h-5 mr-2" />
          {isCorrect ? "Confirmado" : "Confirmar esta planta"}
        </Button>
      </div>
    </Card>
  )
}
