"""
Manual test for T-022 endpoint - Verificar que el endpoint funciona correctamente
"""
import requests
from io import BytesIO

# Base URL
BASE_URL = "http://localhost:8000"

# 1. Login (usar usuario existente o crear uno nuevo)
print("=" * 60)
print("PRUEBA MANUAL T-022: Múltiples imágenes con parámetro organ")
print("=" * 60)

# Intentar login con usuario de prueba
login_data = {
    "email": "admin@plantitas.com",
    "password": "Admin123!"
}

print("\n1. Autenticando usuario...")

# Primero intentar registrar el usuario
registro_data = {
    "nombre_usuario": "test_t022",
    "email": "test_t022@plantitas.com",
    "password": "TestPass123!",
    "nombre_completo": "Usuario Test T-022"
}

response_registro = requests.post(f"{BASE_URL}/api/auth/register", json=registro_data)
if response_registro.status_code == 201:
    print("   ✅ Usuario registrado exitosamente")
elif response_registro.status_code == 409:
    print("   ℹ️  Usuario ya existe, procediendo con login")
else:
    print(f"   ⚠️  Registro: {response_registro.status_code}")

# Ahora hacer login
login_data = {
    "email": "test_t022@plantitas.com",
    "password": "TestPass123!"
}

response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)

if response.status_code != 200:
    print(f"   ❌ Error de autenticación: {response.status_code}")
    print(f"   Respuesta: {response.json()}")
    exit(1)

token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print("   ✅ Autenticación exitosa")

# 2. Crear imágenes fake de prueba
print("\n2. Preparando imágenes de prueba...")
fake_jpeg = b'\xff\xd8\xff\xe0\x00\x10JFIF' + b'\x00' * 100

# 3. Test 1: Una imagen con "sin_especificar"
print("\n3. Test 1: Una imagen con 'sin_especificar'")
files = [
    ("archivos", ("imagen1.jpg", BytesIO(fake_jpeg), "image/jpeg"))
]
data = {"organos": "sin_especificar"}

response = requests.post(
    f"{BASE_URL}/api/identificar/multiple",
    headers=headers,
    files=files,
    data=data
)

print(f"   Status Code: {response.status_code}")
if response.status_code == 201:
    print("   ✅ Endpoint responde correctamente")
    result = response.json()
    print(f"   Identificación ID: {result.get('identificacion_id')}")
    print(f"   Especie: {result.get('especie', {}).get('nombre_cientifico')}")
    print(f"   Confianza: {result.get('confianza')}%")
    print(f"   Número de imágenes: {len(result.get('imagenes', []))}")
else:
    print(f"   ❌ Error: {response.status_code}")
    print(f"   Detalle: {response.json()}")

# 4. Test 2: Tres imágenes con diferentes órganos
print("\n4. Test 2: Tres imágenes con diferentes órganos")
files = [
    ("archivos", ("imagen1.jpg", BytesIO(fake_jpeg), "image/jpeg")),
    ("archivos", ("imagen2.jpg", BytesIO(fake_jpeg), "image/jpeg")),
    ("archivos", ("imagen3.jpg", BytesIO(fake_jpeg), "image/jpeg"))
]
data = {"organos": "leaf,flower,sin_especificar"}

response = requests.post(
    f"{BASE_URL}/api/identificar/multiple",
    headers=headers,
    files=files,
    data=data
)

print(f"   Status Code: {response.status_code}")
if response.status_code == 201:
    print("   ✅ Endpoint responde correctamente con múltiples imágenes")
    result = response.json()
    print(f"   Identificación ID: {result.get('identificacion_id')}")
    print(f"   Número de imágenes: {len(result.get('imagenes', []))}")
    for idx, img in enumerate(result.get('imagenes', []), 1):
        print(f"   Imagen {idx}: organ={img.get('organ')}")
else:
    print(f"   ❌ Error: {response.status_code}")
    print(f"   Detalle: {response.json()}")

# 5. Test 3: Validación - 6 imágenes (debe fallar)
print("\n5. Test 3: Validación - 6 imágenes (debe rechazar)")
files = [
    ("archivos", (f"imagen{i}.jpg", BytesIO(fake_jpeg), "image/jpeg"))
    for i in range(1, 7)
]
data = {"organos": "leaf"}

response = requests.post(
    f"{BASE_URL}/api/identificar/multiple",
    headers=headers,
    files=files,
    data=data
)

print(f"   Status Code: {response.status_code}")
if response.status_code == 400:
    print("   ✅ Validación funcionando correctamente (rechazó 6 imágenes)")
    print(f"   Mensaje: {response.json().get('detail')}")
else:
    print(f"   ❌ Esperaba error 400, recibió: {response.status_code}")

# 6. Test 4: Un órgano aplicado a múltiples imágenes
print("\n6. Test 4: Un órgano aplicado a 2 imágenes")
files = [
    ("archivos", ("imagen1.jpg", BytesIO(fake_jpeg), "image/jpeg")),
    ("archivos", ("imagen2.jpg", BytesIO(fake_jpeg), "image/jpeg"))
]
data = {"organos": "flower"}  # Un solo órgano para 2 imágenes

response = requests.post(
    f"{BASE_URL}/api/identificar/multiple",
    headers=headers,
    files=files,
    data=data
)

print(f"   Status Code: {response.status_code}")
if response.status_code == 201:
    print("   ✅ Un órgano se aplicó a todas las imágenes")
    result = response.json()
    for idx, img in enumerate(result.get('imagenes', []), 1):
        print(f"   Imagen {idx}: organ={img.get('organ')}")
else:
    print(f"   ❌ Error: {response.status_code}")

print("\n" + "=" * 60)
print("PRUEBAS MANUALES COMPLETADAS")
print("=" * 60)
