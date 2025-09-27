#!/usr/bin/env python3
"""
Script de verificación del backend

Verifica que todos los componentes funcionen correctamente.
"""

import sys
import os
import httpx
import asyncio
from datetime import datetime

# Agregar el directorio de la aplicación al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def verificar_importaciones():
    """Verificar que todas las importaciones funcionen"""
    print("🔍 Verificando importaciones...")
    
    try:
        from app.main import app
        print("✅ app.main importado correctamente")
        
        from app.core.config import obtener_configuracion
        config = obtener_configuracion()
        print(f"✅ Configuración cargada: {config.nombre_app}")
        
        return True
    except Exception as e:
        print(f"❌ Error en importaciones: {e}")
        return False

def verificar_aplicacion():
    """Verificar la aplicación FastAPI"""
    print("\n🔍 Verificando aplicación FastAPI...")
    
    try:
        from app.main import app
        
        # Verificar que la app existe
        print(f"✅ Aplicación creada: {app.title}")
        print(f"✅ Versión: {app.version}")
        
        # Verificar rutas
        rutas = [route.path for route in app.routes]
        print(f"✅ Rutas disponibles: {rutas}")
        
        return True
    except Exception as e:
        print(f"❌ Error en aplicación: {e}")
        return False

async def probar_servidor():
    """Probar servidor iniciándolo temporalmente"""
    print("\n🚀 Iniciando servidor de prueba...")
    
    import uvicorn
    from app.main import app
    
    # Configurar servidor de prueba
    config = uvicorn.Config(
        app,
        host="127.0.0.1",
        port=8001,  # Puerto diferente para evitar conflictos
        log_level="error"  # Reducir logs
    )
    
    server = uvicorn.Server(config)
    
    try:
        # Iniciar servidor en background
        await server.startup()
        
        print("✅ Servidor iniciado en http://127.0.0.1:8001")
        
        # Probar endpoints
        async with httpx.AsyncClient() as client:
            # Test endpoint raíz
            response = await client.get("http://127.0.0.1:8001/")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Endpoint raíz: {data['mensaje']}")
            
            # Test health check
            response = await client.get("http://127.0.0.1:8001/salud")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health check: {data['estado']}")
            
            # Test info
            response = await client.get("http://127.0.0.1:8001/info")
            if response.status_code == 200:
                print("✅ Endpoint info funcionando")
            
            # Test comunicación frontend
            response = await client.get("http://127.0.0.1:8001/test-frontend")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Test frontend: {data['mensaje']}")
        
        await server.shutdown()
        print("✅ Servidor detenido correctamente")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en servidor: {e}")
        try:
            await server.shutdown()
        except:
            pass
        return False

def main():
    """Función principal de verificación"""
    print("🧪 VERIFICACIÓN DEL BACKEND - Proyecto IA Aplicada")
    print("=" * 60)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🐍 Python: {sys.version}")
    print(f"📁 Directorio: {os.getcwd()}")
    print()
    
    # Lista de verificaciones
    verificaciones = [
        ("Importaciones", verificar_importaciones),
        ("Aplicación FastAPI", verificar_aplicacion),
    ]
    
    resultados = []
    
    # Ejecutar verificaciones síncronas
    for nombre, funcion in verificaciones:
        resultado = funcion()
        resultados.append((nombre, resultado))
    
    # Ejecutar prueba del servidor (asíncrona)
    try:
        resultado_servidor = asyncio.run(probar_servidor())
        resultados.append(("Servidor", resultado_servidor))
    except Exception as e:
        print(f"❌ Error al probar servidor: {e}")
        resultados.append(("Servidor", False))
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE VERIFICACIONES")
    print("=" * 60)
    
    exitosos = 0
    for nombre, resultado in resultados:
        estado = "✅ EXITOSO" if resultado else "❌ FALLIDO"
        print(f"{nombre:.<30} {estado}")
        if resultado:
            exitosos += 1
    
    print(f"\n📈 Resultado: {exitosos}/{len(resultados)} verificaciones exitosas")
    
    if exitosos == len(resultados):
        print("\n🎉 ¡BACKEND FUNCIONANDO CORRECTAMENTE!")
        print("\nPróximos pasos:")
        print("1. Iniciar servidor: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload")
        print("2. Visitar: http://localhost:8000")
        print("3. Documentación: http://localhost:8000/docs")
        print("4. Health check: http://localhost:8000/salud")
        
        return True
    else:
        print("\n⚠️  HAY PROBLEMAS QUE RESOLVER")
        return False

if __name__ == "__main__":
    try:
        exito = main()
        sys.exit(0 if exito else 1)
    except Exception as e:
        print(f"\n💥 Error inesperado: {e}")
        sys.exit(1)