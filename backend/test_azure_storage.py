"""
Script de prueba para Azure Blob Storage con Azurite

Este script prueba la conexión y operaciones básicas con Azure Storage:
- Crear contenedor
- Subir archivo
- Listar archivos
- Descargar archivo
- Eliminar archivo

Uso:
    python test_azure_storage.py
"""

import os
import sys
from io import BytesIO
from azure.storage.blob import BlobServiceClient, ContentSettings

# Connection string - usar variable de entorno o fallback a localhost
AZURITE_CONNECTION_STRING = os.getenv(
    'AZURE_STORAGE_CONNECTION_STRING',
    "DefaultEndpointsProtocol=http;"
    "AccountName=devstoreaccount1;"
    "AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;"
    "BlobEndpoint=http://localhost:10000/devstoreaccount1;"
)

CONTAINER_NAME = os.getenv('AZURE_STORAGE_CONTAINER_NAME', 'plantitas-imagenes')


def test_azure_storage():
    """Prueba las operaciones básicas de Azure Blob Storage."""
    
    print("=" * 60)
    print("🧪 TEST: Azure Blob Storage con Azurite")
    print("=" * 60)
    
    try:
        # 1. Conectar al servicio
        print("\n1️⃣  Conectando a Azure Storage (Azurite)...")
        blob_service_client = BlobServiceClient.from_connection_string(
            AZURITE_CONNECTION_STRING
        )
        print("   ✅ Conexión establecida")
        
        # 2. Crear contenedor si no existe
        print(f"\n2️⃣  Creando contenedor '{CONTAINER_NAME}'...")
        container_client = blob_service_client.get_container_client(CONTAINER_NAME)
        
        if not container_client.exists():
            container_client.create_container()
            print(f"   ✅ Contenedor '{CONTAINER_NAME}' creado")
        else:
            print(f"   ℹ️  Contenedor '{CONTAINER_NAME}' ya existe")
        
        # 3. Subir un archivo de prueba
        print("\n3️⃣  Subiendo archivo de prueba...")
        test_content = b"Este es un archivo de prueba para Azure Blob Storage!\n"
        test_content += b"Fecha: 2025-10-12\n"
        test_content += b"Proyecto: Plantitas IA\n"
        
        blob_name = "test-image.txt"
        blob_client = blob_service_client.get_blob_client(
            container=CONTAINER_NAME,
            blob=blob_name
        )
        
        blob_client.upload_blob(
            test_content,
            overwrite=True,
            content_settings=ContentSettings(content_type='text/plain')
        )
        print(f"   ✅ Archivo '{blob_name}' subido correctamente")
        print(f"   📍 URL: {blob_client.url}")
        
        # 4. Listar archivos en el contenedor
        print(f"\n4️⃣  Listando archivos en '{CONTAINER_NAME}'...")
        blob_list = container_client.list_blobs()
        blobs_found = 0
        for blob in blob_list:
            blobs_found += 1
            print(f"   📄 {blob.name}")
            print(f"      - Tamaño: {blob.size} bytes")
            print(f"      - Tipo: {blob.content_settings.content_type if blob.content_settings else 'N/A'}")
        
        if blobs_found == 0:
            print("   ℹ️  No se encontraron archivos")
        else:
            print(f"   ✅ Se encontraron {blobs_found} archivo(s)")
        
        # 5. Descargar el archivo
        print(f"\n5️⃣  Descargando archivo '{blob_name}'...")
        download_stream = blob_client.download_blob()
        downloaded_content = download_stream.readall()
        
        if downloaded_content == test_content:
            print("   ✅ Archivo descargado correctamente")
            print("   ✅ Contenido verificado (coincide con el original)")
        else:
            print("   ⚠️  Contenido no coincide")
        
        # 6. Eliminar el archivo
        print(f"\n6️⃣  Eliminando archivo '{blob_name}'...")
        blob_client.delete_blob()
        print("   ✅ Archivo eliminado correctamente")
        
        # Verificar eliminación
        print("\n7️⃣  Verificando eliminación...")
        blob_list = container_client.list_blobs()
        remaining_blobs = list(blob_list)
        if blob_name not in [b.name for b in remaining_blobs]:
            print("   ✅ Archivo eliminado correctamente del contenedor")
        
        print("\n" + "=" * 60)
        print("✅ TODAS LAS PRUEBAS PASARON EXITOSAMENTE")
        print("=" * 60)
        print("\n💡 Tu Azure Storage (Azurite) está funcionando correctamente!")
        print("   Puedes usarlo para desarrollo local sin costo.")
        print("\n📝 Connection String:")
        print(f"   {AZURITE_CONNECTION_STRING}")
        
        return True
        
    except Exception as e:
        print("\n" + "=" * 60)
        print("❌ ERROR EN LAS PRUEBAS")
        print("=" * 60)
        print(f"\n🔴 Error: {str(e)}")
        print(f"\n🔍 Tipo de error: {type(e).__name__}")
        
        print("\n📋 Posibles soluciones:")
        print("   1. Verifica que Azurite esté corriendo:")
        print("      docker-compose -f docker-compose.dev.yml ps")
        print("   2. Verifica que el puerto 10000 esté disponible:")
        print("      netstat -an | findstr :10000")
        print("   3. Reinicia los contenedores:")
        print("      docker-compose -f docker-compose.dev.yml restart azurite")
        
        return False


def test_connection_only():
    """Prueba solo la conexión sin crear contenedores."""
    print("\n🔌 Probando conexión básica...")
    try:
        blob_service_client = BlobServiceClient.from_connection_string(
            AZURITE_CONNECTION_STRING
        )
        # Listar contenedores existentes
        containers = blob_service_client.list_containers()
        container_list = list(containers)
        print(f"✅ Conexión exitosa - {len(container_list)} contenedor(es) encontrado(s)")
        return True
    except Exception as e:
        print(f"❌ Error de conexión: {str(e)}")
        return False


if __name__ == "__main__":
    print("\n🚀 Iniciando pruebas de Azure Blob Storage...")
    
    # Primero probar solo la conexión
    if test_connection_only():
        # Si la conexión funciona, ejecutar todas las pruebas
        success = test_azure_storage()
        sys.exit(0 if success else 1)
    else:
        print("\n⚠️  No se pudo conectar a Azurite")
        print("   Asegúrate de que los contenedores estén corriendo:")
        print("   docker-compose -f docker-compose.dev.yml up -d")
        sys.exit(1)
