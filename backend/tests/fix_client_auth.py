"""
Script para reemplazar client_with_db y mocks por client_with_auth en tests
"""
import re

# Leer el archivo
with open('test_health_endpoints.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Patrón para encontrar tests con patch de autenticación
# Buscar bloques que tengan: with patch('app.utils.jwt.get_current_user', return_value=usuario_test):
pattern_auth = r"with patch\('app\.utils\.jwt\.get_current_user', return_value=usuario_test\):\s*#[^\n]*\n\s*response = client_with_db\."

# Reemplazar por uso directo de client_with_auth
replacement_auth = r"# Usando autenticación automática\n        response = client_with_auth."

content = re.sub(pattern_auth, replacement_auth, content)

# También cambiar la firma de las funciones que usan client_with_db con usuario_test
# De: def test_xxx(client_with_db, db, planta_test, usuario_test, ...):
# A:  def test_xxx(client_with_auth, db, planta_test, usuario_test, ...):
content = content.replace(
    'def test_verificar_salud_sin_imagen_success(client_with_db, db, planta_test, usuario_test,',
    'def test_verificar_salud_sin_imagen_success(client_with_auth, db, planta_test, usuario_test,'
)

content = content.replace(
    'def test_verificar_salud_con_imagen_principal_success(client_with_db, db, planta_test, usuario_test,',
    'def test_verificar_salud_con_imagen_principal_success(client_with_auth, db, planta_test, usuario_test,'
)

content = content.replace(
    'def test_verificar_salud_con_imagen_subida_success(client_with_db, db, planta_test, usuario_test,',
    'def test_verificar_salud_con_imagen_subida_success(client_with_auth, db, planta_test, usuario_test,'
)

content = content.replace(
    'def test_verificar_salud_planta_no_existe(client_with_db, db, usuario_test',
    'def test_verificar_salud_planta_no_existe(client_with_auth, db, usuario_test'
)

content = content.replace(
    'def test_verificar_salud_planta_otro_usuario(client_with_db, db, planta_test',
    'def test_verificar_salud_planta_otro_usuario(client_with_auth, db, planta_test'
)

content = content.replace(
    'def test_verificar_salud_sin_imagen_principal(client_with_db, db, planta_test, usuario_test',
    'def test_verificar_salud_sin_imagen_principal(client_with_auth, db, planta_test, usuario_test'
)

content = content.replace(
    'def test_verificar_salud_gemini_error(client_with_db, db, planta_test, usuario_test',
    'def test_verificar_salud_gemini_error(client_with_auth, db, planta_test, usuario_test'
)

content = content.replace(
    'def test_verificar_salud_persiste_en_bd(client_with_db, db, planta_test, usuario_test,',
    'def test_verificar_salud_persiste_en_bd(client_with_auth, db, planta_test, usuario_test,'
)

content = content.replace(
    'def test_obtener_historial_basico_success(client_with_db, db, planta_test, usuario_test,',
    'def test_obtener_historial_basico_success(client_with_auth, db, planta_test, usuario_test,'
)

content = content.replace(
    'def test_obtener_historial_paginacion(client_with_db, db, planta_test, usuario_test',
    'def test_obtener_historial_paginacion(client_with_auth, db, planta_test, usuario_test'
)

content = content.replace(
    'def test_obtener_historial_filtro_estado(client_with_db, db, planta_test, usuario_test',
    'def test_obtener_historial_filtro_estado(client_with_auth, db, planta_test, usuario_test'
)

content = content.replace(
    'def test_obtener_historial_filtro_fechas(client_with_db, db, planta_test, usuario_test',
    'def test_obtener_historial_filtro_fechas(client_with_auth, db, planta_test, usuario_test'
)

content = content.replace(
    'def test_obtener_historial_planta_no_existe(client_with_db, db, usuario_test',
    'def test_obtener_historial_planta_no_existe(client_with_auth, db, usuario_test'
)

content = content.replace(
    'def test_obtener_historial_planta_otro_usuario(client_with_db, db, planta_test',
    'def test_obtener_historial_planta_otro_usuario(client_with_auth, db, planta_test'
)

content = content.replace(
    'def test_obtener_historial_estado_invalido(client_with_db, db, planta_test, usuario_test',
    'def test_obtener_historial_estado_invalido(client_with_auth, db, planta_test, usuario_test'
)

content = content.replace(
    'def test_obtener_historial_vacio(client_with_db, db, planta_test, usuario_test',
    'def test_obtener_historial_vacio(client_with_auth, db, planta_test, usuario_test'
)

content = content.replace(
    'def test_obtener_historial_orden_descendente(client_with_db, db, planta_test, usuario_test',
    'def test_obtener_historial_orden_descendente(client_with_auth, db, planta_test, usuario_test'
)

content = content.replace(
    'def test_obtener_historial_limite_maximo(client_with_db, db, usuario_test',
    'def test_obtener_historial_limite_maximo(client_with_auth, db, usuario_test'
)

content = content.replace(
    'def test_flujo_completo_analisis_y_historial(client_with_db, db, planta_test, usuario_test,',
    'def test_flujo_completo_analisis_y_historial(client_with_auth, db, planta_test, usuario_test,'
)

content = content.replace(
    'def test_multiples_analisis_y_filtros(client_with_db, db, planta_test, usuario_test,',
    'def test_multiples_analisis_y_filtros(client_with_auth, db, planta_test, usuario_test,'
)

content = content.replace(
    'def test_historial_con_muchos_registros(client_with_db, db, planta_test, usuario_test',
    'def test_historial_con_muchos_registros(client_with_auth, db, planta_test, usuario_test'
)

# Reemplazar todas las llamadas client_with_db por client_with_auth en el cuerpo
# pero solo para tests que ya tienen usuario_test
content = content.replace('response = client_with_db.post(', 'response = client_with_auth.post(')
content = content.replace('response = client_with_db.get(', 'response = client_with_auth.get(')
content = content.replace('response1 = client_with_db.get(', 'response1 = client_with_auth.get(')
content = content.replace('response2 = client_with_db.get(', 'response2 = client_with_auth.get(')
content = content.replace('response_todos = client_with_db.get(', 'response_todos = client_with_auth.get(')
content = content.replace('response_enfermedades = client_with_db.get(', 'response_enfermedades = client_with_auth.get(')
content = content.replace('response_analisis = client_with_db.post(', 'response_analisis = client_with_auth.post(')
content = content.replace('response_historial = client_with_db.get(', 'response_historial = client_with_auth.get(')
content = content.replace('client_with_db.post(', 'client_with_auth.post(')
content = content.replace('client_with_db.get(', 'client_with_auth.get(')

# Eliminar todos los bloques with patch
lines = content.split('\n')
new_lines = []
skip_until = 0
indent_level = 0

for i, line in enumerate(lines):
    if i < skip_until:
        continue
        
    # Detectar inicio de bloque with patch
    if "with patch('app.utils.jwt.get_current_user'" in line:
        # Calcular indentación del with
        indent_level = len(line) - len(line.lstrip())
        # Agregar comentario simple
        new_lines.append(' ' * indent_level + '# Autenticación manejada por client_with_auth')
        # Buscar el final del bloque with (cuando la indentación vuelve al nivel original)
        for j in range(i + 1, len(lines)):
            next_line = lines[j]
            if next_line.strip() and not next_line.strip().startswith('#'):
                next_indent = len(next_line) - len(next_line.lstrip())
                if next_indent <= indent_level:
                    # Encontramos el final del bloque
                    skip_until = j
                    break
                elif 'response' in next_line or 'client_with_auth' in next_line:
                    # Agregar la línea de response sin indentación extra
                    new_lines.append(' ' * indent_level + next_line.lstrip())
    else:
        new_lines.append(line)

content = '\n'.join(new_lines)

# Guardar el archivo
with open('test_health_endpoints.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Archivo actualizado correctamente")
print("✅ Reemplazados client_with_db → client_with_auth en tests con autenticación")
print("✅ Eliminados bloques with patch() innecesarios")
