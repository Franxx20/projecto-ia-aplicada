"""
Configuración de fixtures compartidos para todos los tests

Este archivo define fixtures de pytest que son compartidos por todos los módulos de test.
Los fixtures incluyen configuración de base de datos, sesiones, clientes HTTP, y datos de prueba.

IMPORTANTE: Los tests deben ejecutarse en Docker con PostgreSQL para paridad con producción.
Usar: python -m pytest (en Docker) o ./tests/docker_test_runner.ps1

@author Equipo Backend
@date Enero 2026
"""

import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.db.models import Base
from app.db.session import get_db


# ==================== Database Fixtures ====================

@pytest.fixture(scope="function")
def engine():
    """
    Crea un engine SQLAlchemy con base de datos PostgreSQL.
    
    CAMBIO IMPORTANTE: Ahora usa PostgreSQL en lugar de SQLite para paridad con producción.
    La URL se obtiene de la variable de entorno DATABASE_URL (configurada en docker-compose.test.yml)
    
    Scope: function - Se crea un nuevo engine para cada test
    
    Yields:
        Engine: SQLAlchemy engine configurado con PostgreSQL
    """
    from sqlalchemy import text
    
    # Obtener URL de base de datos (PostgreSQL en Docker)
    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql://test_user:test_password@localhost:5433/plantitas_test"
    )
    
    engine = create_engine(database_url, echo=False)
    Base.metadata.create_all(engine)
    yield engine
    
    # Limpieza manual para evitar dependencia circular
    with engine.begin() as conn:
        # Desactivar temporalmente las FKs para limpiar
        conn.execute(text("SET session_replication_role = 'replica';"))
        
        # Truncar tablas en orden inverso
        conn.execute(text("TRUNCATE TABLE analisis_salud CASCADE;"))
        conn.execute(text("TRUNCATE TABLE plantas CASCADE;"))
        conn.execute(text("TRUNCATE TABLE identificaciones CASCADE;"))
        conn.execute(text("TRUNCATE TABLE imagenes CASCADE;"))
        conn.execute(text("TRUNCATE TABLE especies CASCADE;"))
        conn.execute(text("TRUNCATE TABLE usuarios CASCADE;"))
        
        # Reactivar FKs
        conn.execute(text("SET session_replication_role = 'origin';"))
    
    engine.dispose()


@pytest.fixture(scope="function")
def db(engine):
    """
    Crea una sesión de base de datos para tests.
    
    Este es el fixture principal que los tests deben usar cuando necesiten
    acceso a la base de datos. Proporciona aislamiento entre tests mediante
    rollback automático.
    
    Scope: function - Se crea una nueva sesión para cada test
    
    Args:
        engine: Engine de SQLAlchemy (fixture)
        
    Yields:
        Session: Sesión de SQLAlchemy para operaciones de BD
        
    Example:
        def test_crear_usuario(db):
            usuario = Usuario(email="test@example.com")
            db.add(usuario)
            db.commit()
            assert usuario.id is not None
    """
    Session = sessionmaker(bind=engine)
    session = Session()
    
    yield session
    
    session.rollback()
    session.close()


@pytest.fixture(scope="function")
def session(engine):
    """
    Alias de 'db' para compatibilidad con tests existentes.
    
    Algunos tests usan 'session' en lugar de 'db'. Este fixture
    asegura que ambos nombres funcionen.
    """
    Session = sessionmaker(bind=engine)
    session = Session()
    
    yield session
    
    session.rollback()
    session.close()


# ==================== Client Fixtures ====================

@pytest.fixture
def client():
    """
    Cliente de prueba para FastAPI.
    
    Proporciona un TestClient que permite hacer requests HTTP a la aplicación
    sin necesidad de levantar un servidor real.
    
    Returns:
        TestClient: Cliente de prueba de FastAPI
        
    Example:
        def test_health_endpoint(client):
            response = client.get("/api/health")
            assert response.status_code == 200
    """
    return TestClient(app)


@pytest.fixture
def client_with_db(db):
    """
    Cliente de prueba con override de dependencia de base de datos.
    
    Sobrescribe la dependencia get_db() de FastAPI para usar la sesión
    de prueba en lugar de la sesión de producción.
    
    Args:
        db: Sesión de base de datos (fixture)
        
    Returns:
        TestClient: Cliente configurado con BD de prueba
        
    Example:
        def test_with_db(client_with_db, db):
            # La app usará automáticamente la BD de prueba
            response = client_with_db.get("/api/usuarios")
            assert response.status_code == 200
    """
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def client_with_auth(db, usuario_test):
    """
    Cliente de prueba con autenticación y base de datos configuradas.
    
    Sobrescribe tanto get_db como get_current_user para tests que requieren
    un usuario autenticado.
    
    Args:
        db: Sesión de base de datos (fixture)
        usuario_test: Usuario autenticado (fixture)
        
    Returns:
        TestClient: Cliente configurado con BD y autenticación
        
    Example:
        def test_protected(client_with_auth):
            response = client_with_auth.get("/api/plantas")
            assert response.status_code == 200
    """
    from app.utils.jwt import get_current_user
    
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    async def override_get_current_user():
        return usuario_test
    
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


# ==================== Authentication Fixtures ====================

@pytest.fixture
def usuario_autenticado(client):
    """
    Crea un usuario y retorna su token de autenticación.
    
    Este fixture es útil para tests que requieren autenticación.
    Registra un usuario nuevo, hace login, y retorna el token JWT
    junto con la información del usuario.
    
    Args:
        client: Cliente de prueba (fixture)
        
    Returns:
        dict: Diccionario con:
            - token (str): JWT access token
            - usuario_id (int): ID del usuario creado
            - headers (dict): Headers listo para usar en requests
            - email (str): Email del usuario
            
    Example:
        def test_protected_endpoint(client, usuario_autenticado):
            response = client.get(
                "/api/protected",
                headers=usuario_autenticado["headers"]
            )
            assert response.status_code == 200
    """
    # Registrar usuario
    datos_registro = {
        "email": "test_auth@example.com",
        "nombre": "Usuario Test Auth",
        "password": "TestPass123!"
    }
    
    response = client.post("/api/auth/register", json=datos_registro)
    
    # Si el usuario ya existe (en tests con scope más amplio), hacer login directamente
    if response.status_code == 409:  # Conflict - usuario ya existe
        pass
    else:
        assert response.status_code == 201, f"Error al registrar: {response.json()}"
    
    # Login para obtener token
    datos_login = {
        "email": "test_auth@example.com",
        "password": "TestPass123!"
    }
    
    response = client.post("/api/auth/login", json=datos_login)
    assert response.status_code == 200, f"Error al hacer login: {response.json()}"
    
    data = response.json()
    
    return {
        "token": data["access_token"],
        "usuario_id": data.get("usuario_id") or data.get("usuario", {}).get("id"),
        "headers": {"Authorization": f"Bearer {data['access_token']}"},
        "email": "test_auth@example.com"
    }


# ==================== Cleanup Fixtures ====================

@pytest.fixture(autouse=True)
def reset_db_state():
    """
    Limpia el estado de la base de datos entre tests.
    
    Este fixture se ejecuta automáticamente (autouse=True) antes y después
    de cada test para asegurar aislamiento completo.
    """
    # Setup: nada que hacer antes
    yield
    # Teardown: limpiar cualquier estado global si es necesario
    pass


# ==================== Configuration ====================

def pytest_configure(config):
    """
    Configuración personalizada de pytest.
    
    Se ejecuta una vez al inicio de la sesión de testing.
    """
    # Configurar markers personalizados
    config.addinivalue_line(
        "markers", "slow: marca tests que son lentos (> 1s)"
    )
    config.addinivalue_line(
        "markers", "integration: marca tests de integración que requieren servicios externos"
    )
    config.addinivalue_line(
        "markers", "unit: marca tests unitarios puros"
    )


def pytest_collection_modifyitems(config, items):
    """
    Modifica la colección de tests antes de ejecutarlos.
    
    Permite agregar markers automáticamente basados en nombres o rutas.
    """
    for item in items:
        # Agregar marker 'unit' a todos los tests que no tienen otros markers
        if not any(item.iter_markers()):
            item.add_marker(pytest.mark.unit)


# ==================== Data Fixtures para Health Endpoints ====================

@pytest.fixture
def usuario_test(db):
    """
    Crea un usuario de prueba para health endpoints.
    
    Genera email único con timestamp+UUID para evitar duplicados.
    """
    import uuid
    from datetime import datetime
    from app.db.models import Usuario
    
    email_unico = f"test_salud_{datetime.utcnow().timestamp()}_{uuid.uuid4().hex[:8]}@example.com"
    
    usuario = Usuario(
        email=email_unico,
        nombre="Usuario Test Salud",
        password_hash="$2b$12$test_hash"
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


@pytest.fixture
def especie_test(db):
    """Crea una especie de prueba."""
    from app.db.models import Especie
    
    # Query-or-create pattern
    especie = db.query(Especie).filter(
        Especie.nombre_cientifico == "Epipremnum aureum"
    ).first()
    
    if not especie:
        especie = Especie(
            nombre_cientifico="Epipremnum aureum",
            nombre_comun="Potus",
            familia="Araceae"
        )
        db.add(especie)
        db.commit()
        db.refresh(especie)
    
    return especie


@pytest.fixture
def planta_test(db, usuario_test, especie_test):
    """Crea una planta de prueba."""
    from app.db.models import Planta
    
    planta = Planta(
        usuario_id=usuario_test.id,
        especie_id=especie_test.id,
        nombre_personal="Potus de Prueba",
        ubicacion="Sala",
        luz_actual="indirecta",
        frecuencia_riego_dias=3,
        notas="Planta para tests"
    )
    db.add(planta)
    db.commit()
    db.refresh(planta)
    return planta


@pytest.fixture
def imagen_test(db, usuario_test):
    """Crea una imagen de prueba."""
    from app.db.models import Imagen
    
    imagen = Imagen(
        usuario_id=usuario_test.id,
        nombre_archivo="test_planta.jpg",
        nombre_blob="images/test_planta.jpg",
        url_blob="https://test.blob.core.windows.net/images/test_planta.jpg",
        content_type="image/jpeg",
        tamano_bytes=1024000,
        container_name="plantitas-imagenes"
    )
    db.add(imagen)
    db.commit()
    db.refresh(imagen)
    return imagen


@pytest.fixture
def analisis_salud_test(db, usuario_test, planta_test, imagen_test):
    """
    Crea un análisis de salud de prueba.
    
    IMPORTANTE: problemas_detectados y recomendaciones deben ser strings JSON.
    """
    import json
    from app.db.models import AnalisisSalud
    
    analisis = AnalisisSalud(
        planta_id=planta_test.id,
        usuario_id=usuario_test.id,
        imagen_id=imagen_test.id,
        estado_salud="saludable",
        confianza=85.5,
        resumen_diagnostico="Planta en buen estado",
        diagnostico_detallado="Análisis detallado...",
        problemas_detectados=json.dumps([
            {
                "nombre": "Test problema",
                "descripcion": "Descripción test",
                "severidad": "baja",
                "confianza": 60.0
            }
        ]),
        recomendaciones=json.dumps([
            {
                "titulo": "Test recomendación",
                "descripcion": "Descripción test",
                "prioridad": "media",
                "implementacion": "corto_plazo"
            }
        ]),
        con_imagen=True,
        modelo_ia_usado="gemini-1.5-pro",
        tiempo_analisis_ms=1500,
        version_prompt="v1.0"
    )
    db.add(analisis)
    db.commit()
    db.refresh(analisis)
    return analisis
