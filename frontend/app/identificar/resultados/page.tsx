'use client';

/**
 * Página de Resultados de Identificación de Plantas (T-023)
 * 
 * Actualizada para soportar múltiples imágenes con visualización en carousel
 * y función de confirmación para agregar plantas al jardín del usuario.
 * 
 * @author Equipo Frontend
 * @date Enero 2026
 * @sprint Sprint 3
 * @task T-023
 */

import { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  ArrowLeft, 
  Leaf, 
  CheckCircle2, 
  AlertCircle, 
  Info,
  ExternalLink,
  Loader2,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';
import {
  IdentificarResponse,
  PlantNetResult,
  obtenerColorConfianza,
  obtenerNivelConfianza,
  formatearConfianza,
  ImagenIdentificacionResponse
} from '@/models/plant.types';
import plantService from '@/lib/plant.service';
import { useToast } from '@/hooks/use-toast';

/**
 * Componente de carrusel automático para imágenes de referencia
 */
interface CarruselImagenesProps {
  readonly imagenes: any[];
  readonly especieNombre: string;
}

function CarruselImagenes({ imagenes, especieNombre }: CarruselImagenesProps) {
  const [indiceActual, setIndiceActual] = useState(0);
  
  // Auto-avanzar el carrusel cada 3 segundos
  useEffect(() => {
    if (imagenes.length <= 1) return;
    
    const intervalo = setInterval(() => {
      setIndiceActual((prev) => (prev + 1) % imagenes.length);
    }, 3000);
    
    return () => clearInterval(intervalo);
  }, [imagenes.length]);
  
  if (imagenes.length === 0) return null;
  
  const imagenActual = imagenes[indiceActual];
  
  const siguiente = () => {
    setIndiceActual((prev) => (prev + 1) % imagenes.length);
  };
  
  const anterior = () => {
    setIndiceActual((prev) => 
      prev === 0 ? imagenes.length - 1 : prev - 1
    );
  };
  
  return (
    <div className="pt-3 border-t">
      <p className="text-sm font-medium text-gray-700 mb-3">
        Imágenes de referencia ({indiceActual + 1}/{imagenes.length}):
      </p>
      
      <div className="relative group">
        {/* Imagen principal */}
        <div className="relative aspect-video rounded-lg overflow-hidden bg-gray-100 border border-gray-200">
          <img
            src={imagenActual.url.m}
            alt={`${especieNombre} - ${imagenActual.organ}`}
            className="w-full h-full object-contain"
          />
          
          {/* Botones de navegación */}
          {imagenes.length > 1 && (
            <>
              <button
                type="button"
                onClick={anterior}
                className="absolute left-2 top-1/2 -translate-y-1/2 bg-black/50 hover:bg-black/70 text-white rounded-full p-2 transition-all opacity-0 group-hover:opacity-100"
                aria-label="Imagen anterior"
              >
                <ChevronLeft className="w-5 h-5" />
              </button>
              
              <button
                type="button"
                onClick={siguiente}
                className="absolute right-2 top-1/2 -translate-y-1/2 bg-black/50 hover:bg-black/70 text-white rounded-full p-2 transition-all opacity-0 group-hover:opacity-100"
                aria-label="Siguiente imagen"
              >
                <ChevronRight className="w-5 h-5" />
              </button>
            </>
          )}
          
          {/* Badge del tipo de órgano */}
          <div className="absolute bottom-3 left-3 px-3 py-1.5 bg-black/70 text-white text-sm rounded-full font-medium capitalize">
            {imagenActual.organ}
          </div>
          
          {/* Botón para ver imagen completa */}
          <button
            type="button"
            onClick={() => window.open(imagenActual.url.o, '_blank')}
            className="absolute top-3 right-3 bg-black/50 hover:bg-black/70 text-white rounded-full p-2 transition-all opacity-0 group-hover:opacity-100"
            aria-label="Ver imagen completa"
          >
            <ExternalLink className="w-4 h-4" />
          </button>
        </div>
        
        {/* Indicadores de posición */}
        {imagenes.length > 1 && (
          <div className="flex justify-center gap-1.5 mt-3">
            {imagenes.map((img, idx) => (
              <button
                key={`indicator-${img.organ}-${idx}`}
                type="button"
                onClick={() => setIndiceActual(idx)}
                className={`h-1.5 rounded-full transition-all ${
                  idx === indiceActual 
                    ? 'w-6 bg-primary' 
                    : 'w-1.5 bg-gray-300 hover:bg-gray-400'
                }`}
                aria-label={`Ir a imagen ${idx + 1}`}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default function ResultadosPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const identificacionId = searchParams?.get('identificacionId');
  const { toast } = useToast();
  
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [resultado, setResultado] = useState<IdentificarResponse | null>(null);
  const [plantasConfirmadas, setPlantasConfirmadas] = useState<Set<number>>(new Set());
  const [confirmando, setConfirmando] = useState<number | null>(null);

  useEffect(() => {
    if (!identificacionId) {
      setError('No se proporcionó una imagen para identificar');
      setCargando(false);
      return;
    }

    cargarResultado();
  }, [identificacionId]);

  /**
   * Carga el resultado de la identificación
   */
  const cargarResultado = async () => {
    try {
      setCargando(true);
      setError(null);

      // Obtener los detalles de la identificación ya realizada
      const detalle = await plantService.obtenerDetalleIdentificacion(
        Number(identificacionId)
      );

      // Adaptar la respuesta al formato esperado
      const respuestaAdaptada: IdentificarResponse = {
        id: detalle.id,
        usuario_id: detalle.usuario_id,
        imagenes: detalle.imagen ? [{
          id: detalle.imagen.id,
          nombre_archivo: detalle.imagen.nombre,
          url_blob: detalle.imagen.url,
          tamano_bytes: 0
        }] : [],
        especie_id: undefined,
        confianza: detalle.confianza,
        origen: 'plantnet',
        resultados: detalle.plantnet_response,
        fecha_identificacion: detalle.fecha_creacion,
        proyecto_usado: 'all',
        cantidad_imagenes: detalle.imagen ? 1 : 0
      };

      setResultado(respuestaAdaptada);
    } catch (err) {
      const mensaje = err instanceof Error ? err.message : 'Error al cargar la identificación';
      setError(mensaje);
    } finally {
      setCargando(false);
    }
  };

  /**
   * Confirma una especie y la agrega al jardín del usuario
   */
  const confirmarEspecie = async (resultIndex: number) => {
    if (!resultado || !identificacionId) return;

    try {
      setConfirmando(resultIndex);
      
      const especieSeleccionada = resultado.resultados.results[resultIndex];
      
      await plantService.agregarPlantaAlJardin({
        identificacion_id: resultado.id,
        nombre_personalizado: especieSeleccionada.species.commonNames[0] || 
                             especieSeleccionada.species.scientificName,
        notas: `Identificación confirmada con ${(especieSeleccionada.score * 100).toFixed(1)}% de confianza`,
        ubicacion: undefined
      });

      // Marcar como confirmada
      setPlantasConfirmadas(prev => new Set([...prev, resultIndex]));

      toast({
        title: '¡Planta agregada!',
        description: `${especieSeleccionada.species.scientificName} se agregó a tu jardín`,
        variant: 'default'
      });

      // Opcional: redirigir al dashboard después de 2 segundos
      setTimeout(() => {
        router.push('/dashboard');
      }, 2000);

    } catch (err) {
      const mensaje = err instanceof Error ? err.message : 'Error al agregar la planta';
      toast({
        title: 'Error',
        description: mensaje,
        variant: 'destructive'
      });
    } finally {
      setConfirmando(null);
    }
  };

  /**
   * Vuelve a la página de identificación
   */
  const volverAIdentificar = () => {
    router.push('/identificar');
  };

  /**
   * Renderiza el estado de carga
   */
  if (cargando) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex flex-col items-center justify-center min-h-[60vh]">
          <Loader2 className="w-16 h-16 text-green-600 animate-spin mb-4" />
          <h2 className="text-2xl font-semibold text-gray-900 mb-2">
            Cargando resultados...
          </h2>
          <p className="text-gray-600 text-center max-w-md">
            Estamos recuperando los resultados de la identificación.
          </p>
        </div>
      </div>
    );
  }

  /**
   * Renderiza el estado de error
   */
  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-2xl mx-auto">
          <Card className="p-8 border-red-200 bg-red-50">
            <div className="flex items-start space-x-4">
              <AlertCircle className="w-8 h-8 text-red-600 flex-shrink-0 mt-1" />
              <div className="flex-1">
                <h2 className="text-xl font-semibold text-red-900 mb-2">
                  Error al cargar la identificación
                </h2>
                <p className="text-red-700 mb-6">{error}</p>
                <Button
                  onClick={volverAIdentificar}
                  variant="outline"
                  className="border-red-600 text-red-600 hover:bg-red-100"
                >
                  <ArrowLeft className="w-4 h-4 mr-2" />
                  Volver a identificar
                </Button>
              </div>
            </div>
          </Card>
        </div>
      </div>
    );
  }

  /**
   * Renderiza el carrusel de imágenes
   */
  const renderCarruselImagenes = (imagenes: ImagenIdentificacionResponse[]) => {
    if (imagenes.length === 0) return null;

    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
        {imagenes.map((imagen) => (
          <div key={imagen.id} className="aspect-square rounded-lg overflow-hidden">
            <img
              src={imagen.url_blob}
              alt={imagen.nombre_archivo}
              className="w-full h-full object-cover hover:scale-105 transition-transform"
            />
          </div>
        ))}
      </div>
    );
  };

  /**
   * Renderiza un resultado individual de identificación
   */
  const renderResultado = (result: PlantNetResult, index: number) => {
    const confianza = result.score * 100;
    const colorConfianza = obtenerColorConfianza(confianza);
    const nivelConfianza = obtenerNivelConfianza(confianza);
    const estaConfirmada = plantasConfirmadas.has(index);
    const estaConfirmando = confirmando === index;

    return (
      <Card 
        key={index}
        className={`p-6 transition-all hover:shadow-lg ${
          index === 0 ? 'border-green-500 border-2' : ''
        } ${estaConfirmada ? 'bg-green-50 border-green-300' : ''}`}
      >
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center space-x-3">
            <div className="bg-primary/10 rounded-full p-2 flex items-center justify-center">
              <Leaf className="w-5 h-5 text-primary" />
            </div>
            <div>
              <span className="text-sm text-gray-500 font-medium">
                #{index + 1} {index === 0 && '(Mejor coincidencia)'}
              </span>
            </div>
          </div>
          
          <Badge variant="secondary" className="text-base font-semibold">
            {formatearConfianza(result.score)}
          </Badge>
        </div>

        <div className="space-y-4">
          <div>
            <h3 className="text-2xl font-bold text-primary italic mb-1">
              {result.species.scientificName}
            </h3>
            {result.species.scientificNameAuthorship && (
              <p className="text-sm text-gray-500 italic">
                Autor: {result.species.scientificNameAuthorship}
              </p>
            )}
          </div>

          {result.species.commonNames && result.species.commonNames.length > 0 && (
            <div>
              <p className="text-sm font-medium text-gray-700 mb-2">
                Nombres comunes:
              </p>
              <div className="flex flex-wrap gap-2">
                {result.species.commonNames.slice(0, 5).map((nombre) => (
                  <span
                    key={`${result.species.scientificName}-${nombre}`}
                    className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm"
                  >
                    {nombre}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Imágenes de referencia de PlantNet - Carrusel automático */}
          {result.images && result.images.length > 0 && (
            <CarruselImagenes 
              imagenes={result.images} 
              especieNombre={result.species.scientificName}
            />
          )}

          <div className="grid grid-cols-3 gap-4 text-sm">
            {result.species.commonNames && result.species.commonNames.length > 0 && (
              <div>
                <p className="text-muted-foreground uppercase text-xs mb-1">
                  Nombre Común
                </p>
                <p className="font-medium">{result.species.commonNames[0]}</p>
              </div>
            )}
            {result.species.genus && (
              <div>
                <p className="text-muted-foreground uppercase text-xs mb-1">
                  Género
                </p>
                <p className="font-medium italic">
                  {result.species.genus.scientificNameWithoutAuthor}
                </p>
              </div>
            )}
            {result.species.family && (
              <div>
                <p className="text-muted-foreground uppercase text-xs mb-1">
                  Familia
                </p>
                <p className="font-medium italic">
                  {result.species.family.scientificNameWithoutAuthor}
                </p>
              </div>
            )}
          </div>

          <div className="pt-3 border-t">
            <p className="text-sm text-gray-500 mb-2">Nivel de confianza</p>
            <div className="flex items-center justify-between">
              <span className={`font-semibold ${colorConfianza}`}>
                {nivelConfianza}
              </span>
              <progress
                value={confianza}
                max={100}
                className="w-full max-w-xs ml-4 h-2"
                aria-label={`Confianza: ${confianza.toFixed(0)}%`}
              />
            </div>
          </div>

          {(result.gbif?.id || result.powo?.id) && (
            <div className="pt-3 border-t">
              <p className="text-sm text-gray-500 mb-2">Enlaces externos:</p>
              <div className="flex flex-wrap gap-2">
                {result.gbif?.id && (
                  <a
                    href={`https://www.gbif.org/species/${result.gbif.id}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center px-3 py-1 text-sm text-blue-600 hover:text-blue-800 hover:underline"
                  >
                    GBIF <ExternalLink className="w-3 h-3 ml-1" />
                  </a>
                )}
                {result.powo?.id && (
                  <a
                    href={`https://powo.science.kew.org/taxon/${result.powo.id}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center px-3 py-1 text-sm text-blue-600 hover:text-blue-800 hover:underline"
                  >
                    POWO <ExternalLink className="w-3 h-3 ml-1" />
                  </a>
                )}
              </div>
            </div>
          )}

          {/* Botón de confirmación */}
          <div className="pt-4 border-t">
            <Button
              onClick={() => confirmarEspecie(index)}
              disabled={estaConfirmada || estaConfirmando}
              size="lg"
              className={`w-full text-base font-semibold shadow-lg transition-all ${
                estaConfirmada
                  ? 'bg-green-600 hover:bg-green-700 text-white'
                  : 'bg-primary hover:bg-primary/90 hover:shadow-xl hover:scale-[1.02]'
              }`}
            >
              {estaConfirmando && (
                <>
                  <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                  Agregando...
                </>
              )}
              {!estaConfirmando && estaConfirmada && (
                <>
                  <CheckCircle2 className="w-5 h-5 mr-2" />
                  Confirmado
                </>
              )}
              {!estaConfirmando && !estaConfirmada && (
                <>
                  <CheckCircle2 className="w-5 h-5 mr-2" />
                  Confirmar esta planta
                </>
              )}
            </Button>
          </div>
        </div>
      </Card>
    );
  };

  if (!resultado) {
    return null;
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-card">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={volverAIdentificar}>
            <ArrowLeft className="w-5 h-5" />
          </Button>
          <h1 className="text-2xl font-bold">Resultados de Identificación</h1>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 py-8 space-y-6">
        {/* Carrusel de imágenes */}
        {resultado.imagenes && resultado.imagenes.length > 0 && (
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4">
              {resultado.imagenes.length > 1 ? 'Imágenes analizadas' : 'Imagen analizada'}
            </h2>
            {renderCarruselImagenes(resultado.imagenes)}
          </Card>
        )}

        {/* Información general */}
        <Card className="p-6 bg-blue-50 border-blue-200">
          <div className="flex items-start space-x-3">
            <Info className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <h3 className="font-semibold text-blue-900 mb-2">
                Acerca de estos resultados
              </h3>
              <div className="text-sm text-blue-800 space-y-1">
                <p>
                  • <strong>Confianza alta (≥80%)</strong>: Identificación muy probable
                </p>
                <p>
                  • <strong>Confianza media (60-79%)</strong>: Identificación probable, verificar
                </p>
                <p>
                  • <strong>Confianza baja (&lt;60%)</strong>: Identificación incierta, consultar experto
                </p>
                <p className="pt-2 border-t border-blue-300 mt-2">
                  <strong>Versión IA:</strong> {resultado.resultados.version} • 
                  <strong className="ml-2">Requests restantes:</strong> {resultado.resultados.remainingIdentificationRequests}
                </p>
              </div>
            </div>
          </div>
        </Card>

        {/* Título de resultados */}
        <div>
          <h2 className="text-xl font-semibold mb-2">Resultados de Identificación</h2>
          <p className="text-muted-foreground">
            Selecciona la especie que mejor coincida con tu planta
          </p>
        </div>

        {/* Lista de resultados */}
        <div className="space-y-6">
          {resultado.resultados.results.slice(0, 10).map((result, index) => 
            renderResultado(result, index)
          )}
        </div>

        {/* Footer */}
        <Card className="p-6 bg-gray-50">
          <p className="text-sm text-gray-600 text-center">
            Resultados proporcionados por{' '}
            <a
              href="https://plantnet.org"
              target="_blank"
              rel="noopener noreferrer"
              className="text-green-600 hover:text-green-800 hover:underline font-medium"
            >
              PlantNet
            </a>
            {' '}• Powered by AI Plant Identification
          </p>
        </Card>
      </main>
    </div>
  );
}

      // Obtener los detalles de la identificación ya realizada
