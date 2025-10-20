'use client';

/**
 * Página de Resultados de Identificación de Plantas (T-023)
 * 
 * Actualizada para soportar múltiples imágenes con parámetros organ.
 * Muestra los resultados de la identificación con PlantNet API usando
 * el nuevo componente IdentificationResultCard con carousel de imágenes.
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
import { 
  ArrowLeft, 
  Leaf, 
  CheckCircle2, 
  AlertCircle, 
  Info,
  ExternalLink,
  Loader2
} from 'lucide-react';
import {
  IdentificarResponseSimple,
  PlantNetResult,
  obtenerColorConfianza,
  obtenerNivelConfianza,
  formatearConfianza
} from '@/models/plant.types';
import plantService from '@/lib/plant.service';

export default function ResultadosPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const imagenId = searchParams?.get('imagenId');
  
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [resultado, setResultado] = useState<IdentificarResponseSimple | null>(null);

  useEffect(() => {
    if (!imagenId) {
      setError('No se proporcionó una imagen para identificar');
      setCargando(false);
      return;
    }

    identificarPlanta();
  }, [imagenId]);

  /**
   * Identifica la planta usando el servicio de PlantNet
   */
  const identificarPlanta = async () => {
    try {
      setCargando(true);
      setError(null);

      const respuesta = await plantService.identificarDesdeImagen(
        Number(imagenId),
        ['auto'],
        true
      );

      setResultado(respuesta);
    } catch (err) {
      const mensaje = err instanceof Error ? err.message : 'Error al identificar la planta';
      setError(mensaje);
    } finally {
      setCargando(false);
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
            Identificando planta...
          </h2>
          <p className="text-gray-600 text-center max-w-md">
            Estamos analizando tu imagen con PlantNet AI.
            Esto puede tomar unos segundos.
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
                  Error al identificar la planta
                </h2>
                <p className="text-red-700 mb-6">{error}</p>
                <Button
                  onClick={volverAIdentificar}
                  variant="outline"
                  className="border-red-600 text-red-600 hover:bg-red-100"
                >
                  <ArrowLeft className="w-4 h-4 mr-2" />
                  Volver a intentar
                </Button>
              </div>
            </div>
          </Card>
        </div>
      </div>
    );
  }

  /**
   * Renderiza un resultado individual
   */
  const renderResultado = (result: PlantNetResult, index: number) => {
    const confianza = result.score * 100;
    const colorConfianza = obtenerColorConfianza(confianza);
    const nivelConfianza = obtenerNivelConfianza(confianza);
    const esConfiable = confianza >= 70;

    return (
      <Card 
        key={index}
        className={`p-6 transition-all hover:shadow-lg ${
          index === 0 ? 'border-green-500 border-2' : ''
        }`}
      >
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center space-x-3">
            <Leaf className="w-6 h-6 text-green-600" />
            <div>
              <span className="text-sm text-gray-500 font-medium">
                #{index + 1} {index === 0 && '(Mejor coincidencia)'}
              </span>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            {esConfiable ? (
              <CheckCircle2 className="w-5 h-5 text-green-600" />
            ) : (
              <AlertCircle className="w-5 h-5 text-yellow-600" />
            )}
            <span className={`text-2xl font-bold ${colorConfianza}`}>
              {formatearConfianza(result.score)}
            </span>
          </div>
        </div>

        <div className="space-y-3">
          <div>
            <h3 className="text-2xl font-bold text-gray-900 italic">
              {result.species.scientificName}
            </h3>
            {result.species.scientificNameAuthorship && (
              <p className="text-sm text-gray-500 italic mt-1">
                Autor: {result.species.scientificNameAuthorship}
              </p>
            )}
          </div>

          {result.species.commonNames && result.species.commonNames.length > 0 && (
            <div>
              <p className="text-sm font-medium text-gray-700 mb-1">
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

          <div className="grid grid-cols-2 gap-4 pt-3 border-t">
            {result.species.family && (
              <div>
                <p className="text-sm text-gray-500">Familia</p>
                <p className="font-medium text-gray-900">
                  {result.species.family.scientificNameWithoutAuthor}
                </p>
              </div>
            )}
            
            {result.species.genus && (
              <div>
                <p className="text-sm text-gray-500">Género</p>
                <p className="font-medium text-gray-900">
                  {result.species.genus.scientificNameWithoutAuthor}
                </p>
              </div>
            )}
          </div>

          <div className="pt-3 border-t">
            <p className="text-sm text-gray-500 mb-1">Nivel de confianza</p>
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
        </div>
      </Card>
    );
  };

  if (!resultado) {
    return null;
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <Button
            onClick={volverAIdentificar}
            variant="ghost"
            className="mb-4"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Identificar otra planta
          </Button>
          
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Resultados de Identificación
          </h1>
          <p className="text-gray-600">
            PlantNet AI ha identificado las siguientes especies
          </p>
        </div>

        {/* Información general */}
        <Card className="p-6 mb-6 bg-blue-50 border-blue-200">
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
                  <strong>Versión IA:</strong> {resultado.plantnet_response.version} • 
                  <strong className="ml-2">Requests restantes:</strong> {resultado.plantnet_response.remainingIdentificationRequests}
                </p>
              </div>
            </div>
          </div>
        </Card>

        {/* Lista de resultados */}
        <div className="space-y-4">
          {resultado.plantnet_response.results.slice(0, 10).map((result, index) => 
            renderResultado(result, index)
          )}
        </div>

        {/* Footer */}
        <Card className="p-6 mt-8 bg-gray-50">
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

        {/* Botón de acción */}
        <div className="mt-8 text-center">
          <Button
            onClick={volverAIdentificar}
            size="lg"
            className="bg-green-600 hover:bg-green-700"
          >
            Identificar otra planta
          </Button>
        </div>
      </div>
    </div>
  );
}
