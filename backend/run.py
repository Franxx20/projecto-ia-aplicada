#!/usr/bin/env python3
"""
Script de inicio para el backend FastAPI

Ejecutar con: python run.py
"""

import sys
import os

# Agregar el directorio actual al path de Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import uvicorn
    
    if __name__ == "__main__":
        print("🚀 Iniciando servidor de prueba...")
        print("📝 Modo desarrollo - FastAPI")
        print("🌐 URL: http://localhost:8000")
        print("📚 Documentación: http://localhost:8000/docs")
        print("🔧 Health Check: http://localhost:8000/salud")
        print("")
        print("Para detener el servidor, presiona Ctrl+C")
        print("-" * 50)
        
        # Corregir URLs de Azurite antes de iniciar el servidor
        print("\n🔧 Corrigiendo URLs de Azurite...")
        try:
            from fix_azurite_on_startup import fix_azurite_urls
            fix_azurite_urls()
        except Exception as e:
            print(f"⚠️  No se pudo ejecutar corrección de URLs: {e}")
        
        # Importar después de configurar el path
        from app.main import app
        
        uvicorn.run(
            app,  # Pasar directamente la app
            host="0.0.0.0",
            port=8000,
            reload=False,  # Desactivar reload por ahora
            access_log=True
        )
        
except ImportError as e:
    print(f"❌ Error de importación: {e}")
    print("💡 Primero ejecuta: pip install -r requirements.txt")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error al iniciar servidor: {e}")
    sys.exit(1)