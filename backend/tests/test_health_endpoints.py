"""
Tests para endpoints de análisis de salud de plantas con PostgreSQL

Este módulo contiene tests unitarios y de integración para los endpoints:
- POST /api/plantas/{id}/verificar-salud
- GET /api/plantas/{id}/historial-salud

Versión REESCRITA completamente - Sin corrupción.

@author Equipo Backend
@date Noviembre 8, 2025
@version 2.0
"""

import json
import pytest
from unittest.mock import patch
from datetime import datetime, timedelta
from fastapi import status

from app.db.models import Usuario, Planta, Especie, Imagen, AnalisisSalud


# ==================== Fixtures ====================

@pytest.fixture
def mock_gemini_response_saludable():
    """Mock de respuesta de Gemini para planta saludable."""
    return {
        "estado": "saludable",
        "confianza": 85.5,
        "resumen": "La planta muestra signos saludables.",
        "diagnostico_detallado": "Análisis indica excelente condición.",
        "problemas_detectados": [
            {
                "tipo": "luz",  # Requerido: TipoProblema
                "descripcion": "Amarillamiento leve en hojas inferiores",
                "severidad": "leve"  # Correcto: 'leve' no 'baja'
            }
        ],
        "recomendaciones": [
            {
                "tipo": "luz",  # Requerido: TipoProblema
                "descripcion": "Continuar con riego cada 3-4 días y aumentar exposición a luz indirecta",
                "prioridad": "media",  # Correcto: PrioridadRecomendacion
                "urgencia_dias": 7
            }
        ],
        "metadata": {
            "modelo": "gemini-1.5-pro",
            "version_prompt": "v1.0",
            "tiempo_analisis_ms": 1500,
            "con_imagen": False,
            "timestamp": datetime.now().isoformat()
        }
    }


@pytest.mark.unit
def test_verificar_salud_sin_imagen_success(
    client_with_auth, db, planta_test, usuario_test, mock_gemini_response_saludable
):
    """Test: Verificar salud sin imagen - Éxito"""
    with patch('app.services.gemini_service.GeminiService.analizar_salud_planta') as mock_gemini:
        mock_gemini.return_value = mock_gemini_response_saludable
        
        # Para FastAPI, los Form booleans se envían como strings en multipart/form-data
        response = client_with_auth.post(
            f"/api/plantas/{planta_test.id}/verificar-salud",
            data={"incluir_imagen_principal": False}
        )
    
    # Debug: Ver el error si falla
    if response.status_code != status.HTTP_200_OK:
        print(f"❌ Error {response.status_code}: {response.text}")
    
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["estado"] == "saludable"
    assert abs(data["confianza"] - 85.5) < 0.01
    assert "resumen" in data
    assert data["metadata"]["con_imagen"] is False


@pytest.mark.unit
def test_obtener_historial_basico_success(
    client_with_auth, db, planta_test, usuario_test, analisis_salud_test
):
    """Test: Obtener historial básico - Éxito"""
    response = client_with_auth.get(
        f"/api/plantas/{planta_test.id}/historial-salud"
    )
    
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert "analisis" in data
    assert "total" in data
    assert data["planta_id"] == planta_test.id


# ==================== Test Simple para Validar Infraestructura ====================

@pytest.mark.unit
def test_infraestructura_postgresql(db):
    """Test: Verificar que PostgreSQL está funcionando"""
    from sqlalchemy import text
    result = db.execute(text("SELECT 1")).scalar()
    assert result == 1
