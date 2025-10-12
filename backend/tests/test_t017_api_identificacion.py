"""
Tests de Integración - T-017: API de Identificación de Plantas con PlantNet

Tests end-to-end del flujo completo de identificación:
1. Autenticación de usuario
2. Upload de imagen
3. Llamada a PlantNet API
4. Guardado en base de datos
5. Consultas y validaciones

Author: Equipo Plantitas
Date: Diciembre 2024
Version: 0.1.0
"""
import pytest
import os
from pathlib import Path
from io import BytesIO
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.models import Base, Usuario, Imagen, Especie, Identificacion
from app.schemas.plantnet import PlantNetIdentificacionResponse


# ==================== Fixtures ====================

@pytest.fixture(scope="function")
def engine():
    """Crea un engine SQLAlchemy con base de datos SQLite en memoria."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture(scope="function")
def session(engine):
    """Crea una sesión de base de datos para tests."""
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def client():
    """Cliente de prueba para FastAPI"""
    return TestClient(app)


@pytest.fixture
def usuario_autenticado(client, session):
    """Crea un usuario y retorna su token de autenticación"""
    # Registrar usuario
    datos_registro = {
        "nombre_usuario": "test_plantnet",
        "email": "plantnet@test.com",
        "password": "TestPass123!",
        "nombre_completo": "Usuario Test PlantNet"
    }
    
    response = client.post("/api/auth/register", json=datos_registro)
    assert response.status_code == 201
    
    # Login para obtener token
    datos_login = {
        "nombre_usuario": "test_plantnet",
        "password": "TestPass123!"
    }
    
    response = client.post("/api/auth/login", json=datos_login)
    assert response.status_code == 200
    
    data = response.json()
    return {
        "token": data["access_token"],
        "usuario_id": data["usuario"]["id"],
        "headers": {"Authorization": f"Bearer {data['access_token']}"}
    }


@pytest.fixture
def imagen_test():
    """Crea una imagen de prueba en memoria (sin PIL)"""
    # Crear un BytesIO con contenido fake de JPEG
    # Magic bytes de JPEG: FF D8 FF
    fake_jpeg = b'\xff\xd8\xff\xe0\x00\x10JFIF' + b'\x00' * 100
    img_bytes = BytesIO(fake_jpeg)
    img_bytes.seek(0)
    
    return img_bytes


@pytest.fixture
def mock_plantnet_response():
    """Mock de respuesta exitosa de PlantNet API"""
    return {
        "query": {
            "project": "all",
            "images": ["test_image.jpg"],
            "organs": ["leaf"],
            "includeRelatedImages": False
        },
        "language": "es",
        "preferedReferential": "the-plant-list",
        "switchToProject": None,
        "bestMatch": "Epipremnum aureum (Linden & André) G.S.Bunting",
        "results": [
            {
                "score": 0.5788,
                "species": {
                    "scientificNameWithoutAuthor": "Epipremnum aureum",
                    "scientificNameAuthorship": "(Linden & André) G.S.Bunting",
                    "genus": {
                        "scientificNameWithoutAuthor": "Epipremnum",
                        "scientificNameAuthorship": "",
                        "scientificName": "Epipremnum"
                    },
                    "family": {
                        "scientificNameWithoutAuthor": "Araceae",
                        "scientificNameAuthorship": "",
                        "scientificName": "Araceae"
                    },
                    "commonNames": ["Pothos", "Devil's ivy", "Golden pothos"],
                    "scientificName": "Epipremnum aureum (Linden & André) G.S.Bunting"
                },
                "gbif": {"id": "2856940"},
                "powo": {"id": "64238-1"},
                "iucn": {"id": "195645", "category": "LC"},
                "images": [
                    {
                        "organ": "leaf",
                        "author": "Test Author",
                        "license": "cc-by-sa",
                        "date": {"timestamp": 1234567890, "string": "01/01/2020"},
                        "citation": "Test citation",
                        "url": {
                            "o": "https://example.com/image.jpg",
                            "m": "https://example.com/image_m.jpg",
                            "s": "https://example.com/image_s.jpg"
                        },
                        "score": 0.854
                    }
                ]
            },
            {
                "score": 0.3210,
                "species": {
                    "scientificNameWithoutAuthor": "Philodendron hederaceum",
                    "scientificNameAuthorship": "(Jacq.) Schott",
                    "genus": {
                        "scientificNameWithoutAuthor": "Philodendron",
                        "scientificNameAuthorship": "",
                        "scientificName": "Philodendron"
                    },
                    "family": {
                        "scientificNameWithoutAuthor": "Araceae",
                        "scientificNameAuthorship": "",
                        "scientificName": "Araceae"
                    },
                    "commonNames": ["Heartleaf philodendron"],
                    "scientificName": "Philodendron hederaceum (Jacq.) Schott"
                },
                "images": []
            }
        ],
        "version": "2024-09-15",
        "remainingIdentificationRequests": 498
    }


# ==================== Tests de Endpoints ====================

def test_identificar_desde_imagen_requiere_autenticacion(client):
    """Test: endpoint requiere autenticación"""
    request_data = {
        "imagen_id": 1,
        "organos": ["leaf"],
        "guardar_resultado": True
    }
    
    response = client.post("/api/identificar/desde-imagen", json=request_data)
    assert response.status_code == 403  # FastAPI retorna 403 para no autenticado


def test_identificar_desde_archivo_requiere_autenticacion(client, imagen_test):
    """Test: endpoint de archivo requiere autenticación"""
    files = {"archivo": ("test.jpg", imagen_test, "image/jpeg")}
    data = {"organos": "leaf", "guardar_imagen": "true"}
    
    response = client.post("/api/identificar/desde-archivo", files=files, data=data)
    assert response.status_code == 403  # FastAPI retorna 403 para no autenticado


@patch('app.services.plantnet_service.PlantNetService.identificar_desde_path')
def test_flujo_completo_identificacion_desde_archivo(
    mock_plantnet,
    client,
    usuario_autenticado,
    imagen_test,
    mock_plantnet_response,
    session
):
    """Test: flujo completo - upload imagen → PlantNet → guardar → verificar"""
    # Configurar mock
    mock_plantnet.return_value = PlantNetIdentificacionResponse(**mock_plantnet_response)
    
    # 1. Subir imagen y solicitar identificación
    files = {"archivo": ("potus_test.jpg", imagen_test, "image/jpeg")}
    data = {
        "organos": "leaf",
        "guardar_imagen": "true"
    }
    
    response = client.post(
        "/api/identificar/desde-archivo",
        files=files,
        data=data,
        headers=usuario_autenticado["headers"]
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Verificar estructura de respuesta
    assert "identificacion_id" in data
    assert "especie" in data
    assert "confianza" in data
    assert "confianza_porcentaje" in data
    assert "es_confiable" in data
    assert "plantnet_response" in data
    
    # Verificar datos de la especie
    assert data["especie"]["nombre_cientifico"] == "Epipremnum aureum (Linden & André) G.S.Bunting"
    assert data["especie"]["familia"] == "Araceae"
    assert data["confianza"] == 57.88
    assert data["es_confiable"] == False  # < 70%
    
    # 2. Verificar que se guardó en la base de datos
    identificacion_id = data["identificacion_id"]
    identificacion = session.query(Identificacion).filter_by(id=identificacion_id).first()
    
    assert identificacion is not None
    assert identificacion.usuario_id == usuario_autenticado["usuario_id"]
    assert identificacion.confianza == 57.88
    assert identificacion.origen == "plantnet"
    assert identificacion.validado == False
    
    # 3. Verificar que se creó la especie
    especie = session.query(Especie).filter_by(id=identificacion.especie_id).first()
    assert especie is not None
    assert especie.nombre_cientifico == "Epipremnum aureum (Linden & André) G.S.Bunting"
    assert especie.familia == "Araceae"
    
    # 4. Verificar que se guardó la imagen
    imagen = session.query(Imagen).filter_by(id=identificacion.imagen_id).first()
    assert imagen is not None
    assert imagen.usuario_id == usuario_autenticado["usuario_id"]
    assert "potus_test.jpg" in imagen.nombre_archivo


@patch('app.services.plantnet_service.PlantNetService.identificar_desde_path')
def test_obtener_historial_identificaciones(
    mock_plantnet,
    client,
    usuario_autenticado,
    imagen_test,
    mock_plantnet_response,
    session
):
    """Test: obtener historial de identificaciones del usuario"""
    # Configurar mock
    mock_plantnet.return_value = PlantNetIdentificacionResponse(**mock_plantnet_response)
    
    # Crear 2 identificaciones
    for i in range(2):
        files = {"archivo": (f"test_{i}.jpg", BytesIO(imagen_test.getvalue()), "image/jpeg")}
        data = {"organos": "leaf", "guardar_imagen": "true"}
        
        response = client.post(
            "/api/identificar/desde-archivo",
            files=files,
            data=data,
            headers=usuario_autenticado["headers"]
        )
        assert response.status_code == 200
    
    # Obtener historial
    response = client.get(
        "/api/identificar/historial",
        headers=usuario_autenticado["headers"]
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "total" in data
    assert "identificaciones" in data
    assert data["total"] >= 2
    assert len(data["identificaciones"]) >= 2
    
    # Verificar estructura de cada identificación
    primera = data["identificaciones"][0]
    assert "id" in primera
    assert "fecha" in primera
    assert "confianza" in primera
    assert "especie" in primera
    assert "imagen" in primera


@patch('app.services.plantnet_service.PlantNetService.identificar_desde_path')
def test_obtener_detalle_identificacion(
    mock_plantnet,
    client,
    usuario_autenticado,
    imagen_test,
    mock_plantnet_response,
    session
):
    """Test: obtener detalle completo de una identificación"""
    # Configurar mock
    mock_plantnet.return_value = PlantNetIdentificacionResponse(**mock_plantnet_response)
    
    # Crear identificación
    files = {"archivo": ("test.jpg", imagen_test, "image/jpeg")}
    data = {"organos": "leaf", "guardar_imagen": "true"}
    
    response = client.post(
        "/api/identificar/desde-archivo",
        files=files,
        data=data,
        headers=usuario_autenticado["headers"]
    )
    assert response.status_code == 200
    identificacion_id = response.json()["identificacion_id"]
    
    # Obtener detalle
    response = client.get(
        f"/api/identificar/historial/{identificacion_id}",
        headers=usuario_autenticado["headers"]
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["id"] == identificacion_id
    assert "metadatos_ia" in data
    assert "plantnet_response" in data["metadatos_ia"]


@patch('app.services.plantnet_service.PlantNetService.identificar_desde_path')
def test_validar_identificacion(
    mock_plantnet,
    client,
    usuario_autenticado,
    imagen_test,
    mock_plantnet_response,
    session
):
    """Test: validar una identificación"""
    # Configurar mock
    mock_plantnet.return_value = PlantNetIdentificacionResponse(**mock_plantnet_response)
    
    # Crear identificación
    files = {"archivo": ("test.jpg", imagen_test, "image/jpeg")}
    data = {"organos": "leaf", "guardar_imagen": "true"}
    
    response = client.post(
        "/api/identificar/desde-archivo",
        files=files,
        data=data,
        headers=usuario_autenticado["headers"]
    )
    assert response.status_code == 200
    identificacion_id = response.json()["identificacion_id"]
    
    # Validar identificación
    validar_data = {
        "notas": "Confirmado, es un Pothos"
    }
    
    response = client.post(
        f"/api/identificar/validar/{identificacion_id}",
        json=validar_data,
        headers=usuario_autenticado["headers"]
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["validado"] == True
    assert data["notas_usuario"] == "Confirmado, es un Pothos"
    assert data["fecha_validacion"] is not None
    
    # Verificar en base de datos
    identificacion = session.query(Identificacion).filter_by(id=identificacion_id).first()
    assert identificacion.validado == True
    assert identificacion.notas_usuario == "Confirmado, es un Pothos"


def test_obtener_quota_plantnet(client, usuario_autenticado):
    """Test: obtener información de cuota de PlantNet"""
    response = client.get(
        "/api/identificar/quota",
        headers=usuario_autenticado["headers"]
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "requests_realizados" in data
    assert "requests_restantes" in data
    assert "limite_diario" in data
    assert "porcentaje_usado" in data


@patch('app.services.plantnet_service.PlantNetService.identificar_desde_path')
def test_buscar_o_crear_especie_no_duplica(
    mock_plantnet,
    client,
    usuario_autenticado,
    imagen_test,
    mock_plantnet_response,
    session
):
    """Test: no se duplican especies con mismo nombre científico"""
    # Configurar mock
    mock_plantnet.return_value = PlantNetIdentificacionResponse(**mock_plantnet_response)
    
    # Crear 2 identificaciones de la misma especie
    for i in range(2):
        files = {"archivo": (f"test_{i}.jpg", BytesIO(imagen_test.getvalue()), "image/jpeg")}
        data = {"organos": "leaf", "guardar_imagen": "true"}
        
        response = client.post(
            "/api/identificar/desde-archivo",
            files=files,
            data=data,
            headers=usuario_autenticado["headers"]
        )
        assert response.status_code == 200
    
    # Verificar que solo hay una especie Epipremnum aureum
    especies = session.query(Especie).filter(
        Especie.nombre_cientifico == "Epipremnum aureum (Linden & André) G.S.Bunting"
    ).all()
    
    assert len(especies) == 1


def test_historial_solo_validadas(client, usuario_autenticado, session):
    """Test: filtrar historial por identificaciones validadas"""
    # Crear usuario y obtener ID desde la BD
    usuario = session.query(Usuario).filter_by(id=usuario_autenticado["usuario_id"]).first()
    assert usuario is not None
    
    # Crear especie manualmente
    especie = Especie(
        nombre_comun="Test Plant",
        nombre_cientifico="Plantus testus",
        familia="Testaceae"
    )
    session.add(especie)
    session.commit()
    
    # Crear imagen manualmente
    imagen = Imagen(
        usuario_id=usuario.id,
        ruta_archivo="/test/path.jpg",
        nombre_archivo="test.jpg",
        tipo_mime="image/jpeg",
        tamano_bytes=1000
    )
    session.add(imagen)
    session.commit()
    
    # Crear 2 identificaciones: 1 validada, 1 no validada
    ident1 = Identificacion(
        usuario_id=usuario.id,
        imagen_id=imagen.id,
        especie_id=especie.id,
        confianza=80.0,
        origen="plantnet",
        validado=True
    )
    
    ident2 = Identificacion(
        usuario_id=usuario.id,
        imagen_id=imagen.id,
        especie_id=especie.id,
        confianza=60.0,
        origen="plantnet",
        validado=False
    )
    
    session.add_all([ident1, ident2])
    session.commit()
    
    # Obtener solo validadas
    response = client.get(
        "/api/identificar/historial?solo_validadas=true",
        headers=usuario_autenticado["headers"]
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Verificar que solo hay identificaciones validadas
    for identificacion in data["identificaciones"]:
        assert identificacion["validado"] == True


def test_identificar_imagen_no_existente(client, usuario_autenticado):
    """Test: error al identificar imagen que no existe"""
    request_data = {
        "imagen_id": 99999,
        "organos": ["leaf"],
        "guardar_resultado": True
    }
    
    response = client.post(
        "/api/identificar/desde-imagen",
        json=request_data,
        headers=usuario_autenticado["headers"]
    )
    
    assert response.status_code == 404
    assert "no encontrada" in response.json()["detail"]


def test_validar_identificacion_de_otro_usuario(client, session):
    """Test: no se puede validar identificación de otro usuario"""
    # Crear dos usuarios
    usuario1_data = {
        "nombre_usuario": "user1",
        "email": "user1@test.com",
        "password": "Pass123!",
        "nombre_completo": "User One"
    }
    
    usuario2_data = {
        "nombre_usuario": "user2",
        "email": "user2@test.com",
        "password": "Pass123!",
        "nombre_completo": "User Two"
    }
    
    client_test = TestClient(app)
    
    # Registrar usuarios
    client_test.post("/api/auth/register", json=usuario1_data)
    client_test.post("/api/auth/register", json=usuario2_data)
    
    # Login usuario 1
    response = client_test.post("/api/auth/login", json={
        "nombre_usuario": "user1",
        "password": "Pass123!"
    })
    user1_token = response.json()["access_token"]
    user1_id = response.json()["usuario"]["id"]
    
    # Login usuario 2
    response = client_test.post("/api/auth/login", json={
        "nombre_usuario": "user2",
        "password": "Pass123!"
    })
    user2_token = response.json()["access_token"]
    
    # Crear identificación para usuario 1
    especie = Especie(
        nombre_comun="Test",
        nombre_cientifico="Test test",
        familia="Testaceae"
    )
    session.add(especie)
    session.commit()
    
    imagen = Imagen(
        usuario_id=user1_id,
        ruta_archivo="/test.jpg",
        nombre_archivo="test.jpg",
        tipo_mime="image/jpeg",
        tamano_bytes=1000
    )
    session.add(imagen)
    session.commit()
    
    identificacion = Identificacion(
        usuario_id=user1_id,
        imagen_id=imagen.id,
        especie_id=especie.id,
        confianza=80.0,
        origen="plantnet",
        validado=False
    )
    session.add(identificacion)
    session.commit()
    
    # Intentar validar con usuario 2
    response = client_test.post(
        f"/api/identificar/validar/{identificacion.id}",
        json={"notas": "Intento de validar"},
        headers={"Authorization": f"Bearer {user2_token}"}
    )
    
    assert response.status_code == 404  # No encontrada (no pertenece al usuario)


# ==================== Tests de Rate Limiting ====================

def test_quota_info_estructura(client, usuario_autenticado):
    """Test: estructura de respuesta de quota"""
    response = client.get(
        "/api/identificar/quota",
        headers=usuario_autenticado["headers"]
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Verificar campos requeridos
    assert isinstance(data["requests_realizados"], int)
    assert isinstance(data["requests_restantes"], int)
    assert isinstance(data["limite_diario"], int)
    assert isinstance(data["porcentaje_usado"], (int, float))
    
    # Verificar lógica
    assert data["requests_realizados"] + data["requests_restantes"] == data["limite_diario"]
    assert 0 <= data["porcentaje_usado"] <= 100


# ==================== Tests de Validación ====================

def test_organos_invalidos(client, usuario_autenticado, imagen_test):
    """Test: rechazar órganos inválidos"""
    files = {"archivo": ("test.jpg", imagen_test, "image/jpeg")}
    data = {
        "organos": "invalid_organ",
        "guardar_imagen": "true"
    }
    
    response = client.post(
        "/api/identificar/desde-archivo",
        files=files,
        data=data,
        headers=usuario_autenticado["headers"]
    )
    
    # Debería fallar en validación de PlantNetService
    assert response.status_code in [400, 500]
