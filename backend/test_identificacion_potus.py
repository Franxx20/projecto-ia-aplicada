"""
Script de prueba para identificar el potus con PlantNet API
"""
import asyncio
import sys
from pathlib import Path

# Agregar app al path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.plantnet_service import PlantNetService


async def main():
    """Prueba de identificación con imagen de potus"""
    
    print("=" * 60)
    print("🌿 PRUEBA DE IDENTIFICACIÓN DE PLANTA CON PLANTNET")
    print("=" * 60)
    print()
    
    # Ruta de la imagen
    imagen_path = "/app/potus_test.jpg"
    
    print(f"📷 Imagen a identificar: {imagen_path}")
    print()
    
    # Verificar que la imagen existe
    if not Path(imagen_path).exists():
        print("❌ ERROR: La imagen no existe en la ruta especificada")
        return
    
    print("🔍 Llamando a PlantNet API...")
    print()
    
    try:
        # Llamar a PlantNet
        respuesta = await PlantNetService.identificar_desde_path(
            rutas_imagenes=[imagen_path],
            organos=["leaf"]  # Es una hoja
        )
        
        print("✅ Respuesta recibida de PlantNet!")
        print()
        print("=" * 60)
        print("📊 RESULTADOS DE IDENTIFICACIÓN")
        print("=" * 60)
        print()
        
        # Mostrar información de la query
        query = respuesta.get("query", {})
        print(f"🔎 Proyecto: {query.get('project', 'N/A')}")
        print(f"🌍 Idioma: {respuesta.get('language', 'N/A')}")
        print()
        
        # Mostrar mejor coincidencia
        best_match = respuesta.get("bestMatch")
        if best_match:
            print(f"🏆 MEJOR COINCIDENCIA: {best_match}")
            print()
        
        # Mostrar resultados
        results = respuesta.get("results", [])
        if results:
            print(f"📋 Total de resultados: {len(results)}")
            print()
            
            for i, resultado in enumerate(results[:5], 1):
                species = resultado.get("species", {})
                family = species.get("family", {})
                
                print(f"--- Resultado #{i} ---")
                print(f"   Nombre científico: {species.get('scientificName', 'N/A')}")
                print(f"   Familia: {family.get('scientificName', 'N/A')}")
                print(f"   Confianza: {resultado.get('score', 0) * 100:.2f}%")
                
                # Nombres comunes
                common_names = species.get("commonNames", [])
                if common_names:
                    print(f"   Nombres comunes: {', '.join(common_names[:3])}")
                
                # Información de imágenes
                images = resultado.get("images", [])
                if images:
                    print(f"   Imágenes de referencia: {len(images)}")
                    mejor_imagen = max(images, key=lambda img: img.get("score", 0))
                    organ = mejor_imagen.get("organ")
                    if organ:
                        score = mejor_imagen.get("score", 0) * 100
                        print(f"   Órgano detectado: {organ} ({score:.1f}%)")
                
                print()
        else:
            print("❌ No se encontraron resultados")
        
        # Información de cuota
        remaining_requests = respuesta.get('remainingIdentificationRequests')
        if remaining_requests is not None:
            print("=" * 60)
            print("📊 INFORMACIÓN DE CUOTA")
            print("=" * 60)
            print(f"Requests restantes hoy: {remaining_requests}/500")
            print()
        
        # Extraer mejor resultado simplificado
        print("=" * 60)
        print("🎯 RESULTADO SIMPLIFICADO (para guardar en BD)")
        print("=" * 60)
        mejor = PlantNetService.extraer_mejor_resultado(respuesta)
        if mejor:
            for key, value in mejor.items():
                if key == "nombres_comunes":
                    print(f"{key}: {', '.join(value[:3]) if value else 'N/A'}")
                else:
                    print(f"{key}: {value}")
        print()
        
        # Respuesta formateada en español
        print("=" * 60)
        print("📝 RESPUESTA FORMATEADA")
        print("=" * 60)
        formateada = PlantNetService.formatear_respuesta_completa(respuesta)
        print(formateada.get("mensaje", "N/A"))
        print()
        
        print("✅ PRUEBA COMPLETADA EXITOSAMENTE!")
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
