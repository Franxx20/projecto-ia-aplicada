"""
Script para probar migraciones de Alembic con PostgreSQL

Este script verifica que todas las migraciones funcionen correctamente
con PostgreSQL (la base de datos de producción).
"""
import os
import sys
import subprocess
from pathlib import Path

def main():
    """
    Ejecuta las migraciones en un ambiente PostgreSQL de prueba
    """
    print("=" * 80)
    print("🧪 PRUEBA DE MIGRACIONES CON POSTGRESQL")
    print("=" * 80)
    
    # Obtener credenciales de PostgreSQL desde .env o usar valores por defecto
    postgres_user = os.getenv('POSTGRES_USER', 'postgres')
    postgres_password = os.getenv('POSTGRES_PASSWORD', 'postgres123')
    postgres_host = os.getenv('POSTGRES_HOST', 'localhost')
    postgres_port = os.getenv('POSTGRES_PORT', '5432')
    postgres_db = os.getenv('POSTGRES_DB', 'proyecto_ia_db')
    
    # Construir URL de PostgreSQL
    database_url = f"postgresql://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db}"
    
    print(f"\n📋 Configuración de PostgreSQL:")
    print(f"   Host: {postgres_host}:{postgres_port}")
    print(f"   Database: {postgres_db}")
    print(f"   User: {postgres_user}")
    print(f"   URL: postgresql://{postgres_user}:***@{postgres_host}:{postgres_port}/{postgres_db}")
    
    print(f"\n⚠️  IMPORTANTE:")
    print(f"   - Asegúrate de que PostgreSQL esté corriendo (docker-compose up db)")
    print(f"   - Esta prueba ejecutará migraciones en la base de datos: {postgres_db}")
    print(f"   - Recomendado: usa una base de datos de prueba separada")
    
    response = input("\n¿Continuar con las migraciones? (s/n): ")
    if response.lower() != 's':
        print("❌ Prueba cancelada")
        return
    
    # Configurar variable de entorno para Alembic
    os.environ['DATABASE_URL'] = database_url
    
    print(f"\n🔄 Ejecutando: alembic upgrade head")
    print("=" * 80)
    
    try:
        # Ejecutar migraciones
        result = subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"],
            cwd=Path(__file__).parent,
            capture_output=False,
            text=True
        )
        
        if result.returncode == 0:
            print("\n" + "=" * 80)
            print("✅ MIGRACIONES COMPLETADAS EXITOSAMENTE")
            print("=" * 80)
        else:
            print("\n" + "=" * 80)
            print("❌ ERROR EN LAS MIGRACIONES")
            print("=" * 80)
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Error ejecutando migraciones: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
