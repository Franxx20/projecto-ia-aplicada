#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script temporal para corregir los tests de refresh_logout
Reemplaza /auth/ por /api/auth/ y agrega la fixture client
"""

import re

# Leer el archivo
with open('tests/test_t003c_refresh_logout.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Reemplazar endpoints
content = content.replace('client.post("/auth/', 'client.post("/api/auth/')

# Actualizar docstrings
content = content.replace('"""Tests del endpoint POST /auth/', '"""Tests del endpoint POST /api/auth/')

# Agregar client fixture a los métodos de test que no lo tengan
# Pattern: def test_nombre(self, ...otros params)
# Reemplazo: def test_nombre(self, client, ...otros params)
content = re.sub(
    r'def (test_\w+)\(self,\s+(?!client)',  # Si después de 'self, ' no viene 'client'
    r'def \1(self, client, ',  # Agregar 'client, '
    content
)

# Escribir el archivo corregido
with open('tests/test_t003c_refresh_logout.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Archivo corregido exitosamente")
print("- Endpoints actualizados a /api/auth/")
print("- Fixture 'client' agregada a métodos de test")
