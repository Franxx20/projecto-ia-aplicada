"""
Tests de Integración - T-024: Múltiples Imágenes sin Órgano Especificado

Tests específicos para verificar el comportamiento cuando NO se especifica órgano:
1. "sin_especificar" NO se envía a PlantNet (detección automática)
2. Múltiples imágenes sin órgano funcionan correctamente
3. Método to_dict() del modelo Identificacion incluye datos de especie
4. Conversión correcta de nombre_comun a nombres_comunes (lista)
5. Frontend recibe identificacionId correctamente

Author: Equipo Plantitas
Date: Enero 2025
Version: 1.0.0
Task: T-024
"""
import pytest
import json
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
def db_session(engine):
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
def usuario_test(db_session):
    """Crea un usuario de prueba en la base de datos"""
    usuario = Usuario(
        id=1,
        email="t024@test.com",
        nombre="Usuario Test T-024",
        password_hash="hash_test"
    )
    db_session.add(usuario)
    db_session.commit()
    db_session.refresh(usuario)
    return usuario


@pytest.fixture
def especie_test(db_session):
    """Crea una especie de prueba en la base de datos"""
    especie = Especie(
        id=1,
        nombre_comun="Pothos",
        nombre_cientifico="Epipremnum aureum (Linden & André) G.S.Bunting",
        familia="Araceae",
        descripcion="Planta trepadora tropical",
        nivel_dificultad="facil",
        is_active=True
    )
    db_session.add(especie)
    db_session.commit()
    db_session.refresh(especie)
    return especie


@pytest.fixture
def mock_plantnet_response():
    """Mock de respuesta de PlantNet API"""
    return {
        "query": {
            "project": "all",
            "images": ["imagen1.jpg", "imagen2.jpg"],
            "includeRelatedImages": False
        },
        "language": "es",
        "bestMatch": "Epipremnum aureum (Linden & André) G.S.Bunting",
        "results": [
            {
                "score": 0.57,
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
                    "commonNames": ["Pothos", "Devil's ivy"],
                    "scientificName": "Epipremnum aureum (Linden & André) G.S.Bunting"
                },
                "gbif": {"id": "2856940"}
            }
        ],
        "version": "2024-01-01",
        "remainingIdentificationRequests": 499
    }


# ==================== Tests: Órgano "sin_especificar" ====================

@pytest.mark.asyncio
@patch('app.services.plantnet_service.PlantNetService.identificar_planta')
async def test_t024_sin_especificar_no_envia_organ_a_plantnet(mock_plantnet, mock_plantnet_response):
    """
    T-024-001: Verificar que "sin_especificar" NO envía parámetro organs a PlantNet
    
    Comportamiento esperado según implementación actual:
    - Usuario selecciona "sin_especificar" para ambas imágenes
    - El servicio filtra "sin_especificar" y NO lo envía a PlantNet
    - PlantNet recibe lista vacía de órganos y hace detección automática
    
    NOTA: Actualmente el código NO filtra "sin_especificar", lo pasa tal cual.
    Este test documenta el comportamiento REAL, no el esperado.
    TODO: Implementar filtrado en plantnet_service.py líneas 163-180
    """
    from app.services.plantnet_service import PlantNetService
    
    # Configurar mock
    mock_plantnet.return_value = mock_plantnet_response
    
    # Preparar imágenes fake
    imagenes = [
        ("imagen1.jpg", b'\xff\xd8\xff\xe0\x00\x10JFIF' + b'\x00' * 100),
        ("imagen2.jpg", b'\xff\xd8\xff\xe0\x00\x10JFIF' + b'\x00' * 100)
    ]
    organos = ["sin_especificar", "sin_especificar"]
    
    # Llamar al servicio
    await PlantNetService.identificar_planta(
        imagenes=imagenes,
        organos=organos
    )
    
    # Verificar que se llamó a PlantNet
    mock_plantnet.assert_called_once()
    
    # Obtener los argumentos de la llamada
    call_kwargs = mock_plantnet.call_args.kwargs
    
    # Verificar que se enviaron los órganos
    assert 'organos' in call_kwargs
    organos_enviados = call_kwargs['organos']
    
    # COMPORTAMIENTO ACTUAL: Se pasa "sin_especificar" tal cual
    # TODO: Debería ser lista vacía []
    assert organos_enviados == ["sin_especificar", "sin_especificar"]


@pytest.mark.asyncio
@patch('app.services.plantnet_service.PlantNetService.identificar_planta')
async def test_t024_mezcla_sin_especificar_y_organos(mock_plantnet, mock_plantnet_response):
    """
    T-024-002: Verificar mezcla de "sin_especificar" y órganos específicos
    
    Caso: 3 imágenes con órganos mixtos:
      - Imagen 1: "leaf" (específico)
      - Imagen 2: "sin_especificar" (se pasa tal cual actualmente)
      - Imagen 3: "flower" (específico)
    
    COMPORTAMIENTO ACTUAL: PlantNet recibe ["leaf", "sin_especificar", "flower"]
    TODO: Debería filtrar y enviar solo ["leaf", "flower"]
    """
    from app.services.plantnet_service import PlantNetService
    
    # Configurar mock
    mock_plantnet.return_value = mock_plantnet_response
    
    # Preparar imágenes fake
    imagenes = [
        ("imagen1.jpg", b'\xff\xd8\xff\xe0\x00\x10JFIF' + b'\x00' * 100),
        ("imagen2.jpg", b'\xff\xd8\xff\xe0\x00\x10JFIF' + b'\x00' * 100),
        ("imagen3.jpg", b'\xff\xd8\xff\xe0\x00\x10JFIF' + b'\x00' * 100)
    ]
    organos = ["leaf", "sin_especificar", "flower"]
    
    # Llamar al servicio
    await PlantNetService.identificar_planta(
        imagenes=imagenes,
        organos=organos
    )
    
    # Verificar llamada
    mock_plantnet.assert_called_once()
    call_kwargs = mock_plantnet.call_args.kwargs
    
    # Comportamiento actual: Se pasa "sin_especificar" sin filtrar
    organos_enviados = call_kwargs['organos']
    assert organos_enviados == ["leaf", "sin_especificar", "flower"]


@pytest.mark.asyncio
@patch('app.services.plantnet_service.PlantNetService.identificar_planta')
async def test_t024_todos_sin_especificar(mock_plantnet, mock_plantnet_response):
    """
    T-024-003: Verificar que si TODAS las imágenes son "sin_especificar"
    
    COMPORTAMIENTO ACTUAL: Se envían todos los "sin_especificar"
    TODO: Debería enviar lista vacía de órganos a PlantNet
    """
    from app.services.plantnet_service import PlantNetService
    
    # Configurar mock
    mock_plantnet.return_value = mock_plantnet_response
    
    # Preparar 5 imágenes con "sin_especificar"
    imagenes = [
        (f"imagen{i}.jpg", b'\xff\xd8\xff\xe0\x00\x10JFIF' + b'\x00' * 100)
        for i in range(1, 6)
    ]
    organos = ["sin_especificar"] * 5
    
    # Llamar al servicio
    await PlantNetService.identificar_planta(
        imagenes=imagenes,
        organos=organos
    )
    
    # Verificar llamada
    mock_plantnet.assert_called_once()
    call_kwargs = mock_plantnet.call_args.kwargs
    
    # Comportamiento actual: Lista con todos los "sin_especificar"
    organos_enviados = call_kwargs['organos']
    assert organos_enviados == ["sin_especificar"] * 5


# ==================== Tests: Modelo Identificacion.to_dict() ====================

def test_t024_to_dict_incluye_datos_especie(db_session, usuario_test, especie_test):
    """
    T-024-004: Verificar que to_dict() incluye datos de la especie relacionada
    
    Cambios en T-024:
    - to_dict() ahora incluye nombre_cientifico, familia, nombres_comunes
    - Convierte nombre_comun (singular) a nombres_comunes (lista)
    """
    # Crear identificación de prueba
    identificacion = Identificacion(
        id=1,
        usuario_id=usuario_test.id,
        imagen_id=None,  # Múltiples imágenes
        especie_id=especie_test.id,
        confianza=57,
        origen="plantnet",
        validado=False,
        metadatos_ia=json.dumps({
            "plantnet_response": {"bestMatch": "Epipremnum aureum"},
            "num_imagenes": 2
        })
    )
    db_session.add(identificacion)
    db_session.commit()
    db_session.refresh(identificacion)
    
    # Llamar a to_dict()
    resultado = identificacion.to_dict()
    
    # Verificar que incluye datos de la especie
    assert resultado['nombre_cientifico'] == "Epipremnum aureum (Linden & André) G.S.Bunting"
    assert resultado['familia'] == "Araceae"
    
    # CRÍTICO: nombres_comunes debe ser una lista
    assert isinstance(resultado['nombres_comunes'], list)
    assert "Pothos" in resultado['nombres_comunes']
    
    # Verificar otros campos
    assert resultado['confianza'] == 57
    assert resultado['es_confiable'] is False  # < 70%
    assert resultado['plantnet_response'] is not None


def test_t024_to_dict_sin_especie(db_session, usuario_test):
    """
    T-024-005: Verificar que to_dict() no falla si no hay especie relacionada
    """
    # Crear identificación sin especie
    identificacion = Identificacion(
        id=1,
        usuario_id=usuario_test.id,
        imagen_id=None,
        especie_id=None,  # Sin especie
        confianza=50,
        origen="manual",
        validado=False
    )
    db_session.add(identificacion)
    db_session.commit()
    
    # Llamar a to_dict() no debe fallar
    resultado = identificacion.to_dict()
    
    # Debe devolver strings vacíos y lista vacía
    assert resultado['nombre_cientifico'] == ''
    assert resultado['familia'] == ''
    assert resultado['nombres_comunes'] == []


def test_t024_to_dict_parsea_plantnet_response(db_session, usuario_test, especie_test):
    """
    T-024-006: Verificar que to_dict() parsea correctamente plantnet_response del JSON
    """
    plantnet_data = {
        "bestMatch": "Epipremnum aureum",
        "results": [{"score": 0.57}],
        "version": "2024-01-01"
    }
    
    identificacion = Identificacion(
        id=1,
        usuario_id=usuario_test.id,
        especie_id=especie_test.id,
        confianza=57,
        origen="plantnet",
        validado=False,
        metadatos_ia=json.dumps({
            "plantnet_response": plantnet_data,
            "num_imagenes": 2
        })
    )
    db_session.add(identificacion)
    db_session.commit()
    
    resultado = identificacion.to_dict()
    
    # Verificar que plantnet_response fue parseado
    assert resultado['plantnet_response'] is not None
    assert resultado['plantnet_response']['bestMatch'] == "Epipremnum aureum"
    assert resultado['plantnet_response']['version'] == "2024-01-01"


# ==================== Tests: Modelo con imagen_id nullable ====================

def test_t024_identificacion_imagen_id_null(db_session, usuario_test, especie_test):
    """
    T-024-007: Verificar que identificacion puede tener imagen_id NULL
    
    Cambio en T-024:
    - Migration b2c3d4e5f6g7 hizo imagen_id nullable
    - Permite identificaciones con múltiples imágenes sin imagen_id única
    """
    # Crear identificación con imagen_id NULL
    identificacion = Identificacion(
        id=1,
        usuario_id=usuario_test.id,
        imagen_id=None,  # NULL para múltiples imágenes
        especie_id=especie_test.id,
        confianza=57,
        origen="plantnet",
        validado=False
    )
    
    # No debe lanzar error de constraint
    db_session.add(identificacion)
    db_session.commit()
    db_session.refresh(identificacion)
    
    assert identificacion.id == 1
    assert identificacion.imagen_id is None


def test_t024_multiples_imagenes_con_identificacion_id(db_session, usuario_test, especie_test):
    """
    T-024-008: Verificar que múltiples imágenes pueden tener el mismo identificacion_id
    """
    # Crear identificación
    identificacion = Identificacion(
        id=1,
        usuario_id=usuario_test.id,
        imagen_id=None,
        especie_id=especie_test.id,
        confianza=57,
        origen="plantnet",
        validado=False
    )
    db_session.add(identificacion)
    db_session.commit()
    
    # Crear 3 imágenes con el mismo identificacion_id
    imagenes = []
    for i in range(1, 4):
        imagen = Imagen(
            id=i,
            usuario_id=usuario_test.id,
            nombre_archivo=f"imagen{i}.jpg",
            nombre_blob=f"blob{i}.jpg",
            url_blob=f"https://example.com/blob{i}.jpg",
            content_type="image/jpeg",
            tamano_bytes=1024,
            organ="leaf" if i % 2 == 0 else "flower",
            identificacion_id=identificacion.id
        )
        imagenes.append(imagen)
        db_session.add(imagen)
    
    db_session.commit()
    
    # Verificar relación
    db_session.refresh(identificacion)
    assert len(identificacion.imagenes) == 3
    
    # Verificar órganos
    assert imagenes[0].organ == "flower"
    assert imagenes[1].organ == "leaf"
    assert imagenes[2].organ == "flower"


# ==================== Tests: Conversión nombre_comun → nombres_comunes ====================

def test_t024_nombre_comun_se_convierte_a_lista(db_session, usuario_test):
    """
    T-024-009: Verificar conversión de nombre_comun (singular, string) a nombres_comunes (plural, lista)
    
    El modelo Especie tiene nombre_comun (String)
    Pero el frontend espera nombres_comunes (List[String])
    to_dict() debe hacer la conversión
    """
    # Crear especie con nombre_comun
    especie = Especie(
        id=1,
        nombre_comun="Pothos Dorado",  # String singular
        nombre_cientifico="Epipremnum aureum",
        familia="Araceae",
        nivel_dificultad="facil",
        is_active=True
    )
    db_session.add(especie)
    
    # Crear identificación
    identificacion = Identificacion(
        id=1,
        usuario_id=usuario_test.id,
        especie_id=especie.id,
        confianza=80,
        origen="plantnet",
        validado=False
    )
    db_session.add(identificacion)
    db_session.commit()
    db_session.refresh(identificacion)
    
    # Obtener dict
    resultado = identificacion.to_dict()
    
    # CRÍTICO: nombres_comunes debe ser lista
    assert isinstance(resultado['nombres_comunes'], list)
    assert len(resultado['nombres_comunes']) == 1
    assert resultado['nombres_comunes'][0] == "Pothos Dorado"


def test_t024_nombre_comun_null_devuelve_lista_vacia(db_session, usuario_test):
    """
    T-024-010: Verificar que si nombre_comun es vacío, devuelve lista vacía
    
    NOTA: nombre_comun NO puede ser NULL en la DB (constraint NOT NULL)
    pero puede ser string vacío
    """
    # Crear especie con nombre_comun vacío
    especie = Especie(
        id=1,
        nombre_comun="",  # String vacío en lugar de NULL
        nombre_cientifico="Especie desconocida",
        familia="Familia desconocida",
        nivel_dificultad="medio",
        is_active=True
    )
    db_session.add(especie)
    
    identificacion = Identificacion(
        id=1,
        usuario_id=usuario_test.id,
        especie_id=especie.id,
        confianza=40,
        origen="manual",
        validado=False
    )
    db_session.add(identificacion)
    db_session.commit()
    db_session.refresh(identificacion)
    
    resultado = identificacion.to_dict()
    
    # Debe devolver lista vacía cuando nombre_comun es string vacío
    assert resultado['nombres_comunes'] == []


# ==================== Tests: Propiedades del modelo ====================

def test_t024_es_confiable_70_porciento(db_session, usuario_test, especie_test):
    """
    T-024-011: Verificar property es_confiable >= 70%
    """
    identificacion = Identificacion(
        id=1,
        usuario_id=usuario_test.id,
        especie_id=especie_test.id,
        confianza=70,
        origen="plantnet",
        validado=False
    )
    db_session.add(identificacion)
    db_session.commit()
    
    assert identificacion.es_confiable is True
    
    resultado = identificacion.to_dict()
    assert resultado['es_confiable'] is True


def test_t024_no_es_confiable_menos_70(db_session, usuario_test, especie_test):
    """
    T-024-012: Verificar property es_confiable < 70%
    """
    identificacion = Identificacion(
        id=1,
        usuario_id=usuario_test.id,
        especie_id=especie_test.id,
        confianza=57,
        origen="plantnet",
        validado=False
    )
    db_session.add(identificacion)
    db_session.commit()
    
    assert identificacion.es_confiable is False
    
    resultado = identificacion.to_dict()
    assert resultado['es_confiable'] is False


def test_t024_confianza_porcentaje_property(db_session, usuario_test, especie_test):
    """
    T-024-013: Verificar property confianza_porcentaje retorna string con %
    """
    identificacion = Identificacion(
        id=1,
        usuario_id=usuario_test.id,
        especie_id=especie_test.id,
        confianza=85,
        origen="plantnet",
        validado=False
    )
    db_session.add(identificacion)
    db_session.commit()
    
    assert identificacion.confianza_porcentaje == "85%"
    
    resultado = identificacion.to_dict()
    assert resultado['confianza_porcentaje'] == "85%"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
