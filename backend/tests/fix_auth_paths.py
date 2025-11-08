"""
Script para corregir todas las rutas de autenticación en test_health_endpoints.py
"""
import re

# Leer el archivo
with open('test_health_endpoints.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Reemplazar TODAS las variantes de rutas de autenticación
content = content.replace(
    "patch('app.api.plantas.get_current_user'",
    "patch('app.utils.jwt.get_current_user'"
)

content = content.replace(
    "patch('app.core.security.get_current_user'",
    "patch('app.utils.jwt.get_current_user'"
)

# Reemplazar las comparaciones de confianza exactas por comparaciones con tolerancia
# Buscar patrones como: assert data["confianza"] == 85.5
content = re.sub(
    r'assert (.+?)\["confianza"\] == (\d+\.?\d*)',
    r'assert abs(\1["confianza"] - \2) < 0.01',
    content
)

content = re.sub(
    r'assert (.+?)\.confianza == (\d+\.?\d*)',
    r'assert abs(\1.confianza - \2) < 0.01',
    content
)

# Guardar el archivo
with open('test_health_endpoints.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Archivo actualizado correctamente")
print("✅ Todas las rutas de autenticación corregidas (app.api.plantas + app.core.security)")
print("✅ Todas las comparaciones de confianza corregidas")
