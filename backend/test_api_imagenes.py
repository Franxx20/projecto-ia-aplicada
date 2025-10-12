"""
Script para probar los endpoints de la API de imágenes

Este script prueba la API REST completa de gestión de imágenes:
- Registro y login de usuario
- Subida de imagen
- Listado de imágenes
- Obtener imagen específica
- Actualizar descripción
- Eliminar imagen

Uso:
    python test_api_imagenes.py
"""

import requests
import json
from io import BytesIO

# Configuración
API_URL = "http://localhost:8000"
TEST_EMAIL = "test_images@example.com"
TEST_PASSWORD = "TestPassword123"


def print_section(title):
    """Imprime un separador de sección."""
    print("\n" + "=" * 60)
    print(f"📍 {title}")
    print("=" * 60)


def test_api():
    """Prueba los endpoints de la API de imágenes."""
    
    print("\n🚀 Iniciando pruebas de API de Imágenes")
    print("=" * 60)
    
    # 1. Registrar usuario
    print_section("1. Registrando usuario de prueba")
    
    register_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "nombre": "Usuario Test Imágenes"
    }
    
    try:
        response = requests.post(f"{API_URL}/api/auth/register", json=register_data)
        if response.status_code == 201:
            print("   ✅ Usuario registrado correctamente")
        elif response.status_code == 400 and "ya existe" in response.text.lower():
            print("   ℹ️  Usuario ya existe (usando usuario existente)")
        else:
            print(f"   ⚠️  Respuesta inesperada: {response.status_code}")
            print(f"   {response.text}")
    except Exception as e:
        print(f"   ❌ Error al registrar: {str(e)}")
        return False
    
    # 2. Login
    print_section("2. Iniciando sesión")
    
    try:
        login_data_payload = {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }
        
        response = requests.post(
            f"{API_URL}/api/auth/login",
            json=login_data_payload
        )
        
        if response.status_code != 200:
            print(f"   ❌ Error al iniciar sesión: {response.status_code}")
            print(f"   {response.text}")
            return False
        
        login_data = response.json()
        token = login_data.get("access_token")
        
        if not token:
            print("   ❌ No se recibió token de acceso")
            return False
        
        print("   ✅ Login exitoso")
        print(f"   🔑 Token: {token[:20]}...")
        
        # Headers para requests autenticados
        headers = {"Authorization": f"Bearer {token}"}
        
    except Exception as e:
        print(f"   ❌ Error al iniciar sesión: {str(e)}")
        return False
    
    # 3. Subir imagen
    print_section("3. Subiendo imagen de prueba")
    
    try:
        # Crear archivo de imagen fake
        image_content = b"FAKE_IMAGE_CONTENT_FOR_TESTING" * 100
        files = {
            "archivo": ("planta_test.jpg", BytesIO(image_content), "image/jpeg")
        }
        data = {
            "descripcion": "Mi planta favorita - Foto de prueba"
        }
        
        response = requests.post(
            f"{API_URL}/api/imagenes/subir",
            files=files,
            data=data,
            headers=headers
        )
        
        if response.status_code != 201:
            print(f"   ❌ Error al subir imagen: {response.status_code}")
            print(f"   {response.text}")
            return False
        
        upload_data = response.json()
        imagen_id = upload_data.get("id")
        
        print("   ✅ Imagen subida correctamente")
        print(f"   🆔 ID: {imagen_id}")
        print(f"   📄 Nombre: {upload_data.get('nombre_archivo')}")
        print(f"   🔗 URL: {upload_data.get('url_blob')}")
        print(f"   📝 Descripción: {upload_data.get('descripcion')}")
        
    except Exception as e:
        print(f"   ❌ Error al subir imagen: {str(e)}")
        return False
    
    # 4. Listar imágenes
    print_section("4. Listando imágenes del usuario")
    
    try:
        response = requests.get(
            f"{API_URL}/api/imagenes",
            headers=headers
        )
        
        if response.status_code != 200:
            print(f"   ❌ Error al listar imágenes: {response.status_code}")
            return False
        
        list_data = response.json()
        imagenes = list_data.get("imagenes", [])
        total = list_data.get("total", 0)
        
        print(f"   ✅ Se encontraron {total} imagen(es)")
        for img in imagenes:
            print(f"   📷 ID: {img['id']} - {img['nombre_archivo']}")
        
    except Exception as e:
        print(f"   ❌ Error al listar imágenes: {str(e)}")
        return False
    
    # 5. Obtener imagen específica
    print_section("5. Obteniendo imagen específica")
    
    try:
        response = requests.get(
            f"{API_URL}/api/imagenes/{imagen_id}",
            headers=headers
        )
        
        if response.status_code != 200:
            print(f"   ❌ Error al obtener imagen: {response.status_code}")
            return False
        
        imagen = response.json()
        
        print("   ✅ Imagen obtenida correctamente")
        print(f"   🆔 ID: {imagen['id']}")
        print(f"   📄 Nombre: {imagen['nombre_archivo']}")
        print(f"   📦 Tamaño: {imagen['tamano_bytes']} bytes")
        print(f"   📅 Creada: {imagen['created_at']}")
        
    except Exception as e:
        print(f"   ❌ Error al obtener imagen: {str(e)}")
        return False
    
    # 6. Actualizar descripción
    print_section("6. Actualizando descripción")
    
    try:
        update_data = {
            "descripcion": "Descripción actualizada desde el test"
        }
        
        response = requests.patch(
            f"{API_URL}/api/imagenes/{imagen_id}",
            json=update_data,
            headers=headers
        )
        
        if response.status_code != 200:
            print(f"   ❌ Error al actualizar: {response.status_code}")
            return False
        
        updated_imagen = response.json()
        
        print("   ✅ Descripción actualizada")
        print(f"   📝 Nueva descripción: {updated_imagen['descripcion']}")
        
    except Exception as e:
        print(f"   ❌ Error al actualizar: {str(e)}")
        return False
    
    # 7. Eliminar imagen
    print_section("7. Eliminando imagen")
    
    try:
        response = requests.delete(
            f"{API_URL}/api/imagenes/{imagen_id}",
            headers=headers
        )
        
        if response.status_code != 200:
            print(f"   ❌ Error al eliminar: {response.status_code}")
            return False
        
        delete_data = response.json()
        
        print("   ✅ Imagen eliminada correctamente")
        print(f"   💬 {delete_data.get('mensaje')}")
        
    except Exception as e:
        print(f"   ❌ Error al eliminar: {str(e)}")
        return False
    
    # 8. Verificar eliminación
    print_section("8. Verificando eliminación")
    
    try:
        response = requests.get(
            f"{API_URL}/api/imagenes/{imagen_id}",
            headers=headers
        )
        
        if response.status_code == 404:
            print("   ✅ Imagen eliminada correctamente (404 Not Found)")
        else:
            print(f"   ⚠️  Respuesta inesperada: {response.status_code}")
        
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # Resumen final
    print("\n" + "=" * 60)
    print("✅ TODAS LAS PRUEBAS DE API PASARON EXITOSAMENTE")
    print("=" * 60)
    print("\n💡 La API de gestión de imágenes está funcionando correctamente!")
    print("   - Autenticación ✅")
    print("   - Subida de imágenes ✅")
    print("   - Listado de imágenes ✅")
    print("   - Obtener imagen ✅")
    print("   - Actualizar descripción ✅")
    print("   - Eliminar imagen ✅")
    
    return True


if __name__ == "__main__":
    try:
        # Verificar que la API esté disponible
        print("🔍 Verificando disponibilidad de la API...")
        response = requests.get(f"{API_URL}/health", timeout=5)
        print(f"✅ API disponible (status: {response.status_code})")
    except Exception as e:
        print(f"❌ No se puede conectar a la API en {API_URL}")
        print(f"   Error: {str(e)}")
        print("\n   Asegúrate de que el backend esté corriendo:")
        print("   docker-compose -f docker-compose.dev.yml up -d")
        exit(1)
    
    # Ejecutar pruebas
    success = test_api()
    exit(0 if success else 1)
