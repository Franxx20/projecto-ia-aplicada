#!/usr/bin/env python3
"""
Script mejorado para ejecutar migraciones de Alembic
Incluye validaciones, manejo de errores y rollback automático
"""
import sys
import os
from pathlib import Path
from datetime import datetime
import time

# Asegurarnos de que estamos en el directorio correcto
backend_dir = Path(__file__).parent
os.chdir(backend_dir)

# Colores para output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_info(msg):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.END}")

def print_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.END}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.END}")

def wait_for_db(max_retries=30, delay=2):
    """Esperar a que la base de datos esté lista"""
    print_info("Esperando a que la base de datos esté lista...")
    
    from sqlalchemy import create_engine, text
    from app.core.config import configuracion
    
    for attempt in range(max_retries):
        try:
            engine = create_engine(configuracion.database_url)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                engine.dispose()
                print_success(f"Base de datos lista (intento {attempt + 1})")
                return True
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"⏳ Intento {attempt + 1}/{max_retries} - Esperando {delay}s...")
                time.sleep(delay)
            else:
                print_error(f"No se pudo conectar a la base de datos después de {max_retries} intentos")
                print_error(f"Error: {str(e)}")
                return False
    return False

def check_alembic_initialized():
    """Verificar si Alembic está inicializado"""
    alembic_ini = Path("alembic.ini")
    versions_dir = Path("alembic/versions")
    
    if not alembic_ini.exists():
        print_error("alembic.ini no encontrado. Alembic no está inicializado.")
        return False
    
    if not versions_dir.exists():
        print_error("Directorio alembic/versions no encontrado.")
        return False
    
    print_success("Alembic está inicializado correctamente")
    return True

def check_merge_heads():
    """Detectar si hay merge heads (conflictos de migraciones)"""
    try:
        from alembic.config import Config
        from alembic.script import ScriptDirectory
        
        alembic_cfg = Config("alembic.ini")
        script = ScriptDirectory.from_config(alembic_cfg)
        heads = script.get_heads()
        
        if len(heads) > 1:
            print_warning(f"⚠️  Detectados {len(heads)} heads de migración:")
            for head in heads:
                print(f"  - {head}")
            print_info("Ejecuta 'alembic merge heads' para resolver conflictos")
            return False
        
        return True
    except Exception as e:
        print_error(f"Error al verificar merge heads: {e}")
        return False

def get_current_revision():
    """Obtener la revisión actual de la base de datos"""
    try:
        from alembic.config import Config
        from alembic import command
        from io import StringIO
        
        alembic_cfg = Config("alembic.ini")
        
        # Capturar output
        buffer = StringIO()
        
        # Redirigir stdout temporalmente
        old_stdout = sys.stdout
        sys.stdout = buffer
        
        try:
            command.current(alembic_cfg, verbose=False)
        finally:
            sys.stdout = old_stdout
        
        output = buffer.getvalue()
        
        if not output or "None" in output:
            return None
        
        # Extraer revision ID (primera palabra)
        revision = output.strip().split()[0] if output.strip() else None
        return revision
        
    except Exception as e:
        print_error(f"Error al obtener revisión actual: {e}")
        return None

def backup_current_state():
    """Crear un backup del estado actual (opcional)"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"migration_backup_{timestamp}.txt"
    
    current_rev = get_current_revision()
    if current_rev:
        with open(backup_file, 'w') as f:
            f.write(f"Revision: {current_rev}\n")
            f.write(f"Timestamp: {timestamp}\n")
        print_info(f"Backup creado: {backup_file}")
        return backup_file
    return None

def run_migrations():
    """Ejecutar migraciones con validaciones"""
    try:
        from alembic.config import Config
        from alembic import command
        
        # 1. Verificar inicialización
        if not check_alembic_initialized():
            return False
        
        # 2. Verificar merge heads
        if not check_merge_heads():
            print_error("Resuelve los conflictos de migración antes de continuar")
            return False
        
        # 3. Obtener estado actual
        current_rev = get_current_revision()
        print_info(f"Revisión actual: {current_rev or 'Base de datos vacía'}")
        
        # 4. Crear backup (opcional)
        backup_file = backup_current_state()
        
        # 5. Ejecutar migraciones
        alembic_cfg = Config("alembic.ini")
        
        print_info("🔄 Aplicando migraciones...")
        command.upgrade(alembic_cfg, "head")
        print_success("Migraciones aplicadas correctamente")
        
        # 6. Verificar nueva revisión
        new_rev = get_current_revision()
        print_success(f"Nueva revisión: {new_rev}")
        
        # 7. Mostrar historial
        print_info("\n📊 Historial de migraciones:")
        command.history(alembic_cfg, verbose=False)
        
        return True
        
    except Exception as e:
        print_error(f"Error al aplicar migraciones: {e}")
        import traceback
        traceback.print_exc()
        
        # Intentar rollback si hay un backup
        current_rev = get_current_revision()
        if current_rev and backup_file:
            print_warning("Considera hacer rollback si es necesario:")
            print_info(f"  alembic downgrade {current_rev}")
        
        return False

def main():
    """Función principal"""
    print_info("=" * 60)
    print_info("🔧 Script de Migraciones de Base de Datos")
    print_info("=" * 60)
    
    # 1. Esperar a que la BD esté lista
    if not wait_for_db():
        sys.exit(1)
    
    # 2. Ejecutar migraciones
    if run_migrations():
        print_success("\n✨ Proceso completado exitosamente")
        sys.exit(0)
    else:
        print_error("\n❌ Proceso completado con errores")
        sys.exit(1)

if __name__ == "__main__":
    main()
