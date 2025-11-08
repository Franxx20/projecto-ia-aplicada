"""
Script temporal para reparar imágenes de plantas.
Llama al endpoint /api/plantas/reparar-imagenes
"""
import requests
import json

# Configuración
API_URL = "http://localhost:8000"
LOGIN_URL = f"{API_URL}/api/auth/login"
REPAIR_URL = f"{API_URL}/api/plantas/reparar-imagenes"

# Credenciales (usar las del usuario actual)
# CAMBIAR ESTAS CREDENCIALES POR LAS REALES
EMAIL = "test@test.com"  # Cambiar por tu email
PASSWORD = "test123"      # Cambiar por tu password

def main():
    print("🔧 Script de reparación de imágenes de plantas")
    print("=" * 50)
    
    # 1. Login para obtener token
    print(f"\n1. Iniciando sesión como {EMAIL}...")
    login_response = requests.post(
        LOGIN_URL,
        json={"email": EMAIL, "password": PASSWORD}
    )
    
    if login_response.status_code != 200:
        print(f"❌ Error al iniciar sesión: {login_response.status_code}")
        print(f"   Respuesta: {login_response.text}")
        return
    
    token = login_response.json()["access_token"]
    print("✅ Sesión iniciada correctamente")
    
    # 2. Llamar al endpoint de reparación
    print("\n2. Reparando imágenes de plantas...")
    headers = {"Authorization": f"Bearer {token}"}
    repair_response = requests.post(REPAIR_URL, headers=headers)
    
    if repair_response.status_code != 200:
        print(f"❌ Error al reparar: {repair_response.status_code}")
        print(f"   Respuesta: {repair_response.text}")
        return
    
    # 3. Mostrar resultados
    resultado = repair_response.json()
    print("\n✅ Reparación completada!")
    print("=" * 50)
    print(f"Plantas procesadas: {resultado['plantas_procesadas']}")
    print(f"Plantas reparadas: {resultado['plantas_reparadas']}")
    
    if resultado['detalles']:
        print("\nDetalles:")
        for planta in resultado['detalles']:
            print(f"  - {planta['nombre']} (ID: {planta['id']})")
            print(f"    → Imagen principal: {planta['imagen_principal_id']}")
    
    print("\n🎉 ¡Listo! Recarga la página del dashboard para ver los cambios.")

if __name__ == "__main__":
    main()
