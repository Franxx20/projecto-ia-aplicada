"""
Tests de Integración - T-022: Múltiples Imágenes con Parámetro Organ

Tests end-to-end del flujo de identificación con múltiples imágenes:
1. Validación de 1-5 imágenes
2. Parámetro organ por imagen (leaf, flower, fruit, bark, auto, sin_especificar)
3. Conversión de "sin_especificar" a "auto" en PlantNet API
4. Guardado de múltiples imágenes con identificacion_id
5. Validaciones de edge cases (0 imágenes, 6+ imágenes)

Author: Equipo Plantitas
Date: Enero 2025
Version: 1.0.0
Task: T-022
"""
import pytest
from io import BytesIO
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.models import Base, Usuario, Imagen, Especie, Identificacion


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
def usuario_autenticado(client):
    """Crea un usuario y retorna su token de autenticación"""
    # Registrar usuario
    datos_registro = {
        "nombre_usuario": "test_t022",
        "email": "t022@test.com",
        "password": "TestPass123!",
        "nombre_completo": "Usuario Test T-022"
    }
    
    response = client.post("/api/auth/register", json=datos_registro)
    assert response.status_code == 201
    
    # Login para obtener token
    datos_login = {
        "nombre_usuario": "test_t022",
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
def crear_imagen_fake():
    """Factory para crear imágenes fake de prueba"""
    def _crear(nombre="test.jpg"):
        # Magic bytes de JPEG: FF D8 FF
        fake_jpeg = b'\xff\xd8\xff\xe0\x00\x10JFIF' + b'\x00' * 100
        img_bytes = BytesIO(fake_jpeg)
        img_bytes.seek(0)
        img_bytes.name = nombre
        return img_bytes
    return _crear


@pytest.fixture
def mock_plantnet_response_multiple():
    """Mock de respuesta de PlantNet API para múltiples imágenes"""
    return {
        "query": {
            "project": "all",
            "images": ["imagen1.jpg", "imagen2.jpg"],
            "organs": ["auto", "leaf"],
            "includeRelatedImages": False
        },
        "language": "es",
        "bestMatch": "Epipremnum aureum (Linden & André) G.S.Bunting",
        "results": [
            {
                "score": 0.6234,
                "species": {
                    "scientificNameWithoutAuthor": "Epipremnum aureum",
                    "scientificNameAuthorship": "(Linden & André) G.S.Bunting",
                    "genus": {
                        "scientificNameWithoutAuthor": "Epipremnum",
                        "scientificName": "Epipremnum"
                    },
                    "family": {
                        "scientificNameWithoutAuthor": "Araceae",
                        "scientificName": "Araceae"
                    },
                    "commonNames": ["Pothos", "Devil's ivy", "Golden pothos"],
                    "scientificName": "Epipremnum aureum (Linden & André) G.S.Bunting"
                },
                "gbif": {"id": "2856940"},
                "images": [
                    {
                        "organ": "auto",
                        "score": 0.854,
                        "url": {"o": "https://example.com/image1.jpg"}
                    },
                    {
                        "organ": "leaf",
                        "score": 0.792,
                        "url": {"o": "https://example.com/image2.jpg"}
                    }
                ]
            }
        ],
        "version": "2024-01-01 (5.0)",
        "remainingIdentificationRequests": 499
    }


# ==================== Tests: Validaciones Básicas ====================

@pytest.mark.asyncio
async def test_t022_validacion_sin_imagenes(client, usuario_autenticado):
    """
    T-022-001: Validar que rechaza request sin imágenes (0 imágenes)
    """
    response = client.post(
        "/api/identificar/multiple",
        headers=usuario_autenticado["headers"],
        data={"organos": "leaf"},
        files=[]
    )
    
    assert response.status_code == 400
    assert "entre 1 y 5 imágenes" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_t022_validacion_mas_de_5_imagenes(client, usuario_autenticado, crear_imagen_fake):
    """
    T-022-002: Validar que rechaza request con más de 5 imágenes
    """
    # Crear 6 imágenes
    archivos = [
        ("archivos", (f"imagen{i}.jpg", crear_imagen_fake(f"imagen{i}.jpg"), "image/jpeg"))
        for i in range(1, 7)
    ]
    
    response = client.post(
        "/api/identificacion/multiple",
        headers=usuario_autenticado["headers"],
        data={"organos": "leaf"},
        files=archivos
    )
    
    assert response.status_code == 400
    assert "entre 1 y 5 imágenes" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_t022_validacion_organo_invalido(client, usuario_autenticado, crear_imagen_fake):
    """
    T-022-003: Validar que rechaza órganos inválidos
    """
    archivos = [
        ("archivos", ("imagen1.jpg", crear_imagen_fake("imagen1.jpg"), "image/jpeg"))
    ]
    
    response = client.post(
        "/api/identificacion/multiple",
        headers=usuario_autenticado["headers"],
        data={"organos": "invalid_organ"},
        files=archivos
    )
    
    assert response.status_code == 400
    assert "inválido" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_t022_validacion_numero_organos_no_coincide(client, usuario_autenticado, crear_imagen_fake):
    """
    T-022-004: Validar que rechaza si número de órganos no coincide con número de imágenes
    """
    archivos = [
        ("archivos", ("imagen1.jpg", crear_imagen_fake("imagen1.jpg"), "image/jpeg")),
        ("archivos", ("imagen2.jpg", crear_imagen_fake("imagen2.jpg"), "image/jpeg"))
    ]
    
    response = client.post(
        "/api/identificacion/multiple",
        headers=usuario_autenticado["headers"],
        data={"organos": "leaf,flower,fruit"},  # 3 órganos para 2 imágenes
        files=archivos
    )
    
    assert response.status_code == 400
    assert "debe coincidir" in response.json()["detail"].lower()


# ==================== Tests: Funcionalidad Múltiples Imágenes ====================

@pytest.mark.asyncio
@patch('app.services.identificacion_service.ImagenService.guardar_imagen')
@patch('app.services.plantnet_service.PlantNetService.identificar_planta')
@patch('app.services.imagen_service.AzureBlobService.descargar_blob')
async def test_t022_identificar_con_1_imagen(
    mock_descargar,
    mock_plantnet,
    mock_guardar_imagen,
    client,
    usuario_autenticado,
    crear_imagen_fake,
    mock_plantnet_response_multiple
):
    """
    T-022-005: Identificar con 1 imagen (caso mínimo válido)
    """
    # Configurar mocks
    mock_guardar_imagen.return_value = {
        "imagen": MagicMock(
            id=1,
            nombre_archivo="imagen1.jpg",
            nombre_blob="blob1.jpg",
            usuario_id=usuario_autenticado["usuario_id"]
        ),
        "url": "https://example.com/imagen1.jpg"
    }
    mock_descargar.return_value = b'\xff\xd8\xff\xe0\x00\x10JFIF' + b'\x00' * 100
    mock_plantnet.return_value = mock_plantnet_response_multiple
    
    # Crear request
    archivos = [
        ("archivos", ("imagen1.jpg", crear_imagen_fake("imagen1.jpg"), "image/jpeg"))
    ]
    
    response = client.post(
        "/api/identificacion/multiple",
        headers=usuario_autenticado["headers"],
        data={"organos": "leaf"},
        files=archivos
    )
    
    assert response.status_code == 201
    data = response.json()
    
    # Verificar estructura de respuesta
    assert "identificacion_id" in data
    assert "especie" in data
    assert "confianza" in data
    assert "imagenes" in data
    assert len(data["imagenes"]) == 1
    assert data["imagenes"][0]["organ"] == "leaf"


@pytest.mark.asyncio
@patch('app.services.identificacion_service.ImagenService.guardar_imagen')
@patch('app.services.plantnet_service.PlantNetService.identificar_planta')
@patch('app.services.imagen_service.AzureBlobService.descargar_blob')
async def test_t022_identificar_con_5_imagenes(
    mock_descargar,
    mock_plantnet,
    mock_guardar_imagen,
    client,
    usuario_autenticado,
    crear_imagen_fake,
    mock_plantnet_response_multiple
):
    """
    T-022-006: Identificar con 5 imágenes (caso máximo válido)
    """
    # Configurar mocks para 5 imágenes
    def guardar_imagen_side_effect(db, usuario_id, archivo):
        idx = int(archivo.filename.replace("imagen", "").replace(".jpg", ""))
        return {
            "imagen": MagicMock(
                id=idx,
                nombre_archivo=archivo.filename,
                nombre_blob=f"blob{idx}.jpg",
                usuario_id=usuario_id
            ),
            "url": f"https://example.com/{archivo.filename}"
        }
    
    mock_guardar_imagen.side_effect = guardar_imagen_side_effect
    mock_descargar.return_value = b'\xff\xd8\xff\xe0\x00\x10JFIF' + b'\x00' * 100
    mock_plantnet.return_value = mock_plantnet_response_multiple
    
    # Crear 5 imágenes con diferentes órganos
    archivos = [
        ("archivos", (f"imagen{i}.jpg", crear_imagen_fake(f"imagen{i}.jpg"), "image/jpeg"))
        for i in range(1, 6)
    ]
    organos = "leaf,flower,fruit,bark,auto"
    
    response = client.post(
        "/api/identificacion/multiple",
        headers=usuario_autenticado["headers"],
        data={"organos": organos},
        files=archivos
    )
    
    assert response.status_code == 201
    data = response.json()
    
    # Verificar que se guardaron 5 imágenes
    assert len(data["imagenes"]) == 5
    
    # Verificar que los órganos fueron asignados correctamente
    organos_esperados = ["leaf", "flower", "fruit", "bark", "auto"]
    for idx, imagen in enumerate(data["imagenes"]):
        assert imagen["organ"] == organos_esperados[idx]


# ==================== Tests: Parámetro "sin_especificar" ====================

@pytest.mark.asyncio
@patch('app.services.identificacion_service.ImagenService.guardar_imagen')
@patch('app.services.plantnet_service.PlantNetService.identificar_planta')
@patch('app.services.imagen_service.AzureBlobService.descargar_blob')
async def test_t022_sin_especificar_se_convierte_a_auto(
    mock_descargar,
    mock_plantnet,
    mock_guardar_imagen,
    client,
    usuario_autenticado,
    crear_imagen_fake,
    mock_plantnet_response_multiple
):
    """
    T-022-007: Verificar que "sin_especificar" se convierte a "auto" en PlantNet
    
    Requisito clave de T-022: Cuando el usuario selecciona "sin_especificar" desde la UI,
    el servicio debe enviar "auto" a PlantNet para que detecte automáticamente el órgano.
    """
    # Configurar mocks
    mock_guardar_imagen.return_value = {
        "imagen": MagicMock(
            id=1,
            nombre_archivo="imagen1.jpg",
            nombre_blob="blob1.jpg",
            usuario_id=usuario_autenticado["usuario_id"]
        ),
        "url": "https://example.com/imagen1.jpg"
    }
    mock_descargar.return_value = b'\xff\xd8\xff\xe0\x00\x10JFIF' + b'\x00' * 100
    mock_plantnet.return_value = mock_plantnet_response_multiple
    
    # Crear request con "sin_especificar"
    archivos = [
        ("archivos", ("imagen1.jpg", crear_imagen_fake("imagen1.jpg"), "image/jpeg"))
    ]
    
    response = client.post(
        "/api/identificacion/multiple",
        headers=usuario_autenticado["headers"],
        data={"organos": "sin_especificar"},
        files=archivos
    )
    
    assert response.status_code == 201
    
    # Verificar que PlantNetService.identificar_planta fue llamado con "auto"
    mock_plantnet.assert_called_once()
    llamada_args = mock_plantnet.call_args
    organos_enviados = llamada_args[1]["organos"]  # kwargs
    
    # El servicio debe haber convertido "sin_especificar" a "auto"
    assert organos_enviados == ["auto"]


@pytest.mark.asyncio
@patch('app.services.identificacion_service.ImagenService.guardar_imagen')
@patch('app.services.plantnet_service.PlantNetService.identificar_planta')
@patch('app.services.imagen_service.AzureBlobService.descargar_blob')
async def test_t022_mezcla_sin_especificar_y_organos_especificos(
    mock_descargar,
    mock_plantnet,
    mock_guardar_imagen,
    client,
    usuario_autenticado,
    crear_imagen_fake,
    mock_plantnet_response_multiple
):
    """
    T-022-008: Verificar mezcla de "sin_especificar" y órganos específicos
    
    Caso: Usuario envía 3 imágenes:
      - Imagen 1: leaf (específico)
      - Imagen 2: sin_especificar (debe convertirse a auto)
      - Imagen 3: flower (específico)
    """
    # Configurar mocks para 3 imágenes
    def guardar_imagen_side_effect(db, usuario_id, archivo):
        idx = int(archivo.filename.replace("imagen", "").replace(".jpg", ""))
        return {
            "imagen": MagicMock(
                id=idx,
                nombre_archivo=archivo.filename,
                nombre_blob=f"blob{idx}.jpg",
                usuario_id=usuario_id
            ),
            "url": f"https://example.com/{archivo.filename}"
        }
    
    mock_guardar_imagen.side_effect = guardar_imagen_side_effect
    mock_descargar.return_value = b'\xff\xd8\xff\xe0\x00\x10JFIF' + b'\x00' * 100
    mock_plantnet.return_value = mock_plantnet_response_multiple
    
    # Crear 3 imágenes
    archivos = [
        ("archivos", (f"imagen{i}.jpg", crear_imagen_fake(f"imagen{i}.jpg"), "image/jpeg"))
        for i in range(1, 4)
    ]
    organos = "leaf,sin_especificar,flower"
    
    response = client.post(
        "/api/identificacion/multiple",
        headers=usuario_autenticado["headers"],
        data={"organos": organos},
        files=archivos
    )
    
    assert response.status_code == 201
    
    # Verificar que PlantNetService recibió ["leaf", "auto", "flower"]
    mock_plantnet.assert_called_once()
    llamada_args = mock_plantnet.call_args
    organos_enviados = llamada_args[1]["organos"]
    
    assert organos_enviados == ["leaf", "auto", "flower"]


# ==================== Tests: Aplicación de Órgano Único ====================

@pytest.mark.asyncio
@patch('app.services.identificacion_service.ImagenService.guardar_imagen')
@patch('app.services.plantnet_service.PlantNetService.identificar_planta')
@patch('app.services.imagen_service.AzureBlobService.descargar_blob')
async def test_t022_un_organo_se_aplica_a_todas_las_imagenes(
    mock_descargar,
    mock_plantnet,
    mock_guardar_imagen,
    client,
    usuario_autenticado,
    crear_imagen_fake,
    mock_plantnet_response_multiple
):
    """
    T-022-009: Verificar que un solo órgano se aplica a todas las imágenes
    
    Si el usuario envía solo "leaf" para 3 imágenes, todas deben usar "leaf"
    """
    # Configurar mocks para 3 imágenes
    def guardar_imagen_side_effect(db, usuario_id, archivo):
        idx = int(archivo.filename.replace("imagen", "").replace(".jpg", ""))
        return {
            "imagen": MagicMock(
                id=idx,
                nombre_archivo=archivo.filename,
                nombre_blob=f"blob{idx}.jpg",
                usuario_id=usuario_id
            ),
            "url": f"https://example.com/{archivo.filename}"
        }
    
    mock_guardar_imagen.side_effect = guardar_imagen_side_effect
    mock_descargar.return_value = b'\xff\xd8\xff\xe0\x00\x10JFIF' + b'\x00' * 100
    mock_plantnet.return_value = mock_plantnet_response_multiple
    
    # Crear 3 imágenes con un solo órgano
    archivos = [
        ("archivos", (f"imagen{i}.jpg", crear_imagen_fake(f"imagen{i}.jpg"), "image/jpeg"))
        for i in range(1, 4)
    ]
    
    response = client.post(
        "/api/identificacion/multiple",
        headers=usuario_autenticado["headers"],
        data={"organos": "leaf"},  # Solo un órgano para 3 imágenes
        files=archivos
    )
    
    assert response.status_code == 201
    
    # Verificar que PlantNetService recibió ["leaf", "leaf", "leaf"]
    mock_plantnet.assert_called_once()
    llamada_args = mock_plantnet.call_args
    organos_enviados = llamada_args[1]["organos"]
    
    assert organos_enviados == ["leaf", "leaf", "leaf"]


# ==================== Tests: Guardado en Base de Datos ====================

@pytest.mark.asyncio
@patch('app.services.identificacion_service.ImagenService.guardar_imagen')
@patch('app.services.plantnet_service.PlantNetService.identificar_planta')
@patch('app.services.imagen_service.AzureBlobService.descargar_blob')
async def test_t022_guardado_de_imagenes_con_identificacion_id(
    mock_descargar,
    mock_plantnet,
    mock_guardar_imagen,
    client,
    usuario_autenticado,
    crear_imagen_fake,
    mock_plantnet_response_multiple,
    session
):
    """
    T-022-010: Verificar que las imágenes se guardan con identificacion_id correcto
    
    Después de crear la identificación, todas las imágenes deben tener:
      - identificacion_id apuntando a la identificación creada
      - organ almacenado en la columna organ de la tabla imagenes
    """
    # Configurar mocks
    def guardar_imagen_side_effect(db, usuario_id, archivo):
        imagen = Imagen(
            id=1,
            usuario_id=usuario_id,
            nombre_archivo=archivo.filename,
            nombre_blob="blob_test.jpg",
            tipo_mime="image/jpeg",
            tamano_bytes=1024
        )
        db.add(imagen)
        db.commit()
        return {
            "imagen": imagen,
            "url": "https://example.com/test.jpg"
        }
    
    mock_guardar_imagen.side_effect = guardar_imagen_side_effect
    mock_descargar.return_value = b'\xff\xd8\xff\xe0\x00\x10JFIF' + b'\x00' * 100
    mock_plantnet.return_value = mock_plantnet_response_multiple
    
    # Crear request
    archivos = [
        ("archivos", ("imagen1.jpg", crear_imagen_fake("imagen1.jpg"), "image/jpeg")),
        ("archivos", ("imagen2.jpg", crear_imagen_fake("imagen2.jpg"), "image/jpeg"))
    ]
    
    response = client.post(
        "/api/identificacion/multiple",
        headers=usuario_autenticado["headers"],
        data={"organos": "leaf,flower"},
        files=archivos
    )
    
    assert response.status_code == 201
    data = response.json()
    
    # Verificar que se creó una identificación
    assert data["identificacion_id"] is not None
    identificacion_id = data["identificacion_id"]
    
    # Verificar que las imágenes tienen el identificacion_id y organ
    imagenes_db = session.query(Imagen).filter(
        Imagen.identificacion_id == identificacion_id
    ).all()
    
    assert len(imagenes_db) == 2
    assert imagenes_db[0].organ == "leaf"
    assert imagenes_db[1].organ == "flower"


@pytest.mark.asyncio
@patch('app.services.identificacion_service.ImagenService.guardar_imagen')
@patch('app.services.plantnet_service.PlantNetService.identificar_planta')
@patch('app.services.imagen_service.AzureBlobService.descargar_blob')
async def test_t022_no_guardar_resultado(
    mock_descargar,
    mock_plantnet,
    mock_guardar_imagen,
    client,
    usuario_autenticado,
    crear_imagen_fake,
    mock_plantnet_response_multiple
):
    """
    T-022-011: Verificar que con guardar_resultado=False no se crea identificación
    """
    # Configurar mocks
    mock_guardar_imagen.return_value = {
        "imagen": MagicMock(
            id=1,
            nombre_archivo="imagen1.jpg",
            nombre_blob="blob1.jpg",
            usuario_id=usuario_autenticado["usuario_id"]
        ),
        "url": "https://example.com/imagen1.jpg"
    }
    mock_descargar.return_value = b'\xff\xd8\xff\xe0\x00\x10JFIF' + b'\x00' * 100
    mock_plantnet.return_value = mock_plantnet_response_multiple
    
    # Crear request con guardar_resultado=false
    archivos = [
        ("archivos", ("imagen1.jpg", crear_imagen_fake("imagen1.jpg"), "image/jpeg"))
    ]
    
    response = client.post(
        "/api/identificacion/multiple",
        headers=usuario_autenticado["headers"],
        data={"organos": "leaf", "guardar_resultado": "false"},
        files=archivos
    )
    
    assert response.status_code == 201
    data = response.json()
    
    # No debe haber identificacion_id
    assert data["identificacion_id"] is None


# ==================== Tests: Todos los Órganos Válidos ====================

@pytest.mark.parametrize("organ", [
    "leaf",
    "flower", 
    "fruit",
    "bark",
    "auto",
    "sin_especificar"
])
@pytest.mark.asyncio
@patch('app.services.identificacion_service.ImagenService.guardar_imagen')
@patch('app.services.plantnet_service.PlantNetService.identificar_planta')
@patch('app.services.imagen_service.AzureBlobService.descargar_blob')
async def test_t022_todos_los_organos_validos(
    mock_descargar,
    mock_plantnet,
    mock_guardar_imagen,
    organ,
    client,
    usuario_autenticado,
    crear_imagen_fake,
    mock_plantnet_response_multiple
):
    """
    T-022-012: Verificar que todos los órganos válidos son aceptados
    
    Parametrizado para probar: leaf, flower, fruit, bark, auto, sin_especificar
    """
    # Configurar mocks
    mock_guardar_imagen.return_value = {
        "imagen": MagicMock(
            id=1,
            nombre_archivo="imagen1.jpg",
            nombre_blob="blob1.jpg",
            usuario_id=usuario_autenticado["usuario_id"]
        ),
        "url": "https://example.com/imagen1.jpg"
    }
    mock_descargar.return_value = b'\xff\xd8\xff\xe0\x00\x10JFIF' + b'\x00' * 100
    mock_plantnet.return_value = mock_plantnet_response_multiple
    
    # Crear request
    archivos = [
        ("archivos", ("imagen1.jpg", crear_imagen_fake("imagen1.jpg"), "image/jpeg"))
    ]
    
    response = client.post(
        "/api/identificacion/multiple",
        headers=usuario_autenticado["headers"],
        data={"organos": organ},
        files=archivos
    )
    
    assert response.status_code == 201
    
    # Si el órgano era "sin_especificar", PlantNet debe recibir "auto"
    mock_plantnet.assert_called_once()
    llamada_args = mock_plantnet.call_args
    organos_enviados = llamada_args[1]["organos"]
    
    if organ == "sin_especificar":
        assert organos_enviados == ["auto"]
    else:
        assert organos_enviados == [organ]


# ==================== Tests: Estructura de Respuesta ====================

@pytest.mark.asyncio
@patch('app.services.identificacion_service.ImagenService.guardar_imagen')
@patch('app.services.plantnet_service.PlantNetService.identificar_planta')
@patch('app.services.imagen_service.AzureBlobService.descargar_blob')
async def test_t022_estructura_respuesta_correcta(
    mock_descargar,
    mock_plantnet,
    mock_guardar_imagen,
    client,
    usuario_autenticado,
    crear_imagen_fake,
    mock_plantnet_response_multiple
):
    """
    T-022-013: Verificar que la respuesta tiene la estructura correcta según IdentificacionResponse
    """
    # Configurar mocks
    mock_guardar_imagen.return_value = {
        "imagen": MagicMock(
            id=1,
            nombre_archivo="imagen1.jpg",
            nombre_blob="blob1.jpg",
            usuario_id=usuario_autenticado["usuario_id"]
        ),
        "url": "https://example.com/imagen1.jpg"
    }
    mock_descargar.return_value = b'\xff\xd8\xff\xe0\x00\x10JFIF' + b'\x00' * 100
    mock_plantnet.return_value = mock_plantnet_response_multiple
    
    # Crear request
    archivos = [
        ("archivos", ("imagen1.jpg", crear_imagen_fake("imagen1.jpg"), "image/jpeg"))
    ]
    
    response = client.post(
        "/api/identificacion/multiple",
        headers=usuario_autenticado["headers"],
        data={"organos": "leaf"},
        files=archivos
    )
    
    assert response.status_code == 201
    data = response.json()
    
    # Verificar campos requeridos según IdentificacionResponse
    assert "identificacion_id" in data
    assert "especie" in data
    assert "confianza" in data
    assert "confianza_porcentaje" in data
    assert "es_confiable" in data
    assert "imagenes" in data
    assert "fecha_identificacion" in data
    assert "validado" in data
    assert "origen" in data
    assert "metadatos_plantnet" in data
    
    # Verificar estructura de especie
    assert "nombre_cientifico" in data["especie"]
    assert "nombre_comun" in data["especie"]
    assert "familia" in data["especie"]
    
    # Verificar estructura de imágenes
    for imagen in data["imagenes"]:
        assert "id" in imagen
        assert "url" in imagen
        assert "organ" in imagen
        assert "nombre_archivo" in imagen
    
    # Verificar metadatos de PlantNet
    assert "version" in data["metadatos_plantnet"]
    assert "proyecto" in data["metadatos_plantnet"]
    assert "resultados_alternativos" in data["metadatos_plantnet"]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
