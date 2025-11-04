#!/usr/bin/env python3
"""
Script para ejecutar migraciones de Alembic
Útil para ejecutar desde Docker o scripts de automatización
"""
import sys
import os
from pathlib import Path

# Asegurarnos de que estamos en el directorio correcto
backend_dir = Path(__file__).parent
os.chdir(backend_dir)

try:
    from alembic.config import Config
    from alembic import command
    
    # Configurar Alembic
    alembic_cfg = Config("alembic.ini")
    
    # Ejecutar upgrade a head
    print("🔄 Aplicando migraciones de base de datos...")
    command.upgrade(alembic_cfg, "head")
    print("✅ Migraciones aplicadas correctamente")
    
    # Mostrar la versión actual
    print("\n📊 Versión actual de la base de datos:")
    command.current(alembic_cfg, verbose=True)
    
    sys.exit(0)
    
except FileNotFoundError as e:
    print(f"❌ Error: No se encontró el archivo de configuración de Alembic: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error al aplicar migraciones: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
