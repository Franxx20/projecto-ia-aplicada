"""Script para verificar la estructura de la base de datos después de las migraciones."""
import sqlite3

def verify_database():
    conn = sqlite3.connect('test_migrations.db')
    cursor = conn.cursor()
    
    # Obtener todas las tablas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()
    
    print("📋 Tablas en la base de datos:")
    for table in tables:
        print(f"  ✓ {table[0]}")
    
    # Verificar columnas en imagenes
    print("\n📦 Columnas en tabla 'imagenes':")
    cursor.execute("PRAGMA table_info(imagenes)")
    columns = cursor.fetchall()
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
    
    # Verificar columnas en identificaciones
    print("\n📦 Columnas en tabla 'identificaciones':")
    cursor.execute("PRAGMA table_info(identificaciones)")
    columns = cursor.fetchall()
    for col in columns:
        nullable = "NULL" if col[3] == 0 else "NOT NULL"
        print(f"  - {col[1]} ({col[2]}) {nullable}")
    
    # Verificar columnas en especies
    print("\n📦 Columnas en tabla 'especies':")
    cursor.execute("PRAGMA table_info(especies)")
    columns = cursor.fetchall()
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
    
    # Verificar columnas en plantas
    print("\n📦 Columnas en tabla 'plantas':")
    cursor.execute("PRAGMA table_info(plantas)")
    columns = cursor.fetchall()
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
    
    # Verificar foreign keys en imagenes
    print("\n🔗 Foreign Keys en tabla 'imagenes':")
    cursor.execute("PRAGMA foreign_key_list(imagenes)")
    fks = cursor.fetchall()
    for fk in fks:
        print(f"  - {fk[3]} -> {fk[2]}.{fk[4]}")
    
    # Verificar foreign keys en identificaciones
    print("\n🔗 Foreign Keys en tabla 'identificaciones':")
    cursor.execute("PRAGMA foreign_key_list(identificaciones)")
    fks = cursor.fetchall()
    for fk in fks:
        print(f"  - {fk[3]} -> {fk[2]}.{fk[4]}")
    
    # Verificar índices
    print("\n📑 Índices en tabla 'imagenes':")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='imagenes' ORDER BY name")
    indexes = cursor.fetchall()
    for idx in indexes:
        print(f"  - {idx[0]}")
    
    print("\n✅ Verificación completada")
    conn.close()

if __name__ == "__main__":
    verify_database()
